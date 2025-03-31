from fastapi import APIRouter, HTTPException
from langsmith import Client
from pydantic import BaseModel
import os

router = APIRouter()
client = Client()

class Feedback(BaseModel):
    run_id: str
    score: int
    comment: str = ""

@router.get("/projects")
def list_projects():
    projects = client.list_projects()
    return [{"id": p.id, "name": p.name} for p in projects]

@router.get("/recent")
async def get_recent_runs():
    """Get recent runs from LangSmith"""
    try:
        runs = client.list_runs(
            project_name=os.getenv("LANGCHAIN_PROJECT"),
            limit=20
        )
        return [
            {
                "id": run.id,
                "name": run.name,
                "inputs": run.inputs,
                "outputs": run.outputs,
                "start_time": run.start_time,
            }
            for run in runs
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/runs/{project_name}")
def get_llm_calls(project_name: str):
    runs = client.list_runs(
        project_name=project_name,
        execution_order=1,  # LLM calls
        order="desc",
        limit=50
    )
    return [{
        "id": run.id,
        "name": run.name,
        "start_time": str(run.start_time),
        "inputs": run.inputs,
        "outputs": run.outputs
    } for run in runs]

@router.post("/submit")
async def submit_feedback(feedback: Feedback):
    """Submit feedback for a specific run"""
    try:
        client.create_feedback(
            run_id=feedback.run_id,
            key="user_rating",
            score=feedback.score,
            comment=feedback.comment
        )
        return {"success": True, "message": "Feedback submitted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 