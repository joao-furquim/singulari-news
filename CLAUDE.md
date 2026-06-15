# Singulari News — Contexto do Projeto

## Visão Geral
Newsletter inteligente com agente curador de conteúdo, 
resumos por IA e sistema completo de autenticação.

## Stack Completa

### Serviços (docker-compose)
- Frontend: React + Vite + i18next + polling 30s
- Backend: FastAPI + Tortoise ORM + Aerich + JWT + bcrypt
- Agente: Worker Python + APScheduler
- Consumidor: Worker NestJS + BullMQ
- Broker: BullMQ + Redis (também cache JWT)
- Banco: PostgreSQL
- APIs externas: Resend, Cloudflare R2, Claude/Gemini

## Arquitetura do Backend

### Camadas
routes → services → repositories

### Padrão de nomenclatura OBRIGATÓRIO

#### Models (Tortoise ORM) — singular
class News(Model)
class Category(Model)
class UserFavorite(Model)
class PasswordReset(Model)

#### Schemas (Pydantic) — sufixo indica direção
class NewsOut(BaseModel)         # resposta da API
class NewsFilter(BaseModel)      # parâmetros de filtro
class UserCreateIn(BaseModel)    # body de criação
class UserUpdateIn(BaseModel)    # body de atualização
class TokenOut(BaseModel)        # resposta de auth
class PaginatedResponse(BaseModel)

#### Interfaces — prefixo I
class INewsRepository(ABC)
class INewsService(ABC)
class IUserRepository(ABC)
class IStorageService(ABC)
class IEmailService(ABC)

#### Repositories — sufixo Repository
class NewsRepository(INewsRepository)
class UserRepository(IUserRepository)

#### Services — sufixo Service
class NewsService(INewsService)
class AuthService(IAuthService)
class StorageService(IStorageService)
class EmailService(IEmailService)

#### Dependências FastAPI — prefixo get_
def get_news_repository() -> INewsRepository
def get_news_service() -> INewsService
def get_current_user() -> UserOut

#### Variáveis — descritivas, sem abreviação
# ERRADO: usr, dt, pg, p, f
# CERTO: current_user, current_date, current_page, inbox_path

#### Booleans — prefixo is/has/can
is_authenticated = True
has_preferences = True
can_reset_password = True
is_inbox_empty = True

#### Coleções — plural
categories = []
selected_category_ids = []
news_items = []

## Banco de Dados (PostgreSQL + Tortoise ORM + Aerich)

### Tabelas
- users (id, name, email, password_hash, avatar_url, locale, created_at, updated_at)
- categories (id, name, slug, icon, description, created_at)
- news (id, category_id FK, title, source, summary, content, published_at, created_at)
- user_preferences (user_id FK, category_id FK, created_at)
- user_favorites (user_id FK, news_id FK, saved_at)
- news_queue (id, news_id FK, status, error_message, processed_at, created_at)
- password_resets (id, user_id FK, token, used, expires_at, created_at)

### Seed obrigatório de categories
Tecnologia, IA, Negócios, Inovação, Ciência, Política

## Rotas do Backend

### Públicas
GET  /news?date_from&date_to&categories&page&limit
GET  /preferences

### Auth
POST /users                     (cadastro)
POST /login                     (retorna token + user + preferences)
POST /auth/forgot-password
POST /auth/reset-password

### Autenticadas (JWT obrigatório)
GET  /users/me
PUT  /users/me
POST /users/me/avatar           (multipart/form-data → Cloudflare R2)
GET  /users/me/preferences
PUT  /users/me/preferences
GET  /users/me/favorites
POST /news/:id/favorite
DELETE /news/:id/favorite

## Estrutura de Pastas do Backend

backend/
├── app/
│   ├── api/
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── news.py
│   │       ├── auth.py
│   │       ├── users.py
│   │       └── preferences.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py       (Pydantic BaseSettings)
│   │   ├── security.py     (JWT + bcrypt)
│   │   └── dependencies.py (injeção de dependência)
│   ├── interfaces/
│   │   ├── __init__.py
│   │   ├── news_repository.py
│   │   ├── news_service.py
│   │   ├── user_repository.py
│   │   ├── user_service.py
│   │   ├── storage_service.py
│   │   └── email_service.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── news.py
│   │   ├── user.py
│   │   └── category.py
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── news_repository.py
│   │   └── user_repository.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── news.py
│   │   ├── auth.py
│   │   └── user.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── news_service.py
│   │   ├── auth_service.py
│   │   ├── storage_service.py
│   │   └── email_service.py
│   └── main.py
├── migrations/
├── tests/
├── Dockerfile
└── pyproject.toml

## Variáveis de Ambiente (.env)

DATABASE_URL=postgres://user:pass@db:5432/singulari_news
JWT_SECRET_KEY=<CHAVE_SEGURA>
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
JWT_RESET_TOKEN_EXPIRE_MINUTES=15
REDIS_URL=redis://redis:6379
RESEND_API_KEY=<CHAVE_DE_API>
EMAIL_FROM=newsletter@singulari.com.br
R2_ACCOUNT_ID=<CHAVE_DE_API>
R2_ACCESS_KEY_ID=<CHAVE_DE_API>
R2_SECRET_ACCESS_KEY=<CHAVE_DE_API>
R2_BUCKET_NAME=singulari-news
R2_PUBLIC_URL=https://pub-xxx.r2.dev
AI_API_KEY=<CHAVE_DE_API>
AI_MODEL=claude-haiku-4-5-20251001
AGENT_SCHEDULER_INTERVAL_MINUTES=5
AGENT_QUEUE_PATH=data/queue
AGENT_INBOX_PATH=data/inbox
AGENT_PROCESSED_PATH=data/processed

## Agente Curador (Python + APScheduler)

### Fluxo
1. Scheduler roda a cada AGENT_SCHEDULER_INTERVAL_MINUTES
2. Chama reabastecer_inbox() — se inbox vazio, move primeiro 
   arquivo de queue/ para inbox/ (sort alfabético)
3. Chama processar_inbox() — lê arquivos de inbox/
4. Classifica por keywords, fallback para API de IA
5. Publica na fila BullMQ via Redis
6. Move arquivo para processed/

### Nomenclatura do agente
- inbox_path, queue_path, processed_path
- pending_articles, processed_articles
- article_file, raw_content, curated_article
- is_inbox_empty, has_pending_articles

## Consumidor NestJS

### Fluxo
1. Consome fila BullMQ
2. Chama API de IA para gerar summary
3. Salva notícia no PostgreSQL com summary preenchido
4. Atualiza status em news_queue

## Frontend (React + Vite)

### Telas
1. Feed público (não logado)
2. Modal auth (login/cadastro/recuperação de senha)
3. Modal de preferências (onboarding + edição)
4. Feed logado (filtros com preferências)
5. Modal de detalhe da notícia
6. Modal de intervalo de datas
7. Modal de perfil (edição de dados + avatar)

### Identidade visual Singulari
background: #0d1117
surface: #161b22
primary: #2d8eff
text-primary: #e6edf3
text-secondary: #8b949e
border: #30363d
success: #3fb950
warning: #e6c85a
danger: #e85555