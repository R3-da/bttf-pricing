from dataclasses import dataclass
from typing import List, Optional
from uuid import UUID


@dataclass
class Movie:
    title: str
    series_id: Optional[UUID] = None
    series_title: Optional[str] = None
    price: float = 0.0


@dataclass
class Cart:
    items: List[Movie]

    def add(self, movie: Movie) -> None:
        self.items.append(movie)

    @classmethod
    def from_text(cls, text: str) -> "Cart":
        if not text.strip():
            return cls(items=[])
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        movies = [Movie(title=line) for line in lines]
        return cls(items=movies)
