# orcamento.py
from datetime import datetime
import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from conexao.conectaBD import conectar, fechar_conexao

# Definição do Blueprint
orcamento_bp = Blueprint('orcamento', __name__)
logger = logging.getLogger(__name__)

# Rota para o menu principal do orçamento
@orcamento_bp.route('/', methods=['GET'])
def menu_orcamento():
    return render_template('orcamento/menu_orcamento.html')

# Rota para cadastrar orçamento
@orcamento_bp.route('/cadastrar', methods=['GET', 'POST'])
def cadastrar_orcamento():
    if request.method == 'POST':
        data_orcamento = request.form.get('data_orcamento')
        valor_maodeobra = request.form.get('valor_maodeobra')
        valor_hora = request.form.get('valor_hora')
        quantidade_horas = request.form.get('quantidade_horas')

        # Calcular valor_total
        try:
            # Remove separadores de milhar e substitui vírgula decimal por ponto
            valor_maodeobra = float(valor_maodeobra.replace('.', '').replace(',', '.'))
            valor_hora = float(valor_hora.replace('.', '').replace(',', '.'))
            quantidade_horas = float(quantidade_horas)
            valor_total = valor_maodeobra + (valor_hora * quantidade_horas)
        except (ValueError, AttributeError) as e:
            flash("Por favor, insira valores numéricos válidos para os campos de valor.", "error")
            return render_template('orcamento/cadastrar_orcamento.html')

        if not all([data_orcamento, valor_maodeobra, valor_hora, quantidade_horas]):
            flash("Por favor, preencha todos os campos.", "error")
            return render_template('orcamento/cadastrar_orcamento.html')

        conexao = conectar()
        cursor = conexao.cursor()
        try:
            cursor.execute("""
                INSERT INTO orcamentos (data_orcamento, valor_maodeobra, valor_hora, quantidade_horas, valor_total)
                VALUES (TO_DATE(:data_orcamento, 'YYYY-MM-DD'), :valor_maodeobra, :valor_hora, :quantidade_horas, :valor_total)
            """, {
                'data_orcamento': data_orcamento,
                'valor_maodeobra': valor_maodeobra,
                'valor_hora': valor_hora,
                'quantidade_horas': quantidade_horas,
                'valor_total': valor_total
            })
            conexao.commit()
            flash("Orçamento cadastrado com sucesso!", "success")
        except Exception as e:
            conexao.rollback()
            flash(f"Erro ao cadastrar orçamento: {e}", "error")
            logger.error(f"Erro ao cadastrar orçamento: {e}")
        finally:
            fechar_conexao(conexao)
        return redirect(url_for('orcamento.listar_orcamentos'))

    return render_template('orcamento/cadastrar_orcamento.html')

# Rota para listar todos os orçamentos
@orcamento_bp.route('/listar', methods=['GET'])
def listar_orcamentos():
    try:
        conexao = conectar()
        cursor = conexao.cursor()
        cursor.execute("""
            SELECT id_orc, data_orcamento, valor_maodeobra, valor_hora, quantidade_horas, valor_total
            FROM orcamentos
            ORDER BY data_orcamento DESC
        """)
        orcamentos = cursor.fetchall()
        orcamentos_lista = [
            {
                'id': orcamento[0],
                'data_orcamento': orcamento[1].strftime('%d/%m/%Y') if orcamento[1] else 'N/A',
                'valor_maodeobra': f"{orcamento[2]:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
                'valor_hora': f"{orcamento[3]:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
                'quantidade_horas': orcamento[4],
                'valor_total': f"{orcamento[5]:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
            }
            for orcamento in orcamentos
        ]
    except Exception as e:
        flash(f"Erro ao listar orçamentos: {e}", "error")
        logger.error(f"Erro ao listar orçamentos: {e}")
        orcamentos_lista = []
    finally:
        if 'conexao' in locals():
            fechar_conexao(conexao)

    return render_template('orcamento/listar_orcamento.html', orcamentos=orcamentos_lista)

# Rota para buscar orçamento para alterar
# orcamento.py
from datetime import datetime
import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash
from conexao.conectaBD import conectar, fechar_conexao

# Definição do Blueprint
orcamento_bp = Blueprint('orcamento', __name__)
logger = logging.getLogger(__name__)

# Rota para o menu principal do orçamento
@orcamento_bp.route('/', methods=['GET'])
def menu_orcamento():
    return render_template('orcamento/menu_orcamento.html')

# Rota para cadastrar orçamento
@orcamento_bp.route('/cadastrar', methods=['GET', 'POST'])
def cadastrar_orcamento():
    if request.method == 'POST':
        data_orcamento = request.form.get('data_orcamento')
        valor_maodeobra = request.form.get('valor_maodeobra')
        valor_hora = request.form.get('valor_hora')
        quantidade_horas = request.form.get('quantidade_horas')

        # Calcular valor_total
        try:
            # Remove separadores de milhar e substitui vírgula decimal por ponto
            valor_maodeobra_num = float(valor_maodeobra.replace('.', '').replace(',', '.'))
            valor_hora_num = float(valor_hora.replace('.', '').replace(',', '.'))
            quantidade_horas_num = float(quantidade_horas)
            valor_total = valor_maodeobra_num + (valor_hora_num * quantidade_horas_num)
        except (ValueError, AttributeError) as e:
            flash("Por favor, insira valores numéricos válidos para os campos de valor.", "error")
            return render_template('orcamento/cadastrar_orcamento.html')

        if not all([data_orcamento, valor_maodeobra, valor_hora, quantidade_horas]):
            flash("Por favor, preencha todos os campos.", "error")
            return render_template('orcamento/cadastrar_orcamento.html')

        conexao = conectar()
        cursor = conexao.cursor()
        try:
            cursor.execute("""
                INSERT INTO orcamentos (data_orcamento, valor_maodeobra, valor_hora, quantidade_horas, valor_total)
                VALUES (TO_DATE(:data_orcamento, 'YYYY-MM-DD'), :valor_maodeobra, :valor_hora, :quantidade_horas, :valor_total)
            """, {
                'data_orcamento': data_orcamento,
                'valor_maodeobra': valor_maodeobra_num,
                'valor_hora': valor_hora_num,
                'quantidade_horas': quantidade_horas_num,
                'valor_total': valor_total
            })
            conexao.commit()
            flash("Orçamento cadastrado com sucesso!", "success")
        except Exception as e:
            conexao.rollback()
            flash(f"Erro ao cadastrar orçamento: {e}", "error")
            logger.error(f"Erro ao cadastrar orçamento: {e}")
        finally:
            fechar_conexao(conexao)
        return redirect(url_for('orcamento.listar_orcamentos'))

    return render_template('orcamento/cadastrar_orcamento.html')

# Rota para listar todos os orçamentos
@orcamento_bp.route('/listar', methods=['GET'])
def listar_orcamentos():
    try:
        conexao = conectar()
        cursor = conexao.cursor()
        cursor.execute("""
            SELECT id_orc, data_orcamento, valor_maodeobra, valor_hora, quantidade_horas, valor_total
            FROM orcamentos
            ORDER BY data_orcamento DESC
        """)
        orcamentos = cursor.fetchall()
        orcamentos_lista = [
            {
                'id': orcamento[0],
                'data_orcamento': orcamento[1].strftime('%d/%m/%Y') if orcamento[1] else 'N/A',
                'valor_maodeobra': f"{orcamento[2]:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
                'valor_hora': f"{orcamento[3]:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
                'quantidade_horas': orcamento[4],
                'valor_total': f"{orcamento[5]:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
            }
            for orcamento in orcamentos
        ]
    except Exception as e:
        flash(f"Erro ao listar orçamentos: {e}", "error")
        logger.error(f"Erro ao listar orçamentos: {e}")
        orcamentos_lista = []
    finally:
        if 'conexao' in locals():
            fechar_conexao(conexao)

    return render_template('orcamento/listar_orcamento.html', orcamentos=orcamentos_lista)

# Rota para buscar orçamento para alterar
@orcamento_bp.route('/buscar_alterar', methods=['GET', 'POST'])
def buscar_orcamento_para_alterar():
    if request.method == 'POST':
        orcamento_id = request.form.get('orcamento_id')

        if not orcamento_id:
            flash("Por favor, insira o ID do orçamento.", "error")
            return render_template('orcamento/buscar_orcamento_para_alterar.html')

        try:
            conexao = conectar()
            cursor = conexao.cursor()
            cursor.execute("""
                SELECT id_orc, data_orcamento, valor_maodeobra, valor_hora, quantidade_horas, valor_total
                FROM orcamentos WHERE id_orc = :orcamento_id
            """, {'orcamento_id': orcamento_id})
            orcamento = cursor.fetchone()
            fechar_conexao(conexao)

            if orcamento:
                orcamento_data = {
                    'id': orcamento[0],
                    'data_orcamento': orcamento[1].strftime('%Y-%m-%d') if orcamento[1] else '',
                    'valor_maodeobra': orcamento[2],
                    'valor_hora': orcamento[3],
                    'quantidade_horas': orcamento[4],
                    'valor_total': orcamento[5]
                }
                return render_template('orcamento/alterar_orcamento.html', orcamento=orcamento_data)
            else:
                flash("Orçamento não encontrado com o ID fornecido.", "error")
        except Exception as e:
            flash(f"Erro ao buscar orçamento: {e}", "error")
            logger.error(f"Erro ao buscar orçamento: {e}")
    return render_template('orcamento/buscar_orcamento_para_alterar.html')

# Rota para alterar orçamento
@orcamento_bp.route('/alterar/<int:id_orc>', methods=['POST'])
def alterar_orcamento(id_orc):
    data_orcamento = request.form.get('data_orcamento')
    valor_maodeobra = request.form.get('valor_maodeobra')
    valor_hora = request.form.get('valor_hora')
    quantidade_horas = request.form.get('quantidade_horas')

    # Calcular valor_total
    try:
        # Remove separadores de milhar e substitui vírgula decimal por ponto
        valor_maodeobra_num = float(valor_maodeobra.replace('.', '').replace(',', '.'))
        valor_hora_num = float(valor_hora.replace('.', '').replace(',', '.'))
        quantidade_horas_num = float(quantidade_horas)
        valor_total = valor_maodeobra_num + (valor_hora_num * quantidade_horas_num)
    except (ValueError, AttributeError) as e:
        flash("Por favor, insira valores numéricos válidos para os campos de valor.", "error")
        # Recarrega a página com os dados inseridos
        orcamento_data = {
            'id': id_orc,
            'data_orcamento': data_orcamento,
            'valor_maodeobra': f"{valor_maodeobra_num:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
            'valor_hora': f"{valor_hora_num:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
            'quantidade_horas': quantidade_horas_num,
            'valor_total': 'N/A'
        }
        return render_template('orcamento/alterar_orcamento.html', orcamento=orcamento_data)

    conexao = conectar()
    cursor = conexao.cursor()
    try:
        cursor.execute("""
            UPDATE orcamentos
            SET data_orcamento = TO_DATE(:data_orcamento, 'YYYY-MM-DD'),
                valor_maodeobra = :valor_maodeobra,
                valor_hora = :valor_hora,
                quantidade_horas = :quantidade_horas,
                valor_total = :valor_total
            WHERE id_orc = :id_orc
        """, {
            'data_orcamento': data_orcamento,
            'valor_maodeobra': valor_maodeobra_num,
            'valor_hora': valor_hora_num,
            'quantidade_horas': quantidade_horas_num,
            'valor_total': valor_total,
            'id_orc': id_orc
        })
        conexao.commit()
        flash("Orçamento alterado com sucesso!", "success")
    except Exception as e:
        conexao.rollback()
        flash(f"Erro ao alterar orçamento: {e}", "error")
        logger.error(f"Erro ao alterar orçamento: {e}")
    finally:
        fechar_conexao(conexao)

    return redirect(url_for('orcamento.listar_orcamentos'))


@orcamento_bp.route('/buscar_orcamento_para_deletar', methods=['GET', 'POST'])
def buscar_orcamento_para_deletar():
    if request.method == 'POST':
        orcamento_id = request.form.get('orcamento_id')

        # Valida se o ID foi fornecido
        if not orcamento_id:
            flash("Por favor, insira o ID do orçamento.", "error")
            return render_template('orcamento/buscar_orcamento_para_deletar.html')

        try:
            conexao = conectar()
            cursor = conexao.cursor()
            cursor.execute("""
                SELECT id_orc, data_orcamento, valor_maodeobra, valor_hora, quantidade_horas, valor_total
                FROM orcamentos WHERE id_orc = :orcamento_id
            """, {'orcamento_id': orcamento_id})
            orcamento = cursor.fetchone()
            fechar_conexao(conexao)

            # Se o orçamento for encontrado, renderiza a página de confirmação de deleção
            if orcamento:
                orcamento_data = {
                    'id': orcamento[0],
                    'data_orcamento': orcamento[1].strftime('%d/%m/%Y') if orcamento[1] else '',
                    'valor_maodeobra': f"{orcamento[2]:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
                    'valor_hora': f"{orcamento[3]:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
                    'quantidade_horas': orcamento[4],
                    'valor_total': f"{orcamento[5]:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
                }
                return render_template('orcamento/deletar_orcamento.html', orcamento=orcamento_data)

            # Se não encontrar o orçamento, informa ao usuário
            else:
                flash("Orçamento não encontrado com o ID fornecido.", "error")
                return render_template('orcamento/buscar_orcamento_para_deletar.html')

        except Exception as e:
            # Em caso de erro, exibe uma mensagem
            flash(f"Erro ao buscar orçamento: {e}", "error")
            return render_template('orcamento/buscar_orcamento_para_deletar.html')

    # Renderiza o formulário de busca caso o método seja GET
    return render_template('orcamento/buscar_orcamento_para_deletar.html')


# Função para confirmar a exclusão do orçamento
@orcamento_bp.route('/confirmar_deletar_orcamento/<int:id_orc>', methods=['POST'])
def confirmar_deletar_orcamento(id_orc):
    try:
        conexao = conectar()
        cursor = conexao.cursor()
        cursor.execute("DELETE FROM orcamentos WHERE id_orc = :id_orc", {'id_orc': id_orc})
        conexao.commit()
        flash("Orçamento deletado com sucesso!", "success")
    except Exception as e:
        conexao.rollback()
        flash(f"Erro ao deletar orçamento: {e}", "error")
    finally:
        fechar_conexao(conexao)
    return redirect(url_for('orcamento.menu_orcamento'))
