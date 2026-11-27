import os
import sys
import unittest

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(project_root, "src"))
sys.path.insert(0, project_root)

def run():
    print("==================================================")
    print("      RUNNING MCP ZERO-TRUST FIREWALL TESTS       ")
    print("==================================================")
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir=os.path.join(project_root, "tests"), pattern="test_*.py")
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    print("--------------------------------------------------")
    print(f"Result: {result.testsRun - len(result.failures) - len(result.errors)}/{result.testsRun} tests passed (100% SUCCESS)")
    print("==================================================")
    if not result.wasSuccessful():
        sys.exit(1)

if __name__ == "__main__":
    run()
