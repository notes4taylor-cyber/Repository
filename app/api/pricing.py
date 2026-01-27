"""
Pricing API endpoints.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.database import get_db
from app.models.user import User, SubscriptionTier
from app.core.security import get_current_user_id
from app.core.config import settings

router = APIRouter()


class PricingPlan(BaseModel):
    """Schema for pricing plan."""
    id: str
    name: str
    price_cents: int
    price_display: str
    description: str
    features: List[str]
    is_subscription: bool
    billing_period: str = None


class PurchaseRequest(BaseModel):
    """Schema for purchase request."""
    plan_id: str
    payment_method_id: str = None  # For Stripe integration


class CreditPurchaseRequest(BaseModel):
    """Schema for credit purchase."""
    credits: int  # Number of credits to buy


@router.get("/plans", response_model=List[PricingPlan])
async def get_pricing_plans():
    """
    Get all available pricing plans.

    MasterFlow offers the most competitive pricing in the industry!

    Compare to LANDR:
    - LANDR Basic: $9.99 → MasterFlow Basic: $4.99 (50% cheaper!)
    - LANDR Advanced: $14.99 → MasterFlow Advanced: $7.99 (47% cheaper!)
    - LANDR Pro: $24.99 → MasterFlow Pro: $12.99 (48% cheaper!)
    - LANDR Unlimited: $199/year → MasterFlow Unlimited: $99/year (50% cheaper!)
    """
    plans = []

    for plan_id, plan_data in settings.PRICING.items():
        is_subscription = "unlimited" in plan_id
        billing_period = None

        if plan_id == "unlimited_monthly":
            billing_period = "monthly"
            price_display = f"${plan_data['price'] / 100:.2f}/month"
        elif plan_id == "unlimited_yearly":
            billing_period = "yearly"
            price_display = f"${plan_data['price'] / 100:.2f}/year"
        else:
            price_display = f"${plan_data['price'] / 100:.2f}"

        plans.append(PricingPlan(
            id=plan_id,
            name=plan_data["name"],
            price_cents=plan_data["price"],
            price_display=price_display,
            description=plan_data["description"],
            features=plan_data["features"],
            is_subscription=is_subscription,
            billing_period=billing_period,
        ))

    return plans


@router.get("/compare")
async def compare_to_competitors():
    """
    Compare MasterFlow pricing to competitors.
    """
    return {
        "message": "MasterFlow offers the best value in music mastering!",
        "comparison": {
            "basic_master": {
                "landr": {"price": "$9.99", "description": "Basic mastering"},
                "masterflow": {"price": "$4.99", "description": "AI mastering + MP3 output"},
                "savings": "50%"
            },
            "advanced_master": {
                "landr": {"price": "$14.99", "description": "Advanced mastering"},
                "masterflow": {"price": "$7.99", "description": "AI mastering + WAV + Genre optimization"},
                "savings": "47%"
            },
            "pro_master": {
                "landr": {"price": "$24.99", "description": "Pro mastering"},
                "masterflow": {"price": "$12.99", "description": "Full suite + Stem mastering"},
                "savings": "48%"
            },
            "unlimited_yearly": {
                "landr": {"price": "$199/year", "description": "Unlimited masters"},
                "masterflow": {"price": "$99/year", "description": "Unlimited + Priority processing"},
                "savings": "50%"
            }
        },
        "why_masterflow": [
            "Same professional quality at half the price",
            "Advanced AI-powered mastering algorithms",
            "More output format options",
            "Faster processing times",
            "Better customer support",
            "No hidden fees"
        ]
    }


@router.post("/purchase")
async def purchase_plan(
    request: PurchaseRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Purchase a mastering plan or subscription.

    Note: This is a placeholder for Stripe integration.
    In production, this would create a Stripe checkout session.
    """
    if request.plan_id not in settings.PRICING:
        raise HTTPException(status_code=400, detail="Invalid plan ID")

    plan = settings.PRICING[request.plan_id]

    # Get user
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # In production, you would:
    # 1. Create a Stripe checkout session
    # 2. Return the checkout URL
    # 3. Handle the webhook to update user subscription

    # For demo, we'll just add credits/subscription directly
    if "unlimited" in request.plan_id:
        user.subscription_tier = SubscriptionTier.UNLIMITED
        user.credits = 999999  # Effectively unlimited
    elif request.plan_id == "pro":
        user.credits += 10
    elif request.plan_id == "advanced":
        user.credits += 5
    else:  # basic
        user.credits += 1

    await db.commit()

    return {
        "success": True,
        "message": f"Successfully purchased {plan['name']}!",
        "plan": plan,
        "new_credits": user.credits,
        "subscription_tier": user.subscription_tier.value,
        # In production: "checkout_url": stripe_checkout_session.url
    }


@router.post("/credits")
async def purchase_credits(
    request: CreditPurchaseRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Purchase individual mastering credits.

    Credits can be used for any tier of mastering.
    $4.99 per credit.
    """
    if request.credits < 1:
        raise HTTPException(status_code=400, detail="Must purchase at least 1 credit")

    if request.credits > 100:
        raise HTTPException(status_code=400, detail="Maximum 100 credits per transaction")

    price_per_credit = 499  # $4.99
    total_price = request.credits * price_per_credit

    # Apply bulk discounts
    if request.credits >= 50:
        total_price = int(total_price * 0.8)  # 20% off
    elif request.credits >= 20:
        total_price = int(total_price * 0.85)  # 15% off
    elif request.credits >= 10:
        total_price = int(total_price * 0.9)  # 10% off

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # In production, process payment first
    user.credits += request.credits
    await db.commit()

    return {
        "success": True,
        "credits_purchased": request.credits,
        "total_price_cents": total_price,
        "total_price_display": f"${total_price / 100:.2f}",
        "new_balance": user.credits,
    }


@router.get("/credits")
async def get_credit_balance(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current credit balance.
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "credits": user.credits,
        "subscription_tier": user.subscription_tier.value,
        "can_master": user.can_master,
    }
