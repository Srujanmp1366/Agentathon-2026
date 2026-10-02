# Retail Analytics Agent

This project analyzes retail order data and asks a Groq-hosted language model to turn the results into a short, structured report. It uses a LangGraph workflow to connect data analysis, report writing, and a sentence-count validation loop.

## How It Works

`main.py` builds and runs a graph with three nodes:

1. **Analyzer** calls `retail_analyzer("test_data.csv")` from `tools.py` and stores the calculated metrics in the graph state.
2. **Writer** sends those metrics to the Groq chat model `llama-3.3-70b-versatile`, requesting sections Q1 through Q5 and exactly three sentences in Q5.
3. **Validator** counts periods in the text after `Q5:`. If the count is not three, the graph asks the writer to try again. It stops when the count is three or after three writing attempts.

The final model response is written to `Agent47.txt`, replacing the file each time the program runs. The generated file is ignored by Git.

## Analysis

The analyzer loads `test_data.csv`, normalizes its column names, and calculates:

- **Q1:** Total estimated revenue by product category: quantity multiplied by unit price and adjusted for the discount percentage.
- **Q2:** Average delivery days by customer region.
- **Q3:** Counts of duplicate order IDs, quantities above 1,000, unit prices containing non-numeric formatting, discounts outside 0-100, and null cells.
- **Q4:** Return rate by payment method.
- **Q5 context:** Descriptive statistics from the cleaned data, provided to the language model so it can write the final summary.

For the calculations, currency symbols and commas are stripped from unit prices. Invalid numeric values in unit price, quantity, and discount are coerced and filled with zero. The analyzer expects columns for `order_id`, `quantity`, `unit_price`, `discount_percent`, `product_category`, `customer_region`, `delivery_days`, `return_status`, and `payment_method`. The `train_data.csv` file is included in the repository but is not currently read by the program.

## Requirements

- Python 3.10 or newer
- A Groq API key
- Internet access when generating a report, because the language model is called through Groq

## Setup

From this directory, run these commands in PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Set `GROQ_API_KEY` in `.env` to your own key. Keep that file private; it is excluded from Git.

## Run

```powershell
python main.py
```

The report is written to `Agent47.txt` in the current project directory and also printed with a completion message in the terminal.

## Data and Limitations

The application reads `test_data.csv` using a relative path, so run it from the project directory. The analyzer requires the columns listed above. The sentence validator is intentionally simple: it counts periods after `Q5:` and does not fully understand sentence boundaries. The graph also stops after three attempts even if the generated Q5 still does not meet the requested count. Model output can vary between runs.

## Repository Files

- `main.py` defines the agent state, graph nodes, retry flow, and command-line entry point.
- `tools.py` contains the retail CSV analysis function.
- `test_data.csv` is the dataset currently analyzed by the program.
- `train_data.csv` is an additional dataset not currently consumed by the program.
- `.env.example` documents the required environment variable without containing a working key.
- `requirements.txt` lists the Python packages needed to run the project.