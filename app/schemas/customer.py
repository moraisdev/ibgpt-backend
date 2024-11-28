from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class CustomerBase(BaseModel):
    company_representative_name: str
    company_representative_last_name: str
    company_representative_email: EmailStr
    company_representative_phone_number: str
    company_name: str
    company_email: EmailStr
    company_phone_number: str
    company_website: str
    company_activity_sector: str
    company_cnpj: str
    company_address_street: str
    company_address_number: str
    company_address_complement: Optional[str] = None
    company_address_neighbourhood: str
    company_address_city: str
    company_address_state: str
    company_address_country: str
    company_address_zip_code: str
    is_active: Optional[bool] = True


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    company_representative_name: Optional[str] = None
    company_representative_last_name: Optional[str] = None
    company_representative_email: Optional[EmailStr] = None
    company_representative_phone_number: Optional[str] = None
    company_name: Optional[str] = None
    company_email: Optional[EmailStr] = None
    company_phone_number: Optional[str] = None
    company_website: Optional[str] = None
    company_activity_sector: Optional[str] = None
    company_cnpj: Optional[str] = None
    company_address_street: Optional[str] = None
    company_address_number: Optional[str] = None
    company_address_complement: Optional[str] = None
    company_address_neighbourhood: Optional[str] = None
    company_address_city: Optional[str] = None
    company_address_state: Optional[str] = None
    company_address_country: Optional[str] = None
    company_address_zip_code: Optional[str] = None
    is_active: Optional[bool] = None


class CustomerResponse(BaseModel):
    id: int
    company_representative_name: str
    company_representative_last_name: str
    company_representative_email: EmailStr
    company_representative_phone_number: str
    company_name: str
    company_email: EmailStr
    company_phone_number: str
    company_website: str
    company_activity_sector: str
    company_cnpj: str
    company_address_street: str
    company_address_number: str
    company_address_complement: Optional[str] = None
    company_address_neighbourhood: str
    company_address_city: str
    company_address_state: str
    company_address_country: str
    company_address_zip_code: str
    is_active: Optional[bool] = True
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
