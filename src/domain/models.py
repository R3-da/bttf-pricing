from dataclasses import dataclass
from typing import List

@dataclass(frozen=True)
class Movie:
    title: str

    @property
    def is_bttf(self) -> bool:
        return "Back to the Future" in self.title

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
