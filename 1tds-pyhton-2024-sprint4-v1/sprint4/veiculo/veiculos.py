from datetime import datetime
import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash
from conexao.conectaBD import conectar, fechar_conexao

# Definição do Blueprint
veiculo_bp = Blueprint('veiculo', __name__, template_folder='../templates/veiculo')
logger = logging.getLogger(__name__)

# Rota para o menu principal de veículos
@veiculo_bp.route('/', methods=['GET'])
def menu_veiculo():
    return render_template('veiculo/menu_veiculo.html')

# Rota para cadastrar veículo
@veiculo_bp.route('/cadastrar', methods=['GET', 'POST'])
def cadastrar_veiculo():
    if request.method == 'POST':
        tipo = request.form.get('tipo')
        renavam = request.form.get('renavam')
        placa = request.form.get('placa')
        modelo = request.form.get('modelo')
        proprietario = request.form.get('proprietario')
        montadora = request.form.get('montadora')
        cor = request.form.get('cor')
        motor = request.form.get('motor')
        ano_fabricacao = int(request.form.get('ano_fabricacao'))

        # Verificação de todos os campos
        if not all([tipo, renavam, placa, modelo, proprietario, montadora, cor, motor, ano_fabricacao]):
            flash("Por favor, preencha todos os campos.", "error")
            return render_template('veiculo/cadastrar_veiculo.html')

        # Conectando ao banco e executando o SQL
        conexao = conectar()
        cursor = conexao.cursor()
        try:
            logger.info(f"Cadastro de veículo: tipo={tipo}, ano_fabricacao={ano_fabricacao}")
            cursor.execute("""
                INSERT INTO VEICULOS (TIPO_VEICULO, RENAVAM, PLACA, MODELO, PROPRIETARIO, MONTADORA, COR, MOTOR, ANO_FABRICACAO)
                VALUES (:tipo, :renavam, :placa, :modelo, :proprietario, :montadora, :cor, :motor, TO_DATE(:ano_fabricacao, 'YYYY'))
            """, {
                'tipo': tipo,
                'renavam': renavam,
                'placa': placa,
                'modelo': modelo,
                'proprietario': proprietario,
                'montadora': montadora,
                'cor': cor,
                'motor': motor,
                'ano_fabricacao': ano_fabricacao
            })
            conexao.commit()
            flash("Veículo cadastrado com sucesso!", "success")
        except Exception as e:
            conexao.rollback()
            flash(f"Erro ao cadastrar veículo: {e}", "error")
            logger.error(f"Erro ao cadastrar veículo: {e}")
        finally:
            fechar_conexao(conexao)
        return redirect(url_for('veiculo.listar_veiculos'))

    return render_template('veiculo/cadastrar_veiculo.html')

# Rota para listar todos os veículos
@veiculo_bp.route('/listar', methods=['GET'])
def listar_veiculos():
    try:
        conexao = conectar()
        cursor = conexao.cursor()
        cursor.execute("""
            SELECT ID_VEI, TIPO_VEICULO, RENAVAM, PLACA, MODELO, PROPRIETARIO, MONTADORA, COR, MOTOR, TO_CHAR(ANO_FABRICACAO, 'YYYY')
            FROM VEICULOS
            ORDER BY MODELO ASC
        """)
        veiculos = cursor.fetchall()
        veiculos_lista = [
            {
                'id': veiculo[0],
                'tipo': veiculo[1],
                'renavam': veiculo[2],
                'placa': veiculo[3],
                'modelo': veiculo[4],
                'proprietario': veiculo[5],
                'montadora': veiculo[6],
                'cor': veiculo[7],
                'motor': veiculo[8],
                'ano_fabricacao': veiculo[9]
            }
            for veiculo in veiculos
        ]
    except Exception as e:
        flash(f"Erro ao listar veículos: {e}", "error")
        logger.error(f"Erro ao listar veículos: {e}")
        veiculos_lista = []
    finally:
        if 'conexao' in locals():
            fechar_conexao(conexao)

    return render_template('veiculo/listar_veiculos.html', veiculos=veiculos_lista)

# Rota para buscar veículo para alteração
@veiculo_bp.route('/buscar_alterar', methods=['GET', 'POST'])
def buscar_veiculo_para_alterar():
    if request.method == 'POST':
        search_term = request.form.get('search_term')
        if not search_term:
            flash("Por favor, insira o ID ou Modelo do Veículo.", "error")
            return render_template('veiculo/buscar_veiculo_para_alterar.html')

        try:
            conexao = conectar()
            cursor = conexao.cursor()
            cursor.execute("""
                SELECT ID_VEI, TIPO_VEICULO, RENAVAM, PLACA, MODELO, PROPRIETARIO, MONTADORA, COR, MOTOR, TO_CHAR(ANO_FABRICACAO, 'YYYY')
                FROM VEICULOS
                WHERE ID_VEI = :search_term OR LOWER(MODELO) LIKE LOWER(:search_pattern)
            """, {
                'search_term': search_term if search_term.isdigit() else None,
                'search_pattern': f'%{search_term}%'
            })
            veiculo = cursor.fetchone()
            fechar_conexao(conexao)

            if veiculo:
                veiculo_data = {
                    'id': veiculo[0],
                    'tipo': veiculo[1],
                    'renavam': veiculo[2],
                    'placa': veiculo[3],
                    'modelo': veiculo[4],
                    'proprietario': veiculo[5],
                    'montadora': veiculo[6],
                    'cor': veiculo[7],
                    'motor': veiculo[8],
                    'ano_fabricacao': veiculo[9]
                }
                return render_template('veiculo/alterar_veiculo.html', veiculo=veiculo_data)
            else:
                flash("Nenhum veículo encontrado com os critérios fornecidos.", "error")
        except Exception as e:
            flash(f"Erro ao buscar veículo: {e}", "error")
    return render_template('veiculo/buscar_veiculo_para_alterar.html')

# Rota para alterar veículo
@veiculo_bp.route('/alterar/<int:id_veiculo>', methods=['POST'])
def alterar_veiculo(id_veiculo):
    tipo = request.form.get('tipo')
    renavam = request.form.get('renavam')
    placa = request.form.get('placa')
    modelo = request.form.get('modelo')
    proprietario = request.form.get('proprietario')
    montadora = request.form.get('montadora')
    cor = request.form.get('cor')
    motor = request.form.get('motor')
    ano_fabricacao = request.form.get('ano_fabricacao')

    try:
        conexao = conectar()
        cursor = conexao.cursor()
        cursor.execute("""
            UPDATE VEICULOS
            SET TIPO_VEICULO = :tipo, RENAVAM = :renavam, PLACA = :placa, MODELO = :modelo,
                PROPRIETARIO = :proprietario, MONTADORA = :montadora, COR = :cor, MOTOR = :motor,
                ANO_FABRICACAO = TO_DATE(:ano_fabricacao, 'YYYY')
            WHERE ID_VEI = :id_veiculo
        """, {
            'tipo': tipo,
            'renavam': renavam,
            'placa': placa,
            'modelo': modelo,
            'proprietario': proprietario,
            'montadora': montadora,
            'cor': cor,
            'motor': motor,
            'ano_fabricacao': ano_fabricacao,
            'id_veiculo': id_veiculo
        })
        conexao.commit()
        flash("Veículo alterado com sucesso!", "success")
    except Exception as e:
        conexao.rollback()
        flash(f"Erro ao alterar veículo: {e}", "error")
    finally:
        fechar_conexao(conexao)
    return redirect(url_for('veiculo.listar_veiculos'))

# Rota para buscar veículo para deletar
@veiculo_bp.route('/buscar_deletar', methods=['GET', 'POST'])
def buscar_veiculo_para_deletar():
    if request.method == 'POST':
        search_term = request.form.get('search_term')
        if not search_term or not search_term.isdigit():
            flash("Por favor, insira um ID numérico válido do Veículo.", "error")
            return render_template('veiculo/buscar_veiculo_para_deletar.html')

        try:
            conexao = conectar()
            cursor = conexao.cursor()
            cursor.execute("""
                SELECT ID_VEI, MODELO, PLACA FROM VEICULOS
                WHERE ID_VEI = :search_term
            """, {'search_term': int(search_term)})  # Convertendo para inteiro

            veiculo = cursor.fetchone()
            fechar_conexao(conexao)

            if veiculo:
                veiculo_data = {
                    'id': veiculo[0],
                    'modelo': veiculo[1],
                    'placa': veiculo[2]
                }
                return render_template('veiculo/deletar_veiculo.html', veiculo=veiculo_data)
            else:
                flash("Nenhum veículo encontrado com o ID fornecido.", "error")
        except Exception as e:
            flash(f"Erro ao buscar veículo: {e}", "error")

    return render_template('veiculo/buscar_veiculo_para_deletar.html')



# Rota para confirmar exclusão de veículo
@veiculo_bp.route('/deletar/<int:id_veiculo>', methods=['POST'])
def deletar_veiculo(id_veiculo):
    try:
        conexao = conectar()
        cursor = conexao.cursor()
        cursor.execute("DELETE FROM VEICULOS WHERE ID_VEI = :id_veiculo", {'id_veiculo': id_veiculo})
        conexao.commit()
        flash("Veículo deletado com sucesso!", "success")
    except Exception as e:
        conexao.rollback()
        flash(f"Erro ao deletar veículo: {e}", "error")
    finally:
        fechar_conexao(conexao)
    return redirect(url_for('veiculo.menu_veiculo'))