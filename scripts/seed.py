import asyncio
from datetime import date
from sqlmodel import select, SQLModel
from src.core.database import engine, init_db, get_session
from src.domain.sql_models import Series, Movie


async def seed_data():
    # Only creating data if not exists or just clearing everything?
    # For now, let's just create if clean or just insert
    # Ideally checking if exists first

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
        # pass

    # Iterate over the async generator to get the session
    async for session in get_session():
        try:
            # Check if data exists
            result = await session.execute(
                select(Series).where(Series.title == "Back to the Future")
            )
            existing_series = result.scalars().first()
            if existing_series:
                print("Data already exists. Skipping.")
                return

            print("Seeding BTTF data...")
            bttf_series = Series(
                title="Back to the Future", description="The legendary time travel saga"
            )
            session.add(bttf_series)
            await session.commit()
            await session.refresh(bttf_series)

            movies = [
                Movie(
                    title="Back to the Future 1",
                    release_date=date(1985, 7, 3),
                    duration_min=116,
                    price=15.0,
                    series=bttf_series,
                    series_index=1,
                ),
                Movie(
                    title="Back to the Future 2",
                    release_date=date(1989, 11, 22),
                    duration_min=108,
                    price=15.0,
                    series=bttf_series,
                    series_index=2,
                ),
                Movie(
                    title="Back to the Future 3",
                    release_date=date(1990, 5, 25),
                    duration_min=118,
                    price=15.0,
                    series=bttf_series,
                    series_index=3,
                ),
            ]

            for movie in movies:
                session.add(movie)

            # Add other movies
            la_chevre = Movie(
                title="La chèvre",
                release_date=date(1981, 12, 9),
                duration_min=91,
                price=20.0,
            )
            session.add(la_chevre)

            await session.commit()
            print("Seeding complete.")
        except Exception as e:
            print(f"Error seeding data: {e}")
            await session.rollback()
        finally:
            break  # Exit generator


if __name__ == "__main__":
    asyncio.run(seed_data())
