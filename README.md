# Google Cloud Data Lake Project

> ISIT312 Big Data Management Project · University of Wollongong in Dubai · Python · Google Cloud Storage · BigQuery · Tableau

This repository contains a Google Cloud based data lake project developed for a UAE logistics firm that relied heavily on manual data handling across spreadsheets, PDFs, logs, vehicle documents, and financial records.

The project was designed to solve a practical business problem: operational and financial data was scattered across disconnected folders, email inboxes, accounting exports, job sheets, payment vouchers, statements of account, vehicle registration documents, checklist files, rate lists, and system logs. This made reporting slow, reconciliation difficult, and decision-making mostly retrospective.

The solution introduces a 3-zone data lake architecture using Google Cloud Storage, Python ETL pipelines, curated Parquet outputs, BigQuery analytics tables, and a Tableau dashboard. The goal was to move the business from fragmented manual workflows to a cleaner, more reliable, and analysis-ready data environment.

---

## What This Project Does

* Designs a 3-zone cloud data lake structure using raw, processed, and curated layers
* Ingests operational, financial, vehicle, and system activity data from multiple file formats
* Processes CSV, PDF, image, log, Parquet, and JSON-based data workflows
* Uses Python ETL scripts to clean, standardise, extract, and transform raw business data
* Converts final analytical outputs into curated Parquet files
* Loads curated datasets into BigQuery for structured querying and reporting
* Supports Tableau dashboards for operational, financial, and vehicle maintenance insights
* Replaces manual spreadsheet and PDF based reporting with repeatable data pipelines
* Demonstrates how a small logistics business can begin moving toward cloud-based data management

---

## Project Objective

The objective of this project was to build a functional data lake solution that could centralise and process the company's scattered business data.

The project focused on answering practical business questions such as:

* How can vendor job sheets be consolidated automatically?
* How can payment vouchers and statements of account support reconciliation?
* How can rate lists be cleaned and standardised for cost analysis?
* How can system logs be converted into usage summaries?
* How can vehicle registration and inspection data support maintenance analytics?
* How can curated outputs be connected to BigQuery and visualised in Tableau?

The final system provides a foundation for more reliable financial reporting, operational visibility, vendor analysis, and maintenance planning.

---

## My Contributions

My specific contributions included:

* **Data lake architecture design** - structured the raw, processed, and curated zones so that original files, intermediate outputs, and analytics-ready datasets were clearly separated
* **Python ETL pipeline development** - contributed to scripts that ingest, clean, transform, and export logistics data into Parquet format
* **Job sheet and vendor analytics** - worked on pipelines that scan vendor folders, combine job sheet CSV files, clean dates and monetary fields, and generate monthly cost trends
* **Rate list processing** - supported the standardisation of vehicle rate list data, including numeric rate conversion, source tracking, and average rate calculations
* **Voucher and financial extraction** - contributed to the payment voucher workflow that extracts PDF text, parses payment amounts, and flags missing or unusual values
* **Statement of account processing** - supported vendor-level reconciliation by linking job totals, payment amounts, and balance due calculations
* **Vehicle maintenance analytics** - helped build logic for vehicle registration extraction, checklist processing, inspection failure metrics, and reliability scoring
* **BigQuery and Tableau integration** - supported the process of moving curated Parquet outputs into BigQuery
* **Documentation and reporting** - contributed to explaining the system architecture, pipeline flow, limitations, and business value in the final academic report

---

## Architecture

The project uses a 3-zone data lake architecture.

```text
Raw Data Sources
    |
    v
Google Cloud Storage - Raw Zone
    |
    v
Python ETL Processing - Processed Zone
    |
    v
Curated Parquet Outputs - Curated Zone
    |
    v
BigQuery Analytics Tables
    |
    v
Tableau Dashboard
```

### Raw Zone

The raw zone stores original source files exactly as received. This includes vendor folders, job sheets, payment vouchers, statements of account, rate lists, vehicle registration files, checklist CSVs, logs, and image-based data.

This layer acts as the source of truth and preserves the original business records before any transformations are applied.

### Processed Zone

The processed zone contains intermediate outputs created by the Python ETL scripts. These include extracted voucher text, registration data, image metadata, processed vehicle files, and unified intermediate datasets.

This layer is useful because it separates extraction and cleaning work from the final curated analytics layer.

### Curated Zone

The curated zone contains cleaned, structured, analytics-ready Parquet files. These outputs are designed to be loaded into BigQuery and used for dashboard reporting.

Examples include vendor trends, voucher issues, rate list summaries, SOA summaries, and vehicle maintenance outputs.

---

## Repository Structure

| Folder or File | Purpose |
| --- | --- |
| `etl/` | Contains the Python ETL scripts used to process job sheets, rate lists, logs, vouchers, SOA files, and vehicle data |
| `curated_data/` | Contains curated Parquet outputs used for analytics and BigQuery loading |
| `integration_samples/` | Contains sample Parquet files used to support dashboard and integration work |
| `logos/` | Contains project-related branding or visual assets |
| `.gitignore` | Defines files and folders that should not be committed |
| `README.md` | Project documentation |

---

## ETL Pipelines

The project includes several Python ETL pipelines that process different parts of the logistics data environment.

### Rate Lists Pipeline

The rate list pipeline reads CSV files from the rate list directory, combines them into one dataset, standardises column names, converts rate columns into numeric values, and normalises Yes or No fields into Boolean values.

It generates:

* `rate_lists.parquet`
* `rate_lists_avg_rates.parquet`

These outputs support vehicle cost analysis by calculating average hourly, daily, monthly, and overtime rates per vehicle type.

### Job Sheet Pipeline

The job sheet pipeline scans vendor folders and looks for `job_sheet.csv` files. It adds the vendor name, cleans dates and total amount fields, and creates a monthly trend dataset showing total job charges over time.

It generates:

* `pair1_job_sheets.parquet`
* `pair1_vendor_trends.parquet`

This replaces the manual process of opening and reviewing each vendor spreadsheet separately.

### Logs Pipeline

The logs pipeline loads and combines system log CSV files, converts timestamps, and creates summaries for daily activity, user activity, and system usage.

It generates outputs such as:

* `logs_full.parquet`
* `logs_daily_activity.parquet`
* `logs_user_summary.parquet`
* `logs_system_summary.parquet`

This allows system behaviour and user activity to be analysed more easily.

### Payment Voucher Pipeline

The voucher pipeline finds payment voucher PDFs inside vendor folders and extracts raw text using Python PDF processing. A second script converts the extracted text into a curated table by parsing invoice amounts and flagging missing or extreme values.

It generates:

* `pair2_voucher_text.parquet`
* `pair2_vouchers.parquet`
* `pair2_voucher_issues.parquet`
* `vouchers_sample.parquet`

This helps identify financial anomalies that would otherwise require manual review.

### Statement of Account Pipeline

The SOA pipeline processes vendor-level financial records by combining job sheet totals, payment voucher amounts, and statement of account details.

It calculates:

* Total job amount
* Payment amount
* Balance due
* Vendor-level reconciliation summaries

The final curated output is:

* `pair3_soa.parquet`

This supports financial reconciliation and helps reduce the risk of missed payments, duplicate payments, or unclear outstanding balances.

### Vehicle Registration and Checklist Pipeline

The vehicle pipeline processes registration PDFs, image metadata, and checklist CSVs. It extracts vehicle registration details, identifies brands, links checklist data to vehicle IDs, and creates a unified vehicle master dataset.

The pipeline produces processed outputs for:

* Image metadata
* Registration data
* Vehicle master data

This creates a single view of vehicle inspection and registration information.

### Vehicle Analytics Pipeline

The vehicle analytics pipeline uses the vehicle master dataset to calculate inspection and maintenance indicators.

It calculates:

* Tire failures per inspection
* Brake failures per inspection
* Engine failures per inspection
* Light failures per inspection
* Vehicle-level reliability scores
* Brand-level maintenance summaries
* Highest-risk vehicles based on weighted failure patterns

The final outputs include:

* `vehicle_level_maintenance.parquet`
* `brand_level_maintenance.parquet`

These outputs support proactive maintenance analysis and help identify vehicles or brands that require closer attention.

---

## BigQuery and Tableau

After the ETL process is complete, curated Parquet outputs are loaded into BigQuery. BigQuery acts as the analytics layer where structured datasets can be queried and connected to dashboard tools.

Tableau is then connected to the curated data layer to visualise key business indicators.

The dashboard includes views such as:

* Total events
* Payment amount
* Number of vehicle types
* Jobs completed by user
* Failures per vehicle inspection
* Tire failure patterns by brand
* Light failure patterns by brand
* Vehicle reliability scores

This makes the results easier to interpret for business users who may not work directly with Python, SQL, or cloud storage.

---

## Tech Stack

**Languages and Core Tools:** Python, SQL  
**Cloud Platform:** Google Cloud Platform  
**Storage:** Google Cloud Storage  
**Analytics Warehouse:** BigQuery  
**Data Processing:** Pandas, NumPy  
**PDF Processing:** PyPDF2, pdfplumber, PyMuPDF  
**Image Handling:** Pillow  
**Data Format:** Parquet, CSV, PDF, JSON  
**Dashboarding:** Tableau  
**Execution Environment:** Google Cloud Shell  
**Version Control:** Git, GitHub  

---

## Key Skills Demonstrated

* Cloud data lake design
* Big data architecture planning
* Python ETL development
* Multi-format data ingestion
* CSV, PDF, image, log, JSON, and Parquet processing
* Data cleaning and schema standardisation
* Financial reconciliation logic
* Vendor-level analytics
* Vehicle maintenance analytics
* Reliability score calculation
* BigQuery loading and analytics preparation
* Tableau dashboard integration
* Translating manual business workflows into automated data pipelines
* Academic and technical documentation

---

## Limitations

The project met its core objectives, but there were some limitations.

Some data had to be synthetic because the original business records could not be shared due to privacy and confidentiality restrictions. The synthetic data was designed to match the structure and relationships of the real data, but it did not fully capture every messy edge case found in real operational systems.

The ETL scripts were also executed through Google Cloud Shell rather than a distributed Spark environment. This meant the project was functional but not fully scalable for large production workloads. A future version should migrate the processing layer to Dataproc or another Spark-based environment.

The dashboard layer was originally expected to use Power BI, but platform compatibility issues led to Tableau being used instead. Tableau still provided the required visualisation capability, but the change added pressure during the final stage of the project.

---

## Future Improvements

Future improvements could include:

* Migrating Python ETL scripts to PySpark for distributed processing
* Automating scheduled pipeline execution
* Adding stronger schema validation and error handling
* Creating a full data quality monitoring layer
* Building a complete BigQuery data model with fact and dimension tables
* Adding access control rules for sensitive financial documents
* Expanding Tableau dashboards with drill-down views for finance, vendors, and maintenance
* Replacing local path dependencies with fully cloud-native GCS paths
* Adding CI checks for pipeline scripts before deployment

---

## Key Takeaways

This project shows how a fragmented logistics data environment can be moved into a structured data lake workflow.

Rather than treating each spreadsheet, PDF, image, or log file as a separate manual task, the project brings them into one coordinated pipeline. Raw files are preserved, processed outputs are created, curated Parquet files are generated, and the final datasets are made available for BigQuery and Tableau.

The final result is a practical big data management project that demonstrates cloud architecture, ETL development, data engineering, analytics preparation, and dashboard integration in a business context.

---

## Project Status

This project is complete as part of the ISIT312 Big Data Management module at the University of Wollongong in Dubai.

---

## Author

**Ibrar Bhatti**  
GitHub: [ibrawr](https://github.com/ibrawr)
