import pytest
import time
import base64
from fastapi.testclient import TestClient
from unittest.mock import patch

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.main import app
from app.schemas.analysis_schema import ResultType, TaskStatus

client = TestClient(app)

@pytest.fixture
def mock_services():
    """A pytest fixture to mock the analysis and sandbox services."""
    with patch('app.api.v1.analysis.analysis_service') as mock_analysis, \
         patch('app.api.v1.analysis.sandbox_service') as mock_sandbox:
        yield mock_analysis, mock_sandbox

def test_full_successful_flow_with_table_result(mock_services):
    """
    Tests the entire asynchronous flow from upload to a successful table result.
    """
    mock_analysis, mock_sandbox = mock_services
    mock_analysis.generate_analysis_code.return_value = "print(df.head())"
    mock_sandbox.execute_code.return_value = {
        "success": True, "stdout": "col1,col2\n1,2", "stderr": "", "image": None
    }

    csv_data = "col1,col2\n1,2"
    files = {'file': ('test.csv', csv_data, 'text/csv')}
    response = client.post("/api/v1/upload", files=files)
    assert response.status_code == 200
    session_id = response.json()["session_id"]

    response = client.post("/api/v1/query", json={"session_id": session_id, "question": "Show head"})
    assert response.status_code == 202
    task_id = response.json()["task_id"]

    for _ in range(10):
        response = client.get(f"/api/v1/results/{task_id}")
        assert response.status_code == 200
        result_data = response.json()
        if result_data["status"] == "COMPLETED":
            break
        time.sleep(0.01)

    assert result_data["status"] == "COMPLETED"
    assert result_data["result"]["result_type"] == ResultType.TABLE
    assert result_data["result"]["result"] == "col1,col2\n1,2"

def test_successful_flow_with_image_result(mock_services):
    """
    Tests the flow for a query that successfully generates an image.
    """
    mock_analysis, mock_sandbox = mock_services
    mock_analysis.generate_analysis_code.return_value = "df.plot()"
    mock_sandbox.execute_code.return_value = {
        "success": True, "stdout": "", "stderr": "", "image": b"fakeimagedata"
    }

    files = {'file': ('test.csv', "c,v\n1,2", 'text/csv')}
    response = client.post("/api/v1/upload", files=files)
    session_id = response.json()["session_id"]

    response = client.post("/api/v1/query", json={"session_id": session_id, "question": "plot"})
    task_id = response.json()["task_id"]

    for _ in range(10):
        response = client.get(f"/api/v1/results/{task_id}")
        result_data = response.json()
        if result_data["status"] == "COMPLETED":
            break
        time.sleep(0.01)

    assert result_data["status"] == "COMPLETED"
    assert result_data["result"]["result_type"] == ResultType.IMAGE
    expected_image = base64.b64encode(b"fakeimagedata").decode('utf-8')
    assert result_data["result"]["image"] == expected_image

def test_successful_flow_with_single_value_result(mock_services):
    """
    Tests the flow for a query that successfully returns a single value.
    """
    mock_analysis, mock_sandbox = mock_services
    mock_analysis.generate_analysis_code.return_value = "print(df.shape[0])"
    mock_sandbox.execute_code.return_value = {
        "success": True, "stdout": "1", "stderr": "", "image": None
    }

    files = {'file': ('test.csv', "c,v\n1,2", 'text/csv')}
    response = client.post("/api/v1/upload", files=files)
    session_id = response.json()["session_id"]

    response = client.post("/api/v1/query", json={"session_id": session_id, "question": "count"})
    task_id = response.json()["task_id"]

    for _ in range(10):
        response = client.get(f"/api/v1/results/{task_id}")
        result_data = response.json()
        if result_data["status"] == "COMPLETED":
            break
        time.sleep(0.01)

    assert result_data["status"] == "COMPLETED"
    assert result_data["result"]["result_type"] == ResultType.SINGLE_VALUE
    assert result_data["result"]["result"] == "1"

def test_flow_with_ai_validation_error(mock_services):
    """
    Tests the flow where the AI service determines the query is invalid.
    """
    mock_analysis, _ = mock_services
    error_message = "I'm sorry, I couldn't understand that as a data analysis question."
    mock_analysis.generate_analysis_code.side_effect = ValueError(error_message)

    files = {'file': ('test.csv', "c,v\n1,2", 'text/csv')}
    response = client.post("/api/v1/upload", files=files)
    session_id = response.json()["session_id"]

    response = client.post("/api/v1/query", json={"session_id": session_id, "question": "hey"})
    task_id = response.json()["task_id"]

    for _ in range(10):
        response = client.get(f"/api/v1/results/{task_id}")
        result_data = response.json()
        if result_data["status"] == "FAILED":
            break
        time.sleep(0.01)

    assert result_data["status"] == "FAILED"
    assert result_data["result"]["result_type"] == ResultType.ERROR
    assert error_message in result_data["result"]["error"]

def test_flow_with_ai_service_runtime_error(mock_services):
    """
    Tests the flow where the AI service raises a critical exception during API call.
    """
    mock_analysis, _ = mock_services
    mock_analysis.generate_analysis_code.side_effect = RuntimeError("AI model failed")

    files = {'file': ('test.csv', "c,v\n1,2", 'text/csv')}
    response = client.post("/api/v1/upload", files=files)
    session_id = response.json()["session_id"]

    response = client.post("/api/v1/query", json={"session_id": session_id, "question": "fail"})
    task_id = response.json()["task_id"]

    for _ in range(10):
        response = client.get(f"/api/v1/results/{task_id}")
        result_data = response.json()
        if result_data["status"] == "FAILED":
            break
        time.sleep(0.01)

    assert result_data["status"] == "FAILED"
    assert result_data["result"]["result_type"] == ResultType.ERROR
    assert "AI model failed" in result_data["result"]["error"]

def test_flow_with_sandbox_execution_error(mock_services):
    """
    Tests the flow where the sandboxed code execution returns an error.
    """
    mock_analysis, mock_sandbox = mock_services
    mock_analysis.generate_analysis_code.return_value = "print(df['non_existent_col'])"
    mock_sandbox.execute_code.return_value = {
        "success": False, "stdout": "", "stderr": "KeyError: 'non_existent_col'", "image": None
    }

    files = {'file': ('test.csv', "c,v\n1,2", 'text/csv')}
    response = client.post("/api/v1/upload", files=files)
    session_id = response.json()["session_id"]

    response = client.post("/api/v1/query", json={"session_id": session_id, "question": "bad code"})
    task_id = response.json()["task_id"]

    for _ in range(10):
        response = client.get(f"/api/v1/results/{task_id}")
        result_data = response.json()
        if result_data["status"] == "COMPLETED":
            break
        time.sleep(0.01)
    
    assert result_data["status"] == "COMPLETED"
    assert result_data["result"]["result_type"] == ResultType.ERROR
    assert "KeyError: 'non_existent_col'" in result_data["result"]["error"]

def test_upload_invalid_file_type():
    """
    Tests that uploading a non-CSV file returns a 400 Bad Request error.
    """
    files = {'file': ('test.txt', b'some text data', 'text/plain')}
    response = client.post("/api/v1/upload", files=files)
    assert response.status_code == 400
    assert "Invalid file type" in response.json()["detail"]

def test_query_with_invalid_session_id():
    """
    Tests that submitting a query with a non-existent session ID returns a 404 Not Found error.
    """
    response = client.post("/api/v1/query", json={"session_id": "invalid-session-id", "question": "test"})
    assert response.status_code == 404
    assert "Session not found." in response.json()["detail"]

def test_get_results_for_invalid_task_id():
    """
    Tests that querying for a non-existent task ID returns a 404 Not Found error.
    """
    response = client.get("/api/v1/results/invalid-task-id")
    assert response.status_code == 404
    assert response.json() == {"detail": "Task not found."}

