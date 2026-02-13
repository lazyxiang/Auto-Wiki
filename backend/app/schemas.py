from pydantic import BaseModel, HttpUrl

class IngestRequest(BaseModel):
    repo_url: str
