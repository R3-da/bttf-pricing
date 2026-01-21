from fastapi import APIRouter, Body, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from src.core.services import PricingService
from src.core.database import get_session

router = APIRouter()
service = PricingService()

class PriceResponse(BaseModel):
    price: float

@router.post("/price", response_model=PriceResponse)
async def calculate_price(
    cart_content: str = Body(
        "",
        media_type="text/plain",
        description="Raw text content of the cart",
        example="Back to the Future 1\nBack to the Future 2\nLa chèvre"
    ),
    session: AsyncSession = Depends(get_session)
) -> PriceResponse:
    """
    Calculate the total price for a list of movies provided as raw text.
    """
    try:
        price = await service.calculate_price(cart_content, session)
        return PriceResponse(price=price)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        # Generic error handling, in production we would log this and be more specific
        raise HTTPException(status_code=500, detail=str(e))
