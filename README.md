# Data Infrastructure & Platform Engineering Projects

A collection of Python-based projects focused on data engineering, infrastructure monitoring, automation, and cloud cost optimization.

These projects demonstrate practical applications of Python, SQL, PostgreSQL, Docker, API integrations, and data processing workflows.

## Projects

### 1. Automated Log Parsing Pipeline

**Technologies:** Python, PostgreSQL, Docker, SQL

Developed a data pipeline designed to process raw Nginx server logs, extract meaningful performance metrics, and store structured records in PostgreSQL.

**Key Features:**
- Parses server logs to extract HTTP status codes, request information, and response times.
- Stores structured log data in PostgreSQL for analysis.
- Supports continuous ingestion of log records.
- Provides a foundation for identifying server errors and performance bottlenecks.

### 2. API Performance Monitor

**Technologies:** Python, REST APIs, HTTP, JSON

Built an automated monitoring application that evaluates API availability, response latency, and HTTP error rates.

**Key Features:**
- Sends requests to public API endpoints, including GitHub.
- Measures API response times and HTTP status codes.
- Tracks errors and identifies performance degradation.
- Generates alerts when configured performance thresholds are exceeded.

### 3. Infrastructure Cost Optimizer

**Technologies:** Python, CSV, Cloud Infrastructure, Data Analysis

Created a Python-based cost analysis tool that processes cloud billing and resource utilization data to identify potential infrastructure inefficiencies.

**Key Features:**
- Processes billing exports and resource utilization datasets.
- Identifies potentially underutilized compute instances and idle databases.
- Generates recommendations for reducing unnecessary cloud expenses.
- Produces estimated cost-saving opportunities using configurable assumptions.

## Technical Skills Demonstrated

- **Programming:** Python, SQL
- **Databases:** PostgreSQL
- **Infrastructure:** Docker, cloud infrastructure concepts
- **Data Engineering:** Log parsing, data ingestion, ETL workflows
- **Monitoring:** REST API requests, latency tracking, error detection
- **Optimization:** Billing analysis, resource utilization, cost estimation
- **Development:** Git, GitHub, automated testing

## Repository Structure

```text
data-platform-portfolio/
├── api_monitor/
├── cost_optimizer/
├── log_pipeline/
├── samples/
├── tests/
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Getting Started

Clone the repository:

```bash
git clone https://github.com/akshitamareddy/data-platform-engineering-projects.git
cd data-platform-engineering-projects/data-platform-portfolio
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start PostgreSQL:

```bash
docker compose up -d
```

Run the log parsing pipeline:

```bash
python -m log_pipeline.main --file samples/access.log
```

Run the API monitor:

```bash
python -m api_monitor.main --once
```

Run the infrastructure cost optimizer:

```bash
python -m cost_optimizer.main
```

## Project Goals

These projects explore how software automation and data engineering can improve infrastructure reliability, system observability, and operational efficiency.

They serve as hands-on portfolio projects for developing skills relevant to data engineering, cloud infrastructure, and platform engineering roles.

## Author

**Akshita Mareddy**

GitHub: [akshitamareddy](https://github.com/akshitamareddy)
