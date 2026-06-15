# Agentic RAG on AWS

A production-grade **Agentic Retrieval-Augmented Generation (RAG)** system built on AWS. Upload company documents and ask intelligent questions — the agent reasons, retrieves, and answers with cited sources.

---

##  Architecture

```
Client
  │
  ▼
FastAPI (API Layer)
  │
  ├── POST /documents/upload_url  ──► S3 (presigned URL)
  ├── POST /documents/ingest      ──► Ingestion Pipeline
  └── POST /query/ask             ──► Query Pipeline
                                          │
                                    LangGraph Agent
                                          │
                              ┌───────────┼───────────┐
                              ▼           ▼           ▼
                        Retriever    Document     Summarizer
                          Tool        Tool          Tool
                              │           │
                              ▼           ▼
                          ChromaDB    DynamoDB
                        (child chunks) (parent docs)
                              │
                              ▼
                       AWS Bedrock LLM
                      (MiniMax M2.5)
```

**Parent-Child Chunking Strategy:**
- PDFs are split into large **parent chunks** → stored in DynamoDB
- Parent chunks split into small **child chunks** → embedded and stored in ChromaDB
- At query time: retrieve precise child chunks → fetch rich parent context → send to LLM

---

##  Tech Stack

| Layer | Technology |
|-------|-----------|
| API | FastAPI |
| Agent | LangGraph + LangChain |
| LLM | AWS Bedrock (MiniMax M2.5) |
| Embeddings | AWS Bedrock (Titan Embeddings v2) |
| Reranker | AWS Bedrock amazon.rerank-v1:0 (us-west-2) |
| Vector Store | ChromaDB |
| Document Store | AWS DynamoDB |
| File Storage | AWS S3 |
| Observability | Langfuse |
| Containerization | Docker + Docker Compose |

---

## Features

- **Agentic RAG** — agent reasons and decides which tool to use (retriever, document fetcher, summarizer)
- **Parent-Child Retrieval** — dynamic chunking with smart parent context fetching
- **Conversation Memory** — session-based memory via LangGraph checkpointer
- **S3 Presigned URLs** — secure direct-to-S3 file uploads (data never passes through app server)
- **Request ID Tracking** — every request has a unique ID traced across all logs
- **Production Patterns** — factory pattern, dependency injection, retry logic, global exception handling
- **Fully Containerized** — runs with a single `docker-compose up` command
- **Data Sovereignty** — all data stays within AWS infrastructure

---

## Project Structure

```
aws_rag/
├── app/
│   ├── agent/                  # LangGraph agent + tools + memory
│   │   ├── tools/              # retriever, document, summarizer tools
│   │   ├── prompts/            # system prompts
│   │   └── middleware/         # logging middleware
│   ├── api/v1/routes/          # FastAPI endpoints
│   ├── core/                   # config, logging, exceptions, middleware
│   ├── models/                 # pydantic schemas
│   ├── pipeline/               # ingestion + query pipelines
│   └── services/               # pluggable service layer
│       ├── llm/                # LLM factory + Bedrock provider
│       ├── embeddings/         # Embeddings factory + Titan provider
│       ├── retriever/          # Retriever factory + ChromaDB provider
│       ├── docstore/           # Docstore factory + DynamoDB provider
│       ├── ingestion/          # Ingestion factory + PDF provider
│       └── reranker/           # Reranker factory + Bedrock provider
├── tests/                      # unit + integration tests (WIP)
├── main.py                     # FastAPI entry point
├── Dockerfile                  # multi-stage Docker build
├── docker-compose.yml          # app + ChromaDB containers
└── requirements.txt
```

---

## Environment Variables

Create a `.env` file in the root directory:

```env
# AWS
AWS_ACCESS_KEY=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1

# S3
S3_BUCKET=your-bucket-name

# DynamoDB
DYNAMODB_TABLE_NAME=rag-parent-docs

# ChromaDB
CHROMA_HOST=localhost
CHROMA_PORT=8001
CHROMA_COLLECTION=rag_documents

# Bedrock Models
BEDROCK_MODEL_ID=minimax.minimax-m2.5
BEDROCK_EMBEDDING_MODEL_ID=amazon.titan-embed-text-v2:0
BEDROCK_RERANK_MODEL=cohere.rerank-v3-5:0
BEDROCK_TEMPERATURE=0.0

# App
APP_NAME=AWS_RAG
APP_ENV=development
APP_DEBUG=True
APP_VERSION=1.0.0
API_VERSION=v1

# Langfuse (optional)
LANGFUSE_PUBLIC_KEY=your_public_key
LANGFUSE_SECRET_KEY=your_secret_key
LANGFUSE_BASE_URL=https://cloud.langfuse.com
```

---

## Running the Project

### Prerequisites
- Docker + Docker Compose
- AWS account with:
  - S3 bucket created
  - DynamoDB table `rag-parent-docs` with partition key `parent_id` (String)
  - IAM user with `AmazonS3FullAccess`, `AmazonBedrockFullAccess`, `AmazonDynamoDBFullAccess`

### With Docker (recommended)

```bash
# Clone the repo
git clone https://github.com/yourusername/aws_rag.git
cd aws_rag

# Create .env file with your credentials
cp .env.example .env
# Edit .env with your values

# Start everything
docker-compose up --build
```

App will be available at `http://localhost:8000`
Swagger docs at `http://localhost:8000/docs`

### Locally (without Docker)

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start ChromaDB in separate terminal
chroma run --host localhost --port 8001

# Start the app
uvicorn main:app --reload
```

---

## API Endpoints

### Upload Document
```bash
# Step 1 — Get presigned S3 URL
curl -X POST http://localhost:8000/api/v1/documents/upload_url \
  -H "Content-Type: application/json" \
  -d '{"filename": "document.pdf"}'

# Step 2 — Upload file directly to S3
curl -X PUT "PRESIGNED_URL_FROM_STEP_1" \
  --upload-file "/path/to/document.pdf" \
  -H "Content-Type: application/pdf"

# Step 3 — Trigger ingestion
curl -X POST http://localhost:8000/api/v1/documents/ingest \
  -H "Content-Type: application/json" \
  -d '{"s3_key": "uploads/document.pdf"}'
```

### Query
```bash
# First query (no session_id = new conversation)
curl -X POST http://localhost:8000/api/v1/query/ask \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the leave policy?"}'

# Follow-up query (pass session_id for memory)
curl -X POST http://localhost:8000/api/v1/query/ask \
  -H "Content-Type: application/json" \
  -d '{"query": "How many days can I carry forward?", "session_id": "YOUR_SESSION_ID"}'
```

### Health Check
```bash
curl http://localhost:8000/health
```

---

## Future Improvements

- **Redis Memory** — replace in-memory session store with Redis for persistent cross-restart conversation history
- **Authentication** — JWT-based user auth with per-user document isolation
- **Multi-tenancy** — namespace documents by organization
- **Async Ingestion Queue** — SQS + Lambda workers for high-volume document processing
- **Self-hosted Langfuse** — deploy Langfuse on EC2 for full data sovereignty observability
- **Unit + Integration Tests** — pytest test suite for all core components
- **CI/CD Pipeline** — GitHub Actions for automated testing and deployment
- **Streaming Responses** — stream LLM responses for better UX

---

## License

MIT