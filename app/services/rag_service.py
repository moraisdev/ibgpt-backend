# app/services/rag_service.py

import os
from openai import OpenAI
from qdrant_client import QdrantClient
from qdrant_client.models import ScoredPoint

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", "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"))

QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "meus_documentos_tributarios")
QDRANT_HOST = os.getenv("QDRANT_HOST", "qdrant")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))

EMBEDDING_MODEL = "text-embedding-ada-002"
SCORE_THRESHOLD = 0.7

def generate_embedding(text: str) -> list[float]:
    """Gera embedding usando OpenAI (text-embedding-ada-002)."""
    response = client.embeddings.create(input=[text], model=EMBEDDING_MODEL)
    return response.data[0].embedding

qdrant_client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)


async def process_rag_query(question: str) -> str:
    """
    Tenta buscar contexto no Qdrant. Se achar algo relevante (score >= threshold), 
    injeta no prompt. Caso contrário, chama GPT sem restrições (fallback).
    """

    # 1) Gerar embedding da pergunta
    question_embedding = generate_embedding(question)

    # 2) Buscar no Qdrant
    search_result: list[ScoredPoint] = qdrant_client.search(
        collection_name=QDRANT_COLLECTION,
        query_vector=question_embedding,
        limit=3,
    )

    if not search_result:
        # Fallback: sem resultados => chama GPT normal
        return await call_gpt_fallback(question)

    top_score = search_result[0].score
    if top_score < SCORE_THRESHOLD:
        # Fallback: menor que threshold => chama GPT normal
        return await call_gpt_fallback(question)

    # 3) Monta contexto
    retrieved_chunks = [hit.payload["text"] for hit in search_result]
    context = "\n\n".join(retrieved_chunks)

    # 4) Monta prompt dizendo "use APENAS esse contexto"
    # Mas se você quer que ele também possa usar conhecimento geral, não fale “APENAS” 
    # ou use outra formulação. Exemplo:
    user_message_content = f"""
    CONTEXTO:
    {context}

    Você é um assistente especializado em questões tributárias,
    mas também pode usar seu conhecimento geral. Se o CONTEXTO ajudar, use-o.
    Se não tiver nada no CONTEXTO, responda com seu próprio conhecimento.

    PERGUNTA: {question}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Você é um assistente tributário, mas tem conhecimento amplo. "
                        "Se o contexto não ajudar, responda mesmo assim com seu próprio conhecimento."
                    )
                },
                {
                    "role": "user",
                    "content": user_message_content,
                },
            ],
            temperature=0.3,
        )
        final_answer = response.choices[0].message.content.strip()
        return final_answer

    except Exception as e:
        raise e


async def call_gpt_fallback(question: str) -> str:
    """
    Se não tiver dados relevantes no Qdrant, chamamos GPT sem restrições,
    deixando-o responder com base no conhecimento geral.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "Você é um assistente amplo com conhecimento geral."
                },
                {
                    "role": "user",
                    "content": question
                },
            ],
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        raise e


async def summarize_text(content: str) -> str:
    """
    Exemplo de função de sumarização (opcional).
    """
    prompt = f"Por favor, faça um resumo breve do texto:\n\n{content}"
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        raise e
