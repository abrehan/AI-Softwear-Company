import asyncio
import sys
import traceback

sys.path.insert(0, "backend")

from app.registry.agent_registry import AgentRegistry


async def main():
    registry = AgentRegistry()
    results = []

    print("=" * 70)
    print("AI SOFTWARE COMPANY — AGENT SMOKE TEST")
    print("=" * 70)
    print(f"Agents registered: {len(registry.agents)}")
    print()

    for name, agent_class in registry.agents.items():
        print(f"Testing: {name}")

        try:
            agent = agent_class()

            if not hasattr(agent, "name"):
                raise RuntimeError("Missing agent.name")

            if not hasattr(agent, "role"):
                raise RuntimeError("Missing agent.role")

            if not hasattr(agent, "model"):
                raise RuntimeError("Missing agent.model")

            if not hasattr(agent, "run"):
                raise RuntimeError("Missing agent.run()")

            print(f"  Class : {agent_class.__name__}")
            print(f"  Name  : {agent.name}")
            print(f"  Role  : {agent.role}")
            print(f"  Model : {agent.model}")

            # Lightweight execution test.
            task = (
                "Reply with exactly one short sentence confirming that "
                "you are available for work. Do not invent company facts."
            )

            result = await agent.run(task)

            if result is None:
                raise RuntimeError("Agent returned None")

            result_text = str(result).strip()

            if not result_text:
                raise RuntimeError("Agent returned an empty response")

            print(f"  Result: PASS")
            print(f"  Reply : {result_text[:180]}")
            results.append((name, "PASS", ""))

        except Exception as exc:
            print("  Result: FAIL")
            print(f"  Error : {type(exc).__name__}: {exc}")
            traceback.print_exc()
            results.append((name, "FAIL", str(exc)))

        print("-" * 70)

    passed = sum(1 for _, status, _ in results if status == "PASS")
    failed = sum(1 for _, status, _ in results if status == "FAIL")

    print()
    print("=" * 70)
    print("FINAL RESULT")
    print("=" * 70)
    print(f"PASS: {passed}")
    print(f"FAIL: {failed}")
    print()

    if failed:
        print("FAILED AGENTS:")
        for name, status, error in results:
            if status == "FAIL":
                print(f"  - {name}: {error}")
    else:
        print("ALL AGENTS PASSED")


if __name__ == "__main__":
    asyncio.run(main())