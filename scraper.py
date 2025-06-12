import requests
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from config import Config
from utils import setup_logger, clean_text
import urllib.parse

logger = setup_logger()


class JobScraper:

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': Config.USER_AGENT})
        self.driver = None

    def setup_driver(self):
        """Setup Chrome WebDriver"""
        chrome_options = Options()
        if Config.HEADLESS_BROWSER:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument(f"--user-agent={Config.USER_AGENT}")

        # Try to use system chromedriver first, fallback to ChromeDriverManager
        try:
            # Use system chromedriver if available
            service = Service("/opt/homebrew/bin/chromedriver")
            self.driver = webdriver.Chrome(service=service,
                                           options=chrome_options)
            logger.info("Using system chromedriver")
        except Exception as e:
            logger.info(
                f"System chromedriver failed: {e}, trying ChromeDriverManager..."
            )
            try:
                # Download driver and get the correct path
                driver_path = ChromeDriverManager().install()
                # Fix the path to point to the actual chromedriver binary
                if "THIRD_PARTY_NOTICES.chromedriver" in driver_path:
                    driver_path = driver_path.replace(
                        "THIRD_PARTY_NOTICES.chromedriver", "chromedriver")

                # Make sure the driver is executable
                import os
                os.chmod(driver_path, 0o755)

                service = Service(driver_path)
                self.driver = webdriver.Chrome(service=service,
                                               options=chrome_options)
                logger.info(f"Using downloaded chromedriver: {driver_path}")
            except Exception as e2:
                logger.error(f"ChromeDriverManager also failed: {e2}")
                raise
        return self.driver

    def get_job_listings(self):
        """Scrape job listings from the search page with pagination support"""
        logger.info(f"Fetching job listings from: {Config.SEARCH_URL}")

        try:
            if not self.driver:
                self.setup_driver()

            self.driver.get(Config.SEARCH_URL)

            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body")))

            time.sleep(3)  # Additional wait for dynamic content

            # Find job listings using the specific table structure with pagination
            job_listings = []
            page_number = 1
            next_button_selector = "body > div.css-py5jdu > div.css-33z2be > div.chakra-stack.css-1old6bn > button:nth-child(2)"
            job_table_selector = "body > div.css-py5jdu > div.css-33z2be > div.chakra-table__container.css-zipzvv > table > tbody > tr"

            while len(job_listings) < Config.MAX_JOBS_TO_PROCESS:
                logger.info(f"Processing page {page_number}...")

                # Wait for table to load
                try:
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR, "table tbody")))
                    time.sleep(2)  # Additional wait for content to stabilize
                except TimeoutException:
                    logger.warning(f"Table not found on page {page_number}")
                    break

                soup = BeautifulSoup(self.driver.page_source, 'html5lib')
                job_rows = soup.select(job_table_selector)

                if not job_rows:
                    logger.warning(f"No job rows found on page {page_number}")
                    break

                logger.info(
                    f"Found {len(job_rows)} job rows on page {page_number}")

                # Process jobs on current page
                jobs_on_page = 0
                for row in job_rows:
                    if len(job_listings) >= Config.MAX_JOBS_TO_PROCESS:
                        break

                    job_info = self._extract_job_info_from_table_row(row)
                    if job_info:
                        job_listings.append(job_info)
                        jobs_on_page += 1

                logger.info(
                    f"Extracted {jobs_on_page} valid jobs from page {page_number}"
                )

                # Check if we've reached the limit
                if len(job_listings) >= Config.MAX_JOBS_TO_PROCESS:
                    logger.info(
                        f"Reached maximum job limit ({Config.MAX_JOBS_TO_PROCESS})"
                    )
                    break

                # Try to find and click the next button
                try:
                    next_button = self.driver.find_element(
                        By.CSS_SELECTOR, next_button_selector)

                    # Check if button is clickable (not disabled)
                    if next_button.is_enabled() and next_button.is_displayed():
                        # Scroll to button to ensure it's visible
                        self.driver.execute_script(
                            "arguments[0].scrollIntoView(true);", next_button)
                        time.sleep(1)

                        logger.info(
                            f"Clicking next page button for page {page_number + 1}"
                        )
                        next_button.click()

                        # Wait for page to load
                        time.sleep(3)
                        page_number += 1

                        # Additional wait to ensure new content is loaded
                        try:
                            WebDriverWait(self.driver,
                                          10).until(lambda driver: len(
                                              driver.find_elements(
                                                  By.CSS_SELECTOR,
                                                  job_table_selector)) > 0)
                        except TimeoutException:
                            logger.warning(
                                "New page content not loaded in time")
                            break

                    else:
                        logger.info(
                            "Next button is disabled or not visible - reached last page"
                        )
                        break

                except NoSuchElementException:
                    logger.info("Next button not found - reached last page")
                    break
                except Exception as e:
                    logger.warning(f"Error clicking next button: {e}")
                    break

            logger.info(
                f"Found {len(job_listings)} total job listings across {page_number} pages"
            )
            return job_listings

        except Exception as e:
            logger.error(f"Error fetching job listings: {str(e)}")
            return []

    def _extract_job_info(self, element):
        """Extract job information from a job listing element"""
        try:
            # Try to find title
            title_selectors = [
                'h1', 'h2', 'h3', 'h4', '.title', '.job-title', 'a'
            ]
            title = ""
            job_url = ""

            for selector in title_selectors:
                title_elem = element.select_one(selector)
                if title_elem:
                    title = clean_text(title_elem.get_text())
                    if title_elem.name == 'a' and title_elem.get('href'):
                        job_url = urllib.parse.urljoin(Config.BASE_URL,
                                                       title_elem.get('href'))
                    break

            # If no URL found in title, look for any link in the element
            if not job_url:
                link_elem = element.select_one('a[href]')
                if link_elem:
                    job_url = urllib.parse.urljoin(Config.BASE_URL,
                                                   link_elem.get('href'))

            # Try to find company
            company_selectors = ['.company', '.employer', '.company-name']
            company = ""
            for selector in company_selectors:
                company_elem = element.select_one(selector)
                if company_elem:
                    company = clean_text(company_elem.get_text())
                    break

            # Try to find location
            location_selectors = ['.location', '.city', '.address']
            location = ""
            for selector in location_selectors:
                location_elem = element.select_one(selector)
                if location_elem:
                    location = clean_text(location_elem.get_text())
                    break

            if title and job_url:
                return {
                    'title': title,
                    'url': job_url,
                    'company': company,
                    'location': location,
                    'date_posted': ''
                }

        except Exception as e:
            logger.debug(f"Error extracting job info: {str(e)}")

        return None

    def _extract_job_info_from_table_row(self, row_element):
        """Extract job information from a table row element with specific selectors"""
        try:
            # Extract job title and URL using the specific selector you provided
            title_div = row_element.select_one(
                'td.css-1c5obzm > div > a > div')
            title_link = row_element.select_one('td.css-1c5obzm > div > a')

            if not title_div or not title_link:
                # Fallback to generic selectors
                title_link = row_element.select_one('a')
                if not title_link:
                    return None
                title = clean_text(title_link.get_text())
            else:
                title = clean_text(title_div.get_text())

            job_url = urllib.parse.urljoin(Config.BASE_URL,
                                           title_link.get('href', ''))

            # Extract company - try multiple column positions
            company = ""
            for col_num in [2, 3, 4]:
                company_cell = row_element.select_one(
                    f'td:nth-child({col_num})')
                if company_cell:
                    company_text = clean_text(company_cell.get_text())
                    # Skip if it looks like a location or date
                    if company_text and not any(
                            indicator in company_text.lower()
                            for indicator in [
                                'london', 'uk', 'england', 'kingdom', 'ago',
                                'day', 'week', 'month'
                            ]):
                        company = company_text
                        break

            # Extract location - try multiple column positions
            location = ""
            for col_num in [3, 4, 5]:
                location_cell = row_element.select_one(
                    f'td:nth-child({col_num})')
                if location_cell:
                    location_text = clean_text(location_cell.get_text())
                    # Check if it looks like a location
                    if location_text and any(
                            indicator in location_text.lower()
                            for indicator in [
                                'london', 'uk', 'england', 'kingdom',
                                'manchester', 'birmingham', 'scotland', 'wales'
                            ]):
                        location = location_text
                        break

            # Extract date posted using the specific selector
            date_cell = row_element.select_one('td.css-xumdn4')
            date_posted = ""
            raw_date_text = ""
            if date_cell:
                raw_date_text = clean_text(date_cell.get_text())
                date_posted = self._parse_date(raw_date_text)

            if title and job_url:
                return {
                    'title': title,
                    'url': job_url,
                    'company': company,
                    'location': location,
                    'date_posted': date_posted,
                    'raw_date_text': raw_date_text
                }

        except Exception as e:
            logger.debug(f"Error extracting job info from table row: {str(e)}")

        return None

    def _parse_date(self, date_text):
        """Parse date from various formats"""
        import re
        from datetime import datetime, timedelta

        if not date_text:
            return ""

        date_text = date_text.lower().strip()

        # Handle relative dates (e.g., "2 days ago", "1 week ago")
        if "ago" in date_text:
            if "day" in date_text:
                days_match = re.search(r'(\d+)\s*day', date_text)
                if days_match:
                    days = int(days_match.group(1))
                    return (datetime.now() -
                            timedelta(days=days)).strftime("%Y-%m-%d")
            elif "week" in date_text:
                weeks_match = re.search(r'(\d+)\s*week', date_text)
                if weeks_match:
                    weeks = int(weeks_match.group(1))
                    return (datetime.now() -
                            timedelta(weeks=weeks)).strftime("%Y-%m-%d")
            elif "month" in date_text:
                months_match = re.search(r'(\d+)\s*month', date_text)
                if months_match:
                    months = int(months_match.group(1))
                    return (datetime.now() -
                            timedelta(days=months * 30)).strftime("%Y-%m-%d")
            elif "hour" in date_text:
                return datetime.now().strftime("%Y-%m-%d")

        # Handle absolute dates
        date_patterns = [
            r"(\d{4})-(\d{1,2})-(\d{1,2})",  # YYYY-MM-DD
            r"(\d{1,2})/(\d{1,2})/(\d{4})",  # MM/DD/YYYY or DD/MM/YYYY
            r"(\d{1,2})-(\d{1,2})-(\d{4})",  # MM-DD-YYYY or DD-MM-YYYY
        ]

        for pattern in date_patterns:
            match = re.search(pattern, date_text)
            if match:
                try:
                    if pattern.startswith(r"(\d{4})"):  # YYYY-MM-DD
                        year, month, day = match.groups()
                        return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                    else:  # Assume MM/DD/YYYY format
                        part1, part2, year = match.groups()
                        # Simple heuristic: if first part > 12, assume DD/MM
                        if int(part1) > 12:
                            day, month = part1, part2
                        else:
                            month, day = part1, part2
                        return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                except ValueError:
                    continue

        return date_text  # Return original if no pattern matches

    def get_job_description(self, job_url):
        """Get detailed job description from job page"""
        logger.info(f"Fetching job description from: {job_url}")

        try:
            if not self.driver:
                self.setup_driver()

            self.driver.get(job_url)

            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body")))

            time.sleep(2)

            soup = BeautifulSoup(self.driver.page_source, 'html5lib')

            # Try different selectors for job description
            description_selectors = [
                '.job-description', '.description', '.job-content', '.content',
                '.job-details', '.details', 'main', '.main-content',
                '[class*="description"]', '[class*="content"]'
            ]

            description = ""
            for selector in description_selectors:
                desc_elem = soup.select_one(selector)
                if desc_elem:
                    description = clean_text(desc_elem.get_text())
                    if len(description
                           ) > 100:  # Ensure we got substantial content
                        break

            # If no specific description found, get main content
            if not description or len(description) < 100:
                # Remove header, footer, navigation elements
                for tag in soup(["header", "footer", "nav", "script",
                                 "style"]):
                    tag.decompose()

                # Get main content
                main_content = soup.select_one('main') or soup.select_one(
                    'body')
                if main_content:
                    description = clean_text(main_content.get_text())

            logger.info(
                f"Extracted description of {len(description)} characters")
            return description

        except Exception as e:
            logger.error(
                f"Error fetching job description from {job_url}: {str(e)}")
            return ""

    def get_application_url(self, job_url):
        """Get the actual application URL from the Apply Now button"""
        logger.info(f"Extracting application URL from: {job_url}")

        try:
            if not self.driver:
                self.setup_driver()

            self.driver.get(job_url)

            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body")))

            time.sleep(2)

            # Try to find the Apply Now button using the specific selector
            apply_button_selector = "body > div.css-py5jdu > div.css-33z2be > div > div.chakra-stack.css-1igwmid > div:nth-child(1) > button > a"

            try:
                apply_button = self.driver.find_element(
                    By.CSS_SELECTOR, apply_button_selector)
                application_url = apply_button.get_attribute('href')

                if application_url:
                    logger.info(f"Found application URL: {application_url}")
                    return application_url
                else:
                    logger.warning("Apply button found but no href attribute")
                    return job_url  # Fallback to original URL

            except NoSuchElementException:
                logger.warning(
                    "Apply button not found, trying alternative selectors")

                # Try alternative selectors for apply button
                alternative_selectors = [
                    "a[href*='apply']", "button a[href]", ".apply-btn a",
                    "[class*='apply'] a"
                ]

                soup = BeautifulSoup(self.driver.page_source, 'html5lib')

                for selector in alternative_selectors:
                    apply_link = soup.select_one(selector)
                    if apply_link and apply_link.get('href'):
                        application_url = apply_link.get('href')
                        # Make sure it's a full URL
                        if not application_url.startswith('http'):
                            application_url = urllib.parse.urljoin(
                                Config.BASE_URL, application_url)
                        logger.info(
                            f"Found application URL via alternative selector: {application_url}"
                        )
                        return application_url

                logger.warning(
                    "No application URL found, using original job URL")
                return job_url  # Fallback to original URL

        except Exception as e:
            logger.error(
                f"Error extracting application URL from {job_url}: {str(e)}")
            return job_url  # Fallback to original URL

    def close(self):
        """Close the browser driver"""
        if self.driver:
            self.driver.quit()
            self.driver = None
