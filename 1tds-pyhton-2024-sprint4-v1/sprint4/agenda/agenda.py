from datetime import datetime, date
import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash
from conexao.conectaBD import conectar, fechar_conexao

# Definição do Blueprint sem especificar 'template_folder'
agenda_bp = Blueprint('agenda', __name__)

logger = logging.getLogger(__name__)

# Rota para menu de agenda
@agenda_bp.route('/agenda/')
def menu_agenda():
    return render_template('agenda/menu_agenda.html')  # Caminho completo do template

# Rota para cadastrar agenda
@agenda_bp.route('/agenda/cadastrar', methods=['GET', 'POST'])
def cadastrar_agenda():
    if request.method == 'POST':
        try:
            # Obtenção dos dados do formulário
            logger.debug("Recebendo dados do formulário de cadastro de agenda.")
            data_agendamento = request.form.get('data_agendamento')
            obs_agendamento = request.form.get('obs_agendamento')

            if not data_agendamento:
                flash("Data de agendamento é obrigatória.", "error")
                return render_template('agenda/cadastrar_agenda.html')

            conexao = conectar()
            cursor = conexao.cursor()

            # Inserir no banco de dados
            cursor.execute("""
                INSERT INTO agendar (data_agendamento, obs_agendamento)
                VALUES (TO_DATE(:data_agendamento, 'YYYY-MM-DD'), :obs_agendamento)
            """, {
                'data_agendamento': data_agendamento,
                'obs_agendamento': obs_agendamento
            })
            conexao.commit()
            flash("Agenda cadastrada com sucesso!", "success")
            return redirect(url_for('agenda.listar_agenda'))
        except Exception as e:
            if 'conexao' in locals():
                conexao.rollback()
            flash(f"Erro ao cadastrar agenda: {e}", "error")
            logger.error(f"Erro ao cadastrar agenda: {e}")
        finally:
            if 'conexao' in locals():
                fechar_conexao(conexao)
    return render_template('agenda/cadastrar_agenda.html')

# Rota para listar agendamentos
@agenda_bp.route('/agenda/listar', methods=['GET'])
def listar_agenda():
    try:
        conexao = conectar()
        cursor = conexao.cursor()
        cursor.execute("""
            SELECT id_age, data_agendamento, obs_agendamento
            FROM agendar
            ORDER BY data_agendamento DESC
        """)
        agenda = cursor.fetchall()
        agenda_lista = [
            {
                'id': ag[0],
                'data_agendamento': ag[1].strftime('%d/%m/%Y'),
                'obs_agendamento': ag[2]
            }
            for ag in agenda
        ]
    except Exception as e:
        flash(f"Erro ao listar agendas: {e}", "error")
        logger.error(f"Erro ao listar agendas: {e}")
        agenda_lista = []
    finally:
        if 'conexao' in locals():
            fechar_conexao(conexao)

    return render_template('agenda/listar_agenda.html', agendamentos=agenda_lista)

# Rota para alterar agendas
@agenda_bp.route('/agenda/buscar', methods=['GET', 'POST'])
def buscar_agenda():
    if request.method == 'POST':
        agenda_id = request.form.get('agenda_id')

        if not agenda_id:
            flash("Por favor, insira o ID do agendamento.", "error")
            return render_template('agenda/buscar_agenda.html')

        try:
            conexao = conectar()
            cursor = conexao.cursor()
            cursor.execute("SELECT id_age, data_agendamento, obs_agendamento FROM agendar WHERE id_age = :id", {'id': agenda_id})
            agenda = cursor.fetchone()
            if agenda:
                agenda_data = {
                    'id': agenda[0],
                    'data_agendamento': agenda[1].strftime('%Y-%m-%d'),
                    'obs_agendamento': agenda[2]
                }
                return render_template('agenda/alterar_agenda.html', agenda=agenda_data)
            else:
                flash("Agendamento não encontrado.", "error")
        except Exception as e:
            flash(f"Erro ao buscar agendamento: {e}", "error")
        finally:
            if 'conexao' in locals():
                fechar_conexao(conexao)

    return render_template('agenda/buscar_agenda.html')

@agenda_bp.route('/agenda/alterar/<int:id_agendamento>', methods=['POST'])
def alterar_agenda(id_agendamento):
    try:
        data_agendamento = request.form.get('data_agendamento')
        obs_agendamento = request.form.get('obs_agendamento')

        if not data_agendamento:
            flash("Data do agendamento é obrigatória.", "error")
            return redirect(url_for('agenda.buscar_agenda'))

        conexao = conectar()
        cursor = conexao.cursor()
        cursor.execute("""
            UPDATE agendar
            SET data_agendamento = TO_DATE(:data_agendamento, 'YYYY-MM-DD'),
                obs_agendamento = :obs_agendamento
            WHERE id_age = :id_agendamento
        """, {
            'data_agendamento': data_agendamento,
            'obs_agendamento': obs_agendamento,
            'id_agendamento': id_agendamento
        })
        conexao.commit()
        flash("Agendamento alterado com sucesso!", "success")
    except Exception as e:
        flash(f"Erro ao alterar agendamento: {e}", "error")
    finally:
        if 'conexao' in locals():
            fechar_conexao(conexao)

    return redirect(url_for('agenda.buscar_agenda'))




@agenda_bp.route('/agenda/confirmar_deletar/<int:id_agendamento>', methods=['POST'])
def confirmar_deletar_agenda(id_agendamento):
    try:
        conexao = conectar()
        cursor = conexao.cursor()
        cursor.execute("DELETE FROM agendar WHERE id_age = :id_agendamento", {'id_agendamento': id_agendamento})
        conexao.commit()
        flash("Agendamento deletado com sucesso!", "success")
    except Exception as e:
        flash(f"Erro ao deletar agendamento: {e}", "error")
    finally:
        if 'conexao' in locals():
            fechar_conexao(conexao)

    return redirect(url_for('agenda.menu_agenda'))


# Rota para deletar agendamentos
@agenda_bp.route('/agenda/deletar', methods=['GET', 'POST'])
def deletar_agenda():
    if request.method == 'POST':
        agenda_id = request.form.get('agenda_id')

        if not agenda_id:
            flash("Por favor, insira o ID do agendamento.", "error")
            return render_template('agenda/deletar_agenda.html')

        try:
            conexao = conectar()
            cursor = conexao.cursor()
            cursor.execute("SELECT id_age, data_agendamento, obs_agendamento FROM agendar WHERE id_age = :id", {'id': agenda_id})
            agenda = cursor.fetchone()
            if agenda:
                agenda_data = {
                    'id': agenda[0],
                    'data_agendamento': agenda[1].strftime('%Y-%m-%d'),
                    'obs_agendamento': agenda[2]
                }
                return render_template('agenda/deletar_agenda.html', agenda=agenda_data)
            else:
                flash("Agendamento não encontrado com o ID fornecido.", "error")
                return render_template('agenda/deletar_agenda.html', agenda_not_found=True)
        except Exception as e:
            flash(f"Erro ao buscar agendamento: {e}", "error")
        finally:
            if 'conexao' in locals():
                fechar_conexao(conexao)

    return render_template('agenda/deletar_agenda.html')
