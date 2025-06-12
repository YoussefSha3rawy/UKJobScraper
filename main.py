#!/usr/bin/env python3
"""
UK Job Hunt - Software Engineering Jobs Scraper
Searches for junior-level software engineering jobs and analyzes them with LLM
"""

import sys
import time
from datetime import datetime
from scraper import JobScraper
from llm_analyzer import JobAnalyzer
from utils import setup_logger, is_excluded_job, save_suitable_job, is_within_date_range
from config import Config


def main():
    logger = setup_logger()
    logger.info("=" * 60)
    logger.info("UK Job Hunt - Software Engineering Jobs Scraper")
    logger.info("=" * 60)
    logger.info(
        f"Date range: Jobs posted within last {Config.MAX_JOB_AGE_DAYS} days")

    # Initialize CSV file with headers (the save function will handle this)
    import os
    if os.path.exists(Config.OUTPUT_FILE):
        os.remove(Config.OUTPUT_FILE)  # Clear previous results

    # Initialize components
    scraper = JobScraper()
    analyzer = JobAnalyzer()

    try:
        # Test LLM connection first
        logger.info("Testing connection to Ollama...")
        if not analyzer.test_connection():
            logger.error(
                "Cannot connect to Ollama. Please ensure it's running with the required model."
            )
            logger.error(f"Run: ollama pull {Config.OLLAMA_MODEL}")
            return 1

        # Get job listings
        logger.info("Starting job search...")
        job_listings = scraper.get_job_listings()

        if not job_listings:
            logger.error(
                "No job listings found. The website structure might have changed."
            )
            return 1

        logger.info(f"Found {len(job_listings)} job listings to process")

        suitable_jobs = []
        processed_count = 0

        for i, job in enumerate(job_listings, 1):
            try:
                logger.info(
                    f"Processing job {i}/{len(job_listings)}: {job['title']}")

                # Check if job title contains excluded keywords
                if is_excluded_job(job['title']):
                    logger.info(
                        f"Skipping job (excluded keyword): {job['title']}")
                    continue

                # Check if job is within date range
                if not is_within_date_range(job.get('date_posted')):
                    logger.info(
                        f"Skipping job (outside date range): {job['title']} - Posted: {job.get('date_posted', 'Unknown')}"
                    )
                    continue

                # Get detailed job description
                job_description = scraper.get_job_description(job['url'])

                if not job_description:
                    logger.warning(
                        f"Could not extract description for: {job['title']}")
                    continue

                # Analyze with LLM
                is_suitable, reasoning, full_analysis = analyzer.is_suitable_for_junior(
                    job['title'], job_description, job.get('company', ''))

                if is_suitable:
                    logger.info(f"✓ SUITABLE: {job['title']}")

                    # Get the actual application URL instead of the listing URL
                    application_url = scraper.get_application_url(job['url'])

                    # Add reasoning and application URL to job info
                    job_with_reasoning = job.copy()
                    job_with_reasoning['reason'] = reasoning
                    job_with_reasoning['application_url'] = application_url

                    save_suitable_job(application_url, job['title'],
                                      job_with_reasoning)
                    suitable_jobs.append(job_with_reasoning)
                else:
                    logger.info(f"✗ Not suitable: {job['title']}")

                processed_count += 1

                # Add delay between requests to be respectful
                time.sleep(Config.DELAY_BETWEEN_REQUESTS)

            except Exception as e:
                logger.error(f"Error processing job {job['title']}: {str(e)}")
                continue

        # Summary
        logger.info("=" * 60)
        logger.info("SEARCH COMPLETE")
        logger.info(f"Total jobs found: {len(job_listings)}")
        logger.info(f"Jobs processed: {processed_count}")
        logger.info(f"Suitable jobs found: {len(suitable_jobs)}")
        logger.info(f"Results saved to: {Config.OUTPUT_FILE}")
        logger.info("=" * 60)

        # Print suitable jobs summary
        if suitable_jobs:
            print("\n🎉 SUITABLE JOBS FOUND:")
            for job in suitable_jobs:
                print(f"• {job['title']}")
                # Show application URL if available, otherwise listing URL
                display_url = job.get('application_url', job['url'])
                print(f"  Apply: {display_url}")
                if job.get('company'):
                    print(f"  Company: {job['company']}")
                if job.get('location'):
                    print(f"  Location: {job['location']}")
                print()
        else:
            print("\n😔 No suitable junior-level jobs found in this search.")
            print("Consider:")
            print("- Adjusting search criteria")
            print("- Checking again later as new jobs are posted")
            print("- Expanding search to include more job sites")

        return 0

    except KeyboardInterrupt:
        logger.info("\nSearch interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return 1
    finally:
        scraper.close()


if __name__ == "__main__":
    sys.exit(main())
