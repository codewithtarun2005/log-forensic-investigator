from fastapi import FastAPI
from pydantic import BaseModel
from query import search_logs, build_attack_story

app = FastAPI()

class LogRequest(BaseModel):
    logs: list[str]
    query: str = "failed login"

@app.post("/analyze")
def analyze_logs(request: LogRequest):

    # Convert logs into chunks
    chunks = ["\n".join(request.logs)]

    # Analyze using your existing logic
    story = build_attack_story(request.query, chunks)

    return {
        "analysis": story,
        "logs": request.logs
    }