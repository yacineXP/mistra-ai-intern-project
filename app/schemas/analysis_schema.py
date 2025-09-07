from pydantic import BaseModel, Field
from typing import Dict, Optional
from enum import Enum

# --- Task Status Enum ---

class TaskStatus(str, Enum):
    """
    Defines the possible statuses of an asynchronous analysis task.
    """
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class ResultType(str, Enum):
    """
    Defines the explicit type of a successful analysis result.
    This allows the frontend to render the data correctly without guesswork.
    """
    TABLE = "table"
    SINGLE_VALUE = "single_value"
    IMAGE = "image"
    ERROR = "error"


# --- API Schemas ---

class UploadResponse(BaseModel):
    """
    Defines the response structure after a successful file upload.
    """
    session_id: str = Field(..., description="A unique identifier for the analysis session.")
    filename: str = Field(..., description="The name of the uploaded file.")
    columns: Dict[str, str] = Field(..., description="A dictionary of column names and their detected data types.")

class QueryRequest(BaseModel):
    """
    Defines the request structure for asking a question about the data.
    """
    session_id: str = Field(..., description="The session ID returned from the upload endpoint.")
    question: str = Field(..., description="The natural language question to be answered.")

class QueryResponse(BaseModel):
    """
    Defines the structure of a successfully executed analysis result.
    This model is nested inside the TaskStatusResponse.
    """
    success: bool
    result_type: Optional[ResultType] = None
    result: Optional[str] = Field(None, description="The text output (stdout) from the executed code.")
    error: Optional[str] = Field(None, description="The error output (stderr) or a high-level error message.")
    image: Optional[str] = Field(None, description="A base64-encoded PNG image, if a plot was generated.")

class TaskCreationResponse(BaseModel):
    """
    Defines the response sent immediately after a query is submitted.
    """
    task_id: str = Field(..., description="A unique identifier for the background task.")

class TaskStatusResponse(BaseModel):
    """
    Defines the response for the /results/{task_id} endpoint.
    """
    task_id: str
    status: TaskStatus
    result: Optional[QueryResponse] = None
