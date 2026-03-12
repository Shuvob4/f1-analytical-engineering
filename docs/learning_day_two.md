# Day Two *Build the Data Lake on AWS*

## 🧠 Key Concepts for Day 2

### Concept 1: What is Data Lake and Why S3?

**Data Lake:**
- A massive storage repository where data is kept in it's original, raw, and unprocessed format.
- *Object Storage* are now the *gold standard* of storage for data lakes. i.e. Amazon S3.
- Without proper management and organization, a data lake can quickly turn into a *Data Swamp*, a dumping ground of unusable, undocumented data that is written once and never read.
-The key difference from a data warehouse is that a data lake is `schema-on-read` - you don't enforce structure at write time, impose it at read time.

**Why not Database? :** Databases enforce schemas and are optimized for transactional read/write. S3 is really cheap, infinitely scalable, and accepts any file format (i.e. Parquet, JSON, CSV, binary, etc.). For data lake ingestion target, S3 wins every time.

### Concept 2: The Medallion Architecture (Bronze / Silver / Gold)

#### Data Architecture: The Medallion Pipeline

```text
SOURCE DATA
    │
    ▼
┌─────────────────────────────────────────┐
│  BRONZE  (Raw, immutable, as-is)        │
│  - Exact copy of source data            │
│  - Never overwritten after landing      │
│  - Your "rewind" button                 │
└────────────────┬────────────────────────┘
                 │  Spark job 
                 ▼
┌─────────────────────────────────────────┐
│  SILVER  (Cleaned, typed, deduplicated) │
│  - Schema enforced                      │
│  - Bad rows filtered or flagged          │
│  - Joins applied                        │
└────────────────┬────────────────────────┘
                 │  Spark job 
                 ▼
┌─────────────────────────────────────────┐
│  GOLD    (Business-level aggregates)    │
│  - Ready for ML and dashboards          │
│  - Opinionated, domain-specific         │
└─────────────────────────────────────────┘
```

- F1 Analogy:
    - *Bronze* = Raw telemetry dump from the car, exactly as the sensor sent it (some values might be null, wrong units, duplicated).
    - *Silver* = The cleaned engineering dataset, consistent units, nulls handled, joined with driver metadata.
    - *Gold* = *Verstappen's average sector 2 pace across the last 5 races on medium compounds* — an actual analytical fact.

**`Bronze is sacred and immutable. Silver is trusted and typed. Gold is opinionated and ready to consume`**


### Concept 3: S3 Key Design and Partitioning

S3 has no real folders — it's a flat key-value store. What look like folders are just prefixes in the object key. But the design of those prefixes matters enormously for performance and cost.

*Good key design enables:*
- Partition pruning (Spark reads only the files it needs, not the whole bucket).
- Clear lineage (humans can understand what's in each path at a glance).
- Idempotent writes (re-running a job doesn't create duplicate data).

#### S3 Data Lake: Bronze Layer Structure

The **Bronze** layer follows a Hive-style partitioning strategy to optimize Spark query performance and partition pruning.

```text
s3://f1-bronze/
└── fastf1/
    ├── laps/
    │   └── year=2022/
    │       └── round=01/
    │           └── session=R/
    │               └── data.parquet
    └── telemetry/
        └── year=2022/
            └── round=01/
                └── session=R/
                    └── driver=VER/
                        └── data.parquet
```

**Why** `year=`, `round=`, `session=`? Because Spark and Athena understand this naming convention natively. When query "give me all 2022 laps," Spark will skip every other `year=` folder automatically — this is called **partition pruning** and it *can make queries 100x faster.*

**Mental Model: `S3 keys are query optimization knobs. Design them before write a single byte of data`**

### Concept 4: IAM (Identify and Access Management)

AWS's system for controlling who can do what on which resources.

*The golden rule:* **Principle of Least Privilege** — every user, service, and process should only have the minimum permissions it needs.

#### The 3 things in IAM need to know
- **Root account** — the nuclear option. Create it, lock it away, never use it for day-to-day work.
- **IAM Users** — human or programmatic identities. CLI user goes here.
- **IAM Policies** — JSON documents that say "this user/role can do X on resource Y."

### Concept 5: AWS CLI — Command-Line Cockpit

The AWS CLI lets us interact with all AWS services from the terminal, which means we can script everything. This is the gateway to Infrastructure as Code.

## Concept Check 