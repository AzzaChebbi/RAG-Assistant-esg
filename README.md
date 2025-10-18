# 🌱 ESG RAG Assistant

AI-powered ESG assistant using RAG (Retrieval Augmented Generation) with Gemini, FAISS, and LangChain. Query sustainability reports, analyze infographics, and get intelligent ESG insights with multilingual support (English, French, Arabic).

[![Live Demo](https://img.shields.io/badge/demo-live-brightgreen)](https://ac-hk-projet-streamlit-1021317796643.europe-west1.run.app)
[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)

## 🚀 Live Demo

**Try the application:** [https://ac-hk-projet-streamlit-1021317796643.europe-west1.run.app](https://ac-hk-projet-streamlit-1021317796643.europe-west1.run.app)

## 👥 Team

This project was developed in collaboration by:
- **Hiba Kabeda** - 


## 📋 Table of Contents

1. [Features](#-features)
2. [Architecture](#-architecture)
3. [Prerequisites](#-prerequisites)
4. [Installation](#-installation)
5. [Project Structure](#-project-structure)
6. [Usage](#-usage)
7. [API Endpoints](#-api-endpoints)
8. [Evaluation & Metrics](#-evaluation--metrics)
9. [Configuration](#-configuration)
10. [Screenshots](#-screenshots)
11. [Contributing](#-contributing)
12. [License](#-license)

## ✨ Features

- 🤖 **RAG-based Chatbot**: Query ESG documents with context-aware responses
- 🖼️ **Image Analysis**: Analyze ESG infographics and sustainability reports using Gemini Vision
- 🌍 **Multilingual Support**: English, French, and Arabic interfaces
- 📊 **Feedback System**: Collect user feedback with interactive dashboard
- 🔍 **Semantic Search**: FAISS vector store for efficient document retrieval
- 📈 **Similarity Scores**: Visual representation of document relevance
- 🔄 **Real-time Vector Store Refresh**: Update knowledge base on-the-fly
- 🎯 **Source Attribution**: Track and display source documents for answers

## 🏗️ Architecture

```
┌─────────────────┐
│   Streamlit UI  │ (app.py)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   FastAPI API   │ (api.py)
└────────┬────────┘
         │
         ├──────────────┐
         ▼              ▼
┌──────────────┐  ┌──────────────┐
│  Vector.py   │  │ Google Cloud │
│ (RAG Logic)  │  │  SQL (Docs)  │
└──────┬───────┘  └──────────────┘
       │
       ├─────────────┬─────────────┐
       ▼             ▼             ▼
┌───────────┐  ┌─────────┐  ┌──────────┐
│  Gemini   │  │  FAISS  │  │  Pandas  │
│    API    │  │ Vector  │  │(Feedback)│
└───────────┘  └─────────┘  └──────────┘
```

## 🔧 Prerequisites

- Python 3.9+
- Google Cloud account with:
  - Cloud SQL (PostgreSQL)
  - Vertex AI API enabled
- Gemini API key
- Virtual environment tool (venv or virtualenv)

## 📦 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/AzzaChebbi/RAG-Assistant-esg.git
cd esg-rag-assistant
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a config.py file in the root directory:

```env
# Google Cloud Configuration
PROJECT_ID=your-project-id
REGION=your-region
INSTANCE=your-instance-name
DATABASE=your-database-name
DB_USER=your-db-user
TABLE_NAME=your-table-name

Create a .env file in the root directory
DB_PASSWORD=your-db-password
# Gemini API
GEMINI_API_KEY=your-gemini-api-key

# API Configuration (optional)
PORT=8000
```

### 5. Set Up Cloud SQL Database

Run the notebook to create and populate your database:

Follow the steps in the notebook to:
- Create the PostgreSQL table
- Upload ESG documents
- Initialize vector embeddings

### 6. Authenticate with Google Cloud

```bash
gcloud auth login
gcloud auth application-default login
```

## 📁 Project Structure

```
esg-rag-assistant/
├── api.py                      # FastAPI backend endpoints
├── app.py                      # Streamlit frontend application
├── vector.py                   # RAG logic and vector operations
├── config.py                   # Configuration management
├── eval.py                     # Evaluation metrics (BLEU, ROUGE)
├── notebook_cloud_sql.ipynb    # Database setup notebook
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (not in repo)
├── feedback.csv                # User feedback storage
├── faiss_index/               # FAISS vector store (generated)
├── uploads/                    # Temporary image uploads
└── README.md                   # This file
```

## 🚀 Usage

### Running the Application Locally

#### 1. Start the FastAPI Backend

```bash
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`

View API documentation at `http://localhost:8000/docs`

#### 2. Launch the Streamlit Frontend

In a new terminal:

```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

### Using the Application

#### Text Chat Tab
1. Select your preferred language (English/Français/Arabic)
2. Enter your ESG-related query
3. View AI-generated responses with source attribution
4. Click "Show sources" to see relevant document excerpts
5. Click "Show similar documents" for semantic search results

#### Image Analysis Tab
1. Upload an ESG infographic or sustainability report image
2. Click "Analyze Image"
3. View AI-generated insights and recommendations

#### Feedback Tab
1. Enter your question and the model's answer
2. Rate the response (1-5 stars)
3. Add optional comments
4. Submit feedback

#### Dashboard Tab
- View feedback statistics
- See rating distributions
- Analyze user sentiment

## 🔌 API Endpoints

### System Endpoints

- **GET** `/health` - Health check and vector store status
- **POST** `/refresh` - Refresh vector store from database

### RAG Endpoints

- **POST** `/query` - Generate RAG response with sources
  ```json
  {
    "text": "What is ESG investing?",
    "top_k": 3,
    "model": "gemini-pro",
    "language": "English"
  }
  ```

- **POST** `/similar-documents` - Retrieve similar documents
  ```json
  {
    "text": "carbon emissions",
    "top_k": 5
  }
  ```

### Vision Endpoints

- **POST** `/analyze-image` - Analyze ESG infographic
  - Upload file as multipart/form-data

### Feedback Endpoints

- **POST** `/submit-feedback` - Submit user feedback
  ```json
  {
    "question": "What is sustainability?",
    "model_answer": "Sustainability is...",
    "rating": 5,
    "comments": "Very helpful!"
  }
  ```

## 📊 Evaluation & Metrics

Run the evaluation script to test chatbot performance:

```bash
python eval.py
```

Metrics calculated:
- **BLEU Score**: Measures n-gram overlap with reference answers
- **ROUGE Score**: Evaluates recall-oriented metrics
- **Response Time**: Average latency per query
- **Retrieval Accuracy**: Percentage of relevant documents retrieved

Results are saved to `evaluation_results.json`

## ⚙️ Configuration

### Vector Store Configuration

Edit `vector.py` to customize:
- Embedding model: `textembedding-gecko@latest`
- Vector dimensions: `768`
- Similarity metric: `L2 distance`

### Language Model Configuration

Edit `api.py` to customize:
- Default model: `gemini-pro`
- Temperature: `0.2`
- Max tokens: Configure in API calls

### Feedback Storage

Feedback is stored in `feedback.csv` with columns:
- Timestamp
- Question
- Model Answer
- Rating
- Comments

## 📸 Screenshots

### Chat Interface
![ESG Chat Interface](https://github.com/user-attachments/assets/5244df60-cf9c-43da-8f8e-3f12ec726ea6)

### Image Analysis
![ESG Image Analysis](https://github.com/user-attachments/assets/db6d217e-1e0a-4e95-8dc4-b7d636a0e962)

### Feedback Dashboard
![ESG Feedback Dashboard](https://github.com/user-attachments/assets/f5ca17f8-d92e-46f4-b676-2375ec3c03ae)

## 🛠️ Development

### Code Quality

We use Flake8 for code linting:

```bash
flake8 .
```

### Testing

Run unit tests:

```bash
pytest tests/
```

---

**Made by Azza & Hiba | Powered by Gemini, FAISS, and LangChain**
