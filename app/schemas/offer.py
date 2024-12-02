from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict


class InssSynthesizedCalculation(BaseModel):
    description: str
    values: dict

    class Config:
        orm_mode = True


class OfferDocument(BaseModel):
    filename: str
    content: bytes
    processed_text: Optional[str]

    class Config:
        orm_mode = True


class OfferCreate(BaseModel):
    customer_id: Optional[int]
    status: Optional[str]
    offer_type: Optional[str]
    company_service_type: Optional[str]
    company_profit_type: Optional[str]
    company_time_profit_type: Optional[str]
    company_work_regime: Optional[str]
    company_clt_employees: Optional[int]
    company_pj_employees: Optional[int]
    company_freelance_employees: Optional[int]
    company_internship_employees: Optional[int]
    company_cooperative_employees: Optional[int]
    company_total_employees: Optional[int]


class OfferUpdate(BaseModel):
    status: Optional[str] = None
    offer_type: Optional[str] = None
    company_service_type: Optional[str] = None
    company_profit_type: Optional[str] = None
    company_time_profit_type: Optional[str] = None
    company_work_regime: Optional[str] = None
    company_clt_employees: Optional[int] = None
    company_pj_employees: Optional[int] = None
    company_freelance_employees: Optional[int] = None
    company_internship_employees: Optional[int] = None
    company_cooperative_employees: Optional[int] = None
    company_total_employees: Optional[int] = None
    accuracy_ia: Optional[float] = None
    periodicity: Optional[str] = None
    calculated_value: Optional[float] = None
    commission: Optional[float] = None
    liquidation_value: Optional[float] = None
    observations: Optional[str] = None


class OfferDocumentResponse(BaseModel):
    filename: str
    processed_text: Optional[str]

    class Config:
        orm_mode = True


class InssSynthesizedCalculationResponse(BaseModel):
    id: Optional[int]
    description: str
    values: Dict[str, float]

    model_config = ConfigDict(from_attributes=True)


class OfferResponse(BaseModel):
    id: int
    customer_id: int
    status: Optional[str]
    offer_type: Optional[str]
    company_service_type: Optional[str]
    company_profit_type: Optional[str]
    company_time_profit_type: Optional[str]
    company_work_regime: Optional[str]
    company_clt_employees: Optional[int]
    company_pj_employees: Optional[int]
    company_freelance_employees: Optional[int]
    company_internship_employees: Optional[int]
    company_cooperative_employees: Optional[int]
    company_total_employees: Optional[int]
    accuracy_ia: Optional[float]
    periodicity: Optional[str]
    calculated_value: Optional[float]
    commission: Optional[float]
    liquidation_value: Optional[float]
    observations: Optional[str]
    result_openai: Optional[str]
    documents: Optional[List[OfferDocumentResponse]] = []
    calculations: Optional[List[InssSynthesizedCalculationResponse]] = []

    class Config:
        orm_mode = True


class FineTuneResponse(BaseModel):
    result_openai: str
    accuracy_ia: float
    periodicity: str
    calculated_value: float
    calculations: List[InssSynthesizedCalculationResponse]

    model_config = ConfigDict(from_attributes=True)
