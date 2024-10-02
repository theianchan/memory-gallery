import os
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
STABILITY_API_KEY = os.getenv("STABILITY_API_KEY")
PHONE_NUMBER = os.getenv("PHONE_NUMBER")
NUM_MEMORIES = int(os.getenv("NUM_MEMORIES", 4))

base_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.dirname(base_dir)
template_dir = os.path.join(project_root, "templates")
static_dir = os.path.join(project_root, "static")
