# =============================================
#  ConectaMonga — app.py
#  Backend Flask (Python)
#  Instalar: pip install flask flask-cors mysql-connector-python
# =============================================

from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
import hashlib
import os
import re
from datetime import datetime

app = Flask(__name__)
CORS(app)

# ── CONFIGURAÇÃO DO BANCO ──
DB_CONFIG = {
    'host':     os.getenv('DB_HOST', 'localhost'),
    'user':     os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'conectamonga'),
    'charset':  'utf8mb4'
}


def get_connection():
    """Retorna uma conexão com o banco de dados MySQL."""
    return mysql.connector.connect(**DB_CONFIG)


def hash_senha(senha: str) -> str:
    """Gera hash SHA-256 da senha."""
    return hashlib.sha256(senha.encode()).hexdigest()


def validar_cnpj(cnpj: str) -> bool:
    """Valida CNPJ removendo caracteres não numéricos."""
    digits = re.sub(r'\D', '', cnpj)
    return len(digits) == 14


# =============================================
#  ROTAS — CIDADES
# =============================================

@app.route('/api/cidades', methods=['GET'])
def listar_cidades():
    """Lista todas as cidades cadastradas."""
    conn = get_connection()
    cur  = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM cidade ORDER BY nome")
    cidades = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(cidades)


@app.route('/api/cidades', methods=['POST'])
def criar_cidade():
    """Cria uma nova cidade."""
    data   = request.json
    conn   = get_connection()
    cur    = conn.cursor()
    cur.execute(
        "INSERT INTO cidade (nome, estado) VALUES (%s, %s)",
        (data['nome'], data.get('estado', 'SP'))
    )
    conn.commit()
    new_id = cur.lastrowid
    cur.close()
    conn.close()
    return jsonify({'id': new_id, 'mensagem': 'Cidade criada com sucesso'}), 201


# =============================================
#  ROTAS — SEGMENTOS
# =============================================

@app.route('/api/segmentos', methods=['GET'])
def listar_segmentos():
    conn = get_connection()
    cur  = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM segmento ORDER BY nome")
    segmentos = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(segmentos)


@app.route('/api/segmentos', methods=['POST'])
def criar_segmento():
    data = request.json
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute(
        "INSERT INTO segmento (nome, descricao) VALUES (%s, %s)",
        (data['nome'], data.get('descricao', ''))
    )
    conn.commit()
    new_id = cur.lastrowid
    cur.close()
    conn.close()
    return jsonify({'id': new_id, 'mensagem': 'Segmento criado com sucesso'}), 201


# =============================================
#  ROTAS — CATEGORIAS
# =============================================

@app.route('/api/categorias', methods=['GET'])
def listar_categorias():
    conn = get_connection()
    cur  = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM categoria ORDER BY nome")
    cats = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(cats)


@app.route('/api/categorias', methods=['POST'])
def criar_categoria():
    data = request.json
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute(
        "INSERT INTO categoria (nome, slug, cor_hex) VALUES (%s, %s, %s)",
        (data['nome'], data['slug'], data.get('cor_hex', '#3a7fa0'))
    )
    conn.commit()
    new_id = cur.lastrowid
    cur.close()
    conn.close()
    return jsonify({'id': new_id, 'mensagem': 'Categoria criada com sucesso'}), 201


# =============================================
#  ROTAS — EMPRESAS
# =============================================

@app.route('/api/empresas', methods=['GET'])
def listar_empresas():
    """Lista todas as empresas."""
    conn = get_connection()
    cur  = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT e.id, e.nome, e.cnpj, e.email, e.telefone, e.criado_em,
               c.nome AS cidade, s.nome AS segmento
        FROM empresa e
        LEFT JOIN cidade   c ON c.id = e.cidade_id
        LEFT JOIN segmento s ON s.id = e.segmento_id
        ORDER BY e.nome
    """)
    empresas = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(empresas)


@app.route('/api/empresas/<int:empresa_id>', methods=['GET'])
def obter_empresa(empresa_id):
    conn = get_connection()
    cur  = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT e.*, c.nome AS cidade, s.nome AS segmento
        FROM empresa e
        LEFT JOIN cidade   c ON c.id = e.cidade_id
        LEFT JOIN segmento s ON s.id = e.segmento_id
        WHERE e.id = %s
    """, (empresa_id,))
    empresa = cur.fetchone()
    cur.close()
    conn.close()
    if not empresa:
        return jsonify({'erro': 'Empresa não encontrada'}), 404
    return jsonify(empresa)


@app.route('/api/empresas/cadastro', methods=['POST'])
def cadastrar_empresa():
    """Cadastra uma nova empresa com CNPJ válido."""
    data = request.json

    campos_obrigatorios = ['nome', 'cnpj', 'email', 'senha', 'cidade_id', 'segmento_id']
    for campo in campos_obrigatorios:
        if not data.get(campo):
            return jsonify({'erro': f'Campo {campo} é obrigatório'}), 400

    if not validar_cnpj(data['cnpj']):
        return jsonify({'erro': 'CNPJ inválido'}), 400

    conn = get_connection()
    cur  = conn.cursor(dictionary=True)

    # Verifica duplicidade de email ou CNPJ
    cur.execute("SELECT id FROM empresa WHERE email = %s OR cnpj = %s",
                (data['email'], re.sub(r'\D', '', data['cnpj'])))
    if cur.fetchone():
        cur.close()
        conn.close()
        return jsonify({'erro': 'Email ou CNPJ já cadastrado'}), 409

    senha_hash = hash_senha(data['senha'])
    cur.execute("""
        INSERT INTO empresa (cidade_id, segmento_id, nome, cnpj, email, senha_hash, telefone)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (
        data['cidade_id'],
        data['segmento_id'],
        data['nome'],
        re.sub(r'\D', '', data['cnpj']),
        data['email'],
        senha_hash,
        data.get('telefone', '')
    ))
    conn.commit()
    new_id = cur.lastrowid
    cur.close()
    conn.close()
    return jsonify({'id': new_id, 'mensagem': 'Empresa cadastrada com sucesso'}), 201


@app.route('/api/empresas/login', methods=['POST'])
def login_empresa():
    """Autentica uma empresa."""
    data = request.json
    if not data.get('email') or not data.get('senha'):
        return jsonify({'erro': 'Email e senha são obrigatórios'}), 400

    conn = get_connection()
    cur  = conn.cursor(dictionary=True)
    cur.execute(
        "SELECT id, nome, email, segmento_id FROM empresa WHERE email = %s AND senha_hash = %s",
        (data['email'], hash_senha(data['senha']))
    )
    empresa = cur.fetchone()
    cur.close()
    conn.close()

    if not empresa:
        return jsonify({'erro': 'Credenciais inválidas'}), 401
    return jsonify({'mensagem': 'Login realizado', 'empresa': empresa})


# =============================================
#  ROTAS — EVENTOS
# =============================================

@app.route('/api/eventos', methods=['GET'])
def listar_eventos():
    """Lista todos os eventos (com filtros opcionais)."""
    categoria_id = request.args.get('categoria_id')
    empresa_id   = request.args.get('empresa_id')

    conn = get_connection()
    cur  = conn.cursor(dictionary=True)

    query = """
        SELECT ev.id, ev.titulo, ev.descricao, ev.data_evento, ev.horario,
               ev.local, ev.contato_whatsapp, ev.publicado_em,
               cat.nome AS categoria, cat.cor_hex,
               emp.nome AS empresa, emp.id AS empresa_id
        FROM evento ev
        LEFT JOIN categoria cat ON cat.id = ev.categoria_id
        LEFT JOIN empresa   emp ON emp.id = ev.empresa_id
        WHERE ev.expira_em >= NOW() OR ev.expira_em IS NULL
    """
    params = []

    if categoria_id:
        query += " AND ev.categoria_id = %s"
        params.append(int(categoria_id))

    if empresa_id:
        query += " AND ev.empresa_id = %s"
        params.append(int(empresa_id))

    query += " ORDER BY ev.data_evento ASC"

    cur.execute(query, params)
    eventos = cur.fetchall()

    # Converter tipos para JSON serializável
    for ev in eventos:
        if ev.get('data_evento'):
            ev['data_evento'] = ev['data_evento'].isoformat()
        if ev.get('horario'):
            ev['horario'] = str(ev['horario'])
        if ev.get('publicado_em'):
            ev['publicado_em'] = ev['publicado_em'].isoformat()

    cur.close()
    conn.close()
    return jsonify(eventos)


@app.route('/api/eventos/<int:evento_id>', methods=['GET'])
def obter_evento(evento_id):
    conn = get_connection()
    cur  = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT ev.*, cat.nome AS categoria, cat.cor_hex,
               emp.nome AS empresa, emp.telefone AS empresa_telefone
        FROM evento ev
        LEFT JOIN categoria cat ON cat.id = ev.categoria_id
        LEFT JOIN empresa   emp ON emp.id = ev.empresa_id
        WHERE ev.id = %s
    """, (evento_id,))
    evento = cur.fetchone()
    cur.close()
    conn.close()

    if not evento:
        return jsonify({'erro': 'Evento não encontrado'}), 404

    if evento.get('data_evento'):
        evento['data_evento'] = evento['data_evento'].isoformat()
    if evento.get('horario'):
        evento['horario'] = str(evento['horario'])
    return jsonify(evento)


@app.route('/api/eventos', methods=['POST'])
def criar_evento():
    """Cria um novo evento (empresa autenticada)."""
    data = request.json

    campos_obrigatorios = ['empresa_id', 'categoria_id', 'titulo', 'data_evento', 'local']
    for campo in campos_obrigatorios:
        if not data.get(campo):
            return jsonify({'erro': f'Campo {campo} é obrigatório'}), 400

    # Foto é obrigatória
    if not data.get('foto_url'):
        return jsonify({'erro': 'A foto de divulgação é obrigatória'}), 400

    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("""
        INSERT INTO evento
          (empresa_id, categoria_id, titulo, descricao, data_evento,
           horario, local, contato_whatsapp, publicado_em, expira_em)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), %s)
    """, (
        data['empresa_id'],
        data['categoria_id'],
        data['titulo'],
        data.get('descricao', ''),
        data['data_evento'],
        data.get('horario'),
        data['local'],
        data.get('contato_whatsapp', ''),
        data.get('expira_em')
    ))
    conn.commit()
    new_id = cur.lastrowid
    cur.close()
    conn.close()
    return jsonify({'id': new_id, 'mensagem': 'Evento publicado com sucesso'}), 201


@app.route('/api/eventos/<int:evento_id>', methods=['DELETE'])
def deletar_evento(evento_id):
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("DELETE FROM evento WHERE id = %s", (evento_id,))
    conn.commit()
    afetados = cur.rowcount
    cur.close()
    conn.close()
    if afetados == 0:
        return jsonify({'erro': 'Evento não encontrado'}), 404
    return jsonify({'mensagem': 'Evento removido com sucesso'})


# =============================================
#  TRATAMENTO DE ERROS
# =============================================

@app.errorhandler(404)
def not_found(e):
    return jsonify({'erro': 'Rota não encontrada'}), 404


@app.errorhandler(500)
def internal_error(e):
    return jsonify({'erro': 'Erro interno do servidor'}), 500


# =============================================
#  PONTO DE ENTRADA
# =============================================

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
