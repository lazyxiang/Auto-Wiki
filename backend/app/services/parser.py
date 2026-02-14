import os
from typing import Dict, List, Optional, Any
from tree_sitter import Language, Parser, Node
import tree_sitter_python
import tree_sitter_typescript
import tree_sitter_javascript
from backend.app.schemas import FileStructure, ClassInfo, FunctionInfo, ImportInfo

class CodeParser:
    def __init__(self):
        self.parsers: Dict[str, Parser] = {}
        self.languages: Dict[str, Language] = {}
        self._initialize_parsers()

    def _initialize_parsers(self):
        """Initialize Tree-sitter parsers for supported languages."""
        try:
            # Python
            py_lang = Language(tree_sitter_python.language())
            self.languages['python'] = py_lang
            self.parsers['python'] = Parser(py_lang)

            # TypeScript
            ts_lang = Language(tree_sitter_typescript.language_typescript())
            self.languages['typescript'] = ts_lang
            self.parsers['typescript'] = Parser(ts_lang)

            # TSX (React)
            tsx_lang = Language(tree_sitter_typescript.language_tsx())
            self.languages['tsx'] = tsx_lang
            self.parsers['tsx'] = Parser(tsx_lang)
            
            # JavaScript
            js_lang = Language(tree_sitter_javascript.language())
            self.languages['javascript'] = js_lang
            self.parsers['javascript'] = Parser(js_lang)
            
        except Exception as e:
            print(f"Error initializing parsers: {e}")

    def get_language_from_ext(self, file_path: str) -> Optional[str]:
        """Map file extension to language string."""
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        if ext in ['.py']:
            return 'python'
        elif ext in ['.ts', '.mts', '.cts']:
            return 'typescript'
        elif ext in ['.tsx']:
            return 'tsx'
        elif ext in ['.js', '.jsx', '.mjs', '.cjs']:
            return 'javascript'
        return None

    def parse_code(self, code: str, language_name: str) -> Optional[Node]:
        """Parse source code into an AST root node."""
        parser = self.parsers.get(language_name)
        if not parser:
            return None
        
        # Tree-sitter expects bytes
        tree = parser.parse(bytes(code, "utf8"))
        return tree.root_node

    def extract_structure(self, code: str, language_name: str, file_path: str) -> FileStructure:
        """
        Extracts structural information (imports, classes, functions) from code.
        """
        root_node = self.parse_code(code, language_name)
        if not root_node:
            return FileStructure(file_path=file_path)
            
        if language_name == 'python':
            return self._extract_python_structure(root_node, code, file_path)
        
        # TODO: Implement structure extraction for JS/TS
        return FileStructure(file_path=file_path)

    def _extract_python_structure(self, root_node: Node, code: str, file_path: str) -> FileStructure:
        code_bytes = bytes(code, "utf8")
        
        imports = self._extract_python_imports(root_node, code_bytes)
        classes = self._extract_python_classes(root_node, code_bytes)
        functions = self._extract_python_functions(root_node, code_bytes)
        
        return FileStructure(
            file_path=file_path,
            imports=imports,
            classes=classes,
            functions=functions
        )

    def _extract_python_imports(self, root_node: Node, code_bytes: bytes) -> List[ImportInfo]:
        imports = []
        
        # Manual traversal
        cursor = root_node.walk()
        self._visit_imports(cursor, imports, code_bytes)
        
        return imports

    def _visit_imports(self, cursor, imports: List[ImportInfo], code_bytes: bytes):
        """Helper to traverse and find import nodes."""
        node = cursor.node
        if node.type == 'import_statement':
            # import os, sys
            for child in node.children:
                if child.type == 'dotted_name':
                    name = child.text.decode('utf8')
                    imports.append(ImportInfo(module=name, type=self._classify_import(name)))
                elif child.type == 'aliased_import':
                    # import pandas as pd
                    name_node = child.child_by_field_name('name')
                    alias_node = child.child_by_field_name('alias')
                    if name_node:
                        name = name_node.text.decode('utf8')
                        alias = alias_node.text.decode('utf8') if alias_node else None
                        imports.append(ImportInfo(module=name, alias=alias, type=self._classify_import(name)))

        elif node.type == 'import_from_statement':
            # from . import x
            # from backend.app import main
            module_name = None
            module_node = node.child_by_field_name('module_name')
            if module_node:
                module_name = module_node.text.decode('utf8')
            else:
                # Check for relative import dots
                # relative_import node usually contains the dots
                rel_node = node.child_by_field_name('relative') # Field might be 'relative' or check type
                if not rel_node:
                    # Fallback scan
                    for child in node.children:
                        if child.type == 'relative_import':
                            rel_node = child
                            break
                
                if rel_node:
                    module_name = rel_node.text.decode('utf8')
            
            # Now find imported names
            # They appear after 'import' keyword
            seen_import = False
            for child in node.children:
                if child.type == 'import':
                    seen_import = True
                    continue
                
                if seen_import:
                    if child.type == 'dotted_name':
                        name = child.text.decode('utf8')
                        imports.append(ImportInfo(
                             module=module_name or ".",
                             name=name,
                             type=self._classify_import(module_name)
                         ))
                    elif child.type == 'aliased_import':
                         name_node = child.child_by_field_name('name')
                         alias_node = child.child_by_field_name('alias')
                         if name_node:
                             name = name_node.text.decode('utf8')
                             alias = alias_node.text.decode('utf8') if alias_node else None
                             imports.append(ImportInfo(
                                 module=module_name or ".", 
                                 name=name, 
                                 alias=alias,
                                 type=self._classify_import(module_name)
                             ))
                    # Sometimes simple names are just identifiers? 
                    # tree-sitter-python usually uses dotted_name even for simple ones in imports?
                    # Let's handle identifier just in case
                    elif child.type == 'identifier':
                        name = child.text.decode('utf8')
                        imports.append(ImportInfo(
                             module=module_name or ".",
                             name=name,
                             type=self._classify_import(module_name)
                         ))

        # Recurse
        if cursor.goto_first_child():
            while True:
                self._visit_imports(cursor, imports, code_bytes)
                if not cursor.goto_next_sibling():
                    break
            cursor.goto_parent()

    def _classify_import(self, module_name: Optional[str]) -> str:
        if not module_name:
            return "local_relative"
        if module_name.startswith("."):
            return "local_relative"
        # Heuristic: simple names often stdlib, dotted often local or 3rd party
        # This is hard to perfect without environment inspection.
        # We'll assume if it starts with 'backend' or 'app' it is local_absolute
        if module_name.startswith("backend") or module_name.startswith("app"):
            return "local_absolute"
        return "stdlib" # Default fallback, graph service filters this anyway or we can improve later

    def _extract_python_classes(self, root_node: Node, code_bytes: bytes) -> List[ClassInfo]:
        classes = []
        
        # Manual traversal
        cursor = root_node.walk()
        self._visit_classes(cursor, classes, code_bytes)
        return classes

    def _visit_classes(self, cursor, classes: List[ClassInfo], code_bytes: bytes):
        if cursor.node.type == 'class_definition':
            node = cursor.node
            name_node = node.child_by_field_name('name')
            name = name_node.text.decode('utf8') if name_node else "Unknown"
            
            bases = []
            superclasses_node = node.child_by_field_name('superclasses')
            if superclasses_node:
                for child in superclasses_node.children:
                    if child.type in ('identifier', 'attribute', 'call'): 
                        # call for complex bases like func()
                        bases.append(child.text.decode('utf8'))
            
            classes.append(ClassInfo(
                name=name,
                bases=bases,
                code=node.text.decode('utf8'),
                start_line=node.start_point[0],
                end_line=node.end_point[0]
            ))
            
        if cursor.goto_first_child():
            while True:
                self._visit_classes(cursor, classes, code_bytes)
                if not cursor.goto_next_sibling():
                    break
            cursor.goto_parent()

    def _extract_python_functions(self, root_node: Node, code_bytes: bytes) -> List[FunctionInfo]:
        functions = []
        # Manual traversal
        cursor = root_node.walk()
        self._visit_functions(cursor, functions, code_bytes)
        return functions

    def _visit_functions(self, cursor, functions: List[FunctionInfo], code_bytes: bytes):
        if cursor.node.type == 'function_definition':
            node = cursor.node
            name_node = node.child_by_field_name('name')
            name = name_node.text.decode('utf8') if name_node else "Unknown"
            
            # Check if it's a method? (inside class)
            # Tree-sitter node doesn't explicitly say "method", but parent is class_definition body
            # We treat all as functions for now, graph service handles hierarchy
            
            args = []
            params_node = node.child_by_field_name('parameters')
            if params_node:
                for child in params_node.children:
                    if child.type in ('identifier', 'typed_parameter', 'default_parameter'):
                        args.append(child.text.decode('utf8'))
            
            functions.append(FunctionInfo(
                name=name,
                args=args,
                code=node.text.decode('utf8'),
                start_line=node.start_point[0],
                end_line=node.end_point[0]
            ))
            
        if cursor.goto_first_child():
            while True:
                self._visit_functions(cursor, functions, code_bytes)
                if not cursor.goto_next_sibling():
                    break
            cursor.goto_parent()

    # Legacy method for Chunker compatibility (optional, or we update chunker)
    def extract_definitions(self, root_node: Node, language_name: str, code: str) -> List[Dict[str, Any]]:
        """
        Legacy wrapper: uses new structure extraction to return old format.
        """
        # We need file_path, but this method signature doesn't have it.
        # This is a problem if we rely on this method.
        # But 'extract_definitions' is called by Chunker.
        # I'll implement a basic traversal here similar to what it was, 
        # OR update Chunker to use extract_structure.
        
        # Let's reuse the logic but return dicts
        definitions = []
        code_bytes = bytes(code, "utf8")
        
        if language_name == 'python':
            # Use shared extraction logic to avoid code duplication
            classes = self._extract_python_classes(root_node, code_bytes)
            functions = self._extract_python_functions(root_node, code_bytes)
            
            for c in classes:
                definitions.append({
                    'type': 'class_definition',
                    'name': c.name,
                    'start_line': c.start_line,
                    'end_line': c.end_line,
                    'code': c.code
                })
            for f in functions:
                definitions.append({
                    'type': 'function_definition',
                    'name': f.name,
                    'start_line': f.start_line,
                    'end_line': f.end_line,
                    'code': f.code
                })

        elif language_name in ['typescript', 'tsx', 'javascript']:
            relevant_types = {
                'function_declaration', 
                'class_declaration', 
                'method_definition',
                'interface_declaration',
                'lexical_declaration'
            }
            cursor = root_node.walk()
            
            def visit_ts(cursor):
                if cursor.node.type in relevant_types:
                    name_node = cursor.node.child_by_field_name('name')
                    name = None
                    if name_node:
                        name = name_node.text.decode('utf8')
                    elif cursor.node.type == 'lexical_declaration':
                         # const x = ...
                         # This is complex, skipping for brevity or need to traverse child
                         pass
                    
                    if name:
                        definitions.append({
                            'type': cursor.node.type,
                            'name': name,
                            'start_line': cursor.node.start_point[0],
                            'end_line': cursor.node.end_point[0],
                            'code': cursor.node.text.decode('utf8')
                        })
                if cursor.goto_first_child():
                    while True:
                        visit_ts(cursor)
                        if not cursor.goto_next_sibling():
                            break
                    cursor.goto_parent()
            visit_ts(cursor)
            
        return definitions
