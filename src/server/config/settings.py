"""Module for vars"""

# imports
import json
import os

from dotenv import load_dotenv

# global vars
setup_path: str = os.path.join(os.getcwd(), "..", "..", ".setup")
load_dotenv(dotenv_path=os.path.join(setup_path, ".env"))
