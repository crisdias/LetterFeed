# LetterFeed

LetterFeed is a self-hosted application that transforms your email newsletters into RSS feeds.

It periodically scans your email inbox via IMAP for new emails from the senders you've configured. When it finds a new email, it processes it, and adds it as a new entry to the corresponding newsletter's RSS feed.

<div align="center">
  <img src="./screenshot.png">
</div>

## Features

- **Email to RSS Conversion**: Automatically converts newsletters from your inbox into clean RSS/Atom feeds
- **Content Extraction**: Smart content extraction using `readability-lxml` to strip tracking pixels, ads, and unnecessary HTML, delivering clean article content
- **Flexible Feed Options**:
  - **Master Feed**: Single unified feed containing all newsletters (`/feeds/all`)
  - **Individual Feeds**: Separate feed for each newsletter (`/feeds/{newsletter-id}`)
  - **OPML Export**: Dynamic OPML file (`/feeds/opml`) for importing all newsletters as individual feeds into your RSS reader
- **Auto-Extract Content**: Optional per-newsletter setting to automatically extract clean article content, removing headers, footers, and promotional content
- **Web Dashboard**: Manage newsletters, view articles, configure IMAP settings, and process emails manually
- **Authentication**: Optional HTTP Basic Auth to protect your feeds
- **Scheduled Processing**: Configurable email checking interval (default: 15 minutes)

## Getting Started

### Prerequisites

1. An existing mailbox with IMAP over SSL on port 993.
2. Docker and Docker Compose installed on your system.

### Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/LeonMusCoden/letterfeed.git
    cd letterfeed
    ```

2.  **Configure environment variables:**

    Settings related to IMAP, email processing, and username/password can be set via env variables or the UI. All other settings have to be set via env vars. Settings set in the `.env` file are locked in the UI.

    ```bash
    cp .env.example .env
    ```

    Edit the `.env` file with your specific settings. All settings are explained in the `.env.example`.

3.  **Run the Docker containers:**

    ```bash
    docker compose up -d
    ```

## Development

### Local Development (without Docker)

For local development, you can run the backend and frontend directly without Docker:

1.  **Prerequisites:**

    - Python 3.13+ with [uv](https://docs.astral.sh/uv/) package manager
    - Node.js 22+ with npm
    - SQLite

2.  **Configure environment variables:**

    ```bash
    cp .env.example .env
    ```

    Edit `.env` with local development settings:

    ```bash
    LETTERFEED_APP_BASE_URL=http://localhost:3000
    LETTERFEED_BACKEND_URL=http://localhost:8000
    LETTERFEED_DATABASE_URL=sqlite:////absolute/path/to/letterfeed/data/letterfeed.db
    LETTERFEED_PRODUCTION=false
    LETTERFEED_SECRET_KEY=<generate with: openssl rand -hex 32>
    ```

3.  **Setup backend:**

    ```bash
    cd backend
    uv sync --all-extras

    # Run migrations
    source ../.env && uv run alembic upgrade head

    # Start backend server
    source ../.env && uv run uvicorn app.main:app --reload
    ```

    Backend will be available at http://localhost:8000

4.  **Setup frontend:**

    ```bash
    cd frontend
    npm install

    # Start frontend server
    LETTERFEED_BACKEND_URL=http://localhost:8000 npm run dev
    ```

    Frontend will be available at http://localhost:3000

### Deploying with Docker (Production or Custom Fork)

If you have a fork or want to build from source in production:

1.  **Clone your fork:**

    ```bash
    git clone https://github.com/yourusername/letterfeed.git
    cd letterfeed
    ```

2.  **Configure production environment:**

    ```bash
    cp .env.example .env
    ```

    Edit `.env` with production settings:

    ```bash
    # Production URLs (adjust to your domain)
    LETTERFEED_APP_BASE_URL=https://letterfeed.yourdomain.com
    LETTERFEED_BACKEND_URL=http://backend:8000  # Docker service name

    # Database (use Docker volume path)
    LETTERFEED_DATABASE_URL=sqlite:////data/letterfeed.db

    # Production mode
    LETTERFEED_PRODUCTION=true

    # Security (generate new values)
    LETTERFEED_SECRET_KEY=<generate with: openssl rand -hex 32>
    LETTERFEED_AUTH_USERNAME=your_username
    LETTERFEED_AUTH_PASSWORD=your_secure_password
    ```

3.  **Build and run with Docker Compose:**

    ```bash
    # Build from local source
    docker compose -f docker-compose.dev.yml up -d --build
    ```

### Key Environment Variable Differences

| Variable | Local Development | Docker Production |
|----------|------------------|-------------------|
| `LETTERFEED_APP_BASE_URL` | `http://localhost:3000` | `https://letterfeed.yourdomain.com` |
| `LETTERFEED_BACKEND_URL` | `http://localhost:8000` | `http://backend:8000` |
| `LETTERFEED_DATABASE_URL` | `sqlite:////absolute/path/data/letterfeed.db` | `sqlite:////data/letterfeed.db` |
| `LETTERFEED_PRODUCTION` | `false` | `true` |
