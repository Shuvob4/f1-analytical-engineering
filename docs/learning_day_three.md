# 🎯 DAY 3

## 🧠 KEY DATA ENGINEERING CONCEPTS

### 1. The Medallion Architecture (Bronze → Silver → Gold)

This is the **mental model** for every modern data lake. It comes directly from the Lakehouse pattern

| BRONZE (Raw) | SILVER (Cleaned) | GOLD (Business-Ready) |
| :--- | :--- | :--- |
| Exact copy of source data, as it arrived, no transformations. | Validated, typed, null-handled, schema-enforced, deduplicated. | Aggregated, joined, ML-ready features, dashboard tables. |

#### In F1 terms:

- **Bronze:** Raw FastF1 output → Parquet files, no changes, partitioned by `year/round/session`
- **Silver:** Cleaned lap data: remove laps with `deleted=True`, cast types, handle nulls in sector times
- **Gold:** Aggregated pace tables, driver stint summaries, pit stop windows — what feeds ML and dashboards

### 2. Idempotency — The `#1` Property of a Production Ingestion Pipeline

**Definition:** Running your pipeline 10 times produces exactly the same result as running it once.

**Why this matters:** Pipelines fail. Networks drop. OpenF1 API times out. Your Airflow DAG retries. If your extractor isn't idempotent, every retry creates duplicate data or corrupts your lake.

#### The two idempotency strategies:

- **Overwrite partition:** If the partition already exists, overwrite it entirely. Simple, safe, correct.
- **Check-then-skip:** Before extracting, check if the partition exists. If yes, skip. Faster for large data, but requires careful logic.

### 3. File Format Choice: Why Parquet over CSV

| Property | CSV | Parquet |
| :--- | :--- | :--- |
| **Schema embedded** | ❌ No | ✅ Yes |
| **Columnar (fast for analytics)** | ❌ No | ✅ Yes |
| **Splittable for Spark** | ⚠️ Fragile | ✅ Yes |
| **Null handling** | ❌ Ambiguous | ✅ Native |
| **Nested types** | ❌ No | ✅ Yes |
| **Compression** | ❌ None built-in | ✅ Snappy/gzip |

**Decision:** All Bronze layer writes will be **Parquet with Snappy compression**. This is the correct choice for a data lake that Spark will later read.

### 4. Partitioning Strategy — How Organise Files in the Lake

*Partitioning your data correctly allows Spark to skip many irrelevant files when it only requires data with a specific range of keys.*

**Partition key design for F1 data:**

```text
bronze/
└── fastf1/
    ├── laps/
    │   ├── year=2022/
    │   │   ├── round=01/
    │   │   │   ├── session=R/
    │   │   │   │   └── data.parquet
    │   │   │   └── session=Q/
    │   │   │       └── data.parquet
    │   └── year=2021/
    │       └── ...
    └── telemetry/
        └── year=2022/
            └── round=01/
                └── session=R/
                    └── driver=HAM/
                        └── data.parquet
```

#### Why this partition strategy? 

Downstream Spark jobs and ML model will almost always query by year, sometimes by round. Partitioning on year/round means Spark only reads the relevant folders — massive speedup.

### 5. Separation of Concerns: Extractor vs. Writer vs. Config

From 6 Things Every Data Engineer Should Know *(Mukul Sood, "Design Patterns for Reusability")*: a pipeline has distinct **Ingestion**, **Processing**, and **Result** layers. Even within ingestion, good engineers separate:

- **What to extract** (config/parameters)
- **How to extract** (extractor class — FastF1-specific)
- **Where to write** (writer class — storage-agnostic)

This separation means tomorrow we can swap the writer from local filesystem → S3 without touching the extractor. This is the **Open/Closed Principle** applied to data pipelines.