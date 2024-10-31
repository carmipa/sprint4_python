import requests

def buscar_endereco_por_cep(cep):
    """
    Função para buscar o endereço a partir do CEP usando a API ViaCEP.
    :param cep: String com o CEP do cliente (somente números).
    :return: Dicionário com os dados do endereço ou None em caso de erro.
    """
    # Remover caracteres não numéricos do CEP
    cep = cep.replace("-", "").strip()

    # Verificar se o CEP tem 8 dígitos
    if len(cep) != 8 or not cep.isdigit():
        return {"erro": "CEP inválido. Deve ter 8 números."}

    # URL da API ViaCEP
    url = f"https://viacep.com.br/ws/{cep}/json/"

    try:
        # Fazer a requisição à API
        response = requests.get(url)
        response.raise_for_status()  # Levanta um erro em caso de resposta com status de erro (4xx ou 5xx)
        endereco = response.json()

        # Verifica se houve erro no retorno da API
        if "erro" in endereco:
            return {"erro": "CEP não encontrado."}

        # Retorna o endereço obtido
        return endereco

    except requests.RequestException as e:
        # Em caso de erro de rede ou API, retorna a mensagem de erro
        return {"erro": f"Erro ao consultar o ViaCEP: {str(e)}"}
