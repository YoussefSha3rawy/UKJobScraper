# UK Job Hunt - Project Summary

## 🎯 Project Overview

This Python project successfully implements an automated job hunting system that:

1. **Scrapes** software engineering jobs from https://huntukvisasponsors.com/jobs?q=software+engineer
2. **Filters** out senior-level positions (senior, staff, lead, principal, head)
3. **Extracts** detailed job descriptions and actual application URLs from "Apply Now" buttons
4. **Analyzes** each job using a local Llama LLM (Gemma 3) to determine suitability for junior developers
5. **Saves** suitable job application URLs and details to `suitable_jobs.csv`

## ✅ System Status

**FULLY FUNCTIONAL** ✅

- All dependencies installed successfully
- Chrome WebDriver configured and working
- Ollama LLM integration operational (using Gemma 3)
- Web scraping pipeline functional
- Job filtering logic implemented
- LLM analysis working correctly
- File output system operational

## 🏗️ Project Structure

````
uk-job-hunt/
├── main.py                  # Main application entry point
├── scraper.py              # Web scraping with pagination and application URL extraction
├── llm_analyzer.py         # LLM-based job analysis
├── config.py               # Configuration settings
├── utils.py                # Utility functions and filtering
├── requirements.txt        # Python dependencies
├── setup.sh               # Setup script
├── .env                   # Environment configuration
├── README.md              # Project documentation
├── USAGE.md               # Usage instructions
├── PROJECT_SUMMARY.md     # Comprehensive project overview
├── PAGINATION_SUMMARY.md  # Pagination implementation details
└── suitable_jobs.csv      # Output file with suitable jobs and application URLs

## 🚀 How to Use

### Quick Start

```bash
# Activate virtual environment
source venv/bin/activate

# Run the job scraper
python main.py
````

### Configuration

Edit `.env` file to customize:

- `MAX_JOBS_TO_PROCESS`: Number of jobs to analyze (default: 15)
- `OLLAMA_MODEL`: LLM model to use (default: gemma3:latest)
- `DELAY_BETWEEN_REQUESTS`: Politeness delay (default: 1 second)

## 🧠 LLM Analysis Criteria

The system uses Gemma 3 to evaluate jobs based on:

1. **Experience Requirements** (0-2 years for junior roles)
2. **Technical Complexity** (fundamental vs advanced skills)
3. **Leadership Requirements** (juniors typically don't lead)
4. **Seniority Indicators** in job responsibilities
5. **Educational Requirements** (should accept recent graduates)

## 📊 Test Results

**Recent Test Run:**

- 5 jobs processed from the website
- 1 job filtered out by keyword ("Senior Software Engineer")
- 4 jobs analyzed by LLM
- 0 jobs found suitable for junior developers
- All systems functioning correctly

## 🔧 Technical Features

### Web Scraping

- Selenium WebDriver with Chrome
- Robust error handling
- Respectful request timing
- Multiple fallback strategies for job detection

### LLM Integration

- Local Ollama server integration
- Detailed analysis prompts
- Structured response parsing
- Confidence assessment

### Filtering

- Keyword-based exclusion
- Pattern matching for job titles
- Timeframe support (utilities provided)

### Output

- Structured CSV file output with application URLs
- Detailed logging
- Job URLs and reasoning preservation

## 🎯 Use Cases

1. **Daily Job Hunting**: Run regularly to find new suitable positions
2. **Market Research**: Analyze job market trends for junior developers
3. **Skill Gap Analysis**: Understand what skills are commonly required
4. **Automated Alerts**: Can be extended to send notifications

## 🚀 Future Enhancements

1. **Multiple Job Sites**: Extend to Indeed, LinkedIn, etc.
2. **Email Notifications**: Alert when suitable jobs are found
3. **Database Storage**: Store historical job data
4. **Advanced Filtering**: Location, salary, remote work options
5. **Better Date Handling**: More sophisticated timeframe filtering
6. **Web Interface**: Simple web UI for configuration and results

## 📝 Notes

- The system is designed to be respectful to the target website with appropriate delays
- LLM analysis provides detailed reasoning for each decision
- All job processing is logged for transparency
- The system can be easily extended to support additional job sites
- Works entirely offline after initial setup (except for web scraping)
