from typing import List, Optional, Union, Literal, Dict, Any
from pydantic import BaseModel, Field

# 1. Action Types

class WriteFileAction(BaseModel):
    type: Literal["write_file"] = "write_file"
    path: str = Field(..., description="Relative file path within workspace")
    content: str = Field(..., description="Full text content to write")

class EditFileAction(BaseModel):
    type: Literal["edit_file"] = "edit_file"
    path: str = Field(..., description="Relative file path within workspace")
    expected_hash: Optional[str] = Field(None, description="SHA256 hash of file before editing")
    content: Optional[str] = Field(None, description="Updated full text content")
    patch: Optional[str] = Field(None, description="Unified diff patch to apply")

class DeleteFileAction(BaseModel):
    type: Literal["delete_file"] = "delete_file"
    path: str = Field(..., description="Relative file or folder path to delete")

class MkdirAction(BaseModel):
    type: Literal["mkdir"] = "mkdir"
    path: str = Field(..., description="Relative folder path to create")

class ReadFileAction(BaseModel):
    type: Literal["read_file"] = "read_file"
    path: str = Field(..., description="Relative file path to read")

class ListFilesAction(BaseModel):
    type: Literal["list_files"] = "list_files"
    path: Optional[str] = Field("", description="Relative directory path to list")

class SearchFilesAction(BaseModel):
    type: Literal["search_files"] = "search_files"
    query: str = Field(..., description="Text query to search across workspace")

class RunCommandAction(BaseModel):
    type: Literal["run_command"] = "run_command"
    command: str = Field(..., description="Command line string to execute")
    timeout: Optional[int] = Field(120, description="Timeout in seconds")

class StartServerAction(BaseModel):
    type: Literal["start_server"] = "start_server"
    name: str = Field(..., description="Identifier name for the background server")
    command: str = Field(..., description="Command to start server")
    port: Optional[int] = Field(None, description="Expected server port")

class StopServerAction(BaseModel):
    type: Literal["stop_server"] = "stop_server"
    name: str = Field(..., description="Identifier name of the background server to stop")

class RunTestsAction(BaseModel):
    type: Literal["run_tests"] = "run_tests"
    command: Optional[str] = Field(None, description="Specific test command to run")

class RunBuildAction(BaseModel):
    type: Literal["run_build"] = "run_build"
    command: Optional[str] = Field(None, description="Specific build command to run")

class GitCheckpointAction(BaseModel):
    type: Literal["git_checkpoint"] = "git_checkpoint"
    message: str = Field(..., description="Checkpoint commit message")

class GitDiffAction(BaseModel):
    type: Literal["git_diff"] = "git_diff"

class GitRollbackAction(BaseModel):
    type: Literal["git_rollback"] = "git_rollback"
    commit_hash: Optional[str] = Field(None, description="Commit hash to rollback to")

class AskUserAction(BaseModel):
    type: Literal["ask_user"] = "ask_user"
    question: str = Field(..., description="Clarification question for the user")

class FinishAction(BaseModel):
    type: Literal["finish"] = "finish"
    summary: Optional[str] = Field("Task completed successfully", description="Summary of completed project")
    verification_passed: bool = Field(True, description="Whether all builds/tests passed")

ActionUnion = Union[
    WriteFileAction,
    EditFileAction,
    DeleteFileAction,
    MkdirAction,
    ReadFileAction,
    ListFilesAction,
    SearchFilesAction,
    RunCommandAction,
    StartServerAction,
    StopServerAction,
    RunTestsAction,
    RunBuildAction,
    GitCheckpointAction,
    GitDiffAction,
    GitRollbackAction,
    AskUserAction,
    FinishAction,
]

# 2. Top-Level Agent Response Schema

class AgentResponse(BaseModel):
    version: str = Field("1.0", description="Protocol version")
    type: Literal["agent_response"] = "agent_response"
    summary: str = Field(..., description="High level summary of the actions taken in this turn")
    actions: List[ActionUnion] = Field(default_factory=list, description="List of structured actions to execute")
    next_task: Optional[str] = Field(None, description="Proposed next task to tackle")
    requires_user: bool = Field(False, description="Whether execution must pause for user input")

# 3. Task Plan Schema

class TaskNode(BaseModel):
    id: str
    title: str
    description: str
    depends_on: List[str] = Field(default_factory=list)

class ProjectPlan(BaseModel):
    project_name: str = Field("project", description="Project name")
    summary: str = Field("Software Architecture Plan", description="Summary of project plan")
    tasks: List[TaskNode] = Field(default_factory=list)
