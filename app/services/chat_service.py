from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.models.chat import Chat
from app.models.chat_message import ChatMessage
from app.schemas.chat import ChatCreate
from app.schemas.chat_message import ChatMessageResponse
from app.services import rag_service
from app.utils.token_utils import count_tokens
from app.schemas.chat import ChatSummaryResponse
from typing import List

MAX_TOKENS_THRESHOLD = 3000


# ----------------------
# CRIA CHAT
# ----------------------
async def create_chat(
    session: AsyncSession, chat_data: ChatCreate, user_id: int
) -> Chat:
    """
    Cria um novo Chat vinculado a um user_id.
    """
    new_chat = Chat(user_id=user_id)
    session.add(new_chat)
    await session.commit()
    await session.refresh(new_chat)
    return new_chat


# ----------------------
# PROCESSA PERGUNTA (RAG)
# ----------------------
async def process_user_question(
    session: AsyncSession, chat_id: int, question_text: str, user_id: int
) -> ChatMessageResponse:
    """
    1) Verifica se o chat pertence ao user.
    2) Salva a mensagem do user.
    3) Chama RAG p/ obter resposta do assistant.
    4) Salva a resposta no banco.
    5) Verifica se precisa resumir o histórico.
    6) Retorna a mensagem do assistant.
    """

    # 1) Verificar se o chat existe e pertence ao user
    chat = await get_chat_by_id(session, chat_id, user_id)
    if not chat:
        raise ValueError("Chat não encontrado ou não pertence ao usuário.")

    # 2) Salvar mensagem do user
    user_msg = ChatMessage(content=question_text, role="user", chat_id=chat.id)
    session.add(user_msg)
    await session.commit()
    await session.refresh(user_msg)

    # 3) Chamar RAG
    #    (Esse método vai buscar no Qdrant e chamar GPT, retornando a string)
    assistant_text = await rag_service.process_rag_query(question_text)

    # 4) Salvar a resposta (assistant) no banco
    assistant_msg = ChatMessage(
        content=assistant_text, role="assistant", chat_id=chat.id
    )
    session.add(assistant_msg)
    await session.commit()
    await session.refresh(assistant_msg)

    # 5) Verificar se precisa resumir
    await maybe_summarize_chat(session, chat)

    # 6) Retornar a mensagem do assistente (como ChatMessageResponse)
    return ChatMessageResponse(
        id=assistant_msg.id, content=assistant_msg.content, role=assistant_msg.role
    )


# ----------------------
# GET MESSAGES
# ----------------------
async def get_chat_messages(session: AsyncSession, chat_id: int, user_id: int):
    """
    Retorna todas as mensagens do chat, se pertencer ao user.
    """
    chat = await get_chat_by_id(session, chat_id, user_id)
    if not chat:
        raise ValueError("Chat não encontrado ou não pertence ao usuário.")

    result = await session.execute(
        select(ChatMessage)
        .where(ChatMessage.chat_id == chat_id)
        .order_by(ChatMessage.id)
    )
    messages = result.scalars().all()
    return messages


# ----------------------
# DELETE CHAT
# ----------------------
async def delete_chat(session: AsyncSession, chat_id: int, user_id: int):
    """
    Deleta o chat inteiro (e suas mensagens).
    """
    chat = await get_chat_by_id(session, chat_id, user_id)
    if not chat:
        raise ValueError("Chat não encontrado ou não pertence ao usuário.")

    # Apaga o chat. Se estiver configurado cascade="all, delete-orphan" na relationship,
    # todas as mensagens serão apagadas junto.
    await session.delete(chat)
    await session.commit()


# ----------------------
# FUNÇÕES AUXILIARES
# ----------------------
async def get_chat_by_id(session: AsyncSession, chat_id: int, user_id: int) -> Chat:
    """
    Retorna o chat se pertencer ao user, senão None.
    """
    result = await session.execute(
        select(Chat).where(Chat.id == chat_id, Chat.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def maybe_summarize_chat(session: AsyncSession, chat: Chat):
    """
    Exemplo: se as mensagens do chat passaram certo limite de tokens,
    resumir as primeiras N. Lembre-se de que é opcional.
    """
    result = await session.execute(
        select(ChatMessage)
        .where(ChatMessage.chat_id == chat.id)
        .order_by(ChatMessage.id)
    )
    messages = result.scalars().all()

    # Conta tokens
    total_tokens = 0
    for m in messages:
        total_tokens += count_tokens(m.content)

    # Exemplo: se > 3000 tokens, resume as 10 primeiras
    if total_tokens > MAX_TOKENS_THRESHOLD and len(messages) > 10:
        messages_to_summarize = messages[0:10]
        text_block = ""
        for msg in messages_to_summarize:
            text_block += f"{msg.role.upper()}: {msg.content}\n"

        # Chama GPT para resumir
        summary_text = await rag_service.summarize_text(text_block)

        # Se já existe summary, concatena
        if chat.summary:
            chat.summary += "\n\n" + summary_text
        else:
            chat.summary = summary_text

        # Remove as 10 mensagens do BD
        for msg in messages_to_summarize:
            await session.delete(msg)
        await session.commit()
        await session.refresh(chat)


async def list_user_chats_with_preview(
    session: AsyncSession, user_id: int
) -> List[ChatSummaryResponse]:
    """
    Retorna a lista de chats do usuário, cada um com um preview da primeira mensagem do usuário.
    """

    # 1. Buscar todos os chats do user
    result = await session.execute(
        select(Chat)
        .where(Chat.user_id == user_id)
        .order_by(Chat.created_at.desc())  # ou .asc(), se preferir
    )
    chats = result.scalars().all()

    chat_summaries: List[ChatSummaryResponse] = []

    for chat in chats:
        # 2. Pegar a primeira mensagem do 'user' nesse chat (ordem asc por ID)
        first_msg_result = await session.execute(
            select(ChatMessage)
            .where(ChatMessage.chat_id == chat.id, ChatMessage.role == "user")
            .order_by(ChatMessage.id.asc())
            .limit(1)
        )
        first_user_msg = first_msg_result.scalars().first()

        if not first_user_msg:
            # Se não houver mensagem do usuário ainda, pode colocar preview vazio
            preview = "(Nenhuma mensagem do usuário)"
        else:
            preview = first_user_msg.content
            # se for muito longo, vamos truncar
            max_length = 20  # quantos caracteres deseja mostrar
            if len(preview) > max_length:
                preview = preview[:max_length] + "..."

        chat_summaries.append(ChatSummaryResponse(chat_id=chat.id, preview=preview))

    return chat_summaries
