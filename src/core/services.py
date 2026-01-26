from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.domain.models import Cart, Movie as DomainMovie
from src.domain.sql_models import Movie as SQLMovie
from src.core.strategies import BackToTheFutureStrategy
from src.core.interfaces import PricingStrategy


class MissingMoviesError(ValueError):
    def __init__(self, missing_movies: list[str]):
        self.missing_movies = missing_movies
        super().__init__(f"Movie(s) not found: {', '.join(missing_movies)}")


class PricingService:
    def __init__(self, strategy: PricingStrategy = None):
        # By default use BTTF strategy, but allow injection
        self.strategy = strategy or BackToTheFutureStrategy()

    async def calculate_price_with_breakdown(
        self, cart_text: str, session: AsyncSession
    ) -> tuple[float, dict]:
        # Initial parse to get titles
        temp_cart = Cart.from_text(cart_text)
        if not temp_cart.items:
            return 0.0, {
                "items": [],
                "bttf_subtotal": 0.0,
                "bttf_discount": 0.0,
                "bttf_total": 0.0,
                "other_total": 0.0,
                "total": 0.0,
            }

        # Normalize titles to lowercase for consistent matching
        titles = [m.title.strip().lower() for m in temp_cart.items]

        # Fetch movies from DB using case-insensitive search
        from sqlalchemy import func
        from sqlalchemy.orm import selectinload

        stmt = (
            select(SQLMovie)
            .where(func.lower(SQLMovie.title).in_(titles))
            .options(selectinload(SQLMovie.series))
        )

        result = await session.execute(stmt)
        sql_movies = result.scalars().all()

        # Map by lowercase title for easy lookup
        movie_map = {m.title.strip().lower(): m for m in sql_movies}

        domain_movies = []
        missing_movies = []

        for temp_movie in temp_cart.items:
            search_title = temp_movie.title.strip().lower()
            sql_movie = movie_map.get(search_title)
            if not sql_movie:
                missing_movies.append(temp_movie.title)
                continue

            series_title = (
                sql_movie.series.title if sql_movie and sql_movie.series else None
            )
            series_id = sql_movie.series_id if sql_movie else None
            price = sql_movie.price
            domain_movie = DomainMovie(
                title=sql_movie.title,
                series_id=series_id,
                price=price,
            )
            # Set series_title after initialization
            domain_movie.series_title = series_title
            domain_movies.append(domain_movie)

        if missing_movies:
            # Join unique missing items to avoid spamming same title
            unique_missing = sorted(set(missing_movies))
            raise MissingMoviesError(unique_missing)

        final_cart = Cart(items=domain_movies)

        # Use strategy to calculate price and get breakdown
        total = self.strategy.calculate_price(final_cart)
        breakdown = self.strategy.get_pricing_breakdown(final_cart)

        return total, breakdown
