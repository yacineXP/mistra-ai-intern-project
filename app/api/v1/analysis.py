import pandas as pd
import uuid
import base64
from fastapi import APIRouter, UploadFile, File, HTTPException, Body, BackgroundTasks
from fastapi.responses import JSONResponse

from app.schemas.analysis_schema import (
    UploadResponse,
    QueryRequest,
    TaskCreationResponse,
    TaskStatusResponse,
    ResultType,
    TaskStatus
)
from app.services.analysis_service import analysis_service
from app.services.sandbox_service import sandbox_service

SESSIONS: dict = {}
TASKS: dict = {}

router = APIRouter()

def run_analysis_task(task_id: str, df: pd.DataFrame, schema: dict, question: str):
    """
    The background worker function that performs the analysis.
    This runs asynchronously after the initial request is accepted.
    """
    try:
        # Step 1: Generate Python code from the user's question
        generated_code = analysis_service.generate_analysis_code(question, schema)

        # Step 2: Execute the generated code in the secure sandbox
        execution_result = sandbox_service.execute_code(generated_code, df)

        # Step 3: Analyze the result and set the final task status
        final_result = {"success": execution_result["success"]}
        if not execution_result["success"]:
            final_result["result_type"] = ResultType.ERROR
            final_result["error"] = execution_result["stderr"]
        elif execution_result["image"]:
            final_result["result_type"] = ResultType.IMAGE
            final_result["image"] = base64.b64encode(execution_result["image"]).decode('utf-8')
        elif execution_result["stdout"]:
            stdout_trimmed = execution_result["stdout"].strip()
            # Heuristic to determine if the output is a single value or a table
            lines = stdout_trimmed.split('\n')
            if len(lines) == 1 and len(stdout_trimmed.split()) == 1:
                final_result["result_type"] = ResultType.SINGLE_VALUE
            else:
                final_result["result_type"] = ResultType.TABLE
            final_result["result"] = stdout_trimmed
        
        TASKS[task_id]["result"] = final_result
        TASKS[task_id]["status"] = TaskStatus.COMPLETED

    except Exception as e:
        TASKS[task_id]["status"] = TaskStatus.FAILED
        TASKS[task_id]["result"] = {"success": False, "result_type": ResultType.ERROR, "error": str(e)}


@router.post("/upload", response_model=UploadResponse)
async def upload_csv(file: UploadFile = File(...)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a CSV.")

    try:
        df = pd.read_csv(file.file)
        session_id = str(uuid.uuid4())
        schema = {col: str(dtype) for col, dtype in df.dtypes.items()}
        SESSIONS[session_id] = {"df": df, "schema": schema}
        return UploadResponse(session_id=session_id, filename=file.filename, columns=schema)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process file: {e}")


@router.post("/query", response_model=TaskCreationResponse, status_code=202)
async def query_data(request: QueryRequest, background_tasks: BackgroundTasks):
    """
    Accepts a query, starts a background task for analysis, and immediately
    returns a task ID.
    """
    session = SESSIONS.get(request.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")
    
    task_id = str(uuid.uuid4())
    TASKS[task_id] = {"status": TaskStatus.PENDING, "result": None}

    background_tasks.add_task(
        run_analysis_task,
        task_id=task_id,
        df=session["df"],
        schema=session["schema"],
        question=request.question
    )
    return TaskCreationResponse(task_id=task_id)


@router.get("/results/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str):
    """
    Allows the client to poll for the result of an analysis task.
    """
    task = TASKS.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")
    
    response_data = task.copy()
    response_data['task_id'] = task_id
    
    return TaskStatusResponse(**response_data)

