import oracledb
from flask import Flask, render_template, request, redirect, flash, url_for

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta'  # Mantenha sua chave secreta para o Flask

# Função para conectar ao banco de dados Oracle
def conectar():
    try:
        # Configuração do DSN
        dsn = oracledb.makedsn("localhost", 1521, service_name="XEPDB1")

        # Conectando ao banco de dados
        connection = oracledb.connect(user="challenge", password="12345", dsn=dsn)

        print("Conexão estabelecida com sucesso!")
        return connection

    except oracledb.Error as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None

# Rota principal para testar o servidor Flask
@app.route('/')
def index():
    return "Bem-vindo! O servidor Flask está rodando e a conexão com o banco de dados foi testada."

# Teste de conexão com o banco de dados
@app.route('/testar_conexao')
def testar_conexao():
    conexao = conectar()
    if conexao:
        conexao.close()  # Fechar a conexão se foi bem-sucedida
        return "Conexão com o banco de dados estabelecida e encerrada com sucesso!"
    else:
        return "Falha ao conectar ao banco de dados."

# Iniciando o servidor Flask
if __name__ == '__main__':
    app.run(debug=True)
