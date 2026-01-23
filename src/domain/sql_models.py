from datetime import date
from typing import Optional, List
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field, Relationship


class Series(SQLModel, table=True):
    __tablename__ = "series"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    title: str
    description: Optional[str] = None

    movies: List["Movie"] = Relationship(back_populates="series")


class Movie(SQLModel, table=True):
    __tablename__ = "movies"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    title: str
    release_date: date
    duration_min: int
    price: float = Field(default=0.0)
    series_id: Optional[UUID] = Field(default=None, foreign_key="series.id")
    series_index: Optional[int] = None

    series: Optional[Series] = Relationship(back_populates="movies")
