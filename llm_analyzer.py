import ollama
import json
from config import Config
from utils import setup_logger, clean_text

logger = setup_logger()


class JobAnalyzer:

    def __init__(self):
        self.client = ollama.Client(host=Config.OLLAMA_BASE_URL)

    def is_suitable_for_junior(self, job_title, job_description, company=""):
        """
        Use LLM to determine if a job is suitable for a junior software engineer
        """
        logger.info(f"Analyzing job: {job_title}")

        prompt = self._create_analysis_prompt(job_title, job_description,
                                              company)

        try:
            response = self.client.chat(
                model=Config.OLLAMA_MODEL,
                messages=[{
                    "role":
                    "system",
                    "content":
                    "You are an expert career advisor specializing in software engineering roles. Analyze job postings to determine if they are suitable for junior software engineers (0-2 years experience)."
                }, {
                    "role": "user",
                    "content": prompt
                }])

            analysis_result = response['message']['content']
            logger.info(f"LLM Analysis completed for: {job_title}")

            # Parse the response to determine suitability
            is_suitable, reasoning = self._parse_analysis_result(
                analysis_result)

            return is_suitable, reasoning, analysis_result

        except Exception as e:
            logger.error(f"Error analyzing job with LLM: {str(e)}")
            return False, f"Analysis failed: {str(e)}", ""

    def _create_analysis_prompt(self, job_title, job_description, company):
        """Create a detailed prompt for job analysis"""

        prompt = f"""
Please analyze the following software engineering job posting to determine if it's suitable for a JUNIOR software engineer (0-2 years of experience).

JOB TITLE: {job_title}
COMPANY: {company}

JOB DESCRIPTION:
{job_description[:3000]}  # Limit to avoid token limits

ANALYSIS CRITERIA:
Please evaluate based on these factors:
1. Required years of experience (should be 0-2 years or entry-level)
2. Technical requirements complexity (should not require advanced/expert knowledge)
3. Leadership or mentoring requirements (juniors typically don't lead)
4. Seniority indicators in responsibilities
5. Educational requirements (should accept recent graduates)

RESPONSE FORMAT:
Please respond with:
1. SUITABLE: YES or NO
2. CONFIDENCE: High/Medium/Low
3. REASONING: Brief explanation of your decision
4. KEY_FACTORS: List main factors that influenced your decision

Example response:
SUITABLE: YES
CONFIDENCE: High
REASONING: This position explicitly states "entry-level" and "0-2 years experience required". The technical requirements are fundamental programming skills appropriate for juniors.
KEY_FACTORS: Entry-level position, mentorship provided, fundamental tech stack, no leadership requirements

Be thorough but concise in your analysis.
"""
        return prompt

    def _parse_analysis_result(self, analysis_text):
        """Parse the LLM response to extract suitability decision"""
        analysis_lower = analysis_text.lower()

        # Look for suitable indicator
        is_suitable = False
        if "suitable: yes" in analysis_lower:
            is_suitable = True
        elif "suitable: no" in analysis_lower:
            is_suitable = False
        else:
            # Fallback: look for positive indicators
            positive_indicators = [
                "entry-level", "junior", "graduate", "0-2 years", "beginner",
                "trainee", "apprentice", "suitable for junior"
            ]
            negative_indicators = [
                "senior", "experienced", "5+ years", "lead", "expert",
                "not suitable", "too advanced", "requires experience"
            ]

            positive_count = sum(1 for indicator in positive_indicators
                                 if indicator in analysis_lower)
            negative_count = sum(1 for indicator in negative_indicators
                                 if indicator in analysis_lower)

            is_suitable = positive_count > negative_count

        # Extract reasoning
        reasoning_start = analysis_text.find("REASONING:")
        if reasoning_start != -1:
            reasoning_end = analysis_text.find("KEY_FACTORS:", reasoning_start)
            if reasoning_end == -1:
                reasoning_end = len(analysis_text)
            reasoning = analysis_text[reasoning_start +
                                      10:reasoning_end].strip()
        else:
            reasoning = "Analysis completed - see full response for details"

        return is_suitable, reasoning

    def test_connection(self):
        """Test if Ollama is running and model is available"""
        try:
            models = self.client.list()
            available_models = [model['name'] for model in models['models']]

            if Config.OLLAMA_MODEL in available_models:
                logger.info(
                    f"✓ Ollama is running and {Config.OLLAMA_MODEL} model is available"
                )
                return True
            else:
                logger.error(
                    f"✗ Model {Config.OLLAMA_MODEL} not found. Available models: {available_models}"
                )
                return False

        except Exception as e:
            logger.error(f"✗ Failed to connect to Ollama: {str(e)}")
            logger.error("Make sure Ollama is running: ollama serve")
            return False
