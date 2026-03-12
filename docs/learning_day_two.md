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

1. Why do we use three separate buckets instead of one bucket with three folders? (Question: Your colleague says: "Let's just use one S3 bucket and keep all three layers in `bronze/`, `silver/`, `gold/` subfolders — simpler to manage." What's your counter-argument? Give at least two concrete reasons why separate buckets is better practice.)

    - Using separate buckets enforces the *principle of least privilege* for security, ensuring that users and systems are granted access only to the essential data required for their role. 
    - Applying complex Identity and Access Management (IAM) policies at the folder level within a single bucket is highly prone to human error, which can lead to accidental data leaks.
    - Decoupling the layers into separate buckets limits the "blast radius" of accidents; a buggy script operating in the Bronze bucket cannot accidentally corrupt or delete the highly refined, business-critical data in the Gold bucket.
    - Separate buckets make cost visibility and data lifecycle management much simpler, allowing you to automatically transition cold, raw Bronze data to cheap archival storage without affecting the heavily queried Gold data.

2. What would happen if you re-ran your ingestion job and overwrote the Bronze layer? Why is that a problem?

The Bronze layer is intended to serve as an immutable, append-only repository of raw data in its original format. If you overwrite this layer, you permanently destroy the historical audit trail of your data. This is a major problem because if a bug is discovered in your downstream transformation logic, or if business rules change, you will have lost the original raw data needed to reprocess and fix the downstream Silver and Gold tables.

3. Why create an IAM user instead of using the root account credentials in `.env`?

Using root account credentials violates the *principle of least privilege*, which dictates that you should never give *carte blanche administrative access (refers to granting an individual or entity unconditional authority, full discretionary power, or total control to manage, change, or access administrative systems and data without needing prior approval.)* to users or applications. If root credentials stored in a `.env` file are accidentally leaked (for example, by committing them to a public version control repository), a malicious actor gains full administrative control over your entire AWS environment, which is a "catastrophe waiting to happen".


4. What is partition pruning, and why does your S3 key design affect Spark query performance?

Partition pruning is an optimization technique where a query engine like Apache Spark skips reading irrelevant files by using the folder structure as a filter. If S3 keys are designed logically (e.g., by date or category), Spark evaluates the query's WHERE clause against those folder names and only downloads the specific blocks of data needed. This drastically reduces disk I/O, network transfer time, and memory usage, making Spark queries significantly faster and cheaper.

5. If you were starting a project for a football analytics platform tomorrow, how would you design the medallion structure and S3 key schema? 
    - *Bronze (Raw):* This layer ingests raw JSON event streams, referee logs, and player telemetry directly from the source systems
        - S3 Key Schema: `s3://bronze-football/source_system/year=YYYY/month=MM/match_id=XYZ/`

    - *Silver (Cleaned/Conformed):* Data is parsed, deduplicated, and converted into highly efficient Parquet files
        - S3 Key Schema: `s3://silver-football/player_telemetry/year=YYYY/league=ABC/`

    - *Gold (Aggregated/Business-Ready):* Data is aggregated into structured SQL tables for BI dashboards, such as team possession percentages or player season summaries
        - S3 Key Schema: `s3://gold-football/team_season_summary/year=YYYY/`

6. Scenario: It's Day 6 and you're ingesting telemetry data from FastF1. Each session produces roughly 20 files (one per driver). You could name them either:
    - Option A: `s3://bronze/telemetry/2022_round01_sessionR_VER.parquet`
    - Option B: `s3://bronze/fastf1/telemetry/year=2022/round=01/session=R/driver=VER/data.parquet`

**Option B (s3://bronze/fastf1/telemetry/year=2022/round=01/session=R/driver=VER/data.parquet).** 

Option B uses a *Hive-style* partitioned directory structure that Apache Spark natively understands. If Option A is chosen, Spark cannot automatically utilize partition pruning; it would be forced to scan the entire dataset and parse the filename string to filter for a specific driver or session, crippling query performance and increasing costs.

7. Scenario: Your future project is a real-time financial data platform (stock prices, not F1). You still want to use the medallion architecture on AWS S3. How would you adapt:
    - The bucket structure?
    - The partition key design?
    - Which layer would be most different from F1, and why?

- **The bucket structure:** The foundational three-bucket architecture (Bronze, Silver, Gold) remains exactly the same, as the need to isolate raw, immutable streams from refined reporting data is a universal best practice.
- **The partition key design:** Because stock data is incredibly high-velocity, partitioning solely by year and month will result in massive, unmanageable folders. The partition key must be granular, adding days, hours, and specific stock tickers (e.g., `year=YYYY/month=MM/day=DD/hour=HH/ticker=AAPL`) to distribute the load evenly and optimize query speeds.
- **Which layer would be most different:** The Silver layer would require the most radical adaptation. F1 telemetry generally involves aligning timestamp sensors. Financial data requires strict exactly-once semantics, complex stateful processing, and sliding windows that handle late-arriving data using event-time "watermarks" to ensure trading algorithms do not process out-of-order data incorrectly.
