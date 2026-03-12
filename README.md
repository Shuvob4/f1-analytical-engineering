# 🏎️ F1 Analytical Engineering Platform

> An end-to-end data engineering platform built on AWS, processing Formula 1 data
> from raw ingestion through to machine learning and live dashboards.

![Status](https://img.shields.io/badge/status-in%20progress-yellow)
![Python](https://img.shields.io/badge/python-3.10-blue)
![License](https://img.shields.io/badge/license-MIT-green)

---

## 📖 Overview

<!-- TODO: Fill in once project is complete -->
<!-- Describe in 3–4 sentences what this platform does, what problem it solves,
     and what a visitor to this repo will find. -->

_Coming soon._

---

## 🏗️ Architecture

The platform follows a **Medallion Architecture** (Bronze → Silver → Gold) on AWS S3,
using a **Stream-to-Batch** design pattern to handle both historical and near-real-time F1 data.

```
┌─────────────────────────────────────────────────────────────────┐
│                        DATA SOURCES                             │
│   FastF1 API (batch, historical 2018–2022)                      │
│   OpenF1 API (near-real-time, 2023+)                            │
└──────────────┬──────────────────────────┬───────────────────────┘
               │ Batch Pull               │ Streaming Events
               ▼                          ▼
┌──────────────────────┐      ┌────────────────────────┐
│   Airflow DAGs       │      │   Apache Kafka         │
│   (orchestration)    │      │   (message broker)     │
└──────────┬───────────┘      └────────────┬───────────┘
           │                               │
           ▼                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                    AWS S3 — DATA LAKE                           │
│  bronze/  → raw, immutable, as-received                         │
│  silver/  → cleaned, typed, validated                           │
│  gold/    → aggregated, ML-ready, dashboard-ready               │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
              ┌────────────────────────┐
              │   Apache Spark         │
              │   (batch + structured  │
              │    streaming)          │
              └────────────┬───────────┘
                           │
           ┌───────────────┴───────────────┐
           ▼                               ▼
┌──────────────────┐           ┌───────────────────────┐
│  AWS Athena      │           │  ML Model             │
│  (SQL on S3)     │           │  (race pace predict)  │
└──────────────────┘           └───────────────────────┘
           │                               │
           └───────────────┬───────────────┘
                           ▼
                ┌─────────────────────┐
                │  Dashboard          │
                │  (Streamlit)        │
                └─────────────────────┘
                           ▲
              ┌────────────────────────┐
              │   Terraform            │
              │   (IaC: S3, IAM, EC2,  │
              │    MSK, EMR)           │
              └────────────────────────┘
```

For detailed architectural decisions, see [`docs/architecture.md`](docs/architecture.md).

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Batch Ingestion** | [FastF1](https://theoehrly.github.io/Fast-F1/) | Historical F1 data (2018–2022) |
| **Streaming Ingestion** | [OpenF1 API](https://openf1.org/) + httpx | Near-real-time F1 telemetry |
| **Message Broker** | Apache Kafka | Streaming event bus |
| **Processing** | Apache Spark (PySpark) | Batch + structured streaming transforms |
| **Storage** | AWS S3 | Data lake (Bronze / Silver / Gold) |
| **Query Layer** | AWS Athena | SQL queries directly on S3 Parquet |
| **Orchestration** | Apache Airflow | DAG scheduling and monitoring |
| **Infrastructure** | Terraform | Infrastructure-as-code for all AWS resources |
| **Containerisation** | Docker + Docker Compose | Local dev environment for all services |
| **ML** | scikit-learn / XGBoost | Race pace prediction model |
| **Dashboard** | Streamlit | Interactive analytics and model serving |
| **Language** | Python 3.10 | Primary development language |

---

## 📁 Project Structure

```
f1-analytical-engineering/
│
├── ingestion/
│   ├── batch/                  # FastF1 extractor scripts
│   └── streaming/              # OpenF1 → Kafka producer + S3 consumer
│
├── processing/
│   ├── bronze_to_silver/       # Spark cleaning and typing jobs
│   └── silver_to_gold/         # Spark aggregation and business logic jobs
│
├── orchestration/
│   └── dags/                   # Airflow DAG definitions
│
├── infrastructure/
│   ├── terraform/              # All .tf resource definitions
│   └── docker/                 # Dockerfiles and docker-compose files
│
├── ml/
│   ├── features/               # Feature engineering scripts
│   └── models/                 # Model training and evaluation scripts
│
├── dashboard/                  # Streamlit application
│
├── notebooks/                  # Exploratory analysis (not production code)
│
├── tests/                      # Unit and integration tests
│
├── docs/
│   ├── architecture.md         # Architecture decisions and trade-offs
│   └── quiz/                   # Daily learning checkpoints
│
├── environment.yml             # Conda environment definition
├── .env.example                # Environment variable template
├── .gitignore
├── docker-compose.yml          # Local service orchestration
└── README.md
```

---

## 🚀 Quickstart

### Prerequisites

- [Miniconda](https://docs.conda.io/en/latest/miniconda.html) installed
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed
- [AWS CLI](https://aws.amazon.com/cli/) installed
- An AWS account (free tier is sufficient to start)
- Git

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/f1-analytical-engineering.git
cd f1-analytical-engineering
```

### 2. Set up the Python environment

```bash
conda env create -f environment.yml
conda activate f1-platform
```

### 3. Configure environment variables

```bash
cp .env.example .env
# Open .env and fill in your AWS credentials and configuration values
```

### 4. Configure AWS credentials

```bash
aws configure
# Enter your AWS Access Key ID, Secret, Region
```

### 5. Provision infrastructure

```bash
# Coming in Phase 5 — Terraform
cd infrastructure/terraform
terraform init
terraform plan
terraform apply
```

### 6. Start local services (Kafka + Airflow + Spark)

```bash
# Coming in Phase 3 — Docker Compose
docker-compose up -d
```

### 7. Run the batch ingestion pipeline

```bash
# Coming in Phase 2
python ingestion/batch/fastf1_extractor.py --season 2022
```

### 8. Launch the dashboard

```bash
# Coming in Phase 6
streamlit run dashboard/app.py
```

---

## 📅 Build Roadmap

| Phase | Days | Status | Description |
|---|---|---|---|
| 🏗️ Foundation | 1–3 | ✅ Complete | Repo scaffold, architecture, conda environment |
| 🪣 AWS + S3 Setup | 2–3 | 🔄 In Progress | AWS account, S3 buckets, IAM, CLI |
| 📥 Batch Ingestion | 4–7 | ⏳ Pending | FastF1 → S3 Bronze layer |
| ⚡ Spark Processing | 8–10 | ⏳ Pending | Bronze → Silver → Gold transforms |
| 🌊 Streaming | 11–14 | ⏳ Pending | Kafka + OpenF1 + Spark Structured Streaming |
| 🎼 Orchestration | 15–16 | ⏳ Pending | Airflow DAGs wiring everything together |
| 🏗️ IaC | 17 | ⏳ Pending | Terraform for all AWS resources |
| 🤖 ML + Dashboard | 18–19 | ⏳ Pending | Pace prediction model + Streamlit |
| 🎨 Polish | 20 | ⏳ Pending | Docs, diagrams, LinkedIn post |

---

## 📊 Data Sources

### FastF1 (Batch)
- **Coverage:** 2018–2022 seasons
- **Data available:** Lap times, sector times, tyre strategy, pit stops, car telemetry (speed, throttle, brake, DRS, gear), weather, race results
- **Access:** Python library — no API key required
- **Docs:** [https://theoehrly.github.io/Fast-F1/](https://theoehrly.github.io/Fast-F1/)

### OpenF1 (Streaming / Near-Real-Time)
- **Coverage:** 2023+ seasons (live and recent sessions)
- **Data available:** Car data, driver positions, intervals, pit stops, race control messages, team radio
- **Access:** Free REST API — no API key required
- **Docs:** [https://openf1.org/](https://openf1.org/)

---

## 🤖 ML Model

<!-- TODO: Fill in once model is trained -->
<!-- Describe: what the model predicts, features used, algorithm chosen, performance metrics -->

_Coming in Phase 6 (Day 18)._

---

## 📈 Dashboard

<!-- TODO: Add screenshot once dashboard is built -->
<!-- Describe: what the dashboard shows, how to interact with it -->

_Coming in Phase 6 (Day 19)._

---

## 🧠 Key Learnings

<!-- TODO: Fill in as you progress through the project -->
<!-- What were the hardest problems? What surprised you? What would you do differently? -->

_To be updated throughout the build._

---

## 🤝 Contributing

This is a personal portfolio project. Feel free to fork it and adapt it for your own learning.

---

## 📄 License

MIT — see [LICENSE](LICENSE) for details.