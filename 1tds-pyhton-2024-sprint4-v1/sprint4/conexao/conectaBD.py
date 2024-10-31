import logging
import oracledb

logger = logging.getLogger(__name__)

# Função para conectar ao banco de dados Oracle
def conectar():
    try:
        # Criando a string de conexão usando makedsn
        dados_serv = oracledb.makedsn(host="oracle.fiap.com.br", port=1521, service_name="ORCL")

        # Estabelecendo a conexão com o banco de dados
        connection = oracledb.connect(
            user="RM557881 ",  # Substitua com o usuário correto
            password="121079",  # Substitua com a senha correta
            dsn=dados_serv
        )

        # Log para confirmar a conexão
        logger.info(f"Conexão estabelecida com sucesso! Host: localhost, Porta: 1521, Service Name: XEPDB1, Usuário: challenge")
        return connection

    except oracledb.Error as e:
        # Captura e exibe detalhes do erro
        error, = e.args
        logger.error(f"Erro ao tentar conectar ao banco de dados Oracle. Detalhes do erro: "
                     f"Código do erro: {error.code}, Mensagem: {error.message}, DSN: {dados_serv}")
        return None

# Função para fechar a conexão
def fechar_conexao(connection):
    if connection:
        try:
            connection.close()
            logger.info("Conexão fechada com sucesso.")
        except oracledb.Error as e:
            error, = e.args
            logger.error(f"Erro ao tentar fechar a conexão com o banco de dados. Detalhes do erro: "
                         f"Código do erro: {error.code}, Mensagem: {error.message}")
