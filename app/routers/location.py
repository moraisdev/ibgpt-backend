from fastapi import APIRouter, HTTPException, status
from typing import List, Optional
from app.schemas.location import CEPResponse, Country, State, City
from app.services.location import (
    fetch_cep_info,
    get_all_countries,
    get_brazilian_states,
    fetch_cities_by_state,
)
import httpx

router = APIRouter()


@router.get("/cep/{cep}", response_model=CEPResponse)
async def get_cep_info(cep: str):
    try:
        return await fetch_cep_info(cep)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except httpx.HTTPStatusError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Erro ao consultar CEP.",
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor.",
        )


@router.get("/countries", response_model=List[Country])
async def get_countries():
    return get_all_countries()


@router.get("/states", response_model=List[State])
async def get_states():
    return get_brazilian_states()


@router.get("/cities", response_model=List[City])
async def get_cities(state_code: Optional[str] = None):
    if not state_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Código do estado é obrigatório.",
        )
    try:
        return await fetch_cities_by_state(state_code)
    except httpx.HTTPStatusError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Erro ao consultar cidades.",
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor.",
        )
