from pydantic import BaseModel

class IngestRequest(BaseModel):
    path: str
