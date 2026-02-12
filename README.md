# Ultra Doc-Intelligence 🔳✨

**Audit-Grade Cognitive Logistics Extraction**

Ultra Doc-Intelligence is a high-precision, decoupled RAG (Retrieval-Augmented Generation) platform designed for complex logistics documents (Rate Confirmations, BOLs, Invoices). 

## � Key Features

- **🧠 Cognitive Intelligence Details**: Every answer includes a full transparency report:
    - **Schema Mappings**: Semantic alignment between your query and extracted document data.
    - **Confidence Breakdown**: Weighted scoring (Schema + Vector) to prevent hallucinations.
    - **Source Citations**: Direct links to document pages and sections.
- **⚡️ Ultra-Concise RAG**: AI responses optimized for brevity and professional relevance.
- **🔄 Decoupled Architecture**: Stateless FastAPI backend and Reactive Angular 19 frontend.

---

## 🏗 System Architecture

The platform uses a split-service architecture for scalability and performance.

- **Backend**: Python 3.10+, FastAPI, IBM Docling, FAISS, Groq (Llama 3.1/3.3).
- **Frontend**: Node 18+, Angular 19, RxJS State Management.

---

## 🚀 Production Setup

### 1. Requirements
Ensure you have **Docker** and **Docker Compose** installed.

### 2. Environment Configuration
Create a `.env` file in the `backend/` directory:
```env
GROQ_API_KEY=your_api_key_here
```

### 3. Deployment (Docker Compose)
From the project root, run:
```bash
docker-compose up --build
```
- **Frontend**: [http://localhost:4200](http://localhost:4200)
- **Backend API**: [http://localhost:8000](http://localhost:8000)

---

## 🛠 Manual Development Setup

### Backend (Port 8000)
```bash
cd backend
python -m venv venv
source venv/bin/activate # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend (Port 4200)
```bash
cd frontend
npm install
npx ng serve --host 0.0.0.0 --port 4200
```

---

## 📄 Documentation & Audit
- **[PRD.md](PRD.md)**: Product Requirements & Strategy
- **[TRD.md](TRD.md)**: Technical Architecture & Confidence Logic
- **[walkthrough.md](walkthrough.md)**: Feature demonstration & доказательство работы
