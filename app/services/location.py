import httpx
from typing import List
import pycountry
from app.schemas.location import CEPResponse, Country, State, City


async def fetch_cep_info(cep: str) -> CEPResponse:
    cep = cep.replace("-", "").strip()
    url = f"https://viacep.com.br/ws/{cep}/json/"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        data = response.json()
        if data.get("erro"):
            raise ValueError("CEP não encontrado.")
        return CEPResponse(**data)


def get_all_countries() -> List[Country]:
    return [
        Country(name=country.name, alpha_2=country.alpha_2, alpha_3=country.alpha_3)
        for country in pycountry.countries
    ]


def get_brazilian_states() -> List[State]:
    brazilian_states = [
        {"name": "Acre", "code": "AC"},
        {"name": "Alagoas", "code": "AL"},
        {"name": "Amapá", "code": "AP"},
        {"name": "Amazonas", "code": "AM"},
        {"name": "Bahia", "code": "BA"},
        {"name": "Ceará", "code": "CE"},
        {"name": "Distrito Federal", "code": "DF"},
        {"name": "Espírito Santo", "code": "ES"},
        {"name": "Goiás", "code": "GO"},
        {"name": "Maranhão", "code": "MA"},
        {"name": "Mato Grosso", "code": "MT"},
        {"name": "Mato Grosso do Sul", "code": "MS"},
        {"name": "Minas Gerais", "code": "MG"},
        {"name": "Pará", "code": "PA"},
        {"name": "Paraíba", "code": "PB"},
        {"name": "Paraná", "code": "PR"},
        {"name": "Pernambuco", "code": "PE"},
        {"name": "Piauí", "code": "PI"},
        {"name": "Rio de Janeiro", "code": "RJ"},
        {"name": "Rio Grande do Norte", "code": "RN"},
        {"name": "Rio Grande do Sul", "code": "RS"},
        {"name": "Rondônia", "code": "RO"},
        {"name": "Roraima", "code": "RR"},
        {"name": "Santa Catarina", "code": "SC"},
        {"name": "São Paulo", "code": "SP"},
        {"name": "Sergipe", "code": "SE"},
        {"name": "Tocantins", "code": "TO"},
    ]
    return [State(**state) for state in brazilian_states]


async def fetch_cities_by_state(state_code: str) -> List[City]:
    url = f"https://servicodados.ibge.gov.br/api/v1/localidades/estados/{state_code}/municipios"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        data = response.json()
        return [City(name=city["nome"]) for city in data]
