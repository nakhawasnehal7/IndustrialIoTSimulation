# agentModule.py
# Located in: WebApplication/
# Connects to: langChainAgent/IoTMaintenanceAgent.py

import sys
import os

# ── Path Setup ───────────────────────────────────────────────
# WebApplication/ → project root → langChainAgent/
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
AGENT_DIR = os.path.join(PROJECT_ROOT, 'langChainAgent')
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
sys.path.append(PROJECT_ROOT)
# Add langChainAgent to Python path so `from ss import ...` works
if AGENT_DIR not in sys.path:
    sys.path.insert(0, AGENT_DIR)

# Change working dir so IoTMaintenanceAgent.py's relative DB path '../data/iot_maintenance.db' resolves
os.chdir(AGENT_DIR)

# ── Import Agent ─────────────────────────────────────────────
try:
    from langChainAgent.IoTMaintenanceAgent import IoTMaintenanceAgent
    AGENT_AVAILABLE = True
except ImportError as e:
    AGENT_AVAILABLE = False
    IMPORT_ERROR = str(e)

# ── Singleton Instance ────────────────────────────────────────
_agent_instance = None


def get_agent() -> "IoTMaintenanceAgent":
    """Load agent once and reuse across all Streamlit reruns."""
    global _agent_instance
    if not AGENT_AVAILABLE:
        raise RuntimeError(f"Agent module could not be loaded: {IMPORT_ERROR}")
    if _agent_instance is None:
        _agent_instance = IoTMaintenanceAgent()
    return _agent_instance


# ── Public API ────────────────────────────────────────────────
def run_agent_query(question: str) -> str:
    """
    Send a question to the IoT maintenance agent and return the response.
    Called from application.py (Streamlit UI).
    """
    if not question or not question.strip():
        return "Please enter a valid question."
    try:
        agent = get_agent()
        response = agent.query(question.strip())
        return response if response else "No response from agent."
    except RuntimeError as e:
        return f"Setup error: {str(e)}"
    except Exception as e:
        return f"Agent error: {str(e)}\n\nMake sure Ollama is running: `ollama serve`"


def is_agent_available() -> bool:
    """Check if agent loaded successfully — use in UI to show/hide the page."""
    return AGENT_AVAILABLE


def get_agent_status() -> dict:
    """
    Returns agent status info for display in the UI.
    """
    return {
        "available": AGENT_AVAILABLE,
        "ollama_model": "mistral",
        "agent_dir": AGENT_DIR,
        "data_dir": DATA_DIR,
        "error": IMPORT_ERROR if not AGENT_AVAILABLE else None
    }
