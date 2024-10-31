import requests
import json
import os

def consultarGemini(descricao_problema):
    """Função que consulta a API Gemini do Google, enviando a descrição do problema do veículo
    e recebendo um diagnóstico gerado pela IA."""

    # URL da API Gemini com a chave de API (substitua pela sua própria chave)
    api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key=AIzaSyBwrtNwUBsk7B-uC5fKjaeDI0v-KMGufGA"  # Substitua pela URL correta

    headers = {
        "Content-Type": "application/json",  # Define o tipo de conteúdo como JSON
        "Authorization": "AIzaSyBwrtNwUBsk7B-uC5fKjaeDI0v-KMGufGA"  # Adicione o cabeçalho de autenticação, se necessário
    }

    # Estrutura do payload enviado para a API, contendo a descrição do problema
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": descricao_problema  # Descrição do problema enviada pelo usuário
                    }
                ]
            }
        ]
    }

    try:
        # Faz a requisição POST para a API Gemini
        response = requests.post(api_url, headers=headers, data=json.dumps(payload))

        # Verifica se a requisição foi bem-sucedida (status 200)
        if response.status_code == 200:
            resultado = response.json()  # Converte a resposta em JSON
            # Retorna o diagnóstico gerado pela IA
            return resultado['candidates'][0]['content']['parts'][0]['text']
        else:
            # Retorna uma mensagem de erro caso a requisição não seja bem-sucedida
            return f"Erro ao consultar a API Gemini. Código de status: {response.status_code}. Detalhes: {response.text}"
    except Exception as e:
        # Trata qualquer exceção e retorna uma mensagem de erro
        return f"Erro ao consultar a API Gemini: {e}"

# Obter o diretório do arquivo atual
current_dir = os.path.dirname(os.path.abspath(__file__))

# Construir o caminho completo para o arquivo JSON onde as respostas serão salvas
json_file_path = os.path.join(current_dir, 'resposta_ia.json')

# Função para salvar a resposta em um arquivo JSON
def salvar_resposta(resposta):
    with open(json_file_path, 'w') as json_file:
        json.dump({"resposta": resposta}, json_file, ensure_ascii=False, indent=4)

# Exemplo de uso
if __name__ == "__main__":
    descricao = input("Digite a descrição do problema do veículo: ")
    resposta = consultarGemini(descricao)
    print(resposta)

    # Salvar a resposta em um arquivo JSON
    salvar_resposta(resposta)
