#!/usr/bin/env python3
"""
AlphaFold Retrieve Node for Protein Binder Design Pipeline

This module implements the AlphaFold retrieve node that fetches protein structures
from the AlphaFold database.
"""

import os
import logging
from typing import Dict, Any, Optional
from ..agent_graph import AgentState
from ..tools.alphafold_retrieve import fetch_alphafold_files

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def alphafold_retrieve(state: AgentState) -> AgentState:
    """Retrieve protein structure from AlphaFold DB.

    Args:
        state: Current workflow state

    Returns:
        Updated workflow state with structure information
    """
    logger.info("Retrieving structure from AlphaFold DB")

    # Get UniProt ID from LLM planning output
    llm_planning_output = state.get("steps", {}).get("llm_planning", {}).get("output", {})
    uniprot_id = llm_planning_output.get("uniprot_id")

    if not uniprot_id:
        logger.error("No UniProt ID found in LLM planning output")
        return merge_state(state, {
            "steps": {
                "alphafold_retrieve": {
                    "success": False,
                    "error": "No UniProt ID found in LLM planning output"
                }
            }
        })

    logger.info(f"Fetching structure for UniProt ID: {uniprot_id}")

    # Use AlphaFold
    try:
        # Get output directory
        workflow_dir = state.get("workflow_dir")
        if not workflow_dir:
            logger.error("No workflow directory found in state")
            return merge_state(state, {
                "steps": {
                    "alphafold_retrieve": {
                        "success": False,
                        "error": "No workflow directory found in state"
                    }
                }
            })

        output_dir = os.path.join(workflow_dir, "alphafold")
        os.makedirs(output_dir, exist_ok=True)

        # Retrieve structure from AlphaFold
        result = fetch_alphafold_files(
            uniprot_id=uniprot_id,
            output_dir=output_dir
        )

        # Update state with structure information
        return merge_state(state, {
            "steps": {
                "alphafold_retrieve": {
                    "success": True,
                    "output": {
                        "pdb_path": result.get("pdb_path"),
                        "cif_path": result.get("cif_path"),
                        "pae_path": result.get("pae_path"),
                        "confidence_score": result.get("confidence_score", 0.0),
                        "source": "alphafold"
                    }
                }
            }
        })
    except Exception as e:
        logger.error(f"Error retrieving structure: {str(e)}")
        return merge_state(state, {
            "steps": {
                "alphafold_retrieve": {
                    "success": False,
                    "error": str(e)
                }
            }
        })

def merge_state(base_state: AgentState, updates: Dict[str, Any]) -> AgentState:
    """Merge updates into the base state."""
    new_state = base_state.copy()
    for key, value in updates.items():
        if key == "steps":
            if "steps" not in new_state:
                new_state["steps"] = {}
            new_state["steps"].update(value)
        else:
            new_state[key] = value
    return new_state
