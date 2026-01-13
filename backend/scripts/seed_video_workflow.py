"""
Seed script to create a sample video workflow with all data populated.

Run with: cd backend && uv run python scripts/seed_video_workflow.py
"""

import asyncio
import sys
from pathlib import Path

# Add the backend path for imports
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.models import Organization, VideoWorkflow
from app.services.video_workflow.mocks import (
    MOCK_BRIEF,
    MOCK_CLARIFYING_QUESTIONS,
    MOCK_CONTINUITY_PACK,
    MOCK_SHOT_PLAN,
    MOCK_PROMPT_PACK,
    MOCK_QA_SCORE,
)


async def seed_video_workflow():
    """Create a sample video workflow with complete data."""

    # Get database URL from environment or use default
    import os
    database_url = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./test.db")

    engine = create_async_engine(database_url, echo=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # Get the first organization (or create one if none exists)
        result = await session.execute(select(Organization).limit(1))
        org = result.scalar_one_or_none()

        if not org:
            print("No organization found. Please create an organization first.")
            print("You can do this by signing up in the app.")
            return

        print(f"Using organization: {org.name} ({org.id})")

        # Create the video workflow
        workflow = VideoWorkflow(
            org_id=org.id,
            name="Artisan Coffee Shop Promo",
            current_step=7,  # Completed all steps
            status="completed",
            is_template=False,
            brief={
                **MOCK_BRIEF,
                "clarifying_questions": MOCK_CLARIFYING_QUESTIONS,
            },
            continuity_pack=MOCK_CONTINUITY_PACK,
            shot_plan=MOCK_SHOT_PLAN,
            prompt_pack=MOCK_PROMPT_PACK,
            qa_score=MOCK_QA_SCORE,
            versions=[
                {
                    "step": 2,
                    "version_number": 1,
                    "data": {"brief": MOCK_BRIEF},
                    "created_at": "2024-01-15T10:30:00Z",
                },
                {
                    "step": 5,
                    "version_number": 2,
                    "data": {"prompt_pack": MOCK_PROMPT_PACK},
                    "created_at": "2024-01-15T11:00:00Z",
                },
            ],
        )

        session.add(workflow)
        await session.commit()

        print(f"Created video workflow: {workflow.name} ({workflow.id})")

        # Also create a template version
        template = VideoWorkflow(
            org_id=org.id,
            name="Coffee Shop Template",
            current_step=5,
            status="completed",
            is_template=True,
            brief=MOCK_BRIEF,
            continuity_pack=MOCK_CONTINUITY_PACK,
            shot_plan=MOCK_SHOT_PLAN,
        )

        session.add(template)
        await session.commit()

        print(f"Created template: {template.name} ({template.id})")

        print("\nSeeding complete!")
        print(f"  - 1 complete workflow")
        print(f"  - 1 template")


if __name__ == "__main__":
    asyncio.run(seed_video_workflow())
