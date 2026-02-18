# 🎓 UniRAG — University Document Chatbot

> A **Retrieval-Augmented Generation (RAG)** chatbot that answers questions grounded in university documents — handbooks, rules, timetables, notices, and more — with source citations and zero hallucination.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=black)
![Vite](https://img.shields.io/badge/Vite-7-646CFF?logo=vite&logoColor=white)
![Supabase](https://img.shields.io/badge/Supabase-pgvector-3ECF8E?logo=supabase&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o--mini-412991?logo=openai&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 📑 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [1. Supabase Setup](#1-supabase-setup)
  - [2. Backend Setup](#2-backend-setup)
  - [3. Frontend Setup](#3-frontend-setup)
- [Configuration](#-configuration)
- [API Reference](#-api-reference)
- [How It Works](#-how-it-works)
- [Sample Usage](#-sample-usage)
- [Security Notes](#-security-notes)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🌟 Overview

**UniRAG** is a full-stack AI-powered chatbot purpose-built for university environments. Students and staff can upload institutional documents (PDF, DOCX) and ask natural-language questions. The system retrieves relevant passages using vector similarity search and generates accurate, cited answers using OpenAI's GPT models — never making up information.

---

## ✨ Features

### Core
| Feature | Description |
|---|---|
| 📄 **Document Upload** | Drag-and-drop upload for PDF and DOCX files (up to 50 MB) |
| 💬 **Conversational Chat** | ChatGPT-like interface with streaming-style responses |
| 🎯 **Grounded Answers** | Every response is derived *only* from uploaded documents |
| 📍 **Source Citations** | Answers include document name and page numbers |
| 🚫 **Hallucination Guard** | Politely says *"I don't know"* when information isn't in the documents |

### Advanced
| Feature | Description |
|---|---|
| 📁 **Document Categories** | Organize uploads into categories: Rules, Exams, Courses, Hostel, etc. |
| 📜 **Conversation History** | Persistent chat history stored in Supabase |
| 👍👎 **Feedback System** | Rate answers as helpful/unhelpful to improve retrieval quality |
| ☁️ **Cloud Vector Storage** | Supabase pgvector for scalable, production-ready vector search |
| 🔍 **Category Filtering** | Filter document retrieval by category for more precise answers |
| 💡 **Suggested Questions** | Auto-generated starter questions based on available documents |

---

## 🏗️ Architecture

```
┌──────────────────────┐      ┌──────────────────────┐      ┌──────────────────────┐
│                      │      │                      │      │                      │
│   React + Vite       │─────▶│   FastAPI Backend     │─────▶│   Supabase           │
│   (Chat UI)          │ HTTP │   (RAG Pipeline)      │ SQL  │   (pgvector DB)      │
│                      │◀─────│                      │◀─────│                      │
└──────────────────────┘      └──────────┬───────────┘      └──────────────────────┘
                                         │
                                         │ API
                                         ▼
                              ┌──────────────────────┐
                              │                      │
                              │   OpenAI API         │
                              │   • Embeddings       │
                              │   • Chat Completions │
                              │                      │
                              └──────────────────────┘
```

**Data Flow:**

1. **Upload** → User uploads a document via the React frontend
2. **Ingest** → Backend extracts text → splits into chunks → generates embeddings → stores in Supabase
3. **Query** → User asks a question → backend embeds the query → performs vector similarity search
4. **Generate** → Retrieved chunks are sent to GPT as context → grounded answer with citations is returned

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Frontend** | React 19 + Vite 7 | Single-page application with modern UI |
| **Backend** | FastAPI (Python 3.10+) | Async REST API with auto-generated docs |
| **Vector Database** | Supabase pgvector | Cloud-hosted vector similarity search |
| **Embeddings** | OpenAI `text-embedding-3-small` | 1536-dimensional document/query embeddings |
| **LLM** | OpenAI `gpt-4o-mini` | Answer generation with citation support |
| **PDF Parsing** | PyMuPDF (fitz) | High-fidelity text extraction from PDFs |
| **DOCX Parsing** | python-docx | Microsoft Word document processing |
| **Tokenization** | tiktoken | Accurate token counting for chunking |

---

## 📁 Project Structure

```
UniRAG/
├── 📂 backend/                      # FastAPI backend
│   ├── main.py                      # Application entry point & CORS config
│   ├── requirements.txt             # Python dependencies
│   ├── supabase_setup.sql           # Database schema & vector search function
│   ├── .env.example                 # Environment variable template
│   ├── .env                         # Your local credentials (git-ignored)
│   ├── uploads/                     # Temporary file storage
│   └── 📂 app/
│       ├── config.py                # Pydantic settings (type-safe env vars)
│       ├── 📂 api/                  # Route handlers
│       │   ├── health.py            # GET /health — status & document count
│       │   ├── documents.py         # POST/GET/DELETE /api/documents
│       │   └── chat.py              # POST /api/chat — RAG query endpoint
│       ├── 📂 services/             # Business logic
│       │   ├── vector_store.py      # Supabase pgvector CRUD operations
│       │   ├── rag_chain.py         # Retrieval → Context → Generation pipeline
│       │   └── chat_service.py      # Conversation management & history
│       ├── 📂 ingestion/            # Document processing pipeline
│       │   ├── pipeline.py          # Orchestrator: extract → chunk → embed → store
│       │   ├── extractor.py         # PDF & DOCX text extraction
│       │   ├── chunker.py           # Token-aware text chunking with overlap
│       │   └── embedder.py          # OpenAI embedding generation
│       └── 📂 models/               # Pydantic schemas
│           └── schemas.py           # Request/response models & enums
│
├── 📂 frontend/                     # React + Vite frontend
│   ├── index.html                   # HTML entry point
│   ├── package.json                 # Node.js dependencies
│   ├── vite.config.js               # Vite configuration
│   └── 📂 src/
│       ├── main.jsx                 # React DOM render
│       ├── App.jsx                  # Root component — layout, routing, state
│       ├── App.css                  # Global app styles
│       ├── index.css                # CSS reset & design tokens
│       ├── 📂 components/
│       │   ├── ChatInterface.jsx    # Chat messages, input, citations display
│       │   ├── ChatInterface.css
│       │   ├── DocumentUpload.jsx   # Drag-and-drop file upload with progress
│       │   ├── DocumentUpload.css
│       │   ├── Sidebar.jsx          # Conversation list, navigation
│       │   ├── Sidebar.css
│       │   └── index.js             # Component barrel exports
│       └── 📂 services/
│           └── api.js               # Axios-style API client (fetch-based)
│
├── 📂 docs/                         # Sample documents for testing
│   └── sample_handbook.md
│
├── .gitignore
└── README.md                        # ← You are here
```

---

## 🚀 Getting Started

### Prerequisites

| Requirement | Version | Link |
|---|---|---|
| Python | 3.10+ | [python.org](https://www.python.org/downloads/) |
| Node.js | 18+ | [nodejs.org](https://nodejs.org/) |
| OpenAI API Key | — | [platform.openai.com](https://platform.openai.com/api-keys) |
| Supabase Account | Free tier | [supabase.com](https://supabase.com) |

---

### 1. Supabase Setup

1. Create a new project at [supabase.com/dashboard](https://supabase.com/dashboard)
2. Wait for provisioning (~2 minutes)
3. Go to **SQL Editor** in the left sidebar
4. Copy the contents of [`backend/supabase_setup.sql`](backend/supabase_setup.sql) and run it

   This will:
   - Enable the `pgvector` extension
   - Create the `documents` table with a `vector(1536)` column
   - Create the `match_documents` similarity search function
   - Create `chat_history` and `feedback` tables
   - Set up Row Level Security policies

5. Get your credentials:
   - **`SUPABASE_URL`** → Settings > API > Project URL
   - **`SUPABASE_KEY`** → Settings > API > `anon` key (or `service_role` for server-side)
   - **`SUPABASE_DB_URL`** → Settings > Database > Connection string > URI

---

### 2. Backend Setup

```bash
# Navigate to backend
cd backend

# Create and activate a virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create your environment file
copy .env.example .env    # Windows
cp .env.example .env      # macOS/Linux

# ⚠️ Edit .env and add your real credentials (see Configuration section below)

# Start the development server
uvicorn main:app --reload
```

✅ Backend running at: **http://localhost:8000**
📖 Interactive API docs: **http://localhost:8000/docs**
📘 ReDoc: **http://localhost:8000/redoc**

---

### 3. Frontend Setup

Open a **new terminal window**:

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

✅ Frontend running at: **http://localhost:5173**

---

### 4. Start Using UniRAG!

1. Open **http://localhost:5173** in your browser
2. Check the health badge in the header (should show green)
3. Click **Upload** and drag in a PDF or DOCX file
4. Wait for processing to complete (you'll see the chunk count)
5. Start asking questions in the chat! 🎉

---

## ⚙️ Configuration

All configuration is managed via environment variables in `backend/.env`. Copy from `.env.example`:

```env
# ═══════════════════════════════════════════
# Required — OpenAI
# ═══════════════════════════════════════════
OPENAI_API_KEY=sk-your-api-key-here

# ═══════════════════════════════════════════
# Required — Supabase
# ═══════════════════════════════════════════
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-or-service-role-key
SUPABASE_DB_URL=postgresql://postgres:YOUR-PASSWORD@db.your-project-id.supabase.co:5432/postgres

# ═══════════════════════════════════════════
# Optional — Tuning
# ═══════════════════════════════════════════
UPLOAD_DIR=./uploads          # File upload directory
CHUNK_SIZE=800                # Tokens per chunk (default: 800)
CHUNK_OVERLAP=100             # Overlapping tokens between chunks (default: 100)
TOP_K_RESULTS=5               # Number of chunks retrieved per query (default: 5)
EMBEDDING_MODEL=text-embedding-3-small   # OpenAI embedding model
LLM_MODEL=gpt-4o-mini        # OpenAI chat model
EMBEDDING_DIMENSIONS=1536    # Must match embedding model dimensions
```

### Model Options

| Model | Speed | Quality | Cost |
|---|---|---|---|
| `gpt-4o-mini` *(default)* | ⚡ Fast | ★★★★ | $ Low |
| `gpt-4o` | 🐢 Slower | ★★★★★ | $$$ Higher |

| Embedding Model | Dimensions | Speed |
|---|---|---|
| `text-embedding-3-small` *(default)* | 1536 | ⚡ Fast |
| `text-embedding-3-large` | 3072 | 🐢 Slower |

> **Note:** If you change the embedding model, update `EMBEDDING_DIMENSIONS` accordingly and re-upload all documents.

---

## 📡 API Reference

Base URL: `http://localhost:8000`

### Health Check

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Returns system status, Supabase connectivity, and document count |

### Documents

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/documents/upload` | Upload a PDF/DOCX file with a category |
| `GET` | `/api/documents` | List all uploaded documents |
| `DELETE` | `/api/documents/{document_id}` | Delete a document and all its vector chunks |

### Chat

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/chat/` | Send a question and receive a RAG-grounded answer |
| `GET` | `/api/chat/history/{conversation_id}` | Retrieve full chat history for a conversation |
| `GET` | `/api/chat/conversations` | List all past conversations |
| `POST` | `/api/chat/feedback` | Submit feedback (thumbs up/down) for an answer |

### Example — Chat Request

```bash
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the attendance requirement for exams?",
    "conversation_id": null
  }'
```

### Example — Document Upload

```bash
curl -X POST http://localhost:8000/api/documents/upload \
  -F "file=@handbook.pdf" \
  -F "category=rules"
```

> 💡 Full interactive documentation is available at **http://localhost:8000/docs** (Swagger UI).

---

## 🔄 How It Works

### Document Ingestion Pipeline

```
PDF/DOCX File
    │
    ▼
┌─────────────────┐
│  1. EXTRACT     │  PyMuPDF / python-docx
│   Raw text +    │  Extracts text page-by-page
│   page numbers  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  2. CHUNK       │  Token-aware splitter (tiktoken)
│   800-token     │  100-token overlap for context continuity
│   segments      │  Preserves page number metadata
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  3. EMBED       │  OpenAI text-embedding-3-small
│   1536-dim      │  Batch processing for efficiency
│   vectors       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  4. STORE       │  Supabase pgvector
│   Vectors +     │  IVFFlat index for fast search
│   metadata      │  GIN index on metadata (JSONB)
└─────────────────┘
```

### Query & Answer Pipeline

```
User Question
    │
    ▼
┌─────────────────┐
│  1. EMBED       │  Same embedding model as ingestion
│   Query vector  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  2. RETRIEVE    │  Cosine similarity search
│   Top-K chunks  │  Optional category filtering
│   (default: 5)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  3. GENERATE    │  GPT-4o-mini with system prompt:
│   Grounded      │  "Answer ONLY from the provided context.
│   answer +      │   If not found, say 'I don't know'."
│   citations     │  Includes conversation history for context
└─────────────────┘
```

---

## 💡 Sample Usage

After uploading university documents, try these questions:

- *"What is the attendance requirement to sit for the final exam?"*
- *"When is the deadline for course registration?"*
- *"What are the hostel rules about visitors?"*
- *"How do I apply for medical leave?"*
- *"When does the library close on Saturdays?"*
- *"How do I register for courses?"*

---

## 🔒 Security Notes

- **Never commit `.env`** — it's already in `.gitignore`
- Use `service_role` key for the backend (server-side only)
- Use `anon` key only if Row Level Security (RLS) is configured
- Never expose API keys in the frontend code
- The default RLS policies allow all operations — **restrict these for production!**
- File uploads are validated for type (PDF/DOCX only) and size (≤ 50 MB)

---

## 🐛 Troubleshooting

### Backend won't start

| Issue | Fix |
|---|---|
| `ModuleNotFoundError` | Ensure virtual environment is activated and run `pip install -r requirements.txt` |
| `Supabase credentials not configured` | Verify `.env` exists and has all required values; `SUPABASE_URL` must start with `https://` |
| Port 8000 in use | Run with `uvicorn main:app --reload --port 8001` |

### Supabase connection issues

| Issue | Fix |
|---|---|
| `connection refused` | Check if your IP is allowed: Supabase > Settings > Database > Network |
| `password authentication failed` | Verify database password in `SUPABASE_DB_URL` |
| `pgvector extension not found` | Run `supabase_setup.sql` in the SQL Editor |

### Document upload problems

| Issue | Fix |
|---|---|
| Upload fails silently | Check backend terminal for errors; verify OpenAI API key is valid |
| No text extracted | Ensure the PDF contains selectable text (not scanned images) |
| File rejected | Only `.pdf` and `.docx` files are supported (max 50 MB) |

### Chat issues

| Issue | Fix |
|---|---|
| Empty responses | Make sure at least one document is uploaded and processed |
| `OpenAI API error` | Verify API key is valid and account has credits |
| Irrelevant answers | Try uploading more focused documents or reducing `TOP_K_RESULTS` |

### Frontend issues

| Issue | Fix |
|---|---|
| `npm install` fails | Ensure Node.js 18+ is installed; try deleting `node_modules` and `package-lock.json` |
| Blank page | Check browser console for errors; ensure backend is running |
| Health badge shows red | Backend is not running or CORS is misconfigured |

---

## 🤝 Contributing

Contributions are welcome! To get started:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -m "Add my feature"`
4. Push: `git push origin feature/my-feature`
5. Open a Pull Request

---

## 📝 License

This project is licensed under the **MIT License**.

---

<p align="center">
  Built with ❤️ for university students everywhere
</p>
