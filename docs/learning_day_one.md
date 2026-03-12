## Minimum Concepts for Day 1

*Motivation* `A good architect doesn't start by laying bricks. They start by drawing blueprints.`

1. **Monorepo Project Structure:** A monorepo means everything — ingestion, processing, streaming, infra, ML, dashboard — lives in one Git repository, organized into logical folders. This is standard for data engineering projects because all components need to talk to each other.

2. **Docker and Docker Compose (conceptually):** Docker packages your code + its dependencies into a portable "container." Docker Compose lets you define multiple containers (e.g., Spark + Kafka + Airflow) in a single YAML file and start them all with one command. Think of it as a blueprint for your local mini-cloud.

3. **The `.env` pattern:** Never hardcode secrets (AWS keys, passwords) in your code. Store them in a `.env` file (never committed to Git) and load them as environment variables. This is how real production systems work.

4. **The Medallion Architecture (Bronze/Silver/Gold):** Raw data lands in Bronze (immutable, as-received). Cleaned/typed data lives in Silver. Business-ready aggregates live in Gold.

### Basic Theory

**Q1.** what's the difference between Bronze, Silver, and Gold layers in a data lake?.

Bronze, Silver and Gold layers are known as Medallion Architecture, use to organize data as it flows through a system.

- **Bronze Layer:** Landing zone for raw data in it's original format. (i.e. JSON data fetched from OpenF1 api or through FastF1)

- **Silver Layer:** Here, the raw data gets cleaned, deduplicated and transfromed into a more efficient, query friendly format files. (i.e. Converting raw JSON files into structured tabular format and storing them into a parquet file.)

-**Gold Layer:** Final and highly refined layer, where data is aggregated into structred tables and ready to power BI reports or feed into ML models. (i.e. Drivers point table for each season storing all race informations which will be used to show Drivers performance Chart over the years.)

**Q2.** Why do we store secrets in `.env` instead of directly in Python scripts? What could go wrong if you committed `.env` to GitHub?

It's a good practice to store secrets in `.env` file as these are sensitive informations like `usernames`,`passwords` for databases or `api key` for some paid api's. We do not want everyone to be aware of what is the values of these as they compromise the security aspect, thus we do not hard code them in python code and store them using `.env` file. Also, if we update any of these secrative values we will update them once in the `.env` file and no need to worry how many times they have been used in the scripts.

If we commit the `.env` file into github then it compromises the security. Github is a place where people put their code either for collaborating among teams or for public to see. We do not want others to know what is the password of our database or the api key for Claude. 

**Q3.** What does Docker solve that "just installing Python" doesn't? Why will this matter when we add Spark and Kafka later?

While simply installing Python gives you the language, it does not guarantee that your code will run exactly the same way on another machine or in a production environment. Docker solves this by placing applications into containers, which provides reproducibility, isolation, and deployment consistency. A Docker container packages an isolated user space—including the filesystem, code, and all specific dependencies—without the heavy overhead of a full operating system. Ultimately, Docker prevents the classic "it works on my machine" syndrome and ensures a seamless transition from local development to cloud deployment.

When you add Apache Spark and Kafka later, this containerization becomes incredibly valuable for several reasons:

- **Simulating Distributed Systems Locally:** Spark and Kafka are complex, distributed systems that rely on multiple interconnected components, such as ZooKeeper, Kafka brokers, Spark master nodes, and Spark worker nodes. Docker allows us to bootstrap and simulate these distributed clusters locally on our laptop without needing to pay for or deploy to an actual production environment.

- **Avoiding Configuration Headaches:** Instead of manually installing and configuring Java, Kafka, ZooKeeper, and Spark on our host machine—which often leads to dependency conflicts we can use Docker Compose to spin up a fully self-contained ecosystem of these services in minutes.

- **Testing Complex Interactions:** Running these tools in isolated containers lets us safely test the integrations and distributed nature of our data pipelines in a controlled environment. For example, we can easily simulate a pipeline where a Python producer sends data to a Kafka topic, which is then consumed and processed by Spark Structured Streaming.

**Q4.** Looking at your folder structure: which folder will contain the code that reads from Kafka and writes to S3? Which folder will contain the code that reads Bronze Parquet files and writes cleaned Silver Parquet files?

`f1-analytical-engineering/ingestion/streaming` will contain the code that reads from Kafka and writes to S3.
`f1-analytical-engineering/processing/bronze_to_silver` will contain the code that reads Bronze Parquet files and writes cleaned Silver Parquet files

**Q5.** What format should we store data in on S3 to make Spark reads fast and efficient? 

To make reads fast and efficient for Apache Spark on S3, we should store data in a **columnar file format**, with **Apache Parquet** being the most hightly recommended industry standard.

Here is why Parquet (as well as similar columnar formats like ORC or Apache Arrow) is the superior choice for this architecture:

- **Targeted Column Scanning:** Unlike row-based formats (like CSV or JSON) where the engine must read the entire row to extract a single data point, columnar formats store all the values of a single column together. If our Spark query only analyzes 3 columns out of a 100-column table, it will only scan and load those 3 columns. This drastically reduces the amount of data that needs to be read from the disk and transferred over the network from S3

- **Highly Efficient Compression:** Because the data in a single column is all of the exact same type (e.g., all dates, or all integers), it can be compressed much more effectively than mixed row data. We can pair Parquet files with compression algorithms like Snappy (which prioritizes speed) or Gzip to shrink our dataset. Smaller files mean faster network transfers and cheaper S3 storage bills.

- ** Built-in Schemas and Nested Data:** Plain text formats like CSV are notorious for causing pipeline errors due to delimiter issues and a lack of explicit data types. Parquet embeds the schema (column names and data types) directly into the file itself and can effortlessly handle complex, nested data structures.

- **Native Spark Integration:** Parquet is the default data source file format for Apache Spark. Spark’s optimizer is built to work seamlessly with Parquet, using the statistics tracked within the file to quickly skip over chunks of data that aren't needed for our query.


**Q1.** Why do we pin `python=3.10` instead of just writing python? What could go wrong if we don't pin it?

We pin `python=3.10` as we specifically want to install this version of python which is also most compitable with all other dependencies that we are using for this project. If we didn't pin it then by default conda would have installed the latest version of python which may not be fully stable as well as not compitable with the other dependencies for our project.

**Q2.** why is `pyarrow` going to be critical in this project?

`pyarrow` is the Python library for **Apache Arrow**, an in-memory serialization framework that utilizes a columnar, binary data format designed to be suitable for both in-memory processing and data export.

- **Eliminates Serialization/Deserialization Overhead:** Traditionally, complex data structures must be flattened and translated (serialized) to be stored on a disk or sent over a network, which incurs a massive performance and CPU cost. Arrow solves this by allowing systems to use the exact same format for in-memory processing, network export, and long-term storage.

- **High-Speed Cross-Language Interoperability:** The Arrow project provides software libraries for a variety of programming languages, including Python, C, Java, Go, R, and Rust. This allows seamless, high-speed data exchange between languages. For example, a Scala program can write Arrow data and pass it directly as a message to a Python program without the standard overhead of translating the data.

- **Memory Efficiency for Large Datasets:** Because of its standardized columnar format, Arrow data stored on a disk can be swapped directly into a program's virtual memory space. An engine can swap chunks of a file into memory as it scans, and swap them back out, allowing us to query massive datasets without running out of memory.

- **Native Integration with Big Data Frameworks:** Arrow is seeing rapid adoption across the data ecosystem. For instance, Apache Spark uses Apache Arrow under the hood to power its "pandas UDFs" (User-Defined Functions), which drastically speeds up the performance of distributed Python calculations. Arrow also serves as the core foundation for modern query engines and data warehouses like Dremio.



**Q3.** Why is `fastf1` installed via `pip:` inside the conda environment instead of directly under `conda` dependencies?

`fastf1` installed via `pip` inside the conda environment as it's not available in conda. The creator of `fastf1` didn't provide the options to install it with `conda` thus we have to use `pip` inside the `conda` dependencies.