# RAGBot: AI-Powered Chat Application with LangChain, FAISS & Gemini

RAGBot is an AI-powered chat application that provides contextual answers by retrieving relevant content from documents uploaded by each user. If no relevant content is found, it gracefully falls back to Gemini (Google AI). The application is built using Flask (Python backend), PostgreSQL (chat storage), FAISS (vector store), LangChain, and JWT-based authentication.

---

## 🚀 Features

* JWT-based authentication (Access & Refresh Tokens)
* Each user's documents and vector embeddings are stored in a private directory
* LangChain + FAISS for RAG (Retrieval-Augmented Generation)
* Gemini fallback (Free-tier only)
* Streaming AI response via SSE
* Chat history saved in PostgreSQL

---

## 🛠️ Setup Instructions

### Prerequisites

* Python 3.8 or above
* PostgreSQL (running & configured)
* Ubuntu (Windows WSL is supported)

### 1. Clone the Repository

```bash
cd /path/to/your/folder
git clone https://github.com/YogeshKaushal003/Rag-Application.git
cd ragbot-app
```

### 2. Create Virtual Environment & Install Dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

If errors occur during package installation:

```bash
# Install missing ones manually, e.g.
pip install psycopg2-binary flask_sqlalchemy flask_bcrypt flask_jwt_extended faiss-cpu sentence-transformers langchain-community langchain-huggingface
```

### 3. Environment Variables

Create a `.env` file in the root directory:

```
SECRET_KEY=Yogesh-sharma7489*@123
JWT_SECRET_KEY=dhfniuwcn94879283HIJH78yHguew
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/ragchat

GEMINI_API_KEY=your api key
```

### 4. Initialize Database

```bash
# Access Python shell
flask shell

# Inside shell
from app.extensions import db
from app import create_app
app = create_app()
with app.app_context():
    db.create_all()
exit()
```

### 5. Start the App

```bash
python main.py
```

The app will run at: `http://127.0.0.1:5000`

---

## 🔐 Authentication

Use JWT for all protected endpoints.

### User Registration

```bash
curl -X POST http://127.0.0.1:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "yourpassword",
}'
```

### User Login

```bash
curl -X POST http://127.0.0.1:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "yourpassword"
}'
```

> Response contains `access_token` and `refresh_token`
`

---

## 💬 Chat API (RAG + Gemini)

### Send Chat Query

```bash
curl -N -X POST http://127.0.0.1:5000/api/chat/send \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_access_token>" \
  -d '{
    "query": "What is Python?"
}'
```

### upload document:
curl --location 'http://127.0.0.1:5000/api/chat/upload' \
--header 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc1MDUyNzI4NiwianRpIjoiZDk3NGMwNDAtNGY1Ni00ZDExLWE5YjYtZjdmYjdlYWViYWY5IiwidHlwZSI6ImFjY2VzcyIsInN1YiI6IjQzNjllYWEzLWU3NDMtNDY3OC1hNDEwLWI4NTk4NjBjNDNlNiIsIm5iZiI6MTc1MDUyNzI4NiwiY3NyZiI6IjY1YzcxMTgxLTBhZjAtNGI4MC05YTdmLTZlNjgyY2VkYmY2OSIsImV4cCI6MTc1MDUyOTA4Nn0.NqpGfuMykXEZSWQtXBm_bLuS1QwdqVHmbHmNqgfW5U0' \
--form 'files=@"/C:/Users/HP/Downloads/DCN sol.pdf"'

change files as we can upload multiple text and opdf files

> Response is streamed chunk by chunk using Server-Sent Events (SSE).

---

## 📂 Directory Structure

```
app/
├── auth/            # Authentication module
├── chat/            # Chat logic & vector management
├── models/          # Database models
├── config.py        # Config class (env loading)
├── __init__.py      # App factory
main.py              # Entry point
requirements.txt     # Dependencies
```

---

## 🧠 Notes

* FAISS indexes stored in `vectorstores/<user_id>/`
* Gemini API fallback is used only if no relevant FAISS document is retrieved
* Works well with small to medium document sets

---



## 📞 Contact

For any issues, contact the developer at: (mailto:yks162003@gmail.com)
