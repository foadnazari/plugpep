#!/usr/bin/env python3
"""
Extract Backbone Node for Protein Binder Design Pipeline

This module implements the extract_backbone node for backbone extraction.
"""

import logging
from typing import Dict, Any
from pathlib import Path

from .utils import update_node_state, save_json_result
from ..agent_graph import AgentState

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_backbone(state: AgentState) -> AgentState:
    """Extract backbone node."""
    logger.info("Running extract backbone")
    workflow_dir = state["workflow_dir"]

    try:
        # Get the PDB file path from AlphaFold retrieve step
        alphafold_output = state["steps"]["alphafold_retrieve"].get("output", {})
        if not alphafold_output:
            raise KeyError("No output found in alphafold_retrieve step")

        pdb_path = alphafold_output.get("pdb_path")
        if not pdb_path:
            raise KeyError("No pdb_path found in alphafold_retrieve output")

        # Create output directory
        output_dir = Path(workflow_dir) / "backbone"
        output_dir.mkdir(parents=True, exist_ok=True)

        # Set output path for backbone PDB
        output_path = str(output_dir / "backbone.pdb")

        # Run backbone extraction using the tool
        from ..tools.extract_backbone import extract_backbone as extract_backbone_tool
        result = extract_backbone_tool(pdb_path, output_path)

        if not result["success"]:
            raise Exception(f"Backbone extraction failed: {result['error']}")

        # Save results to file
        output_json = save_json_result(
            workflow_dir=workflow_dir,
            node_name="backbone",
            result=result,
            filename="backbone.json"
        )

        # Update state with success and completed status
        state = update_node_state(
            state=state,
            node_name="extract_backbone",
            success=True,
            input_path=pdb_path,
            output_path=output_path
        )
        state["steps"]["extract_backbone"]["status"] = "completed"

        logger.info("Backbone extraction completed successfully")
        return state

    except Exception as e:
        logger.error(f"Error in backbone extraction: {str(e)}")
        state = update_node_state(
            state=state,
            node_name="extract_backbone",
            success=False,
            error=str(e)
        )
        state["steps"]["extract_backbone"]["status"] = "failed"
        return state
