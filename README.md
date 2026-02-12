# Ultra Doc-Intelligence

Ultra Doc-Intelligence is a high-precision, layout-aware RAG platform tailored for complex logistics audit and extraction. It uses **Deterministic Confidence Scoring** and **Semantic Chunking** to provide verifiable, audit-grade answers from PDFs, DOCX, and HTML documents.

---

## 🚀 Quick Start

### 1. Prerequisites
- **Python 3.10+**
- **Groq API Key** (Get it at [console.groq.com](https://console.groq.com/))
- **Git**

### 2. Installation

Clone the repository:
```bash
git clone <your-repo-url>
cd ultraship
```

Create a virtual environment and install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Environment Configuration
Create a `.env` file in the root directory:
```env
GROQ_API_KEY=your_groq_api_key_here
```

### 4. Running the Development Server
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
The application will be available at `http://localhost:8000`.

---

## 🛠 Features

- **Ingestion**: Powered by IBM Docling for layout-aware parsing.
- **RAG Engine**: Llama 3.1 8B via Groq for high-density, low-fluff answers.
- **Extraction**: Llama 3.3 70B for automated schema proposal and structured data extraction.
- **Internal Intelligence**:
    - **Semantic Chunking**: Hierarchical heading context prepending.
    - **Weighted Confidence**: 50/50 mix of Contextual (Schema) and Semantic (Vector) mappings.
    - **Hard Refusal**: Automatic denial if confidence score < 0.45.
- **Premium UI**: Dark-mode glassmorphism with interactive "Intelligence Toggles."

---

## 🐳 Deployment (Docker)

To deploy using Docker:

1. **Build the image**:
```bash
docker build -t ultra-doc-intel .
```

2. **Run the container**:
```bash
docker run -p 8000:8000 --env-file .env ultra-doc-intel
```

---

## 📄 Documentation
- **[PRD.md](PRD.md)**: Product Requirements & Vision.
- **[TRD.md](TRD.md)**: Technical Architecture, Chunking Strategy, and Scoring Logic.

---

## ⚖️ License
MIT License.
# ContextbasedRAG
