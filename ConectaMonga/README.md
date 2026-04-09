# ConectaMonga — Plataforma de Eventos em Mongaguá

> Sua cidade em movimento. Descubra shows, festas, gastronomia e muito mais.

---

## Estrutura do Projeto

```
ConectaMonga/
├── frontend/
│   ├── html/
│   │   └── index.html          ← Página principal (abrir no navegador)
│   ├── css/
│   │   └── style.css           ← Estilos do site
│   └── js/
│       └── app.js              ← Lógica JavaScript do frontend
│
├── backend/
│   ├── python/
│   │   ├── app.py              ← API REST com Flask (Python)
│   │   └── requirements.txt    ← Dependências Python
│   └── csharp/
│       ├── Program.cs          ← Ponto de entrada ASP.NET Core
│       ├── Models.cs           ← Modelos do banco (Entity Framework)
│       └── Controllers.cs      ← Controllers + Services + DbContext
│
└── database/
    └── banco.sql               ← Script MySQL completo
```

---

## Como Abrir no Visual Studio

### 1. Frontend (HTML/CSS/JS)
- Abra a pasta `ConectaMonga` no **Visual Studio** ou **VS Code**
- Navegue até `frontend/html/index.html`
- Clique com botão direito → **Open with Live Server** (VS Code)
- Ou simplesmente dê duplo clique em `index.html`

### 2. Banco de Dados MySQL
```bash
# Execute no terminal do MySQL
mysql -u root -p < database/banco.sql
```
Isso cria o banco `conectamonga` com todas as tabelas e dados iniciais.

### 3. Backend Python (Flask)
```bash
cd backend/python

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente (opcional)
# DB_HOST, DB_USER, DB_PASSWORD, DB_NAME

# Rodar o servidor
python app.py
# API disponível em: http://localhost:5000
```

### 4. Backend C# (ASP.NET Core)
```bash
cd backend/csharp

# Instalar pacotes NuGet necessários:
# dotnet add package Pomelo.EntityFrameworkCore.MySql
# dotnet add package Microsoft.EntityFrameworkCore.Design

# Configurar appsettings.json:
# "ConnectionStrings": {
#   "DefaultConnection": "server=localhost;database=conectamonga;user=root;password=SUASENHA"
# }

# Rodar a API
dotnet run
# API disponível em: http://localhost:5148
# Swagger: http://localhost:5148/swagger
```

---

## Endpoints da API

| Método | Rota                         | Descrição                      |
|--------|------------------------------|--------------------------------|
| GET    | /api/eventos                 | Lista todos os eventos         |
| GET    | /api/eventos/{id}            | Detalhe de um evento           |
| POST   | /api/eventos                 | Criar evento (foto obrigatória)|
| DELETE | /api/eventos/{id}            | Remover evento                 |
| GET    | /api/empresas                | Lista empresas                 |
| POST   | /api/empresas/cadastro       | Cadastrar empresa (CNPJ req.)  |
| POST   | /api/empresas/login          | Login empresa                  |
| GET    | /api/categorias              | Lista categorias               |
| GET    | /api/cidades                 | Lista cidades                  |
| GET    | /api/segmentos               | Lista segmentos                |

---

## Funcionalidades

- Login via Google e Facebook (OAuth)
- Login/Cadastro por email e senha
- Cadastro de empresa com CNPJ obrigatório
- Foto de perfil em todas as áreas
- Publicação de eventos com foto obrigatória
- Filtros por categoria, segmento e data
- Sistema de curtidas
- Comentários e avaliação por estrelas
- Mapa da localização do evento
- Painel de controle para empresas
- Design responsivo (mobile/desktop)

---

## Tecnologias

| Camada    | Tecnologia                          |
|-----------|-------------------------------------|
| Frontend  | HTML5, CSS3, JavaScript (ES6+)      |
| Backend   | Python 3.12 + Flask 3.0             |
| Backend   | C# 12 + ASP.NET Core 8 + EF Core   |
| Banco     | MySQL 8.x                           |
| UI/Icons  | Font Awesome 6, Google Fonts        |

---

## Paleta de Cores

| Nome       | Hex       |
|------------|-----------|
| Azul Claro | `#6aaec8` |
| Azul Médio | `#3a7fa0` |
| Azul Royal | `#1a4f6e` |
| Branco     | `#ffffff` |
| Off-white  | `#f4f8fb` |

---

© 2025 ConectaMonga — Mongaguá, SP, Brasil
