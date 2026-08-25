import asyncio
from app.generators.main_generator import MainGenerator

async def main():
    generator = MainGenerator()

    result = await generator.generate(
        filepath="backend/app/main.py",
        ceo_summary="Multi-tenant hotel booking platform.",
        project_plan="Create the backend foundation.",
        architecture="Use FastAPI for the AI Software Company internal API. Target product architecture must remain separate.",
        task="Generate the main FastAPI application file."
    )

    print("===== GENERATED MAIN.PY =====")
    print(result)
    print("===== LENGTH =====")
    print(len(result))

asyncio.run(main())
