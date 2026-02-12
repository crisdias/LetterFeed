# Letterfeed - Instruções para Claude

## Visão Geral

Letterfeed transforma newsletters recebidas por email em feeds RSS. O projeto tem:
- **Backend**: FastAPI + SQLAlchemy + SQLite + APScheduler (Python 3.13)
- **Frontend**: Next.js 15 (React)
- **Email**: IMAP para buscar newsletters periodicamente
- **Feeds**: Geração de RSS via `feedgen`

## Estrutura do Projeto

```
letterfeed/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI app entry point
│   │   ├── api/             # API routes
│   │   ├── core/            # Config, scheduler, security
│   │   ├── crud/            # Database operations
│   │   ├── models/          # SQLAlchemy models
│   │   ├── schemas/         # Pydantic schemas
│   │   └── services/        # Business logic (email processor, feed generator)
│   ├── alembic/             # Database migrations
│   ├── pyproject.toml       # Python deps (uv)
│   └── .venv/               # Virtual environment
├── frontend/
│   ├── app/                 # Next.js App Router
│   ├── components/          # React components
│   ├── lib/                 # Utils, API client
│   └── middleware.ts        # Proxy /api/* to backend
├── data/
│   └── letterfeed.db        # SQLite database (local dev)
└── .env                     # Environment config
```

## Configuração de Desenvolvimento Local

O projeto roda **sem containers** em dev. Configuração já feita:

### Ambiente

- **Python**: 3.13 (gerenciado por `uv`)
- **Node**: 22 + npm 10
- **Database**: SQLite em `/home/crisdias/dev/letterfeed/data/letterfeed.db`
- **Backend URL**: http://localhost:8000
- **Frontend URL**: http://localhost:3000

### .env

```env
LETTERFEED_APP_BASE_URL=http://localhost:3000
LETTERFEED_BACKEND_URL=http://localhost:8000
LETTERFEED_DATABASE_URL=sqlite:////home/crisdias/dev/letterfeed/data/letterfeed.db
LETTERFEED_PRODUCTION=false
LETTERFEED_SECRET_KEY=<já configurado>
```

IMAP e auth não estão configurados (serão configurados via UI depois).

### Instalação

```bash
# Backend
cd backend && uv sync --all-extras

# Frontend
cd frontend && npm install

# Migrations
cd backend && set -a && source ../.env && set +a && uv run alembic upgrade head
```

### Rodando os Servidores

**Terminal 1 — Backend:**
```bash
cd backend && set -a && source ../.env && set +a && uv run uvicorn app.main:app --reload
```

**Terminal 2 — Frontend:**
```bash
cd frontend && LETTERFEED_BACKEND_URL=http://localhost:8000 npm run dev
```

### Verificação

- Backend health: http://localhost:8000/health → `{"status":"ok"}`
- Frontend: http://localhost:3000
- Feeds (via proxy): http://localhost:3000/api/feeds/all
- API direta: http://localhost:8000/feeds/all

## Arquitetura

### Backend (FastAPI)

- **Scheduler**: APScheduler roda job periódico (`process_emails`) a cada 15min (configurável via `LETTERFEED_EMAIL_CHECK_INTERVAL`)
- **Email Processing** (`app/services/email_processor.py`):
  1. Conecta via IMAP (SSL, porta 993)
  2. Busca emails não processados na pasta configurada (`LETTERFEED_SEARCH_FOLDER`)
  3. Extrai conteúdo limpo (título, corpo HTML/texto)
  4. Salva como `Article` no banco
  5. Move email para pasta configurada (opcional) e/ou marca como lido
- **Feed Generation** (`app/services/feed_generator.py`):
  - Gera RSS feeds para newsletters individuais ou feed agregado (`/feeds/all`)
  - Usa `feedgen` para criar XML RSS 2.0
  - Ordena artigos por `received_at` (data do email)
- **Auth**: HTTP Basic Auth (opcional, configurável via `LETTERFEED_AUTH_USERNAME` e `LETTERFEED_AUTH_PASSWORD`)
- **Database**: SQLite com migrations Alembic

**Modelos principais:**
- `Newsletter`: representa um sender de email (newsletters individuais)
- `Article`: artigos extraídos de emails
- `Settings`: configurações globais (IMAP, auth, etc.)

### Frontend (Next.js)

- **App Router** (Next.js 15)
- **Middleware** (`middleware.ts`): faz proxy de `/api/*` para o backend via `LETTERFEED_BACKEND_URL`
- **Dashboard**: gerencia newsletters, visualiza artigos, configura IMAP/auth
- **ShadcN UI**: componentes React (Tailwind CSS)

## Fluxo de Dados

1. Scheduler dispara `process_emails()` periodicamente
2. Email processor conecta IMAP, busca novos emails
3. Extrai título/corpo, cria `Article` vinculado a `Newsletter`
4. Feed generator serve RSS em `/feeds/<slug>` ou `/feeds/all`
5. Frontend consome API via proxy `/api/*` (ou direto em prod)

## Próximos Passos para Personalização

- [ ] Configurar IMAP via UI (ou `.env` se preferir)
- [ ] Customizar processamento de emails (parsing, filtros, etc.)
- [ ] Ajustar frontend (layout, temas, etc.)
- [ ] Adicionar features (busca, filtros por data, tags, etc.)
- [ ] Containerizar para produção (Docker Compose)

## Comandos Úteis

```bash
# Backend
cd backend
uv sync --all-extras              # Instalar deps
uv run alembic upgrade head       # Aplicar migrations
uv run alembic revision --autogenerate -m "msg"  # Criar migration
uv run uvicorn app.main:app --reload  # Dev server
uv run pytest                     # Testes

# Frontend
cd frontend
npm install                       # Instalar deps
npm run dev                       # Dev server (Turbopack)
npm run build                     # Build para produção
npm run start                     # Prod server

# Database
sqlite3 data/letterfeed.db        # CLI do SQLite
```

## Convenções de Código

- **Backend**: PEP 8, type hints, docstrings em funções públicas
- **Frontend**: ESLint, Prettier, componentes funcionais React
- **Commits**: mensagens descritivas, convenção: `add/update/fix: descrição`
- **Branches**: feature/bug-fix branches, PR para `master`

## Notas Importantes

- **Sem Docker em dev**: rodar diretamente no sistema para facilitar edição e debugging
- **SQLite**: adequado para dev e produção light; para escala considerar Postgres
- **IMAP SSL obrigatório**: porta 993
- **Auto-add senders**: `LETTERFEED_AUTO_ADD_NEW_SENDERS=false` por padrão (criar newsletters manualmente via UI)
- **Migrations**: sempre criar via `alembic revision --autogenerate` após mudar models
