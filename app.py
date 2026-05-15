# =============================================
#  ConectaMonga — app.py
#  Backend Flask + MySQL + JWT
# =============================================

from flask import Flask, request, jsonify
from flask_cors import CORS
import pymysql
import hashlib
import os
import re
import jwt
import datetime
from functools import wraps

app = Flask(__name__)
CORS(app)

# ── CHAVE JWT ──
JWT_SECRET = os.environ.get("JWT_SECRET", "conectamonga_secret_2026")

# ── CONEXÃO COM O BANCO ──
def get_db():
    return pymysql.connect(
        host        = os.environ.get("DB_HOST",     "localhost"),
        port        = int(os.environ.get("DB_PORT", 3306)),
        user        = os.environ.get("DB_USER",     "root"),
        password    = os.environ.get("DB_PASSWORD", ""),
        database    = os.environ.get("DB_NAME",     "railway"),
        charset     = "utf8mb4",
        cursorclass = pymysql.cursors.DictCursor
    )

def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

def validar_cnpj(cnpj):
    return len(re.sub(r"\D", "", cnpj)) == 14

# =============================================
#  JWT — FUNÇÕES
# =============================================

def gerar_token(usuario_id, tipo):
    """Gera um token JWT válido por 24 horas."""
    payload = {
        "id":   usuario_id,
        "tipo": tipo,
        "exp":  datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

def verificar_token(token):
    """Verifica e decodifica o token. Retorna None se inválido."""
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def token_obrigatorio(f):
    """Decorator — protege rotas que exigem login."""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get("Authorization", "")
        token = auth.replace("Bearer ", "").strip()
        if not token:
            return jsonify({"erro": "Token não fornecido. Faça login primeiro."}), 401
        payload = verificar_token(token)
        if not payload:
            return jsonify({"erro": "Token inválido ou expirado. Faça login novamente."}), 401
        request.usuario_atual = payload
        return f(*args, **kwargs)
    return decorated

# Rota para verificar se o token ainda é válido
@app.route("/api/auth/verificar", methods=["GET"])
@token_obrigatorio
def verificar_sessao():
    return jsonify({
        "valido": True,
        "usuario": request.usuario_atual
    }), 200

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
                SELECT ev.id, ev.titulo AS title, ev.descricao AS `desc`,
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
            for e in eventos:
                if e["date"]: e["date"] = str(e["date"])
                if e["time"]: e["time"] = str(e["time"])
                e["companyInit"] = (e["company"] or "E")[0].upper()
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
            if evento["data_evento"]: evento["data_evento"] = str(evento["data_evento"])
            if evento["horario"]:     evento["horario"]     = str(evento["horario"])
        return jsonify(evento), 200
    finally:
        db.close()

@app.route("/api/eventos", methods=["POST"])
@token_obrigatorio  # ← Só empresas logadas podem criar eventos
def criar_evento():
    if request.usuario_atual.get("tipo") != "empresa":
        return jsonify({"erro": "Apenas empresas podem publicar eventos"}), 403

    data = request.json
    for c in ["categoriaId", "titulo", "dataEvento", "local"]:
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
                request.usuario_atual["id"],
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
@token_obrigatorio
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
                e["init"] = (e["name"] or "E")[0].upper()
                if e["criado_em"]: e["criado_em"] = str(e["criado_em"])
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
    for c in ["nome", "cnpj", "email", "senha", "cidadeId", "segmentoId"]:
        if not data.get(c):
            return jsonify({"erro": f"Campo '{c}' é obrigatório"}), 400

    if not validar_cnpj(data["cnpj"]):
        return jsonify({"erro": "CNPJ inválido"}), 400

    cnpj_digits = re.sub(r"\D", "", data["cnpj"])
    db = get_db()
    try:
        with db.cursor() as cur:
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
                data["cidadeId"], data["segmentoId"], data["nome"],
                cnpj_digits, data["email"], hash_senha(data["senha"]),
                data.get("telefone")
            ))
            db.commit()
            novo_id = cur.lastrowid

        # Gera token JWT automaticamente após cadastro
        token = gerar_token(novo_id, "empresa")
        return jsonify({
            "id": novo_id,
            "token": token,
            "mensagem": "Empresa cadastrada com sucesso!"
        }), 201
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

        # Gera token JWT
        token = gerar_token(empresa["id"], "empresa")
        return jsonify({
            "mensagem": "Login realizado!",
            "token": token,
            "usuario": empresa
        }), 200
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

        # Gera token JWT automaticamente após cadastro
        token = gerar_token(novo_id, "user")
        return jsonify({
            "id": novo_id,
            "token": token,
            "mensagem": "Conta criada com sucesso!"
        }), 201
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

        # Gera token JWT
        token = gerar_token(usuario["id"], "user")
        return jsonify({
            "mensagem": "Login realizado!",
            "token": token,
            "usuario": usuario
        }), 200
    finally:
        db.close()

# =============================================
#  AUXILIARES
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
    return jsonify({"status": "ConectaMonga API rodando!", "versao": "2.0 (JWT)"}), 200

# =============================================
#  INICIALIZAÇÃO
# =============================================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)