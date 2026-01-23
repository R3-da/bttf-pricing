from typing import Protocol
from src.domain.models import Cart


class PricingStrategy(Protocol):
    def calculate_price(self, cart: Cart) -> float: ...
