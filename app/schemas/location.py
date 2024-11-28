from pydantic import BaseModel
from typing import Optional


class CEPResponse(BaseModel):
    cep: str
    logradouro: Optional[str]
    complemento: Optional[str]
    bairro: Optional[str]
    localidade: Optional[str]
    uf: Optional[str]
    ibge: Optional[str]
    gia: Optional[str]
    ddd: Optional[str]
    siafi: Optional[str]


class Country(BaseModel):
    name: str
    alpha_2: str
    alpha_3: str


class State(BaseModel):
    name: str
    code: str


class City(BaseModel):
    name: str
