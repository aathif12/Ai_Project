---
description: How to set up and run the UniRAG chatbot with Supabase
---

# UniRAG Setup Workflow

## Prerequisites

1. **Python 3.10+** - For the FastAPI backend
2. **Node.js 18+** - For the React frontend
3. **OpenAI API Key** - Get one from https://platform.openai.com/api-keys
4. **Supabase Account** - Free at https://supabase.com

## Step 1: Supabase Setup

1. Go to https://supabase.com and create a new project
2. Wait for the project to be provisioned (takes ~2 minutes)
3. Go to **SQL Editor** (left sidebar)
4. Open `backend/supabase_setup.sql` and copy its contents
5. Paste into the SQL Editor and click **Run**
6. Get your credentials:
   - Go to **Settings > API** for URL and anon key
   - Go to **Settings > Database** > Connection string for the DB URL

## Step 2: Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
```

3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`

// turbo
4. Install Python dependencies:
```bash
pip install -r requirements.txt
```

5. Create the environment file:
```bash
copy .env.example .env
```

6. **IMPORTANT**: Edit `.env` and add your credentials:
```
OPENAI_API_KEY=sk-your-api-key
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_DB_URL=postgresql://postgres:YOUR-PASSWORD@db.your-project.supabase.co:5432/postgres
```

// turbo
7. Start the backend server:
```bash
uvicorn main:app --reload
```

The backend will be running at: http://localhost:8000
API docs available at: http://localhost:8000/docs

## Step 3: Frontend Setup (in a new terminal)

// turbo
1. Navigate to the frontend directory:
```bash
cd frontend
```

// turbo
2. Install Node.js dependencies:
```bash
npm install
```

// turbo
3. Start the development server:
```bash
npm run dev
```

The frontend will be running at: http://localhost:5173

## Step 4: Testing the Application

1. Open http://localhost:5173 in your browser
2. Click "Upload" and upload a PDF or DOCX file
3. Wait for processing to complete (you'll see chunk count)
4. Ask questions about your document in the chat!

## Sample Questions to Try

After uploading the sample handbook:
- "What is the attendance requirement for exams?"
- "When does the library close on Saturdays?"
- "What are the hostel visitor rules?"
- "How do I register for courses?"

## Verifying Supabase Connection

1. Open Supabase Dashboard > Table Editor
2. You should see the `vecs_university_documents` table created automatically
3. After uploading documents, check the chat_history and feedback tables

## Troubleshooting

### "Supabase credentials not configured"
- Make sure `.env` file exists and has all required values
- Check that SUPABASE_URL starts with `https://`
- Verify SUPABASE_DB_URL includes your actual password

### Backend can't connect to Supabase
- Check if your IP is allowed (Supabase > Settings > Database > Network)
- Verify the database password is correct
- Make sure pgvector extension is enabled (run the SQL setup script)

### Document upload fails
- Check file size (max 50MB)
- Only PDF and DOCX files are supported
- Check backend logs for OpenAI errors (API key issues)

### Chat returns empty or errors
- Make sure documents are uploaded first
- Check that embeddings were created (check Supabase tables)
- Verify OpenAI API key is valid and has credits

## Monitoring in Supabase

View your data in the Supabase Dashboard:
- **Table Editor**: See raw data in tables
- **SQL Editor**: Run custom queries
- **API**: Test endpoints directly
- **Logs**: Debug database issues
