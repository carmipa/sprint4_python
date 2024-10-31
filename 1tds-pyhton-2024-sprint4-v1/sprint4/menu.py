import os
import logging
from flask import Flask, render_template, url_for

# Configuração do Logger
current_dir = os.path.dirname(os.path.abspath(__file__))
log_filename = os.path.join(current_dir, 'app.log')

if not os.access(current_dir, os.W_OK):
    raise PermissionError(f"Sem permissão de escrita para o diretório: {current_dir}")

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler(log_filename),
                        logging.StreamHandler()
                    ],
                    force=True)
logger = logging.getLogger(__name__)
logger.info("Aplicação iniciada com sucesso.")

# Importação dos blueprints após configurar o logger
from cliente.cliente import cliente_bp

from agenda.agenda import agenda_bp

from oficina.oficina import oficina_bp

from pagamento.pagamento import pagamento_bp

from veiculo.veiculos import veiculo_bp

from orcamento.orcamento import orcamento_bp

# Configuração do caminho para a pasta 'static'
static_dir = os.path.join(current_dir, 'static')

# Inicialize o app Flask
app = Flask(__name__, static_folder=static_dir)
app.secret_key = 'sua_chave_secreta_aqui'

# Registro dos blueprints com prefixos para organização das rotas
app.register_blueprint(cliente_bp, url_prefix='/clientes')
app.register_blueprint(agenda_bp, url_prefix='/agenda')
app.register_blueprint(oficina_bp, url_prefix='/oficina')  # Prefixo '/oficina'
app.register_blueprint(pagamento_bp, url_prefix='/pagamento')
app.register_blueprint(veiculo_bp, url_prefix='/veiculos')

app.register_blueprint(orcamento_bp, url_prefix='/orcamento')

# Rota principal do menu
@app.route('/')
def menu_principal():
    return render_template('menu.html')

# Função para servir o CSS com marcação de data
@app.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)

def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.static_folder, filename)
            if os.path.exists(file_path):
                values['q'] = int(os.stat(file_path).st_mtime)
            else:
                raise FileNotFoundError(f"File not found: {file_path}")
    return url_for(endpoint, **values)

if __name__ == '__main__':
    app.run(debug=True)
