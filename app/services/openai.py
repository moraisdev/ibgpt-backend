from app.config.config import settings

from openai import AsyncOpenAI
from app.models.offer import Offer
import json

aclient = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
model = settings.FINE_TUNE_MODEL
PROMPT_PATH = "app/prompts/offer_prompt.txt"


def load_prompt(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


def extract_json_from_response(ai_message: str) -> str:
    import re

    ai_message_clean = ai_message.strip()

    ai_message_clean = re.sub(
        r"^```(?:json)?\s*", "", ai_message_clean, flags=re.IGNORECASE
    )
    ai_message_clean = re.sub(r"\s*```$", "", ai_message_clean)

    return ai_message_clean.strip()


async def use_fine_tuned_model(prompt: str) -> dict:
    try:
        system_prompt_content = load_prompt(PROMPT_PATH)

        response = await aclient.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt_content},
                {"role": "user", "content": prompt},
            ],
        )

        ai_message = response.choices[0].message.content
        print(f"AI message: {ai_message}")

        json_str = extract_json_from_response(ai_message)

        offer_data = json.loads(json_str)
        return offer_data

    except json.JSONDecodeError as json_err:
        raise ValueError(f"Erro ao decodificar a resposta JSON da IA: {json_err}")
    except Exception as e:
        raise ValueError(f"Erro ao usar o modelo fine-tune: {e}")


async def prepare_prompt(offer: Offer) -> str:
    prompt = f"Detalhes da Oferta ID {offer.id}:\n"
    prompt += f"Tipo de Serviço: {offer.company_service_type or 'null'}\n"
    prompt += f"Tipo de Lucro: {offer.company_profit_type or 'null'}\n"
    prompt += f"Tempo de Lucro: {offer.company_time_profit_type or 'null'}\n"
    prompt += f"Regime de Trabalho: {offer.company_work_regime or 'null'}\n"
    prompt += f"Funcionários CLT: {offer.company_clt_employees or 'null'}\n"
    prompt += f"Funcionários PJ: {offer.company_pj_employees or 'null'}\n"
    prompt += f"Freelancers: {offer.company_freelance_employees or 'null'}\n"
    prompt += f"Estagiários: {offer.company_internship_employees or 'null'}\n"
    prompt += f"Cooperados: {offer.company_cooperative_employees or 'null'}\n"
    prompt += f"Total de Funcionários: {offer.company_total_employees or 'null'}\n\n"

    if offer.documents:
        prompt += "Conteúdo dos Documentos:\n"
        for doc in offer.documents:
            prompt += f"--- Documento: {doc.filename or 'Arquivo sem nome'} ---\n"
            prompt += f"{doc.processed_text or 'Texto não disponível'}\n\n"
    else:
        prompt += "Nenhum documento associado à oferta.\n"

    return prompt
