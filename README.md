# Cloud Companion – Your Friendly Guide to the Cloud

> **AI-Powered Cloud Resource Troubleshooting Assistant**

An open-source, privacy-first solution for intelligent cloud resource discovery, analysis, and AI-driven troubleshooting across AWS, Azure, and GCP using graph databases and semantic search.

## Features

- **Multi-Cloud Support**: AWS, Azure, GCP resource discovery and management
- **Privacy First**: Self-hosted Neo4j + Weaviate + Ollama (no external API calls required)
- **AI-Powered Troubleshooting**: LLM-based step-by-step solutions for cloud issues
- **Semantic Search**: Vector embeddings for intelligent resource discovery
- **API-Key Authentication**: Secure multi-tenant access control
- **WebSocket Streaming**: Real-time chat responses and conversation management
- **Production Ready**: Docker, CI/CD, logging, error handling, testing

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.11+ (for local development)

### Launch

```bash
# Clone repository
git clone <repo-url>
cd cloud-companion

# Start services (Neo4j, Weaviate, FastAPI, Ollama)
docker-compose up -d

# Verify health
curl http://localhost:8000/health
```

### Create API Key

```bash
# Get auth token (see .env.example for credentials)
curl -X POST http://localhost:8000/api/v1/auth/keys \
  -H "Authorization: Bearer <admin-token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "my-key"}'
```

### Use Chat API

```bash
# Single message
curl -X POST http://localhost:8000/api/v1/chat/message \
  -H "X-API-Key: <your-api-key>" \
  -H "Content-Type: application/json" \
  -d '{"message": "How do I debug my EC2 instance?"}'

# WebSocket streaming (ws://localhost:8000/api/v1/chat/ws/<conversation-id>)
```

## Documentation

| Document                                             | Purpose                                     |
| ---------------------------------------------------- | ------------------------------------------- |
| [CONTRIBUTING.md](CONTRIBUTING.md)                   | Contributing guidelines & development setup |
| [.archive/INSTALLATION.md](.archive/INSTALLATION.md) | Detailed installation guide                 |
| [.archive/DEVELOPMENT.md](.archive/DEVELOPMENT.md)   | Development workflow & code standards       |
| [.archive/STRUCTURE.md](.archive/STRUCTURE.md)       | Project structure & file organization       |
| [.archive/ROADMAP.md](.archive/ROADMAP.md)           | Planned features & roadmap                  |
| [docs/architecture.md](docs/architecture.md)         | System architecture & design patterns       |
| [docs/api.md](docs/api.md)                           | API reference documentation                 |

See [.archive/README.md](.archive/README.md) for complete archived documentation index.

## Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Key variables:

- `NEO4J_URI` - Neo4j connection string
- `WEAVIATE_URL` - Weaviate API endpoint
- `LLM_PROVIDER` - LLM service (ollama, openai, etc.)
- `ADMIN_TOKEN` - Admin authentication token

## Architecture

```
┌─────────────────────────────────────────────────┐
│            FastAPI Application                  │
├─────────────────────────────────────────────────┤
│  • API Endpoints (auth, chat, resources, admin) │
│  • WebSocket streaming & conversations          │
│  • Multi-tenant org isolation                   │
└─────────────────────────────────────────────────┘
         ↓                  ↓                ↓
    ┌─────────────┐  ┌────────────┐  ┌──────────────┐
    │   Neo4j     │  │ Weaviate   │  │   Ollama     │
    │  (Graph DB) │  │ (Vector DB)│  │    (LLM)     │
    └─────────────┘  └────────────┘  └──────────────┘
         ↓
    Cloud Crawlers (AWS/Azure/GCP)
```

## Tech Stack

| Layer                | Technology                              |
| -------------------- | --------------------------------------- |
| **Framework**        | FastAPI 0.104+ (async/await)            |
| **Graph DB**         | Neo4j 5.14+ (knowledge graphs)          |
| **Vector DB**        | Weaviate 4.1+ (semantic search)         |
| **LLM**              | LiteLLM 1.13+ (Ollama/OpenAI/Anthropic) |
| **Cloud SDKs**       | boto3, azure-identity, google-cloud     |
| **Security**         | bcrypt, PyJWT, cryptography             |
| **Config**           | Pydantic v2 BaseSettings                |
| **Testing**          | pytest, pytest-asyncio                  |
| **Containerization** | Docker & Docker Compose                 |
| **CI/CD**            | GitHub Actions                          |

## Development

### Setup Local Environment

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Run tests
pytest -v --cov=app
```

### Run Locally

```bash
# Start databases
docker-compose up neo4j weaviate redis -d

# Run FastAPI
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Run Celery Worker

```bash
celery -A app.core.celery_app worker --loglevel=info --concurrency=2
```

### Example Task API

```bash
curl -X POST http://localhost:8000/api/v1/tasks/ping -H "X-API-Key: <your-api-key>"
```

## Testing

```bash
# Run all tests
pytest

# With coverage
pytest --cov=app --cov-report=html

# Watch mode
pytest-watch
```

## License

[Apache License 2.0](LICENSE) - See LICENSE file for details.

## Contributing

Contributions welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for:

- Code of conduct
- Development setup
- Pull request process
- Coding standards

## Support

- 📖 [Documentation](.archive/INSTALLATION.md)
- 🐛 [Bug Reports](https://github.com/vijay/cloud-companion/issues)
- 💬 [Discussions](https://github.com/vijay/cloud-companion/discussions)
- 🔒 [Security Policy](.archive/SECURITY.md)

---

**Status**: Active Development | **License**: Apache 2.0 | **Python**: 3.11+
