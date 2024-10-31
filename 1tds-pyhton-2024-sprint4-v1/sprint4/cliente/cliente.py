from datetime import datetime, date
import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash
from conexao.conectaBD import conectar, fechar_conexao

# Criação do Blueprint
cliente_bp = Blueprint('cliente', __name__, template_folder='templates/cliente')

logger = logging.getLogger(__name__)

@cliente_bp.route('/clientes')
def menu_clientes():
    return render_template('cliente/menu_cliente.html')

@cliente_bp.route('/clientes/cadastrar', methods=['GET', 'POST'])
def cadastrar_cliente():
    if request.method == 'POST':
        try:
            logger.debug("Recebendo dados do formulário de cadastro de cliente.")
            tipo_cliente = request.form.get('tipo_cliente')
            nome = request.form.get('nome')
            sobrenome = request.form.get('sobrenome')
            sexo = request.form.get('sexo')
            tipo_documento = request.form.get('tipo_documento')
            numero_documento = request.form.get('numero_documento')
            data_nascimento = request.form.get('data_nascimento')
            atividade_profissional = request.form.get('atividade_profissional')

            telefone = request.form.get('telefone')  # Este campo não é obrigatório
            celular = request.form.get('celular')
            email = request.form.get('email')
            contato = request.form.get('contato')  # Este campo pode ser opcional ou obrigatório conforme sua lógica

            numero = request.form.get('numeroCasa')
            cep = request.form.get('cep')
            logradouro = request.form.get('logradouro')
            bairro = request.form.get('bairro')
            cidade = request.form.get('cidade')
            estado = request.form.get('estado')
            complemento = request.form.get('complemento')  # Este campo é opcional

            # Verificação dos campos obrigatórios
            if not all([tipo_cliente, nome, sobrenome, sexo, tipo_documento, numero_documento, data_nascimento,
                        atividade_profissional, celular, email, numero, cep, logradouro, bairro, cidade,
                        estado]):
                flash("Preencha todos os campos obrigatórios.", "error")
                return render_template('cliente/cadastrar_cliente.html')

            conexao = conectar()
            cursor = conexao.cursor()

            # Inserir em contatos e obter o ID gerado usando RETURNING
            id_contato_var = cursor.var(int)
            cursor.execute("""
                INSERT INTO contatos (celular, email, contato)
                VALUES (:celular, :email, :contato)
                RETURNING id_cont INTO :id_contato
            """, {
                'celular': celular,
                'email': email,
                'contato': contato,
                'id_contato': id_contato_var
            })
            id_contato = id_contato_var.getvalue()[0]

            # Inserir em enderecos e obter o ID gerado usando RETURNING
            id_endereco_var = cursor.var(int)
            cursor.execute("""
                INSERT INTO enderecos (numero, cep, logradouro, bairro, cidade, estado, complemento)
                VALUES (:numero, :cep, :logradouro, :bairro, :cidade, :estado, :complemento)
                RETURNING id_end INTO :id_endereco
            """, {
                'numero': numero,
                'cep': cep,
                'logradouro': logradouro,
                'bairro': bairro,
                'cidade': cidade,
                'estado': estado,
                'complemento': complemento,
                'id_endereco': id_endereco_var
            })
            id_endereco = id_endereco_var.getvalue()[0]

            # Inserir em clientes usando os IDs obtidos
            cursor.execute("""
                INSERT INTO clientes (tipo_cliente, nome, sobrenome, sexo, tipo_documento, numero_documento, data_nascimento, atividade_profissional, contatos_id_cont, enderecos_id_end)
                VALUES (:tipo_cliente, :nome, :sobrenome, :sexo, :tipo_documento, :numero_documento, TO_DATE(:data_nascimento, 'YYYY-MM-DD'), :atividade_profissional, :id_contato, :id_endereco)
            """, {
                'tipo_cliente': tipo_cliente,
                'nome': nome,
                'sobrenome': sobrenome,
                'sexo': sexo,
                'tipo_documento': tipo_documento,
                'numero_documento': numero_documento,
                'data_nascimento': data_nascimento,
                'atividade_profissional': atividade_profissional,
                'id_contato': id_contato,
                'id_endereco': id_endereco
            })
            conexao.commit()
            flash("Cliente cadastrado com sucesso!", "success")
        except Exception as e:
            if 'conexao' in locals():
                conexao.rollback()
            flash(f"Erro ao cadastrar cliente: {e}", "error")
            logger.error(f"Erro ao cadastrar cliente: {e}")
        finally:
            if 'conexao' in locals():
                fechar_conexao(conexao)

        return redirect(url_for('cliente.menu_clientes'))
    return render_template('cliente/cadastrar_cliente.html')



@cliente_bp.route('/clientes/listar', methods=['GET'])
def listar_clientes():
    try:
        conexao = conectar()
        cursor = conexao.cursor()
        cursor.execute("""
            SELECT c.id_cli, c.nome, c.sobrenome, c.sexo, c.tipo_documento, c.numero_documento, 
                   c.data_nascimento, c.atividade_profissional,
                   t.celular, t.email, t.contato,
                   e.numero, e.cep, e.logradouro, e.bairro, e.cidade, e.estado, e.complemento
            FROM clientes c
            JOIN contatos t ON c.contatos_id_cont = t.id_cont
            JOIN enderecos e ON c.enderecos_id_end = e.id_end
        """)
        clientes = cursor.fetchall()
        clientes_lista = [
            {
                'id': cliente[0],
                'nome': cliente[1],
                'sobrenome': cliente[2],
                'sexo': cliente[3],
                'tipo_documento': cliente[4],
                'numero_documento': cliente[5],
                'data_nascimento': cliente[6].strftime('%d/%m/%Y') if isinstance(cliente[6], (datetime, date)) else cliente[6],
                'atividade_profissional': cliente[7],
                'celular': cliente[8],
                'email': cliente[9],
                'contato': cliente[10],
                'numero': cliente[11],
                'cep': cliente[12],
                'logradouro': cliente[13],
                'bairro': cliente[14],
                'cidade': cliente[15],
                'estado': cliente[16],
                'complemento': cliente[17]
            }
            for cliente in clientes
        ]
    except Exception as e:
        flash(f"Erro ao listar clientes: {e}", "error")
        logger.error(f"Erro ao listar clientes: {e}")
        clientes_lista = []
    finally:
        if 'conexao' in locals():
            fechar_conexao(conexao)

    return render_template('cliente/listar_clientes.html', clientes=clientes_lista)

# Função para alterar cliente
# Função de busca para redirecionar ao formulário de alteração
@cliente_bp.route('/clientes/buscar', methods=['GET', 'POST'])
def buscar_cliente():
    if request.method == 'POST':
        cliente_id = request.form.get('cliente_id')
        nome = request.form.get('nome')

        try:
            conexao = conectar()
            cursor = conexao.cursor()

            # Busca o cliente por ID ou nome
            if cliente_id:
                cursor.execute("SELECT id_cli FROM clientes WHERE id_cli = :cliente_id", {'cliente_id': cliente_id})
            elif nome:
                cursor.execute("SELECT id_cli FROM clientes WHERE nome LIKE :nome", {'nome': f'%{nome}%'})
            else:
                flash("Por favor, insira o ID ou o nome do cliente para buscar.", "error")
                return redirect(url_for('cliente.buscar_cliente'))

            cliente = cursor.fetchone()
            if cliente:
                id_cli = cliente[0]
                return redirect(url_for('cliente.alterar_cliente', id_cli=id_cli))
            else:
                flash("Cliente não encontrado.", "error")
                return redirect(url_for('cliente.buscar_cliente'))

        except Exception as e:
            flash(f"Erro ao buscar cliente: {e}", "error")
            logger.error(f"Erro ao buscar cliente: {e}")
        finally:
            if 'conexao' in locals():
                fechar_conexao(conexao)

    return render_template('cliente/buscar_cliente.html')


# Função para carregar e alterar dados do cliente
@cliente_bp.route('/clientes/alterar/<int:id_cli>', methods=['GET', 'POST'])
def alterar_cliente(id_cli):
    try:
        conexao = conectar()
        cursor = conexao.cursor()

        # Se for POST, processa o formulário para atualizar os dados
        if request.method == 'POST':
            tipo_cliente = request.form.get('tipo_cliente')
            nome = request.form.get('nome')
            sobrenome = request.form.get('sobrenome')
            sexo = request.form.get('sexo')
            tipo_documento = request.form.get('tipo_documento')
            numero_documento = request.form.get('numero_documento')
            data_nascimento = request.form.get('data_nascimento')
            atividade_profissional = request.form.get('atividade_profissional')

            celular = request.form.get('celular')
            email = request.form.get('email')
            contato = request.form.get('contato')

            numero = request.form.get('numeroCasa')
            cep = request.form.get('cep')
            logradouro = request.form.get('logradouro')
            bairro = request.form.get('bairro')
            cidade = request.form.get('cidade')
            estado = request.form.get('estado')
            complemento = request.form.get('complemento')

            # Atualiza os dados do cliente
            cursor.execute("""
                UPDATE clientes
                SET tipo_cliente=:tipo_cliente, nome=:nome, sobrenome=:sobrenome, sexo=:sexo,
                    tipo_documento=:tipo_documento, numero_documento=:numero_documento,
                    data_nascimento=TO_DATE(:data_nascimento, 'YYYY-MM-DD'), atividade_profissional=:atividade_profissional
                WHERE id_cli=:id_cli
            """, {
                'tipo_cliente': tipo_cliente,
                'nome': nome,
                'sobrenome': sobrenome,
                'sexo': sexo,
                'tipo_documento': tipo_documento,
                'numero_documento': numero_documento,
                'data_nascimento': data_nascimento,
                'atividade_profissional': atividade_profissional,
                'id_cli': id_cli
            })

            # Atualiza os dados de contato
            cursor.execute("""
                UPDATE contatos
                SET celular=:celular, email=:email, contato=:contato
                WHERE id_cont=(SELECT contatos_id_cont FROM clientes WHERE id_cli=:id_cli)
            """, {
                'celular': celular,
                'email': email,
                'contato': contato,
                'id_cli': id_cli
            })

            # Atualiza os dados de endereço
            cursor.execute("""
                UPDATE enderecos
                SET numero=:numero, cep=:cep, logradouro=:logradouro, bairro=:bairro,
                    cidade=:cidade, estado=:estado, complemento=:complemento
                WHERE id_end=(SELECT enderecos_id_end FROM clientes WHERE id_cli=:id_cli)
            """, {
                'numero': numero,
                'cep': cep,
                'logradouro': logradouro,
                'bairro': bairro,
                'cidade': cidade,
                'estado': estado,
                'complemento': complemento,
                'id_cli': id_cli
            })

            conexao.commit()
            flash("Cliente alterado com sucesso!", "success")
            return redirect(url_for('cliente.listar_clientes'))

        # Se GET, carrega os dados do cliente para preencher o formulário
        cursor.execute("""
            SELECT c.tipo_cliente, c.nome, c.sobrenome, c.sexo, c.tipo_documento, c.numero_documento,
                   TO_CHAR(c.data_nascimento, 'YYYY-MM-DD') AS data_nascimento, c.atividade_profissional,
                   t.celular, t.email, t.contato,
                   e.numero, e.cep, e.logradouro, e.bairro, e.cidade, e.estado, e.complemento
            FROM clientes c
            JOIN contatos t ON c.contatos_id_cont = t.id_cont
            JOIN enderecos e ON c.enderecos_id_end = e.id_end
            WHERE c.id_cli = :id_cli
        """, {'id_cli': id_cli})
        cliente = cursor.fetchone()

        if cliente is None:
            flash("Cliente não encontrado.", "error")
            return redirect(url_for('cliente.listar_clientes'))

        cliente_data = {
            'id_cli': id_cli,
            'tipo_cliente': cliente[0],
            'nome': cliente[1],
            'sobrenome': cliente[2],
            'sexo': cliente[3],
            'tipo_documento': cliente[4],
            'numero_documento': cliente[5],
            'data_nascimento': cliente[6],
            'atividade_profissional': cliente[7],
            'celular': cliente[8],
            'email': cliente[9],
            'contato': cliente[10],
            'numero': cliente[11],
            'cep': cliente[12],
            'logradouro': cliente[13],
            'bairro': cliente[14],
            'cidade': cliente[15],
            'estado': cliente[16],
            'complemento': cliente[17]
        }

    except Exception as e:
        flash(f"Erro ao carregar dados do cliente: {e}", "error")
        logger.error(f"Erro ao carregar dados do cliente: {e}")
        return redirect(url_for('cliente.listar_clientes'))
    finally:
        if 'conexao' in locals():
            fechar_conexao(conexao)

    return render_template('cliente/alterar_cliente.html', cliente=cliente_data)

# Função para deletar cliente
@cliente_bp.route('/clientes/deletar', methods=['GET', 'POST'])
def deletar_cliente():
    if request.method == 'POST':
        cliente_id = request.form.get('cliente_id')

        if cliente_id:
            try:
                conexao = conectar()
                cursor = conexao.cursor()

                # Buscar o cliente pelo ID
                cursor.execute("""
                    SELECT id_cli, nome, sobrenome
                    FROM clientes
                    WHERE id_cli = :cliente_id
                """, {'cliente_id': cliente_id})
                cliente = cursor.fetchone()

                if cliente:
                    # Cliente encontrado, exibir o nome e o botão de confirmação de exclusão
                    cliente_data = {
                        'id_cli': cliente[0],
                        'nome': cliente[1],
                        'sobrenome': cliente[2]
                    }
                    return render_template('cliente/deletar_cliente.html', cliente=cliente_data)
                else:
                    # Cliente não encontrado
                    flash("Cliente não encontrado.", "error")
                    return render_template('cliente/deletar_cliente.html', cliente_not_found=True)

            except Exception as e:
                flash(f"Erro ao buscar cliente: {e}", "error")
                logger.error(f"Erro ao buscar cliente: {e}")
                return redirect(url_for('cliente.menu_clientes'))

            finally:
                if 'conexao' in locals():
                    fechar_conexao(conexao)

        # Se o cliente_id não for fornecido, exibe a página novamente
        return render_template('cliente/deletar_cliente.html')

    # GET request para exibir a página pela primeira vez
    return render_template('cliente/deletar_cliente.html')


@cliente_bp.route('/clientes/deletar/confirmar/<int:id_cli>', methods=['POST'])
def confirmar_deletar_cliente(id_cli):
    try:
        conexao = conectar()
        cursor = conexao.cursor()

        # Exclui o cliente do banco de dados
        cursor.execute("DELETE FROM clientes WHERE id_cli = :id_cli", {'id_cli': id_cli})
        conexao.commit()
        flash("Cliente deletado com sucesso!", "success")
    except Exception as e:
        flash(f"Erro ao deletar cliente: {e}", "error")
        logger.error(f"Erro ao deletar cliente: {e}")
    finally:
        if 'conexao' in locals():
            fechar_conexao(conexao)

    return redirect(url_for('cliente.menu_clientes'))

