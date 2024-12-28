from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.db.database import get_async_session
from app.services.auth import get_current_user

from app.schemas.chat import (
    ChatCreate,
    ChatResponse,
    ChatWithMessagesResponse,
    ChatSummaryResponse,
)
from app.schemas.chat_message import ChatMessageCreate, ChatMessageResponse
from app.services import chat_service

router = APIRouter()


@router.post("/new-chat", response_model=ChatResponse, status_code=status.HTTP_201_CREATED)
async def create_chat_endpoint(
    chat_data: ChatCreate,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    """
    Cria um novo chat para o usuário atual.
    """
    chat = await chat_service.create_chat(session, chat_data, current_user.id)
    return chat


@router.post("/{chat_id}/ask", response_model=ChatMessageResponse)
async def ask_in_chat_endpoint(
    chat_id: int,
    question: ChatMessageCreate,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    """
    Envia uma pergunta (mensagem do usuário) para o chat, chama a RAG (Qdrant + GPT)
    e salva a resposta no histórico.

    Retorna a mensagem do 'assistant' (a resposta).
    """
    try:
        # question.content é a pergunta do user
        assistant_message = await chat_service.process_user_question(
            session, chat_id, question.content, current_user.id
        )
        return assistant_message
    except ValueError as e:
        # Ex.: se o chat não pertence ao usuário ou não foi encontrado
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{chat_id}/messages", response_model=List[ChatMessageResponse])
async def get_chat_messages_endpoint(
    chat_id: int,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    """
    Retorna todas as mensagens de um chat (para exibir histórico).
    """
    try:
        messages = await chat_service.get_chat_messages(
            session, chat_id, current_user.id
        )
        return messages
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{chat_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chat_endpoint(
    chat_id: int,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    """
    Deleta o chat inteiro (e, em cascata, todas as mensagens).
    """
    try:
        await chat_service.delete_chat(session, chat_id, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return {"detail": "Chat deletado com sucesso."}


@router.get("/", response_model=List[ChatSummaryResponse])
async def list_chats_endpoint(
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    """
    Retorna a lista de chats do usuário atual, com um preview (começo) da primeira mensagem do usuário.
    """
    try:
        summaries = await chat_service.list_user_chats_with_preview(
            session, current_user.id
        )
        return summaries
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
