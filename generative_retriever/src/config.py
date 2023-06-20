import os
from pathlib import Path
from dotenv import load_dotenv

path_env = os.path.join(os.path.abspath(os.getcwd()), '.env')

load_dotenv("src/.env")
ELASTICSEARCH_HOST = os.getenv("ELASTICSEARCH_HOST")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
