import logging
from fastapi import APIRouter, Body, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError, OperationalError, InterfaceError, DBAPIError
from pydantic import BaseModel
from src.core.services import PricingService, MissingMoviesError
from src.core.database import get_session

router = APIRouter()
service = PricingService()
logger = logging.getLogger(__name__)


class MovieItem(BaseModel):
    title: str
    series: str | None
    price: float
    is_bttf: bool
    count: int


class PricingBreakdown(BaseModel):
    items: list[MovieItem]
    bttf_subtotal: float
    bttf_count: int
    discount_percentage: float
    bttf_discount: float
    bttf_total: float
    other_total: float
    total: float


class PriceResponse(BaseModel):
    price: float
    breakdown: PricingBreakdown | None = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "price": 47,
                "breakdown": {
                    "items": [
                        {
                            "title": "Back to the Future 1",
                            "series": "Back to the Future",
                            "price": 15,
                            "is_bttf": True,
                            "count": 1,
                        },
                        {
                            "title": "Back to the Future 2",
                            "series": "Back to the Future",
                            "price": 15,
                            "is_bttf": True,
                            "count": 1,
                        },
                        {
                            "title": "La chèvre",
                            "series": None,
                            "price": 20,
                            "is_bttf": False,
                            "count": 1,
                        },
                    ],
                    "bttf_subtotal": 30,
                    "bttf_count": 2,
                    "discount_percentage": 10,
                    "bttf_discount": 3,
                    "bttf_total": 27,
                    "other_total": 20,
                    "total": 47,
                },
            }
        }
    }


@router.post("/price", response_model=PriceResponse)
async def calculate_price(
    cart_content: str = Body(
        "",
        media_type="text/plain",
        description="Raw text content of the cart",
        example="Back to the Future 1\nBack to the Future 2\nLa chèvre",
    ),
    session: AsyncSession = Depends(get_session),
) -> PriceResponse:
    """
    Calculate the total price for a list of movies provided as raw text.
    """
    try:
        # Log a summary of the request
        lines = [line.strip() for line in cart_content.split("\n") if line.strip()]
        logger.info(
            f"Calculating price for {len(lines)} items: {', '.join(lines[:3])}{'...' if len(lines) > 3 else ''}"
        )

        price, breakdown = await service.calculate_price_with_breakdown(
            cart_content, session
        )

        logger.info(f"Price calculated successfully: {price}")
        return PriceResponse(price=price, breakdown=breakdown)
    except MissingMoviesError as e:
        logger.warning(f"Price calculation failed: Missing movies {e.missing_movies}")
        raise HTTPException(
            status_code=404,
            detail={
                "message": "Some movies were not found in the database.",
                "missing_movies": e.missing_movies,
            },
        )
    except (InterfaceError, OperationalError, DBAPIError, SQLAlchemyError) as e:
        logger.error(f"Database connection error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=503,
            detail="Database is currently unavailable. Please try again later.",
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except OSError as e:
        logger.error(f"Database connection error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=503,
            detail="Database is currently unavailable. Please try again later.",
        )
    except Exception as e:
        logger.error(f"Unexpected error calculating price: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred. Please try again later.",
        )
