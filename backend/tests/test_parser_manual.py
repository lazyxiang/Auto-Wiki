import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.app.services.parser import CodeParser

def test_python_parsing():
    print("Testing Python Parsing...")
    code = """
import os

class MyClass:
    def my_method(self):
        return True

def my_function():
    print("Hello")
"""
    parser = CodeParser()
    root = parser.parse_code(code, 'python')
    assert root is not None
    
    definitions = parser.extract_definitions(root, 'python', code)
    print(f"Found {len(definitions)} definitions")
    for d in definitions:
        print(f"- [{d['type']}] {d['name']} (Lines {d['start_line']}-{d['end_line']})")

    names = [d['name'] for d in definitions]
    assert 'MyClass' in names
    assert 'my_method' in names
    assert 'my_function' in names
    print("Python Parsing OK")

def test_typescript_parsing():
    print("\nTesting TypeScript Parsing...")
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
    parser = CodeParser()
    root = parser.parse_code(code, 'typescript')
    assert root is not None
    
    definitions = parser.extract_definitions(root, 'typescript', code)
    print(f"Found {len(definitions)} definitions")
    for d in definitions:
        print(f"- [{d['type']}] {d['name']} (Lines {d['start_line']}-{d['end_line']})")

    names = [d['name'] for d in definitions]
    assert 'UserManager' in names
    assert 'getUser' in names
    assert 'globalFunc' in names
    assert 'User' in names
    print("TypeScript Parsing OK")

if __name__ == "__main__":
    try:
        test_python_parsing()
        test_typescript_parsing()
        print("\nALL TESTS PASSED")
    except Exception as e:
        print(f"\nTEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
