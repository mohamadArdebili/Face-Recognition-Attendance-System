import sys
import os

# Dynamically resolve project root so this works on any machine / PythonAnywhere account
project_home = os.path.dirname(os.path.abspath(__file__))
if project_home not in sys.path:
    sys.path.insert(0, project_home)

from app import app as application
