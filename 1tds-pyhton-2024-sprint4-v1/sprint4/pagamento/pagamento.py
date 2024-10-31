from datetime import datetime
import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from conexao.conectaBD import conectar, fechar_conexao

pagamento_bp = Blueprint('pagamento', __name__, template_folder='../templates/pagamento')
logger = logging.getLogger(__name__)

# Rota para o menu principal de pagamentos
@pagamento_bp.route('/')
def menu_pagamento():
    return render_template('pagamento/menu_pagamento.html')

# Rota para cadastrar pagamento
@pagamento_bp.route('/cadastrar', methods=['GET', 'POST'])
def cadastrar_pagamento():
    if request.method == 'POST':
        try:
            data_pagamento = request.form.get('data_pagamento')
            tipo_pagamento = request.form.get('tipo_pagamento')
            desconto = float(request.form.get('desconto', 0))
            total_parcelas = int(request.form.get('total_parcelas', 1))

            valor_servico_str = request.form.get('valor_servico', '0').replace('.', '').replace(',', '.')
            valor_servico = float(valor_servico_str)

            total_pagamento_desconto = valor_servico - (valor_servico * desconto / 100)
            valor_parcelas = total_pagamento_desconto / total_parcelas

            # Inserir no banco
            conexao = conectar()
            cursor = conexao.cursor()
            cursor.execute("""
                INSERT INTO pagamentos (data_pagamento, tipo_pagamento, desconto, total_parcelas, valor_parcelas, total_pagamento_desconto)
                VALUES (TO_DATE(:data_pagamento, 'YYYY-MM-DD'), :tipo_pagamento, :desconto, :total_parcelas, :valor_parcelas, :total_pagamento_desconto)
            """, {
                'data_pagamento': data_pagamento,
                'tipo_pagamento': tipo_pagamento,
                'desconto': desconto,
                'total_parcelas': total_parcelas,
                'valor_parcelas': valor_parcelas,
                'total_pagamento_desconto': total_pagamento_desconto
            })
            conexao.commit()
            flash("Pagamento cadastrado com sucesso!", "success")
        except ValueError as e:
            flash(f"Erro ao converter valores monetários: {e}", "error")
        except Exception as e:
            conexao.rollback()
            flash(f"Erro ao cadastrar pagamento: {e}", "error")
            logger.error(f"Erro ao cadastrar pagamento: {e}")
        finally:
            fechar_conexao(conexao)
    return render_template('pagamento/cadastrar_pagamento.html')


# Rota para listar todos os pagamentos
@pagamento_bp.route('/listar', methods=['GET'])
def listar_pagamentos():
    try:
        conexao = conectar()
        cursor = conexao.cursor()
        cursor.execute("""
            SELECT id_pag, data_pagamento, tipo_pagamento, desconto, total_parcelas, valor_parcelas, total_pagamento_desconto
            FROM pagamentos
            ORDER BY data_pagamento DESC
        """)
        pagamentos = cursor.fetchall()
        pagamentos_lista = [
            {
                'id': pagamento[0],
                'data_pagamento': pagamento[1].strftime('%d/%m/%Y') if pagamento[1] else 'N/A',
                'tipo_pagamento': pagamento[2],
                'desconto': pagamento[3],
                'total_parcelas': pagamento[4],
                'valor_parcelas': pagamento[5],
                'total_pagamento_desconto': pagamento[6]
            }
            for pagamento in pagamentos
        ]
    except Exception as e:
        flash(f"Erro ao listar pagamentos: {e}", "error")
        logger.error(f"Erro ao listar pagamentos: {e}")
        pagamentos_lista = []
    finally:
        if 'conexao' in locals():
            fechar_conexao(conexao)

    return render_template('pagamento/listar_pagamento.html', pagamentos=pagamentos_lista)


# Rota para buscar pagamento para alteração
# Rota para buscar pagamento para alteração
@pagamento_bp.route('/buscar_pagamento_para_alterar', methods=['GET', 'POST'])
def buscar_pagamento_para_alterar():
    if request.method == 'POST':
        pagamento_id = request.form.get('pagamento_id')
        if not pagamento_id:
            flash("Por favor, insira o ID do pagamento.", "error")
            return render_template('pagamento/buscar_pagamento_para_alterar.html')

        try:
            conexao = conectar()
            cursor = conexao.cursor()
            cursor.execute("""
                SELECT id_pag, data_pagamento, tipo_pagamento, desconto, total_parcelas, valor_parcelas, total_pagamento_desconto
                FROM pagamentos WHERE id_pag = :pagamento_id
            """, {'pagamento_id': pagamento_id})
            pagamento = cursor.fetchone()
            fechar_conexao(conexao)

            if pagamento:
                pagamento_data = {
                    'id': pagamento[0],
                    'data_pagamento': pagamento[1].strftime('%Y-%m-%d') if pagamento[1] else '',
                    'tipo_pagamento': pagamento[2],
                    'desconto': pagamento[3],
                    'total_parcelas': pagamento[4],
                    'valor_parcelas': pagamento[5],
                    'total_pagamento_desconto': pagamento[6]
                }
                return render_template('pagamento/alterar_pagamento.html', pagamento=pagamento_data)
            else:
                flash("Pagamento não encontrado com o ID fornecido.", "error")
        except Exception as e:
            flash(f"Erro ao buscar pagamento: {e}", "error")
            logger.error(f"Erro ao buscar pagamento: {e}")

    return render_template('pagamento/buscar_pagamento_para_alterar.html')



# Rota para alterar pagamento
# Rota para alterar pagamento
@pagamento_bp.route('/alterar/<int:id_pag>', methods=['POST'])
def alterar_pagamento(id_pag):
    if request.method == 'POST':
        data_pagamento = request.form.get('data_pagamento')
        tipo_pagamento = request.form.get('tipo_pagamento')
        desconto = float(request.form.get('desconto', 0))
        total_parcelas = int(request.form.get('total_parcelas', 1))
        valor_servico_str = request.form.get('valor_servico', '0').replace('.', '').replace(',', '.')
        valor_servico = float(valor_servico_str)

        total_pagamento_desconto = valor_servico - (valor_servico * desconto / 100)
        valor_parcelas = total_pagamento_desconto / total_parcelas

        try:
            conexao = conectar()
            cursor = conexao.cursor()
            cursor.execute("""
                UPDATE pagamentos
                SET data_pagamento = TO_DATE(:data_pagamento, 'YYYY-MM-DD'),
                    tipo_pagamento = :tipo_pagamento,
                    desconto = :desconto,
                    total_parcelas = :total_parcelas,
                    valor_parcelas = :valor_parcelas,
                    total_pagamento_desconto = :total_pagamento_desconto
                WHERE id_pag = :id_pag
            """, {
                'data_pagamento': data_pagamento,
                'tipo_pagamento': tipo_pagamento,
                'desconto': desconto,
                'total_parcelas': total_parcelas,
                'valor_parcelas': valor_parcelas,
                'total_pagamento_desconto': total_pagamento_desconto,
                'id_pag': id_pag
            })
            conexao.commit()
            flash("Pagamento alterado com sucesso!", "success")
        except Exception as e:
            conexao.rollback()
            flash(f"Erro ao alterar pagamento: {e}", "error")
            logger.error(f"Erro ao alterar pagamento: {e}")
        finally:
            fechar_conexao(conexao)

        return redirect(url_for('pagamento.listar_pagamentos'))

    return render_template('pagamento/alterar_pagamento.html')


# Rota para buscar pagamento para deletar
# Rota para buscar pagamento para deletar
@pagamento_bp.route('/buscar_pagamento_para_deletar', methods=['GET', 'POST'])
def buscar_pagamento_para_deletar():
    if request.method == 'POST':
        pagamento_id = request.form.get('pagamento_id')
        if not pagamento_id:
            flash("Por favor, insira o ID do pagamento.", "error")
            return render_template('pagamento/buscar_pagamento_para_deletar.html')

        try:
            conexao = conectar()
            cursor = conexao.cursor()
            cursor.execute("""
                SELECT id_pag, data_pagamento, tipo_pagamento, desconto, total_parcelas, valor_parcelas, total_pagamento_desconto
                FROM pagamentos WHERE id_pag = :pagamento_id
            """, {'pagamento_id': pagamento_id})
            pagamento = cursor.fetchone()
            fechar_conexao(conexao)

            if pagamento:
                pagamento_data = {
                    'id': pagamento[0],
                    'data_pagamento': pagamento[1].strftime('%d/%m/%Y') if pagamento[1] else '',
                    'tipo_pagamento': pagamento[2],
                    'desconto': pagamento[3],
                    'total_parcelas': pagamento[4],
                    'valor_parcelas': pagamento[5],
                    'total_pagamento_desconto': pagamento[6]
                }
                return render_template('pagamento/deletar_pagamento.html', pagamento=pagamento_data)
            else:
                flash("Pagamento não encontrado com o ID fornecido.", "error")
        except Exception as e:
            flash(f"Erro ao buscar pagamento: {e}", "error")
            logger.error(f"Erro ao buscar pagamento: {e}")

    return render_template('pagamento/buscar_pagamento_para_deletar.html')


# Rota para confirmar a exclusão do pagamento
@pagamento_bp.route('/confirmar_deletar/<int:id_pag>', methods=['POST'])
def confirmar_deletar_pagamento(id_pag):
    try:
        conexao = conectar()
        cursor = conexao.cursor()
        cursor.execute("DELETE FROM pagamentos WHERE id_pag = :id_pag", {'id_pag': id_pag})
        conexao.commit()
        flash("Pagamento deletado com sucesso!", "success")
    except Exception as e:
        conexao.rollback()
        flash(f"Erro ao deletar pagamento: {e}", "error")
        logger.error(f"Erro ao deletar pagamento: {e}")
    finally:
        fechar_conexao(conexao)

    return redirect(url_for('pagamento.menu_pagamento'))
