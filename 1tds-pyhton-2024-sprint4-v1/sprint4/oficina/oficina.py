from datetime import datetime
import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from conexao.conectaBD import conectar, fechar_conexao
from conectaAI.gemini import consultarGemini

# Definição do Blueprint
oficina_bp = Blueprint('oficina', __name__)
logger = logging.getLogger(__name__)

# Rota para o menu principal da oficina
@oficina_bp.route('/', methods=['GET'])
def menu_oficina():
    return render_template('oficina/menu_oficina.html')

# Rota para cadastrar oficina
@oficina_bp.route('/cadastrar', methods=['GET', 'POST'])
def cadastrar_oficina():
    if request.method == 'POST':
        data_oficina = request.form.get('data_oficina')
        descricao_problema = request.form.get('descricao_problema')
        diagnostico = request.form.get('diagnostico')
        partes_afetadas = request.form.get('partes_afetadas')
        horas_trabalhadas = request.form.get('horas_trabalhadas')

        if not all([data_oficina, descricao_problema, diagnostico, partes_afetadas, horas_trabalhadas]):
            flash("Por favor, preencha todos os campos.", "error")
            return render_template('oficina/cadastrar_oficina.html')

        conexao = conectar()
        cursor = conexao.cursor()
        try:
            cursor.execute("""
                INSERT INTO oficinas (data_oficina, descricao_problema, diagnostico, partes_afetadas, horas_trabalhadas)
                VALUES (TO_DATE(:data_oficina, 'YYYY-MM-DD'), :descricao_problema, :diagnostico, :partes_afetadas, :horas_trabalhadas)
            """, {
                'data_oficina': data_oficina,
                'descricao_problema': descricao_problema,
                'diagnostico': diagnostico,
                'partes_afetadas': partes_afetadas,
                'horas_trabalhadas': horas_trabalhadas
            })
            conexao.commit()
            flash("Oficina cadastrada com sucesso!", "success")
        except Exception as e:
            conexao.rollback()
            flash(f"Erro ao cadastrar oficina: {e}", "error")
            logger.error(f"Erro ao cadastrar oficina: {e}")
        finally:
            fechar_conexao(conexao)
        return redirect(url_for('oficina.listar_oficinas'))

    return render_template('oficina/cadastrar_oficina.html')

# Rota para buscar diagnóstico usando IA (API Gemini)
@oficina_bp.route('/diagnostico', methods=['POST'])
def buscar_diagnostico():
    data = request.get_json()
    descricao_problema = data.get('descricao_problema')
    diagnostico = consultarGemini(descricao_problema)
    return jsonify({'diagnostico': diagnostico})

# Rota para listar todas as oficinas
@oficina_bp.route('/listar', methods=['GET'])
def listar_oficinas():
    try:
        conexao = conectar()
        cursor = conexao.cursor()
        cursor.execute("""
            SELECT id_ofic, data_oficina, descricao_problema, diagnostico, partes_afetadas, horas_trabalhadas
            FROM oficinas
            ORDER BY data_oficina DESC
        """)
        oficinas = cursor.fetchall()
        oficinas_lista = [
            {
                'id': oficina[0],
                'data_oficina': oficina[1].strftime('%d/%m/%Y') if oficina[1] else 'N/A',
                'descricao_problema': oficina[2],
                'diagnostico': oficina[3],
                'partes_afetadas': oficina[4],
                'horas_trabalhadas': oficina[5]
            }
            for oficina in oficinas
        ]
    except Exception as e:
        flash(f"Erro ao listar oficinas: {e}", "error")
        logger.error(f"Erro ao listar oficinas: {e}")
        oficinas_lista = []
    finally:
        if 'conexao' in locals():
            fechar_conexao(conexao)

    return render_template('oficina/listar_oficina.html', oficinas=oficinas_lista)

# Rota para buscar e redirecionar diretamente para alterar
@oficina_bp.route('/buscar_alterar', methods=['GET', 'POST'])
def buscar_oficina_para_alterar():
    if request.method == 'POST':
        search_term = request.form.get('search_term')

        if not search_term:
            flash("Por favor, insira o ID ou Descrição do Problema da oficina.", "error")
            return render_template('oficina/buscar_oficina.html', action="Alterar")

        try:
            conexao = conectar()
            cursor = conexao.cursor()
            cursor.execute("""
                SELECT id_ofic FROM oficinas
                WHERE id_ofic = :search_term OR LOWER(descricao_problema) LIKE LOWER(:search_pattern)
            """, {
                'search_term': search_term if search_term.isdigit() else None,
                'search_pattern': f'%{search_term}%'
            })
            oficina = cursor.fetchone()
            if oficina:
                return redirect(url_for('oficina.alterar_oficina', id_ofic=oficina[0]))
            else:
                flash("Nenhuma oficina encontrada com os critérios fornecidos.", "error")
        except Exception as e:
            flash(f"Erro ao buscar oficina: {e}", "error")
            logger.error(f"Erro ao buscar oficina: {e}")
        finally:
            if 'conexao' in locals():
                fechar_conexao(conexao)

    return render_template('oficina/buscar_oficina.html', action="Alterar")

# Rota para alterar oficina
@oficina_bp.route('/alterar/<int:id_ofic>', methods=['GET', 'POST'])
def alterar_oficina(id_ofic):
    if request.method == 'POST':
        data_oficina = request.form.get('data_oficina')
        descricao_problema = request.form.get('descricao_problema')
        diagnostico = request.form.get('diagnostico')
        partes_afetadas = request.form.get('partes_afetadas')
        horas_trabalhadas = request.form.get('horas_trabalhadas')

        conexao = conectar()
        cursor = conexao.cursor()
        try:
            cursor.execute("""
                UPDATE oficinas
                SET data_oficina = TO_DATE(:data_oficina, 'YYYY-MM-DD'),
                    descricao_problema = :descricao_problema,
                    diagnostico = :diagnostico,
                    partes_afetadas = :partes_afetadas,
                    horas_trabalhadas = :horas_trabalhadas
                WHERE id_ofic = :id_ofic
            """, {
                'data_oficina': data_oficina,
                'descricao_problema': descricao_problema,
                'diagnostico': diagnostico,
                'partes_afetadas': partes_afetadas,
                'horas_trabalhadas': horas_trabalhadas,
                'id_ofic': id_ofic
            })
            conexao.commit()
            flash("Oficina alterada com sucesso!", "success")
        except Exception as e:
            conexao.rollback()
            flash(f"Erro ao alterar oficina: {e}", "error")
            logger.error(f"Erro ao alterar oficina: {e}")
        finally:
            fechar_conexao(conexao)

        return redirect(url_for('oficina.listar_oficinas'))

    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("""
        SELECT id_ofic, data_oficina, descricao_problema, diagnostico, partes_afetadas, horas_trabalhadas
        FROM oficinas
        WHERE id_ofic = :id_ofic
    """, {'id_ofic': id_ofic})
    oficina = cursor.fetchone()
    fechar_conexao(conexao)

    if oficina:
        oficina_data = {
            'id': oficina[0],
            'data_oficina': oficina[1].strftime('%Y-%m-%d') if oficina[1] else '',
            'descricao_problema': oficina[2],
            'diagnostico': oficina[3],
            'partes_afetadas': oficina[4],
            'horas_trabalhadas': oficina[5]
        }
        return render_template('oficina/alterar_oficina.html', oficina=oficina_data)
    else:
        flash("Oficina não encontrada.", "error")
        return redirect(url_for('oficina.listar_oficinas'))

# Função para buscar e exibir uma oficina para confirmação de deleção
@oficina_bp.route('/buscar_deletar', methods=['GET', 'POST'])
def buscar_oficina_para_deletar():
    if request.method == 'POST':
        oficina_id = request.form.get('oficina_id')

        if not oficina_id:
            flash("Por favor, insira o ID da oficina.", "error")
            return render_template('oficina/deletar_oficina.html')

        try:
            conexao = conectar()
            cursor = conexao.cursor()
            cursor.execute("""
                SELECT id_ofic, data_oficina, descricao_problema, diagnostico, partes_afetadas, horas_trabalhadas
                FROM oficinas WHERE id_ofic = :oficina_id
            """, {'oficina_id': oficina_id})
            oficina = cursor.fetchone()
            fechar_conexao(conexao)

            if oficina:
                oficina_data = {
                    'id': oficina[0],
                    'data_oficina': oficina[1].strftime('%d/%m/%Y') if oficina[1] else '',
                    'descricao_problema': oficina[2],
                    'diagnostico': oficina[3],
                    'partes_afetadas': oficina[4],
                    'horas_trabalhadas': oficina[5]
                }
                return render_template('oficina/deletar_oficina.html', oficina=oficina_data)
            else:
                flash("Oficina não encontrada com o ID fornecido.", "error")

        except Exception as e:
            flash(f"Erro ao buscar oficina: {e}", "error")
            logger.error(f"Erro ao buscar oficina: {e}")
    return render_template('oficina/deletar_oficina.html')

# Função para confirmar a exclusão da oficina
@oficina_bp.route('/confirmar_deletar/<int:id_ofic>', methods=['POST'])
def confirmar_deletar_oficina(id_ofic):
    try:
        conexao = conectar()
        cursor = conexao.cursor()
        cursor.execute("DELETE FROM oficinas WHERE id_ofic = :id_ofic", {'id_ofic': id_ofic})
        conexao.commit()
        flash("Oficina deletada com sucesso!", "success")
    except Exception as e:
        conexao.rollback()
        flash(f"Erro ao deletar oficina: {e}", "error")
        logger.error(f"Erro ao deletar oficina: {e}")
    finally:
        fechar_conexao(conexao)

    return redirect(url_for('oficina.menu_oficina'))



# Rota para deletar oficina
@oficina_bp.route('/deletar/<int:id_ofic>', methods=['POST'])
def deletar_oficina(id_ofic):
    conexao = conectar()
    cursor = conexao.cursor()
    try:
        cursor.execute("DELETE FROM oficinas WHERE id_ofic = :id_ofic", {'id_ofic': id_ofic})
        conexao.commit()
        flash("Oficina deletada com sucesso!", "success")
    except Exception as e:
        conexao.rollback()
        flash(f"Erro ao deletar oficina: {e}", "error")
        logger.error(f"Erro ao deletar oficina: {e}")
    finally:
        fechar_conexao(conexao)

    return redirect(url_for('oficina.listar_oficinas'))

