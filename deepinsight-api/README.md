# 🔬 DeepInsight Starter Suite

**AI-powered analytics backend platform** built with FastAPI, Supabase, pandas, scikit-learn, statsmodels, and Anthropic/OpenAI integration.

Upload datasets → Run automated analysis → Generate ML insights → Chat with your data using AI.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      FastAPI Application                     │
├──────────┬──────────┬──────────┬──────────┬────────────────┤
│ Datasets │ Analysis │   Chat   │ Reports  │  Auth (JWT)    │
│   API    │   API    │   API    │   API    │  Middleware     │
├──────────┴──────────┴──────────┴──────────┴────────────────┤
│                      Service Layer                           │
├──────────┬──────────┬──────────┬──────────┬────────────────┤
│ Dataset  │ Analysis │   Chat   │  Report  │  LLM Client    │
│ Service  │ Service  │ Service  │ Service  │ (Claude/GPT)   │
├──────────┴──────────┴──────────┴──────────┴────────────────┤
│                      Engine Layer                            │
├────────┬─────────┬────────┬──────────┬─────────┬──────────┤
│ Parser │ Quality │ Stats  │ Forecast │Clusterer│ Anomaly  │
│        │ Checker │Profiler│ (SARIMA) │(KMeans) │ Detector │
├────────┴─────────┴────────┴──────────┴─────────┴──────────┤
│                    Database Layer                            │
├─────────────────────┬───────────────────────────────────────┤
│  Supabase PostgreSQL│      Supabase Storage                 │
└─────────────────────┴───────────────────────────────────────┘
```

---

## 📁 Project Structure

```
deepinsight-api/
├── main.py                  # FastAPI app entry point
├── config.py                # Pydantic settings
├── requirements.txt         # Python dependencies
├── .env.example             # Environment template
├── Dockerfile               # Multi-stage Docker build
├── docker-compose.yml       # Docker Compose config
├── pytest.ini               # Test configuration
│
├── api/                     # API route handlers
│   ├── auth.py              # JWT authentication
│   ├── datasets.py          # Dataset upload & retrieval
│   ├── analysis.py          # Run & fetch analyses
│   ├── chat.py              # Chat sessions & messages
│   └── reports.py           # Report generation
│
├── services/                # Business logic layer
│   ├── dataset_service.py   # Upload pipeline orchestration
│   ├── analysis_service.py  # Analysis dispatch & caching
│   ├── chat_service.py      # Chat session management
│   ├── llm_client.py        # Anthropic/OpenAI integration
│   └── report_service.py    # JSON/HTML/PDF reports
│
├── engines/                 # Data processing engines
│   ├── file_parser.py       # CSV/XLSX/JSON parsing
│   ├── quality_checker.py   # Data quality scoring
│   ├── stats_profiler.py    # Descriptive stats & correlation
│   ├── chart_generator.py   # Plotly chart generation
│   ├── forecaster.py        # SARIMA time series forecasting
│   ├── clusterer.py         # KMeans clustering
│   ├── anomaly_detector.py  # IQR/Z-score anomaly detection
│   └── context_builder.py   # LLM context preparation
│
├── db/                      # Database layer
│   ├── client.py            # Supabase client initialization
│   ├── repository.py        # Data access operations
│   └── schema.sql           # Database schema & RLS policies
│
├── models/                  # Data models
│   └── schemas.py           # Pydantic v2 schemas
│
├── data/                    # Sample data
│   └── sample_sales.csv     # 100-row test dataset
│
└── tests/                   # Test suite
    ├── conftest.py           # Shared fixtures
    ├── test_quality_checker.py
    ├── test_file_parser.py
    ├── test_stats_profiler.py
    ├── test_chart_generator.py
    ├── test_forecaster.py
    ├── test_clusterer.py
    ├── test_anomaly_detector.py
    └── test_api.py
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Supabase account (free tier works)
- Anthropic or OpenAI API key (for chat features)

### 1. Clone & Setup

```bash
cd deepinsight-api
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your credentials
```

### 3. Setup Supabase Database

1. Go to your Supabase project → SQL Editor
2. Copy and run the contents of `db/schema.sql`
3. Create a storage bucket named `datasets` (Storage → New Bucket)

### 4. Start the Server

```bash
uvicorn main:app --reload --port 8000
```

### 5. Verify

- **Swagger Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

---

## 🐳 Docker

### Build & Run

```bash
docker-compose up --build
```

### Production Build

```bash
docker build -t deepinsight-api .
docker run -p 8000:8000 --env-file .env deepinsight-api
```

---

## 📡 API Endpoints

### Health
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| GET | `/health` | Detailed health |

### Datasets
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/datasets/upload` | Upload CSV/XLSX/JSON |
| GET | `/api/datasets/{id}` | Get dataset metadata |

### Analysis
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/analysis/run/{dataset_id}` | Run analysis |
| GET | `/api/analysis/{dataset_id}/{type}` | Get cached result |

**Analysis Types**: `quality`, `descriptive_stats`, `correlation`, `distribution`, `trend`, `anomaly`, `forecast`, `clustering`

### Chat
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/chat/sessions` | Create chat session |
| POST | `/api/chat/{session_id}/message` | Send message |
| GET | `/api/chat/{session_id}/history` | Get chat history |

### Reports
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/reports/generate` | Generate JSON/HTML/PDF report |

---

## 🔐 Authentication

All API endpoints (except health checks) require a Supabase JWT token:

```bash
curl -H "Authorization: Bearer YOUR_SUPABASE_JWT" \
     http://localhost:8000/api/datasets/upload \
     -F "file=@data/sample_sales.csv"
```

---

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_quality_checker.py

# Run only unit tests
pytest -m unit
```

---

## 📊 Analysis Capabilities

| Analysis | Engine | Description |
|----------|--------|-------------|
| **Quality** | `quality_checker.py` | Data completeness, duplicates, type consistency |
| **Descriptive Stats** | `stats_profiler.py` | Mean, median, std, quartiles, skewness, kurtosis |
| **Correlation** | `stats_profiler.py` | Correlation matrix with strong correlation detection |
| **Distribution** | `chart_generator.py` | Histograms for all numeric columns |
| **Trend** | `stats_profiler.py` | Rolling means, direction detection |
| **Anomaly** | `anomaly_detector.py` | IQR and Z-score outlier detection |
| **Forecast** | `forecaster.py` | SARIMA time series forecasting |
| **Clustering** | `clusterer.py` | KMeans with auto-K via silhouette score |

---

## 🔧 Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SUPABASE_URL` | Yes | — | Supabase project URL |
| `SUPABASE_ANON_KEY` | Yes | — | Supabase anon/public key |
| `SUPABASE_SERVICE_ROLE_KEY` | No | — | Service role key (admin) |
| `ANTHROPIC_API_KEY` | No* | — | Anthropic Claude API key |
| `OPENAI_API_KEY` | No* | — | OpenAI API key |
| `APP_ENV` | No | development | Environment name |
| `LOG_LEVEL` | No | INFO | Logging level |
| `CORS_ORIGINS` | No | * | Allowed CORS origins |
| `MAX_UPLOAD_SIZE_MB` | No | 50 | Max upload file size |

*At least one LLM API key required for chat features.

---

## 📄 License

MIT