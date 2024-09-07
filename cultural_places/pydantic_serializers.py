# cultural_places\pydantic_serializers.py
from typing import Optional

from pydantic import BaseModel, Field, UUID4
from cultural_places.models import CulturalPlace


class CulturalPlaceIn(BaseModel):
    class Config:
        model = CulturalPlace
        model_fields = ['name', 'description', 'address', 'opening_hours', 'image']
        from_attributes = True


class CulturalPlaceOut(BaseModel):
    class Config:
        model = CulturalPlace
        model_fields = '__all__'
        from_attributes = True


class SuccessCreateResponse(BaseModel):
    detail: dict


class ErrorCreateResponse(BaseModel):
    error: str


class OpeningHoursSchema(BaseModel):
    monday: str
    tuesday: str
    wednesday: str
    thursday: str
    friday: str
    saturday: str
    sunday: str


class CulturalPlaceSchema(BaseModel):
    name: str
    description: str
    address: str
    opening_hours: OpeningHoursSchema
    image: Optional[str] = Field(default=None)
    active: Optional[bool] = None

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True

    @classmethod
    def from_orm(cls, obj, is_admin: bool = False):
        data = {
            field: getattr(obj, field)
            for field in cls.__fields__
            if hasattr(obj, field)
        }

        if hasattr(obj, 'image') and obj.image:
            data['image'] = obj.image.url if obj.image else None
        else:
            data['image'] = None

        if is_admin:
            data['active'] = getattr(obj, 'active', None)

        return cls(**data)


class SuccessCreateResponse(BaseModel):
    detail: str
    place: CulturalPlaceSchema


class ErrorCreateResponse(BaseModel):
    error: str


class SuccessEditResponse(BaseModel):
    detail: str
    place: CulturalPlaceSchema


class ErrorEditResponse(BaseModel):
    error: str


class SuccessDeactivateResponse(BaseModel):
    detail: str
    place: CulturalPlaceSchema


class ErrorDeactivateResponse(BaseModel):
    error: str


class SuccessDeleteResponse(BaseModel):
    detail: str


class ErrorDeleteResponse(BaseModel):
    error: str


class UserPlacePreferenceInputSchema(BaseModel):
    place: UUID4
    rating: int

    class Config:
        from_attributes = True


class UserPlacePreferenceOutputSchema(BaseModel):
    user: UUID4
    place: UUID4
    rating: int

    class Config:
        from_attributes = True
