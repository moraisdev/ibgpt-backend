import tiktoken


def count_tokens(text: str, model_name: str = "gpt-3.5-turbo") -> int:
    """
    Conta quantos tokens existem em 'text' de acordo com o modelo especificado.
    Por padrão, usamos 'gpt-3.5-turbo'.
    """
    try:
        encoding = tiktoken.encoding_for_model(model_name)
    except KeyError:
        # Se o modelo não for reconhecido, usa um encoding padrão (cl100k_base)
        encoding = tiktoken.get_encoding("cl100k_base")

    tokens = encoding.encode(text)
    return len(tokens)
