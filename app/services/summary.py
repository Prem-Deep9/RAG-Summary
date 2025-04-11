"""
Patient Summary Service.

This module provides functionality to generate AI-powered summaries,
integrating with Azure LLM for text generation and handling database queries
for patient submissions and assessments.
"""

import logging
import os
import time
from pathlib import Path
from typing import Dict

import yaml
from fastapi import HTTPException
from openai import AzureOpenAI
from sqlalchemy.ext.asyncio import AsyncSession

from app.data.patient_submissions import (
    get_abc,
    get_abs,
    get_ai_tags,
    get_oasmnrs,
    get_sasbas,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_prompts():
    """Load templates from the YAML configuration file."""
    try:
        prompt_path = Path(__file__).parent.parent / "config" / "prompts.yaml"
        if not prompt_path.exists():
            raise FileNotFoundError(f"Prompts file not found at {prompt_path}")
        with open(prompt_path, encoding="utf-8") as f:
            prompts = yaml.safe_load(f)
            if "patient_summary" not in prompts:
                raise KeyError("patient_summary section not found in prompts.yaml")
            return prompts["patient_summary"]
    except Exception as e:
        logger.error("Error loading prompts: %s", str(e))
        raise


async def get_patient_summary(db_session: AsyncSession, patient_id: str) -> Dict:
    """Generate an AI summary for a patient based on their submissions."""
    try:
        # Log the start of processing
        logger.info("Processing summary for patient %s", patient_id)

        # Get submissions sequentially since they share the same session
        oasmnr_submissions = await get_oasmnrs(db_session, patient_id)
        sasba_submissions = await get_sasbas(db_session, patient_id)
        abs_submissions = await get_abs(db_session, patient_id)
        abc_submissions = await get_abc(db_session, patient_id)
        trends = await get_ai_tags(db_session, patient_id)

        if not any(
            [oasmnr_submissions, sasba_submissions, abs_submissions, abc_submissions]
        ):
            logger.warning("No submissions found for patient %s", patient_id)
            return {"summary": "No data available for this patient"}

        # Check environment variables
        required_env_vars = [
            "AZURE_OPENAI_API_KEY",
            "AZURE_OPENAI_ENDPOINT",
            "AZURE_OPENAI_DEPLOYMENT_NAME",
        ]
        for var in required_env_vars:
            if not os.getenv(var):
                logger.error("Missing environment variable: %s", var)
                raise ValueError(f"Missing required environment variable: {var}")

        # Initialize OpenAI client
        client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_version=os.getenv("AZURE_OPENAI_ENDPOINT").split("api-version=")[1],
        )

        deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
        prompts = load_prompts()

        # Format the context
        oasmnr_context = (
            str(oasmnr_submissions)
            if oasmnr_submissions
            else "No OASMNR submissions available"
        )
        sasba_context = (
            str(sasba_submissions)
            if sasba_submissions
            else "No SASBA submissions available"
        )
        abs_context = (
            str(abs_submissions) if abs_submissions else "No ABS submissions available"
        )
        abc_context = (
            str(abc_submissions) if abc_submissions else "No ABC submissions available"
        )

        # Format the prompt with the context
        user_prompt = prompts["user"].format(
            oasmnr_submissions_context=oasmnr_context,
            sasba_submissions_context=sasba_context,
            abs_submissions_context=abs_context,
            abc_submissions_context=abc_context,
            trends=trends,
        )

        # Prepare messages
        messages = [
            {"role": "system", "content": prompts["system"]},
            {
                "role": "user",
                "content": user_prompt,
            },
        ]

        print("\nMessages:", messages, "\n")

        # Make API call
        start_time = time.time()
        response = client.chat.completions.create(
            messages=messages,
            model=deployment_name,
            temperature=0,
        )
        end_time = time.time()

        # Log response time
        response_time = end_time - start_time
        logger.info("OpenAI API response time: %.2f seconds", response_time)

        formatted_summary = response.choices[0].message.content.replace("\\n", "\n")
        return formatted_summary

    except FileNotFoundError as e:
        logger.error("Configuration error: %s", str(e))
        raise HTTPException(
            status_code=500, detail="Service configuration error"
        ) from e
    except ValueError as e:
        logger.error("Environment error: %s", str(e))
        raise HTTPException(
            status_code=500, detail="Service configuration error"
        ) from e
    except Exception as e:
        logging.error("Error generating summary: %s", str(e))
        raise HTTPException(
            status_code=500, detail="Error generating patient summary"
        ) from e
