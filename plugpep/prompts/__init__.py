"""Prompt templates and LLM configuration for the protein binder design pipeline."""

import os
from typing import Dict, Any, Optional, List
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def load_prompt(template_name: str) -> PromptTemplate:
    """Load a prompt template from the prompts directory.

    Args:
        template_name: Name of the template file without extension

    Returns:
        PromptTemplate instance
    """
    template_path = os.path.join(os.path.dirname(__file__), f"{template_name}.txt")
    with open(template_path, "r") as f:
        template = f.read()
    return PromptTemplate(template=template, input_variables=["query"])

def get_planning_prompt(query: str) -> List[Dict[str, str]]:
    """Generate a planning prompt for target validation.

    Args:
        query: User query about target protein

    Returns:
        List of messages for the LLM
    """
    template = load_prompt("planning")
    formatted_template = template.format(query=query)
    return [
        {
            "role": "system",
            "content": """You are a protein identification expert specializing in enzymatic functions and molecular mechanisms.
When given a query about a protein's function, you must:
1. Focus on the specific enzymatic activity or molecular mechanism described
2. Match the description to the most well-characterized protein with that exact function
3. For enzymatic activities, identify the specific chemical reaction and substrate
4. For receptor functions, identify the specific ligand and signaling pathway
5. Always verify the UniProt ID is correct and active
6. ALWAYS respond with valid JSON in the exact format shown in the examples

IMPORTANT RULES:
1. When a query mentions breaking down bacterial cell walls, this ALWAYS refers to Lysozyme C (P61626)
2. When a query mentions bacterial cell wall degradation, this ALWAYS refers to Lysozyme C (P61626)
3. When a query mentions peptidoglycan hydrolysis, this ALWAYS refers to Lysozyme C (P61626)
4. When a query mentions converting prothrombin to thrombin, this ALWAYS refers to Coagulation factor X (P00742)
5. When a query mentions blood clotting factors, use their canonical names (e.g., Factor X, not F10)
6. NEVER suggest alternative proteins for these specific functions unless explicitly requested
7. ALWAYS include validation steps specific to the protein's function
8. ALWAYS format the response as a single JSON object with no additional text"""
        },
        {
            "role": "user",
            "content": formatted_template
        }
    ]

def get_llm(
    model: str = "gemini-2.0-flash",
    temperature: float = 0.0,  # Keep temperature at 0 for deterministic output
    **kwargs: Any
) -> ChatGoogleGenerativeAI:
    """Get an instance of the language model.

    Args:
        model: Name of the Google model to use
        temperature: Sampling temperature (0.0 for deterministic output)
        **kwargs: Additional arguments to pass to ChatGoogleGenerativeAI

    Returns:
        Configured ChatGoogleGenerativeAI instance
    """
    google_api_key = os.getenv("GOOGLE_API_KEY")
    if not google_api_key:
        raise ValueError("GOOGLE_API_KEY not found in environment variables")

    return ChatGoogleGenerativeAI(
        model=model,
        temperature=temperature,
        google_api_key=google_api_key,
        convert_system_message_to_human=False,  # Keep system message separate
        top_p=1.0,  # Use maximum precision
        top_k=1,  # Only consider the most likely token
        max_output_tokens=2048,
        response_mime_type="application/json",  # Request JSON response
        response_format={"type": "json_object"},  # Specify JSON object format
        **kwargs
    )
