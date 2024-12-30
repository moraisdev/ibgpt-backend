import os
from datetime import datetime, timedelta
from openai import OpenAI
from qdrant_client import QdrantClient
from qdrant_client.models import ScoredPoint, Filter, FieldCondition, Range

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", "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"))

QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "meus_documentos_tributarios")
QDRANT_HOST = os.getenv("QDRANT_HOST", "qdrant")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))

EMBEDDING_MODEL = "text-embedding-ada-002"
SCORE_THRESHOLD = 0.7

qdrant_client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

def generate_embedding(text: str) -> list[float]:
    response = client.embeddings.create(input=[text], model=EMBEDDING_MODEL)
    return response.data[0].embedding

async def process_rag_query(question: str) -> str:
    # 1) Gerar embedding da pergunta
    question_embedding = generate_embedding(question)
    
    # 2) Definindo data limite (ex.: últimos 30 dias)
    recent_cutoff = datetime.now() - timedelta(days=30)
    recent_cutoff_iso = recent_cutoff.isoformat()  # string no formato ISO

    # 3) Busca usando filtro de data_insercao >= recent_cutoff_iso
    try:
        search_result_recent: list[ScoredPoint] = qdrant_client.search(
            collection_name=QDRANT_COLLECTION,
            query_vector=question_embedding,
            limit=3,
            filter=Filter(
                must=[
                    FieldCondition(
                        key="data_insercao",
                        range=Range(gte=recent_cutoff_iso)
                    )
                ]
            )
        )
    except Exception as e:
        # Em caso de erro, podemos logar e seguir
        search_result_recent = []

    # 4) Se não achou nada OU o score do top for muito baixo, fallback:
    if not search_result_recent or search_result_recent[0].score < SCORE_THRESHOLD:
        # Tenta buscar sem filtro de data
        search_result = qdrant_client.search(
            collection_name=QDRANT_COLLECTION,
            query_vector=question_embedding,
            limit=3,
        )
        if not search_result:
            # Fallback final: GPT sem contexto
            return await call_gpt_fallback(question)
        # Verifica score do resultado
        if search_result[0].score < SCORE_THRESHOLD:
            return await call_gpt_fallback(question)
        # Monta contexto com os resultados
        retrieved_chunks = [hit.payload["texto"] for hit in search_result]
    else:
        # Se achou resultado recente (e top_score >= threshold)
        retrieved_chunks = [hit.payload["texto"] for hit in search_result_recent]

    # 5) Monta contexto
    context = "\n\n".join(retrieved_chunks)

    # 6) Monta prompt e chama GPT
    user_message_content = f"""
    CONTEXTO:
    {context}

    Você é um assistente especializado em questões tributárias e contabilidade,
    mas também pode usar seu conhecimento geral. Se o CONTEXTO ajudar, use-o.
    Se não tiver nada no CONTEXTO, responda com seu próprio conhecimento.

    PERGUNTA: {question}
    """

    try:
        response = client.chat.completions.create(
            model="chatgpt-4o-latest",
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
            model="chatgpt-4o-latest",
            messages=[
                {
                    "role": "system",
                    "content": "Você é um assistente amplo com conhecimento em contabilidade e questões tributarias e questões gerais."
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
