# 📋 Progress Report — Day 1
**F1 Analytical Engineering Platform**
*Date: Day 1 of 20-Day Bootcamp*
*Branch: `phase/02-aws-setup` (merged to `main` via PR)*

---

## ✅ What We Achieved

### 1. Project Scaffold
- Initialised the GitHub repository with the full folder structure
- Created all core directories with `.gitkeep` placeholders:
  `ingestion/batch`, `ingestion/streaming`, `processing/bronze_to_silver`,
  `processing/silver_to_gold`, `orchestration/dags`, `infrastructure/terraform`,
  `infrastructure/docker`, `ml/features`, `ml/models`, `dashboard`,
  `notebooks`, `tests`, `docs`

### 2. Environment Setup
- Chose **conda** over pip/venv as the environment manager
- Created `environment.yml` pinned to **Python 3.10** with all project
  dependencies across conda-forge and pip channels
- Key packages confirmed working: `fastf1`, `pyspark`, `boto3`, `pandas`, `pyarrow`
- Registered the `f1-platform` conda environment as a Jupyter kernel
- **Resolved:** `openf1` does not exist as a pip package — replaced with
  `httpx` for direct REST API calls to the OpenF1 API

### 3. Project Configuration Files
- `.gitignore` — covers Python, conda, Jupyter, Terraform state, secrets, OS files
- `.env.example` — template for AWS credentials, S3 bucket names, Kafka config
- `environment.yml` — reproducible conda environment definition (committed to Git)
- `docker-compose.yml` — stub only; will grow each phase

### 4. Documentation
- `README.md` — full project README including architecture ASCII diagram,
  tech stack table, folder structure, stubbed quickstart, and phase progress tracker
- `docs/architecture.md` — 12 Architecture Decision Records (ADRs) covering
  every major technology choice, each with decision, reasoning, alternatives
  considered, and a blank `Notes / Learnings` section for progressive updates

### 5. Git Workflow Established
- Confirmed **GitHub Flow** as the branching strategy
- Naming convention agreed: `phase/XX-description`, `fix/`, `chore/`, `docs/`
- Conventional commit prefixes in use: `feat:`, `fix:`, `chore:`, `docs:`,
  `refactor:`, `test:`
- Branch protection discussion completed — PR-before-merge habit established
- First PR merged: `phase/02-aws-setup` → `main`

---

## 🏛️ Key Architectural Decisions Made

| ADR | Decision | Rationale |
|-----|----------|-----------|
| ADR-001 | AWS S3 as data lake | Separation of compute/storage, unlimited scale, native AWS integration |
| ADR-002 | Medallion Architecture (Bronze/Silver/Gold) | Immutable raw layer, clean reprocessing path, industry standard |
| ADR-003 | Apache Parquet as file format | Columnar, compressed, embedded schema, native Spark support |
| ADR-004 | Apache Spark for processing | Unified batch + streaming engine, scales from local to EMR |
| ADR-005 | Stream-to-Batch pattern | Avoids dual codebases of Lambda; simpler than pure Kappa |
| ADR-006 | Apache Kafka as message broker | Decoupled, replayable log, production path to AWS MSK |
| ADR-007 | Apache Airflow for orchestration | DAG-based dependencies, Python-native, industry standard |
| ADR-008 | Terraform for IaC | Reproducible, version-controlled infrastructure |
| ADR-009 | Docker + Docker Compose | Isolated services, eliminates "works on my machine" |
| ADR-010 | AWS Athena as query layer | Serverless SQL on S3, feeds Streamlit dashboard |
| ADR-011 | scikit-learn + XGBoost for ML | Baseline + gradient boosting for race pace prediction |
| ADR-012 | Streamlit for dashboard | Pure Python, fast to build, supports ML serving |

---

## 📚 Concepts Understood

All Day 1 quiz questions answered at a senior level:

- ✅ Medallion Architecture with concrete F1 examples per layer
- ✅ Why secrets belong in `.env` and the risks of committing them
- ✅ Docker's value beyond Python installs — distributed system simulation
- ✅ Correct folder mapping for streaming consumer and Spark Silver jobs
- ✅ Parquet as the correct S3 format for Spark (columnar, compression, schema, native support)
- ✅ Why Python is pinned to `3.10` in `environment.yml`
- ✅ PyArrow's role as the columnar bridge between Pandas, Spark, and Parquet
- ✅ Why `fastf1` is pip-installed inside conda (not available on conda channels)

---

## 📁 Current Repo State

```
f1-analytical-engineering/
├── ingestion/
│   ├── batch/.gitkeep
│   └── streaming/.gitkeep
├── processing/
│   ├── bronze_to_silver/.gitkeep
│   └── silver_to_gold/.gitkeep
├── orchestration/
│   └── dags/.gitkeep
├── infrastructure/
│   ├── terraform/.gitkeep
│   └── docker/.gitkeep
├── ml/
│   ├── features/.gitkeep
│   └── models/.gitkeep
├── dashboard/.gitkeep
├── notebooks/.gitkeep
├── tests/.gitkeep
├── docs/
│   └── architecture.md         ✅ 12 ADRs, learnings sections blank
├── environment.yml              ✅ conda, Python 3.10, all deps
├── .env.example                 ✅ AWS, S3, Kafka placeholders
├── .gitignore                   ✅ secrets, conda, Terraform, OS
├── docker-compose.yml           ✅ stub only
└── README.md                    ✅ full documentation
```

**Git log (main):**
```
docs: add project README and architecture decision records
feat: initial project scaffold and architecture docs
```

---

## ⏳ Incomplete / Deferred Items

| Item | Reason Deferred | Planned For |
|------|----------------|-------------|
| AWS account creation | Day 2 scope | Day 2 |
| S3 bucket provisioning (bronze/silver/gold) | Day 2 scope | Day 2 |
| IAM user + CLI configuration | Day 2 scope | Day 2 |
| `docker-compose.yml` real services | Added phase by phase | Days 8, 11, 15 |
| ADR `Notes / Learnings` sections | Filled progressively as built | End of each phase |
| Branch protection rules on GitHub | Optional for solo; habit established | Ongoing |

---

# 📊 Day 2 Progress Report
**F1 Analytical Engineering Platform**
**Date:** Day 2 of 20 | **Phase:** Foundation

---

## ✅ What We Achieved

### Infrastructure
- AWS Free Tier account secured with MFA on root account
- Zero-spend budget alert configured to prevent surprise charges
- IAM user `f1-pipeline-user` created with `AmazonS3FullAccess` policy
- Root account access keys audited and cleaned up
- AWS CLI v2 installed on macOS and configured with IAM credentials

### S3 Data Lake
- 3 S3 buckets provisioned in `us-east-1`
- Public access fully blocked on all three buckets
- Hive-style folder structure created across all layers

### Documentation & Repo
- `infra/s3/README.md` created documenting all infrastructure decisions
- `.env.example` committed as a safe credentials template
- `.env` confirmed excluded from Git via `.gitignore`
- Branch `phase/02-aws-setup` merged to `main` via PR

---

## 🏗️ Architecture Decisions Made

| Decision | Choice | Reason |
|---|---|---|
| Storage layer | AWS S3 | Industry gold standard for data lakes |
| Architecture pattern | Medallion (Bronze/Silver/Gold) | Clean separation of raw, clean, and business data |
| Bucket strategy | 3 separate buckets | Independent access control, cost visibility, lifecycle policies |
| Region | `us-east-1` | Most feature-complete and cost-effective AWS region |
| Partitioning | Hive-style `year=/round=/session=` | Enables partition pruning in Spark and Athena |
| Credentials | `.env` without quotes | Prevents literal quote characters breaking boto3 and Docker |
| IAM strategy | Dedicated pipeline user, not root | Principle of least privilege |

---

## 📁 Current Repo State

```
f1-analytical-engineering/
├── .env                          ✅ credentials (not committed)
├── .env.example                  ✅ safe template (committed)
├── .gitignore                    ✅ .env excluded
├── README.md                     ✅ data lake section added
└── infra/
    └── s3/
        └── README.md             ✅ bucket docs + partitioning convention
```

---

## ☁️ Current AWS State

```
IAM
└── f1-pipeline-user              ✅ programmatic access, AmazonS3FullAccess

S3 (us-east-1)
├── XX-f1-bronze-2024
│   ├── fastf1/laps/
│   ├── fastf1/telemetry/
│   ├── fastf1/results/
│   ├── openf1/positions/
│   └── openf1/intervals/
├── XX-f1-silver-2024
│   ├── laps/
│   ├── telemetry/
│   └── results/
└── XX-f1-gold-2024
    ├── race_pace/
    ├── pit_analysis/
    └── driver_performance/
```

---

## ⚠️ Incomplete / Deferred Items

| Item | Status | When |
|---|---|---|
| `infra/s3/test_connection.py` | Skeleton only — not implemented | Day 4 when boto3 is introduced |
| IAM policy tightening | Currently `AmazonS3FullAccess` — too broad | Day 17 Terraform phase |
| S3 lifecycle policies | Not configured — old data won't auto-archive | Day 17 Terraform phase |
| Bucket versioning | Not enabled | Day 17 Terraform phase |

---

## 🧠 Key Mental Models Locked In

- **Bronze is sacred** — raw data is never overwritten after landing
- **Design S3 keys like SQL indexes** — partition structure drives query performance
- **Least privilege IAM** — every identity gets only what it needs
- **Document as you build** — if it's not in the repo, it doesn't exist
- **No quotes in `.env`** — values are literal strings, not shell assignments

---

# 📋 Progress Report — Day 3
**F1 Analytical Engineering Platform**
**Date:** Day 3 of 20 | **Phase:** Foundation
**Branch:** `feature/day-3-openf1-exploration` → merged to `main` via PR

---

## ✅ What We Achieved

### 1. Git Housekeeping
- Renamed branch `feature/day-3-fastf1-exploration` → `feature/day-3-openf1-exploration`
- Deleted stale local and remote branch `phase/03-fastf1-exploration`
- Pruned remote-tracking refs with `git fetch --prune`
- PR opened and merged cleanly into `main`

### 2. OpenF1 API — Source System Analysis
Profiled 4 core endpoints against the 2023 Bahrain Grand Prix Race session (`session_key: 7953`, `meeting_key: 1141`):

| Endpoint | Rows | Columns | Nulls | Key Finding |
|---|---|---|---|---|
| `/sessions` | 118 (full 2023 season) | 14 | 0 | Driving table — use `meeting_key` not `round_number` |
| `/laps` | 1,058 | 16 | i1_speed 24%, sector times small | `is_pit_out_lap` is clean boolean — foundational for pit analysis |
| `/position` | 666 | 5 | 0 | Position changes only — not fixed-frequency time series |
| `/intervals` | 27,797 | 6 | interval (leader), gap_to_leader (mixed) | Highest volume endpoint — design ingestion with chunking |

### 3. Critical Data Quality Findings
- **Sprint race trap:** `session_type == "Race"` includes both Sprint and full Grand Prix sessions. Correct filter: `session_type == "Race" AND session_name == "Race"`
- **Cancelled race in API:** 2023 Imola GP (cancelled due to flooding) exists as a valid session record in OpenF1. Mitigation: validate lap count > 0 before promoting session to Silver layer
- **Timestamp inconsistency:** `/sessions` and `/laps` return dates as strings; `/position` and `/intervals` return proper `datetime64[ns, UTC]`. Silver layer must handle each endpoint individually
- **`gap_to_leader` mixed types:** Returns both float `0.0` and `None` — requires `pd.to_numeric(errors='coerce')` in Silver
- **`segments_sector_1/2/3`:** Nested integer arrays (mini-sector colour codes). Store raw in Bronze, deprioritise processing until specific use case demands unpacking

### 4. FastF1 — Source System Analysis
Profiled FastF1 `session.laps` against the same 2023 Bahrain Grand Prix Race session for direct comparison:

| Dimension | OpenF1 `/laps` | FastF1 `session.laps` |
|---|---|---|
| Row count | 1,058 | 1,056 |
| Column count | 16 | 31 |
| Tyre compound | ❌ | ✅ `Compound`, `TyreLife`, `FreshTyre` |
| Deleted laps | ❌ | ✅ `Deleted`, `DeletedReason` |
| Accuracy flag | ❌ | ✅ `IsAccurate`, `FastF1Generated` |
| Pit detection | `is_pit_out_lap` bool | `PitOutTime` / `PitInTime` (timedelta) |
| Timestamp type | string (object) | timedelta64 + datetime64 mixed |

**Verdict:** FastF1 has a significantly richer schema for ML feature engineering. Row counts are equivalent — the difference is in metadata quality, not volume.

### 5. Documentation Skill Development
- Learned the 3-layer documentation reading strategy: Quickstart → Ctrl+F search → Source code
- Applied it live to resolve `session.load()` parameters and `session.laps` attribute access
- Core principle locked in: **never read documentation linearly — always search**

---

## 🏛️ Key Architectural Decisions Made

| Decision | Choice | Rationale |
|---|---|---|
| Batch data source | **FastF1 only (2010–2025+)** | Richer schema, tyre data, accuracy flags — superior for ML feature engineering |
| Streaming data source | **OpenF1 only (live sessions)** | FastF1 has no live data capability; OpenF1 REST API is streaming-compatible |
| Bronze landing strategy | **Raw shape preserved per source** | Bronze is immutable — schema harmonisation belongs in Silver, not at landing |
| API navigation pattern | `meeting_key` as primary scope filter | `round_number` does not exist as an OpenF1 filter parameter |
| Deferred endpoints | `/car_data`, `/location`, `/team_radio` | Too high volume or no current use case — revisit post Day 20 |
| Endpoints for later | `/stints`, `/weather`, `/race_control`, `/drivers` | High value but Silver/Gold enrichment concerns, not Bronze ingestion |

---

## 🤖 ML Strategy Agreed

**Primary model:** Two-stage pipeline combining:

1. **Tyre Degradation & Lap Time Prediction** (XGBoost Regression)
   - Predict next lap time given compound, tyre life, track position, fuel estimate
   - Features: `Compound`, `TyreLife`, `LapNumber`, `TrackStatus`, driver pace baseline

2. **Pit Stop Strategy Classifier** (XGBoost / LightGBM Binary Classifier)
   - Predict whether a driver will pit in the next 3 laps given current race state
   - Uses Stage 1 predictions as input features — two-stage ML pipeline

---

## 📊 Dashboard Strategy Agreed

| Layer | Tool | Purpose |
|---|---|---|
| Technical / ML serving | **Streamlit** (Days 18–19) | Python-native, connects directly to S3/Athena Gold layer, ML model serving |
| Business analytics | **Tableau Public** | Industry-standard, Mac-native desktop app, shareable public dashboards |

Power BI excluded — no native Mac desktop application.

---

## 📁 Current Repo State

```
f1-analytical-engineering/
├── notebooks/
│   ├── openf1_exploration.ipynb     ✅ Full API profiling — 4 endpoints
│   └── fastf1_cache/                ✅ FastF1 local cache (gitignored)
├── ingestion/
│   ├── batch/
│   │   ├── __init__.py              ✅ (scaffolded Day 3 branch)
│   │   ├── config.py                ✅ extraction manifest
│   │   └── utils.py                 ✅ logging helpers, partition path builder
│   └── streaming/.gitkeep
├── docs/
│   └── architecture.md              ✅ 12 ADRs (learnings sections to fill)
├── infra/s3/README.md               ✅ bucket docs
├── environment.yml                  ✅ fastf1 confirmed working
├── .env                             ✅ credentials (not committed)
└── README.md                        ✅ full documentation
```

**Git log (main after Day 3 PR merge):**
```
docs: add fastf1 exploration and schema comparison for silver harmonisation
docs: complete openf1 api exploration and data profiling for day 3
chore: scaffold openf1 exploration notebook for day 3
```

---

## ⚠️ Incomplete / Deferred Items

| Item | Reason Deferred | Planned For |
|---|---|---|
| OpenF1 deferred endpoints (`/stints`, `/weather`, `/race_control`, `/drivers`) | Not needed for Bronze ingestion | Day 9 Silver enrichment |
| FastF1 full historical profile (2010–2022) | Day 3 scoped to 2023 for comparison | Day 4 extractor build will surface further issues |
| Silver harmonisation schema (FastF1 timedelta → float seconds) | Silver layer concern, not Bronze | Day 9 |
| Tableau dashboard setup | Serving layer concern | Day 19 |
| `infra/s3/test_connection.py` | Skeleton only | Day 4 when boto3 is introduced |
| ADR `Notes / Learnings` sections | Filled progressively | End of each phase |
| `fastf1/` S3 paths cleanup in bucket docs | Cosmetic — no functional impact | Day 4 chore commit |

---

## 🧠 Key Mental Models Locked In

- **Source system analysis before pipeline code** — understand the data before building ingestion
- **Bronze is sacred** — raw data lands as-is; harmonisation belongs in Silver
- **The driving table pattern** — fetch `/sessions` first; use `session_key` to scope all downstream queries
- **Structurally expected nulls vs data quality failures** — race leader `interval` null is correct, not broken
- **Never read documentation linearly** — Quickstart → Ctrl+F search → Source code
- **Build for your use case** — ingest only what your deliverables demand; defer the rest

---

## 🔭 Next Up — Day 4

**Branch:** `feature/day-4-batch-extractor`
**Goal:** Build the FastF1 batch extractor — Python class that pulls session lap data and lands it as Parquet in S3 Bronze under `fastf1/laps/year=/round=/session=/`
**Key concepts:** Extraction patterns, Parquet serialisation, partitioned S3 key design, boto3 upload, idempotent writes

---
