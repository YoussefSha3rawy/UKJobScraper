# UK Job Hunt - Software Engineering Jobs Scraper

A Python application that searches for software engineering jobs on huntukvisasponsors.com, filters them for junior-level positions, and uses a local LLM to assess job suitability.

## Features

- Scrapes job listings from huntukvisasponsors.com with pagination support
- Filters out senior and staff-level positions
- Extracts detailed job descriptions and actual application URLs from "Apply Now" buttons
- Uses local LLM (Gemma/Llama) to assess if jobs are suitable for junior developers
- Saves suitable jobs to structured CSV format with application URLs
- Configurable date range filtering
- Automatic multi-page processing

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Make sure you have Ollama installed and running locally:

```bash
# Install Ollama (if not already installed)
# Follow instructions at https://ollama.ai/

# Pull a Gemma model (recommended)
ollama pull gemma3
```

3. Run the job scraper:

```bash
python main.py
```

## Output

- `suitable_jobs.csv`: Contains detailed information about jobs deemed suitable for junior developers, including actual application URLs from "Apply Now" buttons
- `job_analysis.log`: Detailed log of the analysis process

The script will automatically handle pagination and process multiple pages of job listings.
