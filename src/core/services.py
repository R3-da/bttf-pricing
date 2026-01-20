from src.domain.models import Cart
from src.core.strategies import BackToTheFutureStrategy
from src.core.interfaces import PricingStrategy

class PricingService:
    def __init__(self, strategy: PricingStrategy = None):
        # By default use BTTF strategy, but allow injection
        self.strategy = strategy or BackToTheFutureStrategy()

    def calculate_price(self, cart_text: str) -> float:
        cart = Cart.from_text(cart_text)
        return self.strategy.calculate_price(cart)
