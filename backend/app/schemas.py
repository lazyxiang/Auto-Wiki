from pydantic import BaseModel, HttpUrl, Field
from typing import List, Optional, Dict, Any
from enum import Enum

class IngestRequest(BaseModel):
    repo_url: str

class NodeType(str, Enum):
    FILE = "FILE"
    CLASS = "CLASS"
    FUNCTION = "FUNCTION"

class EdgeType(str, Enum):
    DEFINES = "DEFINES"
    INHERITS = "INHERITS"
    IMPORTS = "IMPORTS"

class GraphNode(BaseModel):
    id: str
    type: NodeType
    attributes: Dict[str, Any] = Field(default_factory=dict)

class GraphEdge(BaseModel):
    source: str
    target: str
    type: EdgeType
    attributes: Dict[str, Any] = Field(default_factory=dict)

class GraphData(BaseModel):
    nodes: List[GraphNode]
    edges: List[GraphEdge]

class ImportInfo(BaseModel):
    module: str
    name: Optional[str] = None # For 'from module import name'
    alias: Optional[str] = None
    type: str # 'stdlib', 'local_relative', 'local_absolute', 'third_party'

class ClassInfo(BaseModel):
    name: str
    bases: List[str]
    docstring: Optional[str] = None
    code: Optional[str] = None # Full source code of the class
    start_line: int
    end_line: int

class FunctionInfo(BaseModel):
    name: str
    args: List[str]
    return_type: Optional[str] = None
    docstring: Optional[str] = None
    code: Optional[str] = None # Full source code of the function
    start_line: int
    end_line: int

class FileStructure(BaseModel):
    file_path: str
    classes: List[ClassInfo] = Field(default_factory=list)
    functions: List[FunctionInfo] = Field(default_factory=list)
    imports: List[ImportInfo] = Field(default_factory=list)
