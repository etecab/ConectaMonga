-- =============================================
--  ConectaMonga — banco.sql
--  Script de criação do banco de dados MySQL
--  Execute: mysql -u root -p < banco.sql
-- =============================================

CREATE DATABASE IF NOT EXISTS conectamonga
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE conectamonga;

-- ── CIDADE ──
CREATE TABLE IF NOT EXISTS cidade (
    id     INT          NOT NULL AUTO_INCREMENT,
    nome   VARCHAR(100) NOT NULL,
    estado CHAR(2)      NOT NULL DEFAULT 'SP',
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ── SEGMENTO ──
CREATE TABLE IF NOT EXISTS segmento (
    id        INT          NOT NULL AUTO_INCREMENT,
    nome      VARCHAR(100) NOT NULL,
    descricao VARCHAR(255),
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ── CATEGORIA ──
CREATE TABLE IF NOT EXISTS categoria (
    id      INT         NOT NULL AUTO_INCREMENT,
    nome    VARCHAR(50) NOT NULL,
    slug    VARCHAR(50) NOT NULL,
    cor_hex CHAR(7)     NOT NULL DEFAULT '#3a7fa0',
    PRIMARY KEY (id),
    UNIQUE KEY uq_categoria_slug (slug)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ── EMPRESA ──
CREATE TABLE IF NOT EXISTS empresa (
    id           INT          NOT NULL AUTO_INCREMENT,
    cidade_id    INT          NOT NULL,
    segmento_id  INT          NOT NULL,
    nome         VARCHAR(150) NOT NULL,
    cnpj         CHAR(14)     NOT NULL,
    email        VARCHAR(150) NOT NULL,
    senha_hash   VARCHAR(255) NOT NULL,
    telefone     VARCHAR(20),
    criado_em    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_empresa_email (email),
    UNIQUE KEY uq_empresa_cnpj  (cnpj),
    CONSTRAINT fk_empresa_cidade    FOREIGN KEY (cidade_id)   REFERENCES cidade   (id),
    CONSTRAINT fk_empresa_segmento  FOREIGN KEY (segmento_id) REFERENCES segmento (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ── EVENTO ──
CREATE TABLE IF NOT EXISTS evento (
    id                 INT          NOT NULL AUTO_INCREMENT,
    empresa_id         INT          NOT NULL,
    categoria_id       INT          NOT NULL,
    titulo             VARCHAR(200) NOT NULL,
    descricao          TEXT,
    data_evento        DATE         NOT NULL,
    horario            TIME,
    local              VARCHAR(200) NOT NULL,
    contato_whatsapp   VARCHAR(20),
    publicado_em       DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expira_em          DATETIME,
    PRIMARY KEY (id),
    CONSTRAINT fk_evento_empresa   FOREIGN KEY (empresa_id)   REFERENCES empresa   (id) ON DELETE CASCADE,
    CONSTRAINT fk_evento_categoria FOREIGN KEY (categoria_id) REFERENCES categoria (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =============================================
--  DADOS INICIAIS
-- =============================================

-- Cidades
INSERT INTO cidade (nome, estado) VALUES
    ('Mongaguá', 'SP'),
    ('Itanhaém', 'SP'),
    ('Peruíbe',  'SP');

-- Segmentos
INSERT INTO segmento (nome, descricao) VALUES
    ('Entretenimento', 'Shows, festas e eventos de lazer'),
    ('Gastronomia',    'Restaurantes, bares e eventos gastronômicos'),
    ('Esportes',       'Torneios e competições esportivas'),
    ('Cultura',        'Teatro, exposições e eventos culturais'),
    ('Negócios',       'Feiras, congressos e eventos corporativos');

-- Categorias
INSERT INTO categoria (nome, slug, cor_hex) VALUES
    ('Show',        'show',        '#1a4f6e'),
    ('Festa',       'festa',       '#3a7fa0'),
    ('Gastronomia', 'gastronomia', '#6aaec8'),
    ('Esporte',     'esporte',     '#2e8b57'),
    ('Cultural',    'cultural',    '#7b52ab'),
    ('Outro',       'outro',       '#888888');

-- Empresa de exemplo
INSERT INTO empresa (cidade_id, segmento_id, nome, cnpj, email, senha_hash, telefone) VALUES
    (1, 1, 'Balneário Music', '12345678000190',
     'contato@balneariomusic.com.br',
     -- senha: conectamonga123 (SHA-256)
     'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3',
     '(13) 99811-2233');

-- Evento de exemplo
INSERT INTO evento (empresa_id, categoria_id, titulo, descricao, data_evento, horario, local, contato_whatsapp, expira_em) VALUES
    (1, 1,
     'Festival de Verão Mongaguá 2025',
     'O maior festival de verão do litoral paulista! Com bandas ao vivo, gastronomia local e muito mais.',
     '2025-01-18', '20:00:00',
     'Avenida Beira Mar, 500 – Mongaguá, SP',
     '(13) 99811-2233',
     '2025-01-19 23:59:59');

-- =============================================
--  VIEWS ÚTEIS
-- =============================================

CREATE OR REPLACE VIEW vw_eventos_completos AS
SELECT
    ev.id,
    ev.titulo,
    ev.descricao,
    ev.data_evento,
    ev.horario,
    ev.local,
    ev.contato_whatsapp,
    ev.publicado_em,
    ev.expira_em,
    cat.nome    AS categoria,
    cat.cor_hex AS categoria_cor,
    emp.nome    AS empresa,
    emp.email   AS empresa_email,
    cid.nome    AS cidade,
    seg.nome    AS segmento
FROM evento ev
INNER JOIN categoria cat ON cat.id = ev.categoria_id
INNER JOIN empresa   emp ON emp.id = ev.empresa_id
INNER JOIN cidade    cid ON cid.id = emp.cidade_id
INNER JOIN segmento  seg ON seg.id = emp.segmento_id
WHERE ev.expira_em IS NULL OR ev.expira_em >= NOW();

-- =============================================
--  FIM DO SCRIPT
-- =============================================
