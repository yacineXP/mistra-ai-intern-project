import pytest
import textwrap
from unittest.mock import patch, MagicMock

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.services.analysis_service import AnalysisService

@pytest.fixture
def sample_schema():
    """Provides a sample DataFrame schema for testing."""
    return {"col1": "int64", "col2": "object"}

@patch('app.services.analysis_service.MistralClient')
def test_generate_analysis_code_success(mock_mistral_client, sample_schema):
    """
    Tests successful code generation when the AI returns a valid code block.
    """
    # Arrange
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "```python\nprint(df['col1'].sum())\n```"
    mock_mistral_client.return_value.chat.return_value = mock_response
    
    service = AnalysisService()
    
    # Act
    result = service.generate_analysis_code("sum of col1", sample_schema)
    
    # Assert
    assert result == "print(df['col1'].sum())"
    service.client.chat.assert_called_once()

@patch('app.services.analysis_service.MistralClient')
def test_generate_code_when_ai_returns_invalid(mock_mistral_client, sample_schema):
    """
    Tests that a ValueError is raised when the AI explicitly returns 'INVALID'.
    """
    # Arrange
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "INVALID"
    mock_mistral_client.return_value.chat.return_value = mock_response

    service = AnalysisService()

    # Act & Assert
    with pytest.raises(ValueError) as excinfo:
        service.generate_analysis_code("a nonsensical question", sample_schema)
    
    assert "I was unable to generate analysis code for your request." in str(excinfo.value)
    assert "Model's Raw Response" in str(excinfo.value)
    assert "INVALID" in str(excinfo.value)

@patch('app.services.analysis_service.MistralClient')
def test_generate_code_when_ai_returns_non_code_text(mock_mistral_client, sample_schema):
    """
    Tests that a ValueError is raised when the AI returns text that isn't valid code.
    """
    # Arrange
    raw_response = "I cannot answer this question."
    mock_response = MagicMock()
    mock_response.choices[0].message.content = raw_response
    mock_mistral_client.return_value.chat.return_value = mock_response

    service = AnalysisService()

    # Act & Assert
    with pytest.raises(ValueError) as excinfo:
        service.generate_analysis_code("another bad question", sample_schema)
    
    assert "I was unable to generate analysis code for your request." in str(excinfo.value)
    assert raw_response in str(excinfo.value)

@patch('app.services.analysis_service.MistralClient')
def test_generate_code_handles_api_error(mock_mistral_client, sample_schema):
    """
    Tests that a RuntimeError is raised when the Mistral client fails.
    """
    # Arrange
    mock_mistral_client.return_value.chat.side_effect = Exception("API connection failed")
    
    service = AnalysisService()

    # Act & Assert
    with pytest.raises(RuntimeError) as excinfo:
        service.generate_analysis_code("any question", sample_schema)
        
    assert "Failed to communicate with Mistral AI: API connection failed" in str(excinfo.value)

@patch('app.services.analysis_service.MistralClient')
def test_code_extraction_from_text_with_markdown(mock_mistral_client, sample_schema):
    """
    Tests that code is correctly extracted from a response containing explanations and markdown.
    """
    # Arrange
    mock_response = MagicMock()
    mock_response.choices[0].message.content = textwrap.dedent("""
    Certainly! Here is the code to get the head of the dataframe:
    ```python
    print(df.head())
    """)