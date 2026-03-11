# 🏗️ Architecture Decisions

> This document records every significant architectural choice made during the build,
> the reasoning behind it, and the alternatives that were considered.
> Updated progressively as each phase is completed.

---

## Table of Contents

- [System Overview](#system-overview)
- [ADR-001: Data Lake Storage — AWS S3](#adr-001-data-lake-storage--aws-s3)
- [ADR-002: Medallion Architecture — Bronze / Silver / Gold](#adr-002-medallion-architecture--bronze--silver--gold)
- [ADR-003: File Format — Apache Parquet](#adr-003-file-format--apache-parquet)
- [ADR-004: Processing Engine — Apache Spark](#adr-004-processing-engine--apache-spark)
- [ADR-005: Streaming Architecture — Stream-to-Batch](#adr-005-streaming-architecture--stream-to-batch)
- [ADR-006: Message Broker — Apache Kafka](#adr-006-message-broker--apache-kafka)
- [ADR-007: Orchestration — Apache Airflow](#adr-007-orchestration--apache-airflow)
- [ADR-008: Infrastructure-as-Code — Terraform](#adr-008-infrastructure-as-code--terraform)
- [ADR-009: Containerisation — Docker](#adr-009-containerisation--docker)
- [ADR-010: Query Layer — AWS Athena](#adr-010-query-layer--aws-athena)
- [ADR-011: ML Framework](#adr-011-ml-framework)
- [ADR-012: Dashboard — Streamlit](#adr-012-dashboard--streamlit)
- [Open Questions](#open-questions)
- [Rejected Alternatives](#rejected-alternatives)

---

## System Overview

<!-- TODO: Write a concise paragraph describing the full data flow,
     from raw source to serving layer, once the full system is built. -->

_To be completed at end of Day 20._

### Data Flow Summary

```
FastF1 (batch)          →  Airflow DAG  →  S3 Bronze  →  Spark  →  S3 Silver  →  Spark  →  S3 Gold
OpenF1 (streaming)      →  Kafka Topic  →  Spark Structured Streaming  →  S3 Bronze (streaming)
S3 Gold                 →  Athena SQL   →  Streamlit Dashboard
S3 Gold                 →  ML Model     →  Streamlit Dashboard
```

---

## ADR-001: Data Lake Storage — AWS S3

**Status:** ✅ Decided — Day 2

**Decision:** Use AWS S3 as the primary storage layer for the data lake.

**Reasoning:**

Object storage is now the gold standard for data lakes. S3 provides:
- Virtually limitless and cheap storage (separation of compute from storage)
- Native integration with Spark, Athena, and every major AWS service
- High durability (99.999999999%) with no infrastructure to manage
- Bucket + key-based access that maps cleanly to a partitioned folder structure

**Alternatives Considered:**

| Alternative | Why Rejected |
|---|---|
| HDFS (on-premise) | Requires cluster management, expensive, no cloud separation of compute/storage |
| AWS RDS / Postgres | Row-oriented, not suited for analytical workloads at scale |
| Snowflake | Excellent warehouse but adds cost and vendor lock-in; overkill for solo project |

**S3 Folder / Partition Design:**

```
s3://f1-data-bronze/
  └── fastf1/
        └── year=2022/
              └── round=01/
                    └── session=Race/
                          └── laps.parquet

s3://f1-data-silver/
  └── laps/
        └── year=2022/
              └── round=01/
                    └── laps_clean.parquet

s3://f1-data-gold/
  └── driver_pace_summary/
        └── year=2022/
              └── pace_summary.parquet
```

**Notes / Learnings:**

<!-- TODO: Fill in after Day 2 — any surprises with S3 setup, IAM permissions, naming constraints -->

---

## ADR-002: Medallion Architecture — Bronze / Silver / Gold

**Status:** ✅ Decided — Day 1

**Decision:** Organise the data lake into three layers: Bronze, Silver, and Gold.

**Layer Definitions:**

| Layer | Contents | Mutability | Format |
|---|---|---|---|
| **Bronze** | Raw data, exactly as received from source | Immutable — never modified | Original format (JSON, CSV) or Parquet |
| **Silver** | Cleaned, typed, deduplicated, validated | Replaced by reprocessing from Bronze | Parquet, partitioned |
| **Gold** | Aggregated, business-logic applied, ML-ready | Rebuilt on schedule or on demand | Parquet, partitioned |

**Why immutable Bronze matters:**

If a Silver or Gold job has a bug, we can always reprocess from Bronze. Bronze is the source of truth.
This maps directly to the "immutable, append-only source system" principle from *Fundamentals of Data Engineering*.

**Notes / Learnings:**

<!-- TODO: Fill in after you encounter your first reprocessing scenario -->

---

## ADR-003: File Format — Apache Parquet

**Status:** ✅ Decided — Day 1

**Decision:** Store all processed data (Silver and Gold layers) in Apache Parquet format.

**Reasoning:**

- **Columnar storage:** Spark reads only the columns a query needs — drastically reduces data scanned from S3
- **Compression:** Same-type column data compresses far better than mixed row data (Snappy or Gzip)
- **Embedded schema:** Column names and types stored in the file — no external schema registry needed for basic use
- **Native Spark support:** Parquet is Spark's default format; the optimizer leverages Parquet statistics to skip partitions
- **PyArrow bridge:** PyArrow provides the read/write layer between Pandas, Spark, and Parquet files

**Bronze layer exception:**

Raw Bronze data may land as JSON (from OpenF1 streaming) or as Parquet written directly (from FastF1).
The rule: Bronze stores data in the most faithful representation of the source.

**Alternatives Considered:**

| Alternative | Trade-off |
|---|---|
| CSV | No schema, slow, large files — rejected outright for Silver/Gold |
| JSON | Flexible but row-oriented and verbose — only acceptable in Bronze |
| ORC | Also columnar, excellent in Hive ecosystem, but Parquet has wider Spark + Python support |
| Delta Lake | ACID transactions and versioning — excellent choice; may upgrade to this in a future iteration |
| Apache Iceberg | Similar to Delta Lake; growing fast — worth exploring in Project 2 |

**Notes / Learnings:**

<!-- TODO: Fill in after first Spark job — note any Parquet gotchas encountered -->

---

## ADR-004: Processing Engine — Apache Spark

**Status:** ✅ Decided — Day 1

**Decision:** Use Apache Spark (PySpark) for all data transformations, both batch and streaming.

**Reasoning:**

- Unified engine for batch AND streaming (Structured Streaming) — one codebase, two modes
- Native S3 read/write, native Parquet support
- Scales from local mode (single machine) to EMR cluster (hundreds of nodes) with no code changes
- The DAG-based execution model means Spark only reads what it needs and optimises automatically
- Industry standard for large-scale data processing — high value for portfolio

**Deployment progression:**

```
Day 8–10:  Spark in local mode (inside Docker)
Day 13–14: Spark Structured Streaming (inside Docker)
Day 17:    Terraform EMR stub (production-like cluster definition)
```

**Alternatives Considered:**

| Alternative | Why Not Used |
|---|---|
| Pandas only | Single-machine, memory-bound — does not scale or demonstrate DE skills |
| AWS Glue | Fully managed Spark — excellent for production, but hides the learning; use in Project 2 |
| Dask | Python-native, easier than Spark but less industry-prevalent for DE |
| dbt | Transformation tool, not a processing engine — may use alongside Spark in Gold layer |

**Notes / Learnings:**

<!-- TODO: Fill in after Day 8 — note Spark local mode setup, any Docker configuration issues -->

---

## ADR-005: Streaming Architecture — Stream-to-Batch

**Status:** ✅ Decided — Day 1

**Decision:** Use a **Stream-to-Batch** pattern, not Lambda or Kappa architecture.

**What this means:**

```
OpenF1 API → Kafka → Spark Structured Streaming → S3 Bronze (streaming partition)
                                                        ↓
                                                   (same Spark Silver/Gold jobs
                                                    pick this up in micro-batch)
```

**Why not Lambda Architecture:**

Lambda requires maintaining *two separate codebases* — one for batch, one for streaming — and reconciling them in a serving layer. This is complex, error-prone, and the data engineering community has largely moved on from it.

**Why not pure Kappa Architecture:**

Kappa uses a streaming system as the backbone for everything, including historical reprocessing. In theory elegant; in practice complex and expensive. For a 20-day solo build, the overhead is not justified.

**Why Stream-to-Batch works here:**

F1 streaming data (race telemetry) naturally flows into S3 in micro-batches via Spark Structured Streaming.
Once in S3, the *same* Silver and Gold Spark jobs that process historical data can process streaming data.
One codebase, minimal complexity, clean separation of concerns.

**Notes / Learnings:**

<!-- TODO: Fill in after Day 13 — did streaming behave as expected? Watermarking issues? -->

---

## ADR-006: Message Broker — Apache Kafka

**Status:** ✅ Decided — Day 1

**Decision:** Use Apache Kafka as the streaming message broker between OpenF1 and Spark.

**Reasoning:**

- Industry standard for high-throughput event streaming
- Decouples the producer (OpenF1 poller) from the consumer (Spark Structured Streaming)
- Persistent, replayable log — if Spark goes down, it can resume from last offset
- Prepares for production deployment on AWS MSK (managed Kafka)

**Topic Design:**

```
f1-live-timing          # car telemetry: speed, throttle, brake, DRS
f1-positions            # driver positions per lap
f1-pit-stops            # pit stop events
f1-race-control         # safety car, flag, incident messages
```

**Local vs Production:**

```
Local (Day 11–14):   Kafka in Docker Compose
Production (Day 17): AWS MSK (Managed Streaming for Kafka) — defined in Terraform
```

**Notes / Learnings:**

<!-- TODO: Fill in after Day 11 — Kafka setup learnings, partition count decisions -->

---

## ADR-007: Orchestration — Apache Airflow

**Status:** ✅ Decided — Day 1

**Decision:** Use Apache Airflow for pipeline orchestration.

**Reasoning:**

- DAG-based: defines task *dependencies*, not just schedules — smarter than cron
- Written in Python — DAGs are code, can be version-controlled
- Rich ecosystem of operators (S3Sensor, SparkSubmitOperator, PythonOperator, etc.)
- Industry mindshare leader — high portfolio value
- As noted in *Fundamentals of Data Engineering*: Airflow is the "first truly cloud-oriented data orchestration platform"

**Why Airflow runs in Docker (not in the conda env):**

Airflow has heavy dependency conflicts with PySpark and ML libraries.
The professional solution: Airflow runs in its own Docker containers (webserver, scheduler, worker, metadata DB),
completely isolated from the local development environment.

**DAGs to be built:**

```
dag_batch_ingestion.py       # FastF1 → S3 Bronze (daily/seasonal)
dag_spark_bronze_silver.py   # Bronze → Silver Spark jobs
dag_spark_silver_gold.py     # Silver → Gold Spark jobs
dag_ml_retrain.py            # Retrain pace model on new Gold data (weekly)
```

**Notes / Learnings:**

<!-- TODO: Fill in after Day 15 — Airflow Docker setup, first DAG trigger -->

---

## ADR-008: Infrastructure-as-Code — Terraform

**Status:** ✅ Decided — Day 1

**Decision:** Define all AWS infrastructure using Terraform.

**Reasoning:**

- IaC means infrastructure is reproducible, reviewable, and version-controlled
- Terraform is cloud-agnostic (works with AWS, GCP, Azure) and the most widely adopted IaC tool
- Prevents "click-ops" drift — no manually created resources that are undocumented
- Every resource we create manually in the first phases will be codified in Terraform on Day 17

**Resources to define:**

```
S3 buckets (bronze, silver, gold)    → aws_s3_bucket
IAM roles and policies               → aws_iam_role, aws_iam_policy
EMR cluster (Spark)                  → aws_emr_cluster
MSK cluster (Kafka)                  → aws_msk_cluster
Athena workgroup and database        → aws_athena_workgroup
EC2 instance (Airflow)               → aws_instance
VPC and security groups              → aws_vpc, aws_security_group
```

**Notes / Learnings:**

<!-- TODO: Fill in after Day 17 — Terraform state management, any provider issues -->

---

## ADR-009: Containerisation — Docker

**Status:** ✅ Decided — Day 1

**Decision:** Run all services (Spark, Kafka, Airflow) inside Docker containers via Docker Compose.

**Reasoning:**

- Eliminates "works on my machine" — any developer can run the full stack with `docker-compose up`
- Simulates production distributed systems locally without cloud costs
- Airflow, Kafka/Zookeeper, and Spark each run in isolated containers with no dependency bleed
- Easy to tear down and recreate from scratch

**Services in docker-compose.yml:**

```yaml
# Will grow progressively across phases

Phase 1:   (stub only)
Phase 3:   spark-master, spark-worker
Phase 4:   zookeeper, kafka-broker, kafka-ui
Phase 5:   airflow-webserver, airflow-scheduler, airflow-worker, postgres (metadata DB)
```

**Notes / Learnings:**

<!-- TODO: Fill in after each Docker phase — memory limits, networking gotchas -->

---

## ADR-010: Query Layer — AWS Athena

**Status:** ✅ Decided — Day 1

**Decision:** Use AWS Athena to query Silver and Gold layer data directly from S3.

**Reasoning:**

- Serverless SQL on S3 — no cluster to manage, pay only per query
- Works natively with Parquet and Hive-style partitioning
- Feeds the Streamlit dashboard with SQL queries
- Connects to AWS Glue Data Catalog for schema management
- Effectively free for the data volumes in this project

**Alternatives Considered:**

| Alternative | Trade-off |
|---|---|
| Redshift | Full data warehouse, higher cost, more setup |
| Spark SQL directly | Good for transforms; Athena is better for ad-hoc dashboard queries |
| DuckDB (local) | Excellent for local dev and notebooks; not a cloud serving layer |

**Notes / Learnings:**

<!-- TODO: Fill in after first Athena query — partition projection setup, query cost -->

---

## ADR-011: ML Framework

**Status:** ✅ Decided — Day 1

**Decision:** Use scikit-learn (baseline) and XGBoost (primary model) for race pace prediction.

**Target prediction:** Predicted lap pace (seconds) given driver, circuit, tyre compound, stint length, and weather.

**Feature engineering source:** Gold layer aggregates from S3.

**Model artefacts storage:** S3 (`s3://f1-data-gold/models/`)

**Evaluation metrics:**

<!-- TODO: Fill in after Day 18 — MAE, RMSE, baseline comparison -->

**Notes / Learnings:**

<!-- TODO: Fill in after Day 18 -->

---

## ADR-012: Dashboard — Streamlit

**Status:** ✅ Decided — Day 1

**Decision:** Use Streamlit for the analytics dashboard and ML model serving UI.

**Reasoning:**

- Pure Python — no frontend skills required
- Connects directly to Athena (via PyAthena) or reads Parquet from S3 (via boto3 + PyArrow)
- Fast to build, looks professional with minimal effort
- Can display model predictions alongside historical analysis

**Dashboard pages planned:**

```
1. Season Overview      — race results, championship standings
2. Driver Pace Analysis — lap time distributions, tyre degradation curves
3. Pit Stop Strategy    — undercut windows, tyre delta analysis
4. Live Timing          — near-real-time data from Kafka/OpenF1 (stretch goal)
5. Pace Predictor       — ML model: input race conditions, get predicted lap pace
```

**Alternatives Considered:**

| Alternative | Trade-off |
|---|---|
| Grafana | Better for time-series / ops metrics; less suited for ML serving |
| Apache Superset | More powerful BI tool; heavier setup for a solo project |
| Metabase | Good for SQL dashboards; less flexible for ML integration |

**Notes / Learnings:**

<!-- TODO: Fill in after Day 19 -->

---

## Open Questions

> Questions that are not yet resolved. Update with answers as they are discovered.

| # | Question | Status | Answer |
|---|---|---|---|
| 1 | Deploy Kafka locally (Docker) or on AWS MSK? | 🔄 Decided: Docker local, MSK in Terraform stub | — |
| 2 | Use AWS Glue Data Catalog or standalone Hive Metastore? | ⏳ Pending | — |
| 3 | What Spark cluster size is needed for full 2018–2022 backfill? | ⏳ Pending | — |
| 4 | Will FastF1 rate-limit us during full backfill? | ⏳ Pending | — |
| 5 | Store ML model artefacts in S3 or MLflow? | ⏳ Pending | — |
| 6 | Use Delta Lake or plain Parquet for Silver/Gold? | ⏳ Pending — Delta Lake is better long-term | — |

---

## Rejected Alternatives

A summary of architectures considered but not used, and why.

| Option | Reason Rejected |
|---|---|
| **Lambda Architecture** | Dual codebases (batch + streaming) are complex and error-prone; the community has moved on |
| **Pure Kappa Architecture** | Elegant in theory; complex and expensive for a 20-day solo build |
| **Snowflake as warehouse** | Adds cost and vendor lock-in; S3 + Athena achieves same analytical goals at lower cost |
| **AWS Glue (managed Spark)** | Hides Spark internals — defeats the learning objective; consider for Project 2 |
| **dbt as primary transformer** | Great SQL transformation tool, but this project uses PySpark to demonstrate Spark skills |
| **HDFS** | On-premise, cluster-managed, no separation of compute/storage — superseded by S3 |

---

_Last updated: Day 1 — Architecture & Foundation_