from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from decimal import Decimal
from app.models import WorkspaceType, MemberRole

class WorkspaceCreateRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    type: WorkspaceType = WorkspaceType.SOLO
    currency: str = Field(default='BRL', min_length=3, max_length=3)

class WorkspaceUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    currency: Optional[str] = Field(None, min_length=3, max_length=3)

class MemberResponse(BaseModel):
    id: UUID
    user_id: UUID
    email: Optional[str] = None
    display_name: str
    role: MemberRole
    declared_income: Decimal
    custom_split_percentage: Optional[Decimal] = None
    joined_at: datetime

    class Config:
        from_attributes = True

class WorkspaceResponse(BaseModel):
    id: UUID
    name: str
    type: WorkspaceType
    owner_id: UUID
    currency: str
    created_at: datetime
    role_of_current_user: Optional[str] = None

    class Config:
        from_attributes = True

class WorkspaceDetailResponse(WorkspaceResponse):
    members: List[MemberResponse] = []

class MemberInviteRequest(BaseModel):
    email: EmailStr
    display_name: str = Field(..., min_length=2, max_length=100)
    role: MemberRole = MemberRole.MEMBER
    declared_income: Decimal = Field(default=Decimal('0.00'), ge=0)
    custom_split_percentage: Optional[Decimal] = Field(None, ge=0, le=100)

class MemberUpdateRequest(BaseModel):
    display_name: Optional[str] = Field(None, min_length=2, max_length=100)
    role: Optional[MemberRole] = None
    declared_income: Optional[Decimal] = Field(None, ge=0)
    custom_split_percentage: Optional[Decimal] = Field(None, ge=0, le=100)
