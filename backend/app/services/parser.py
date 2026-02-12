import os
from typing import Dict, List, Optional, Any
from tree_sitter import Language, Parser, Node
import tree_sitter_python
import tree_sitter_typescript
import tree_sitter_javascript

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

    def extract_definitions(self, root_node: Node, language_name: str, code: str) -> List[Dict[str, Any]]:
        """
        Walk the AST and extract class/function definitions.
        Returns a list of definitions with metadata.
        """
        definitions = []
        if not root_node:
            return definitions

        cursor = root_node.walk()
        
        # Define relevant node types for each language
        if language_name == 'python':
            relevant_types = {'function_definition', 'class_definition'}
        elif language_name in ['typescript', 'tsx', 'javascript']:
            relevant_types = {
                'function_declaration', 
                'class_declaration', 
                'method_definition',
                'interface_declaration',
                'lexical_declaration' # For const x = () => {}
            }
        else:
            return definitions

        # Recursive traversal (simple version for now)
        # For a robust solution, we might want to use Tree-sitter Queries
        self._traverse_node(root_node, definitions, relevant_types, code)
        
        return definitions

    def _traverse_node(self, node: Node, definitions: List[Dict], relevant_types: set, code_bytes: str):
        """Recursive AST traversal."""
        if node.type in relevant_types:
            name = self._get_node_name(node, code_bytes)
            if name:
                definitions.append({
                    'type': node.type,
                    'name': name,
                    'start_line': node.start_point[0],
                    'end_line': node.end_point[0],
                    'code': node.text.decode('utf8')
                })

        for child in node.children:
            self._traverse_node(child, definitions, relevant_types, code_bytes)

    def _get_node_name(self, node: Node, code_bytes: str) -> Optional[str]:
        """Extract name from a definition node."""
        # Python: definition -> name node (child_by_field_name('name'))
        # TS/JS: similar
        
        name_node = node.child_by_field_name('name')
        if name_node:
            return name_node.text.decode('utf8')
        
        # Fallback for some JS patterns or if 'name' field isn't used
        # e.g. lexical_declaration might handle `const foo = ...`
        # This is simplified; robust extraction needs queries.
        return None
