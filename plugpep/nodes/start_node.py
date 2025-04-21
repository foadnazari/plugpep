#!/usr/bin/env python3
"""
Start Node for Protein Binder Design Pipeline

This module implements the start node for workflow initialization.
"""

import os
import logging
from typing import Dict, Any, cast

from .utils import create_workflow_dirs, initialize_workflow_state, update_node_state
from ..agent_graph import AgentState

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def start_workflow(state: Dict[str, Any]) -> AgentState:
    """Start node for workflow initialization."""
    logger.info("Initializing workflow")
    workflow_dir = state["workflow_id"]

    try:
        # Create workflow directory structure
        create_workflow_dirs(workflow_dir)

        # Initialize workflow state
        state.update(initialize_workflow_state())
        agent_state = cast(AgentState, state)

        # Copy input files if they exist
        input_files = {}
        if "target_pdb" in state["input"]:
            target_pdb = state["input"]["target_pdb"]
            input_path = os.path.join(workflow_dir, "input", "target.pdb")
            os.system(f"cp {target_pdb} {input_path}")
            input_files["target_pdb"] = input_path

        # Update state with input file information
        agent_state = update_node_state(
            state=agent_state,
            node_name="start",
            success=True,
            input_path=input_files.get("target_pdb"),
            workflow_dir=workflow_dir,
            input_files=input_files
        )

    except Exception as e:
        agent_state = update_node_state(
            state=cast(AgentState, state),
            node_name="start",
            success=False,
            error=str(e)
        )

    return agent_state
