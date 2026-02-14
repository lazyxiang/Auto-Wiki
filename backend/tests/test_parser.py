import pytest
from backend.app.services.parser import CodeParser
from backend.app.schemas import FileStructure, ImportInfo

@pytest.fixture
def parser():
    return CodeParser()

def test_extract_python_structure(parser):
    code = """
import os
from typing import List, Optional
from .local import Utils
import backend.app.config as cfg

class MyClass(BaseClass):
    def my_method(self, arg1):
        pass

def my_func():
    pass
"""
    structure = parser.extract_structure(code, 'python', 'test.py')
    
    assert isinstance(structure, FileStructure)
    assert structure.file_path == 'test.py'
    
    # Check Imports
    imports = structure.imports
    assert len(imports) >= 4
    
    modules = {i.module for i in imports}
    assert 'os' in modules
    assert 'typing' in modules # from typing import ...
    assert '.local' in modules or '.' in modules # depends on how parser handles relative
    assert 'backend.app.config' in modules

    # Check aliased import
    cfg_import = next((i for i in imports if i.module == 'backend.app.config'), None)
    assert cfg_import is not None
    assert cfg_import.alias == 'cfg'
    
    # Check Classes
    assert len(structure.classes) == 1
    cls = structure.classes[0]
    assert cls.name == 'MyClass'
    assert 'BaseClass' in cls.bases
    assert cls.code is not None
    assert 'class MyClass' in cls.code
    
    # Check Functions
    # MyClass.my_method might be treated as function or method depending on parser logic.
    # Current parser logic:
    # _extract_python_functions uses root_node.walk() and finds 'function_definition'.
    # Methods inside classes ARE 'function_definition' in Tree-sitter Python.
    # So they should appear in structure.functions?
    # Let's verify behavior. Ideally we might want to segregate, but flat list is okay for MVP if IDs are unique.
    
    func_names = {f.name for f in structure.functions}
    assert 'my_func' in func_names
    # Depending on tree traversal order, methods might be included
    
def test_extract_structure_no_code(parser):
    structure = parser.extract_structure("", 'python', 'empty.py')
    assert len(structure.classes) == 0
    assert len(structure.functions) == 0
    assert len(structure.imports) == 0

def test_extract_imports_detailed(parser):
    code = """
from . import sibling
from ..parent import uncle
import sys
    """
    structure = parser.extract_structure(code, 'python', 'imports.py')
    
    # Check relative imports
    imp_sib = next((i for i in structure.imports if i.name == 'sibling'), None)
    # Parser logic: module_name for "from . import sibling" might be "." or None.
    # We need to assert based on actual implementation behavior.
    assert imp_sib is not None
    assert imp_sib.type == 'local_relative'

    imp_sys = next((i for i in structure.imports if i.module == 'sys'), None)
    assert imp_sys is not None
    # 'sys' might be classified as stdlib if heuristic works, or local_absolute/relative based on startswith
    # parser._classify_import says: if startswith backend/app -> local_absolute. else stdlib (heuristic).
    assert imp_sys.type == 'stdlib'

def test_typescript_parsing(parser):
    code = """
interface User {
  id: number;
  name: string;
}

class UserManager {
  constructor() {}
  
  getUser(id: number): User {
    return {id, name: 'Test'};
  }
}

function globalFunc() {
  return true;
}
"""
    structure = parser.extract_structure(code, 'typescript', 'test.ts')
    assert structure is not None
    
    class_names = {c.name for c in structure.classes}
    func_names = {f.name for f in structure.functions}
    
    assert 'UserManager' in class_names
    assert 'globalFunc' in func_names
    # Interfaces might not be captured as classes
