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

    async def calculate_price(self, cart_text: str, session: AsyncSession) -> float:
        # Initial parse to get titles
        temp_cart = Cart.from_text(cart_text)
        if not temp_cart.items:
            return 0.0

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
            price = sql_movie.price
            domain_movies.append(
                DomainMovie(
                    title=sql_movie.title, series_title=series_title, price=price
                )
            )

        if missing_movies:
            # Join unique missing items to avoid spamming same title
            unique_missing = sorted(set(missing_movies))
            raise MissingMoviesError(unique_missing)

        final_cart = Cart(items=domain_movies)
        return self.strategy.calculate_price(final_cart)

    async def calculate_price_with_breakdown(
        self, cart_text: str, session: AsyncSession
    ) -> tuple[float, dict]:
        # Initial parse to get titles
        temp_cart = Cart.from_text(cart_text)
        if not temp_cart.items:
            return 0.0, {
                "items": [],
                "bttf_subtotal": 0.0,
                "bttf_count": 0,
                "discount_percentage": 0.0,
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
            price = sql_movie.price
            domain_movies.append(
                DomainMovie(
                    title=sql_movie.title, series_title=series_title, price=price
                )
            )

        if missing_movies:
            # Join unique missing items to avoid spamming same title
            unique_missing = sorted(set(missing_movies))
            raise MissingMoviesError(unique_missing)

        final_cart = Cart(items=domain_movies)

        # Calculate with breakdown details
        bttf_movies = [m for m in final_cart.items if m.is_bttf]
        other_movies = [m for m in final_cart.items if not m.is_bttf]

        # Build items breakdown with counts for duplicates
        items_breakdown = []
        seen_items = {}

        for movie in final_cart.items:
            key = (movie.title, movie.series_title, movie.price)
            if key not in seen_items:
                seen_items[key] = {
                    "title": movie.title,
                    "series": movie.series_title,
                    "price": movie.price,
                    "is_bttf": movie.is_bttf,
                    "count": 0,
                }
            seen_items[key]["count"] += 1

        items_breakdown = list(seen_items.values())

        # Calculate BTTF logic
        unique_bttf_titles = {m.title for m in bttf_movies}
        distinct_count = len(unique_bttf_titles)

        discount = 0.0
        if distinct_count == 2:
            discount = 0.10
        elif distinct_count >= 3:
            discount = 0.20

        bttf_subtotal = sum(m.price for m in bttf_movies)
        discount_amount = bttf_subtotal * discount
        bttf_total = bttf_subtotal - discount_amount

        other_total = sum(m.price for m in other_movies)
        total = bttf_total + other_total

        breakdown = {
            "items": items_breakdown,
            "bttf_subtotal": round(bttf_subtotal, 2),
            "bttf_count": distinct_count,
            "discount_percentage": discount * 100,
            "bttf_discount": round(discount_amount, 2),
            "bttf_total": round(bttf_total, 2),
            "other_total": round(other_total, 2),
            "total": round(total, 2),
        }

        return total, breakdown
