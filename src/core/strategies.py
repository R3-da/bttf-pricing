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
        
        bttf_total = len(bttf_movies) * self.BTTF_PRICE
        discounted_bttf_total = bttf_total * (1 - discount)

        # Calculate Other logic
        other_total = len(other_movies) * self.OTHER_PRICE

        return discounted_bttf_total + other_total
