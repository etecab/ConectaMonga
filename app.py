# =============================================
#  ConectaMonga — app.py
#  Backend Flask + MySQL
#  Porta: 5000 (local) ou automática (Railway)
# =============================================

from flask import Flask, request, jsonify
from flask_cors import CORS
import pymysql
import hashlib
import os
import re

app = Flask(__name__)
CORS(app)  # Permite chamadas do frontend

# ── CONEXÃO COM O BANCO ──
def get_db():
    return pymysql.connect(
        host     = os.environ.get("DB_HOST",     "localhost"),
        user     = os.environ.get("DB_USER",     "root"),
        password = os.environ.get("DB_PASSWORD", ""),  # ← sua senha aqui se rodar local
        database = os.environ.get("DB_NAME",     "conectamonga"),
        charset  = "utf8mb4",
        cursorclass = pymysql.cursors.DictCursor
    )

def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

def validar_cnpj(cnpj):
    digits = re.sub(r"\D", "", cnpj)
    return len(digits) == 14

# =============================================
#  EVENTOS
# =============================================

@app.route("/api/eventos", methods=["GET"])
def listar_eventos():
    categoria_id = request.args.get("categoriaId")
    empresa_id   = request.args.get("empresaId")
    db = get_db()
    try:
        with db.cursor() as cur:
            sql = """
                SELECT ev.id, ev.titulo AS title, ev.descricao AS desc,
                       ev.data_evento AS date, ev.horario AS time,
                       ev.local, ev.contato_whatsapp AS wpp,
                       ev.publicado_em, ev.foto_url AS img,
                       cat.nome AS category, cat.cor_hex AS categoryColor,
                       emp.nome AS company, emp.id AS companyId,
                       seg.nome AS segment
                FROM evento ev
                INNER JOIN categoria cat ON cat.id = ev.categoria_id
                INNER JOIN empresa   emp ON emp.id = ev.empresa_id
                INNER JOIN segmento  seg ON seg.id = emp.segmento_id
                WHERE (ev.expira_em IS NULL OR ev.expira_em >= NOW())
            """
            params = []
            if categoria_id:
                sql += " AND ev.categoria_id = %s"
                params.append(categoria_id)
            if empresa_id:
                sql += " AND ev.empresa_id = %s"
                params.append(empresa_id)
            sql += " ORDER BY ev.data_evento ASC"
            cur.execute(sql, params)
            eventos = cur.fetchall()

            # Formata data e hora
            for e in eventos:
                if e["date"]:
                    e["date"] = str(e["date"])
                if e["time"]:
                    e["time"] = str(e["time"])
                # Iniciais da empresa
                e["companyInit"] = e["company"][0].upper() if e["company"] else "E"

        return jsonify(eventos), 200
    finally:
        db.close()

@app.route("/api/eventos/<int:id>", methods=["GET"])
def obter_evento(id):
    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute("""
                SELECT ev.*, cat.nome AS category, cat.cor_hex AS categoryColor,
                       emp.nome AS company, seg.nome AS segment
                FROM evento ev
                INNER JOIN categoria cat ON cat.id = ev.categoria_id
                INNER JOIN empresa   emp ON emp.id = ev.empresa_id
                INNER JOIN segmento  seg ON seg.id = emp.segmento_id
                WHERE ev.id = %s
            """, (id,))
            evento = cur.fetchone()
            if not evento:
                return jsonify({"erro": "Evento não encontrado"}), 404
            if evento["data_evento"]:
                evento["data_evento"] = str(evento["data_evento"])
            if evento["horario"]:
                evento["horario"] = str(evento["horario"])
        return jsonify(evento), 200
    finally:
        db.close()

@app.route("/api/eventos", methods=["POST"])
def criar_evento():
    data = request.json
    campos = ["empresaId", "categoriaId", "titulo", "dataEvento", "local"]
    for c in campos:
        if not data.get(c):
            return jsonify({"erro": f"Campo '{c}' é obrigatório"}), 400

    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute("""
                INSERT INTO evento
                (empresa_id, categoria_id, titulo, descricao, data_evento,
                 horario, local, contato_whatsapp, foto_url, expira_em)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                data["empresaId"],
                data["categoriaId"],
                data["titulo"],
                data.get("descricao"),
                data["dataEvento"],
                data.get("horario"),
                data["local"],
                data.get("contatoWhatsapp"),
                data.get("fotoUrl"),
                data.get("expiraEm")
            ))
            db.commit()
            novo_id = cur.lastrowid
        return jsonify({"id": novo_id, "mensagem": "Evento publicado com sucesso!"}), 201
    finally:
        db.close()

@app.route("/api/eventos/<int:id>", methods=["DELETE"])
def deletar_evento(id):
    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute("DELETE FROM evento WHERE id = %s", (id,))
            db.commit()
            if cur.rowcount == 0:
                return jsonify({"erro": "Evento não encontrado"}), 404
        return jsonify({"mensagem": "Evento removido com sucesso"}), 200
    finally:
        db.close()

# =============================================
#  EMPRESAS
# =============================================

@app.route("/api/empresas", methods=["GET"])
def listar_empresas():
    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute("""
                SELECT emp.id, emp.nome AS name, emp.email, emp.telefone,
                       emp.criado_em, cid.nome AS city, seg.nome AS segment,
                       (SELECT COUNT(*) FROM evento ev WHERE ev.empresa_id = emp.id) AS events
                FROM empresa emp
                INNER JOIN cidade   cid ON cid.id = emp.cidade_id
                INNER JOIN segmento seg ON seg.id = emp.segmento_id
                ORDER BY emp.nome
            """)
            empresas = cur.fetchall()
            for e in empresas:
                e["init"] = e["name"][0].upper() if e["name"] else "E"
                if e["criado_em"]:
                    e["criado_em"] = str(e["criado_em"])
        return jsonify(empresas), 200
    finally:
        db.close()

@app.route("/api/empresas/<int:id>", methods=["GET"])
def obter_empresa(id):
    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute("""
                SELECT emp.id, emp.nome, emp.email, emp.telefone, emp.criado_em,
                       cid.nome AS cidade, seg.nome AS segmento
                FROM empresa emp
                INNER JOIN cidade   cid ON cid.id = emp.cidade_id
                INNER JOIN segmento seg ON seg.id = emp.segmento_id
                WHERE emp.id = %s
            """, (id,))
            empresa = cur.fetchone()
            if not empresa:
                return jsonify({"erro": "Empresa não encontrada"}), 404
        return jsonify(empresa), 200
    finally:
        db.close()

@app.route("/api/empresas/cadastro", methods=["POST"])
def cadastrar_empresa():
    data = request.json
    campos = ["nome", "cnpj", "email", "senha", "cidadeId", "segmentoId"]
    for c in campos:
        if not data.get(c):
            return jsonify({"erro": f"Campo '{c}' é obrigatório"}), 400

    if not validar_cnpj(data["cnpj"]):
        return jsonify({"erro": "CNPJ inválido"}), 400

    cnpj_digits = re.sub(r"\D", "", data["cnpj"])
    db = get_db()
    try:
        with db.cursor() as cur:
            # Verifica duplicidade
            cur.execute(
                "SELECT id FROM empresa WHERE email = %s OR cnpj = %s",
                (data["email"], cnpj_digits)
            )
            if cur.fetchone():
                return jsonify({"erro": "Email ou CNPJ já cadastrado"}), 409

            cur.execute("""
                INSERT INTO empresa (cidade_id, segmento_id, nome, cnpj, email, senha_hash, telefone)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                data["cidadeId"],
                data["segmentoId"],
                data["nome"],
                cnpj_digits,
                data["email"],
                hash_senha(data["senha"]),
                data.get("telefone")
            ))
            db.commit()
            novo_id = cur.lastrowid
        return jsonify({"id": novo_id, "mensagem": "Empresa cadastrada com sucesso!"}), 201
    finally:
        db.close()

@app.route("/api/empresas/login", methods=["POST"])
def login_empresa():
    data = request.json
    if not data.get("email") or not data.get("senha"):
        return jsonify({"erro": "Email e senha são obrigatórios"}), 400

    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute("""
                SELECT emp.id, emp.nome AS name, emp.email,
                       emp.telefone, seg.nome AS segment
                FROM empresa emp
                INNER JOIN segmento seg ON seg.id = emp.segmento_id
                WHERE emp.email = %s AND emp.senha_hash = %s
            """, (data["email"], hash_senha(data["senha"])))
            empresa = cur.fetchone()
            if not empresa:
                return jsonify({"erro": "Email ou senha incorretos"}), 401
            empresa["type"] = "empresa"
            empresa["init"] = empresa["name"][0].upper()
        return jsonify({"mensagem": "Login realizado!", "usuario": empresa}), 200
    finally:
        db.close()

# =============================================
#  USUÁRIOS
# =============================================

@app.route("/api/usuarios/cadastro", methods=["POST"])
def cadastrar_usuario():
    data = request.json
    if not data.get("nome") or not data.get("email") or not data.get("senha"):
        return jsonify({"erro": "Nome, email e senha são obrigatórios"}), 400

    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute("SELECT id FROM usuario WHERE email = %s", (data["email"],))
            if cur.fetchone():
                return jsonify({"erro": "Email já cadastrado"}), 409

            cur.execute("""
                INSERT INTO usuario (nome, email, senha_hash)
                VALUES (%s, %s, %s)
            """, (data["nome"], data["email"], hash_senha(data["senha"])))
            db.commit()
            novo_id = cur.lastrowid
        return jsonify({"id": novo_id, "mensagem": "Conta criada com sucesso!"}), 201
    finally:
        db.close()

@app.route("/api/usuarios/login", methods=["POST"])
def login_usuario():
    data = request.json
    if not data.get("email") or not data.get("senha"):
        return jsonify({"erro": "Email e senha são obrigatórios"}), 400

    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute("""
                SELECT id, nome AS name, email
                FROM usuario
                WHERE email = %s AND senha_hash = %s
            """, (data["email"], hash_senha(data["senha"])))
            usuario = cur.fetchone()
            if not usuario:
                return jsonify({"erro": "Email ou senha incorretos"}), 401
            usuario["type"] = "user"
            usuario["init"] = usuario["name"][0].upper()
        return jsonify({"mensagem": "Login realizado!", "usuario": usuario}), 200
    finally:
        db.close()

# =============================================
#  AUXILIARES (Categorias, Cidades, Segmentos)
# =============================================

@app.route("/api/categorias", methods=["GET"])
def listar_categorias():
    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute("SELECT * FROM categoria ORDER BY nome")
            return jsonify(cur.fetchall()), 200
    finally:
        db.close()

@app.route("/api/cidades", methods=["GET"])
def listar_cidades():
    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute("SELECT * FROM cidade ORDER BY nome")
            return jsonify(cur.fetchall()), 200
    finally:
        db.close()

@app.route("/api/segmentos", methods=["GET"])
def listar_segmentos():
    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute("SELECT * FROM segmento ORDER BY nome")
            return jsonify(cur.fetchall()), 200
    finally:
        db.close()

# =============================================
#  ROTA DE TESTE
# =============================================

@app.route("/", methods=["GET"])
def index():
    return jsonify({"status": "ConectaMonga API rodando!"}), 200

# =============================================
#  INICIALIZAÇÃO
# =============================================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
