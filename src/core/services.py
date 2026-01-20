from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.domain.models import Cart, Movie as DomainMovie
from src.domain.sql_models import Movie as SQLMovie
from src.core.strategies import BackToTheFutureStrategy
from src.core.interfaces import PricingStrategy

class PricingService:
    def __init__(self, strategy: PricingStrategy = None):
        # By default use BTTF strategy, but allow injection
        self.strategy = strategy or BackToTheFutureStrategy()

    async def calculate_price(self, cart_text: str, session: AsyncSession) -> float:
        # Initial parse to get titles
        temp_cart = Cart.from_text(cart_text)
        if not temp_cart.items:
            return 0.0

        titles = [m.title for m in temp_cart.items]
        
        # Fetch movies from DB
        # We need to join with Series to get series title
        stmt = select(SQLMovie).where(SQLMovie.title.in_(titles)).join(SQLMovie.series, isouter=True) 
        # Actually need to eager load series or just select what we need
        from sqlalchemy.orm import selectinload
        stmt = select(SQLMovie).where(SQLMovie.title.in_(titles)).options(selectinload(SQLMovie.series))
        
        result = await session.execute(stmt)
        sql_movies = result.scalars().all()
        
        # Map by title for easy lookup
        movie_map = {m.title: m for m in sql_movies}
        
        domain_movies = []
        missing_movies = []
        
        for temp_movie in temp_cart.items:
            sql_movie = movie_map.get(temp_movie.title)
            if not sql_movie:
                missing_movies.append(temp_movie.title)
                continue
            
            series_title = sql_movie.series.title if sql_movie and sql_movie.series else None
            price = sql_movie.price
            domain_movies.append(DomainMovie(title=temp_movie.title, series_title=series_title, price=price))
            
        if missing_movies:
            # Join unique missing items to avoid spamming same title
            unique_missing = sorted(list(set(missing_movies)))
            raise ValueError(f"Movie(s) not found: {', '.join(unique_missing)}")
            
        final_cart = Cart(items=domain_movies)
        return self.strategy.calculate_price(final_cart)
            
        final_cart = Cart(items=domain_movies)
        return self.strategy.calculate_price(final_cart)
