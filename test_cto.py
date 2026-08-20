import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
BACKEND_ROOT = PROJECT_ROOT / "backend"

sys.path.insert(0, str(BACKEND_ROOT))

import asyncio

from app.agents.cto.cto_agent import CTOAgent


async def main():
    print("DIRECT CTO TEST")
    print("=" * 70)

    agent = CTOAgent()

    print(f"[CTO] Model: {agent.model}")
    print("[CTO] Sending test task...")

    task = """
Design the current system architecture for the AI Software Company.

Use the supplied project context as the only source of confirmed facts.
Clearly separate confirmed architecture from recommended architecture.

Return the complete required CTO architecture document.
"""

    result = await agent.run(task)

    print("=" * 70)
    print("CTO RESPONSE")
    print("=" * 70)
    print(result)
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
