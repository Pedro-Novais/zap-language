from datetime import datetime
from typing import Optional, List
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class SubscriptionStatusEnum(str, Enum):
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    CANCELED = "CANCELED"
    EXPIRED = "EXPIRED"
    FAILED = "FAILED"


class PaymentItemModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    quantity: int


class FineModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    value: int
    type: str = Field(default="PERCENTAGE")


class InterestModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    value: int


class PaymentSubscriptionDataModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    status: SubscriptionStatusEnum
    custom_id: Optional[str] = Field(default=None, alias="customerId")
    amount: int
    paid_amount: Optional[int] = Field(default=None, alias="paidAmount")
    items: List[PaymentItemModel] = Field(default_factory=list)
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    fine: Optional[FineModel] = None
    interest: Optional[InterestModel] = None


class PaymentSubscriptionResponseModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    data: PaymentSubscriptionDataModel
    error: Optional[str] = None
    success: bool
