import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


# Configuration settings
class Config:
    # Website settings
    BASE_URL = "https://huntukvisasponsors.com"
    SEARCH_URL = "https://huntukvisasponsors.com/jobs?q=software+engineer"

    # LLM settings
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma3:latest")
    OLLAMA_BASE_URL = "http://localhost:11434"

    # Scraping settings
    MAX_JOBS_TO_PROCESS = int(os.getenv("MAX_JOBS_TO_PROCESS", "50"))
    HEADLESS_BROWSER = os.getenv("HEADLESS_BROWSER", "True").lower() == "true"
    DELAY_BETWEEN_REQUESTS = float(os.getenv("DELAY_BETWEEN_REQUESTS", "2"))

    # Filtering keywords (jobs starting with these will be excluded)
    EXCLUDED_KEYWORDS = ["senior", "staff", "lead", "principal", "head"]

    # Date filtering settings (in days)
    MAX_JOB_AGE_DAYS = int(os.getenv(
        "MAX_JOB_AGE_DAYS", "30"))  # Only jobs posted within last 30 days
    MIN_JOB_AGE_DAYS = int(os.getenv("MIN_JOB_AGE_DAYS",
                                     "0"))  # Jobs posted at least N days ago

    # Output files
    OUTPUT_FILE = "suitable_jobs.csv"
    LOG_FILE = "job_analysis.log"

    # User agent for requests
    USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
