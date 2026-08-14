"""
telephony/outbound/agent.py — Entrypoint for LiveKit Outbound Telephony Call Agent
"""

import sys
import importlib.util
from pathlib import Path

src_dir = Path(__file__).resolve().parent.parent.parent
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

# Import main agent module explicitly from src/agent.py to avoid self-import conflict
agent_path = src_dir / "agent.py"
spec = importlib.util.spec_from_file_location("main_agent", agent_path)
main_agent = importlib.util.module_from_spec(spec)
sys.modules["main_agent"] = main_agent
spec.loader.exec_module(main_agent)

server = main_agent.server
from livekit.agents import cli

if __name__ == "__main__":
    cli.run_app(server)
