# S3 Data Lake — Infrastructure Notes

## Buckets

| Layer  | Bucket Name                      | Purpose                        |
|--------|----------------------------------|--------------------------------|
| Bronze | YOUR-INITIALS-f1-bronze-2024     | Raw, immutable source data     |
| Silver | YOUR-INITIALS-f1-silver-2024     | Cleaned, typed, deduplicated   |
| Gold   | YOUR-INITIALS-f1-gold-2024       | Business-level aggregates      |

## Region
us-east-1

## Folder Structure

### Bronze

fastf1/laps/          ← FastF1 batch lap data

fastf1/telemetry/     ← FastF1 car telemetry

fastf1/results/       ← Race/qualifying results

openf1/positions/     ← OpenF1 streaming position data

openf1/intervals/     ← OpenF1 streaming interval data

### Silver

laps/

telemetry/

results/

### Gold

race_pace/

pit_analysis/

driver_performance/

## Partitioning Convention
- Hive-style partitioning: year=YYYY/round=NN/session=X/
- Enables partition pruning in Spark and Athena queries.

## IAM
- Pipeline user: f1-pipeline-user
- Policy: AmazonS3FullAccess (to be tightened in Day 17 Terraform phase)

## Security
- All buckets: public access fully blocked.
- Credentials: stored in .env (never committed to Git).