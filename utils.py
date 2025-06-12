import logging
from datetime import datetime, timedelta
from config import Config


def setup_logger():
    """Set up logging configuration"""
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        handlers=[
                            logging.FileHandler(Config.LOG_FILE),
                            logging.StreamHandler()
                        ])
    return logging.getLogger(__name__)


def is_excluded_job(job_title):
    """Check if job title contains excluded keywords"""
    job_title_lower = job_title.lower().strip()

    for keyword in Config.EXCLUDED_KEYWORDS:
        if job_title_lower.startswith(keyword.lower()):
            return True
    return False


def save_suitable_job(job_url, job_title, job_info=None):
    """Save a suitable job to the CSV output file"""
    import csv
    import os
    from datetime import datetime

    # Prepare row data
    row_data = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'job_title': job_title,
        'job_url': job_url,
        'company': job_info.get('company', '') if job_info else '',
        'location': job_info.get('location', '') if job_info else '',
        'date_posted': job_info.get('date_posted', '') if job_info else '',
        'reason': job_info.get('reason', '') if job_info else '',
        'raw_date_text': job_info.get('raw_date_text', '') if job_info else ''
    }

    # Check if file exists to determine if we need to write headers
    file_exists = os.path.exists(Config.OUTPUT_FILE)

    with open(Config.OUTPUT_FILE, "a", newline="", encoding="utf-8") as f:
        fieldnames = [
            'timestamp', 'job_title', 'job_url', 'company', 'location',
            'date_posted', 'reason', 'raw_date_text'
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        # Write header if file is new
        if not file_exists:
            writer.writeheader()

        writer.writerow(row_data)


def clean_text(text):
    """Clean and normalize text content"""
    if not text:
        return ""

    # Remove extra whitespace and normalize
    cleaned = " ".join(text.split())
    return cleaned.strip()


def extract_date_from_text(text):
    """Extract posting date from job text if available"""
    # This is a simple implementation - can be enhanced with more sophisticated date parsing
    import re

    date_patterns = [
        r"(\d{1,2})/(\d{1,2})/(\d{4})",  # MM/DD/YYYY
        r"(\d{1,2})-(\d{1,2})-(\d{4})",  # MM-DD-YYYY
        r"(\d{4})-(\d{1,2})-(\d{1,2})",  # YYYY-MM-DD
    ]

    for pattern in date_patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(0)

    return None


def is_within_date_range(job_date):
    """Check if job posting date is within the configured date range"""
    from datetime import datetime, timedelta

    if not job_date:
        return True  # If no date available, include the job

    try:
        # Parse the job date
        if isinstance(job_date, str):
            job_date_obj = datetime.strptime(job_date, "%Y-%m-%d")
        else:
            job_date_obj = job_date

        # Calculate date boundaries
        today = datetime.now()
        max_age = today - timedelta(days=Config.MAX_JOB_AGE_DAYS)
        min_age = today - timedelta(days=Config.MIN_JOB_AGE_DAYS)

        # Check if job date is within range
        return max_age <= job_date_obj <= min_age

    except (ValueError, TypeError) as e:
        logger = setup_logger()
        logger.debug(f"Error parsing job date '{job_date}': {e}")
        return True  # Include job if date parsing fails
