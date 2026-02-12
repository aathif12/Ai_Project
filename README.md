# 🎓 UniRAG - University Document Chatbot

A RAG (Retrieval-Augmented Generation) chatbot that answers questions based on university documents like handbooks, rules, timetables, and notices.

## ✨ Features

### Core Features
- 📄 **Document Upload**: Support for PDF and DOCX files
- 💬 **Chat Interface**: ChatGPT-like conversational UI
- 🎯 **Grounded Answers**: Responses based ONLY on uploaded documents
- 📍 **Citations**: Shows source document name and page numbers
- 🚫 **Hallucination Guard**: Says "I don't know" when info isn't in documents

### Advanced Features
- 👥 **Role-Based Access**: Admin and Student roles (extensible)
- 📁 **Document Categories**: Rules, Exams, Courses, Hostel, etc.
- 📜 **Query History**: Saved chats with Supabase persistence
- 👍👎 **Feedback System**: Rate answers to improve retrieval
- ☁️ **Cloud Storage**: Supabase for scalable vector storage

## 🏗️ Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   React Frontend│────▶│  FastAPI Backend│────▶│    Supabase     │
│   (Chat UI)     │     │  (RAG Pipeline) │     │  (pgvector DB)  │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │
                               ▼
                        ┌─────────────────┐
                        │   OpenAI API    │
                        │   (Embeddings   │
                        │    + LLM)       │
                        └─────────────────┘
```

## 📁 Project Structure

```
├── frontend/               # React + Vite frontend
│   ├── src/
│   │   ├── components/     # UI components
│   │   ├── services/       # API services
│   │   └── App.jsx         # Main application
│   └── package.json
│
├── backend/                # FastAPI backend
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── services/       # Business logic + Supabase
│   │   ├── ingestion/      # Document processing
│   │   └── models/         # Data models
│   ├── supabase_setup.sql  # Database setup script
│   ├── requirements.txt
│   └── main.py
│
├── docs/                   # Sample university documents
│
└── README.md
```

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- OpenAI API Key
- Supabase Account (free tier works!)

### 1. Supabase Setup

1. Create a new project at [supabase.com](https://supabase.com)
2. Go to **SQL Editor** and run the contents of `backend/supabase_setup.sql`
3. Get your credentials from **Settings > API**:
   - `SUPABASE_URL`: Project URL
   - `SUPABASE_KEY`: `anon` or `service_role` key
4. Get database URL from **Settings > Database > Connection string > URI**

### 2. Backend Setup

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys!

uvicorn main:app --reload
```

### 3. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### 4. Open the App

Visit http://localhost:5173 and start chatting!

## 🔧 Configuration

Create a `.env` file in the backend folder:

```env
# OpenAI
OPENAI_API_KEY=sk-your-api-key-here

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_DB_URL=postgresql://postgres:password@db.your-project.supabase.co:5432/postgres

# Optional customization
CHUNK_SIZE=800
CHUNK_OVERLAP=100
TOP_K_RESULTS=5
EMBEDDING_MODEL=text-embedding-3-small
LLM_MODEL=gpt-4o-mini
```

## 📚 Tech Stack

| Component | Technology |
|-----------|------------|
| Frontend | React + Vite |
| Backend | FastAPI (Python) |
| Vector DB | Supabase pgvector |
| Embeddings | OpenAI text-embedding-3-small |
| LLM | OpenAI GPT-4o-mini |
| Document Processing | PyMuPDF, python-docx |

## 🎯 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/api/documents/upload` | Upload PDF/DOCX |
| GET | `/api/documents` | List documents |
| DELETE | `/api/documents/{id}` | Delete document |
| POST | `/api/chat/` | Send chat message |
| GET | `/api/chat/history/{id}` | Get chat history |
| GET | `/api/chat/conversations` | List conversations |
| POST | `/api/chat/feedback` | Submit feedback |

## 💡 Sample Questions

After uploading documents, try asking:
- "What is the attendance requirement to sit for final exam?"
- "When is the deadline for course registration?"
- "What are the hostel rules about visitors?"
- "How to apply for medical leave?"

## 🔒 Security Notes

- Use `service_role` key for backend (server-side only!)
- Use `anon` key only with Row Level Security (RLS)
- Never expose keys in frontend code
- Configure RLS policies for production

## 📝 License

MIT License

---

Built with ❤️ for university students everywhere
