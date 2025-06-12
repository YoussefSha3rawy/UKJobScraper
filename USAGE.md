# UK Job Hunt - Usage Guide

## Quick Start

1. **Activate the virtual environment:**

   ```bash
   source venv/bin/activate
   ```

2. **Run the job scraper:**
   ```bash
   python main.py
   ```

## What the Scraper Does

1. **Searches** https://huntukvisasponsors.com/jobs?q=software+engineer for job listings
2. **Filters out** jobs with senior-level keywords (senior, staff, lead, principal, head)
3. **Extracts** detailed job descriptions and actual application URLs from "Apply Now" buttons
4. **Analyzes** each job with Llama LLM to determine if it's suitable for junior developers
5. **Saves** suitable job application URLs to `suitable_jobs.csv`

## Configuration

Edit `config.py` or create a `.env` file to customize:

- `OLLAMA_MODEL`: The Llama model to use (default: llama3.1:latest)
- `MAX_JOBS_TO_PROCESS`: Maximum number of jobs to process (default: 50)
- `DELAY_BETWEEN_REQUESTS`: Delay between requests in seconds (default: 2)
- `EXCLUDED_KEYWORDS`: Keywords to filter out (default: ["senior", "staff", "lead", "principal", "head"])

## Output Files

- `suitable_jobs.csv`: Contains job details and actual application URLs of jobs deemed suitable for junior developers
- `job_analysis.log`: Detailed log of the scraping and analysis process

## Troubleshooting

### Ollama Issues

```bash
# Start Ollama service
ollama serve

# Pull the required model
ollama pull llama3.1
```

### Browser Issues

- The scraper uses Chrome WebDriver
- Make sure Chrome is installed
- The webdriver will be automatically downloaded

### Website Changes

If the target website structure changes, you may need to update the scraper selectors in `scraper.py`.

## Time Frame Filtering

The scraper includes basic date extraction utilities in `utils.py`. You can enhance the `extract_date_from_text()` function to filter jobs by posting date.

## Extending the Scraper

- **Add more job sites**: Create additional scraper classes following the `JobScraper` pattern
- **Improve LLM prompts**: Modify the analysis prompt in `llm_analyzer.py`
- **Add more filters**: Extend the filtering logic in `utils.py`
- **Better date handling**: Enhance date parsing for time frame filtering
