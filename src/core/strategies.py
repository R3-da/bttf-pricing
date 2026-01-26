from src.domain.models import Cart
from src.core.interfaces import PricingStrategy


class BackToTheFutureStrategy(PricingStrategy):
    BTTF_PRICE = 15.0
    OTHER_PRICE = 20.0

    def calculate_price(self, cart: Cart) -> float:
        bttf_movies = [m for m in cart.items if m.is_bttf]
        other_movies = [m for m in cart.items if not m.is_bttf]

        # Calculate BTTF logic
        unique_bttf_titles = {m.title for m in bttf_movies}
        distinct_count = len(unique_bttf_titles)

        discount = 0.0
        if distinct_count == 2:
            discount = 0.10
        elif distinct_count >= 3:
            discount = 0.20

        bttf_total = sum(m.price for m in bttf_movies)
        discounted_bttf_total = bttf_total * (1 - discount)

        # Calculate Other logic
        other_total = sum(m.price for m in other_movies)

        return discounted_bttf_total + other_total

    def get_pricing_breakdown(self, cart: Cart) -> dict:
        """Get detailed pricing breakdown for the cart."""
        bttf_movies = [m for m in cart.items if m.is_bttf]
        other_movies = [m for m in cart.items if not m.is_bttf]

        # Build items breakdown with counts for duplicates
        items_breakdown = []
        seen_items = {}

        for movie in cart.items:
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

        return {
            "items": items_breakdown,
            "bttf_subtotal": round(bttf_subtotal, 2),
            "bttf_count": distinct_count,
            "discount_percentage": discount * 100,
            "bttf_discount": round(discount_amount, 2),
            "bttf_total": round(bttf_total, 2),
            "other_total": round(other_total, 2),
            "total": round(total, 2),
        }
