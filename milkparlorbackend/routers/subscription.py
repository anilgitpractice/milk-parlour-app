from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import (
    MilkType,
    Subscription,
    SubscriptionCreateRequest,
    SubscriptionResponse,
    SubscriptionStatus,
)


router = APIRouter()


@router.post("/", response_model=SubscriptionResponse)
async def start_subscription(payload: SubscriptionCreateRequest, db: Session = Depends(get_db)):
    sub = Subscription(
        customer_id=payload.customer_id,
        milk_type=payload.milk_type.value,
        quantity_litres=payload.quantity_litres,
        start_date=payload.start_date,
        status=SubscriptionStatus.ACTIVE.value,
    )
    db.add(sub)
    db.commit()
    db.refresh(sub)
    return SubscriptionResponse(
        id=sub.id,
        customer_id=sub.customer_id,
        milk_type=MilkType(sub.milk_type),
        quantity_litres=sub.quantity_litres,
        start_date=sub.start_date,
        status=SubscriptionStatus(sub.status),
    )


@router.post("/{subscription_id}/pause", response_model=SubscriptionResponse)
async def pause_subscription(subscription_id: int, db: Session = Depends(get_db)):
    sub = db.query(Subscription).filter(Subscription.id == subscription_id).first()
    if sub is None:
        raise HTTPException(status_code=404, detail="Subscription not found.")

    sub.status = SubscriptionStatus.PAUSED.value
    db.commit()
    db.refresh(sub)
    return SubscriptionResponse(
        id=sub.id,
        customer_id=sub.customer_id,
        milk_type=MilkType(sub.milk_type),
        quantity_litres=sub.quantity_litres,
        start_date=sub.start_date,
        status=SubscriptionStatus(sub.status),
    )


@router.get("/", response_model=List[SubscriptionResponse])
async def list_subscriptions(db: Session = Depends(get_db)):
    subs = db.query(Subscription).order_by(Subscription.id.asc()).all()
    return [
        SubscriptionResponse(
            id=s.id,
            customer_id=s.customer_id,
            milk_type=MilkType(s.milk_type),
            quantity_litres=s.quantity_litres,
            start_date=s.start_date,
            status=SubscriptionStatus(s.status),
        )
        for s in subs
    ]

