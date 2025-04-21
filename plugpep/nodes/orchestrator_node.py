#!/usr/bin/env python3
"""
Orchestrator Node for Protein Binder Design Pipeline

This module implements the orchestrator node that manages the workflow execution.
"""

import logging
from typing import Dict, Any, List, Optional, Callable, cast, TYPE_CHECKING
from datetime import datetime
from ..agent_graph import AgentState, StepState

if TYPE_CHECKING:
    from .extract_backbone_node import extract_backbone
    from .llm_node import llm_planning
    from .alphafold_retrieve_node import alphafold_retrieve

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Node function mapping - using string references to avoid circular imports
NODE_FUNCTIONS = {
    "llm_planning": "llm_planning",
    "alphafold_retrieve": "alphafold_retrieve",
    "extract_backbone": "extract_backbone",
    "llm_report": "llm_report"
}

def get_next_step(current_step: str) -> Optional[str]:
    """Get the next step in the workflow."""
    step_order = [
        "llm_planning",
        "alphafold_retrieve",
        "extract_backbone",
        "llm_report"
    ]
    try:
        current_index = step_order.index(current_step)
        if current_index < len(step_order) - 1:
            return step_order[current_index + 1]
    except ValueError:
        pass
    return None

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

def orchestrate_workflow(
    state: AgentState,
    end_node: Optional[str] = None,
    node_functions: Optional[Dict[str, str]] = None
) -> AgentState:
    """Orchestrate the workflow execution."""
    if node_functions is None:
        node_functions = NODE_FUNCTIONS

    current_step = state.get("current_step", "llm_planning")
    logger.info(f"Starting workflow from step: {current_step}")

    while True:
        if current_step == end_node:
            break

        if current_step not in node_functions:
            logger.error(f"Unknown step: {current_step}")
            break

        logger.info(f"Executing step: {current_step}")
        try:
            # Import node function here to avoid circular imports
            if current_step == "extract_backbone":
                from .extract_backbone_node import extract_backbone
                node_func = extract_backbone
            elif current_step == "llm_planning":
                from .llm_node import llm_planning
                node_func = llm_planning
            elif current_step == "alphafold_retrieve":
                from .alphafold_retrieve_node import alphafold_retrieve
                node_func = alphafold_retrieve
            elif current_step == "llm_report":
                from .llm_node import llm_report
                node_func = llm_report
            else:
                # Import the function dynamically based on the step name
                module_name = node_functions[current_step]
                module = __import__(f".{module_name}_node", fromlist=[module_name], package="plugpep.nodes")
                node_func = getattr(module, module_name)

            state = node_func(state)
        except Exception as e:
            logger.error(f"Error in step {current_step}: {str(e)}")
            state = merge_state(state, {
                "steps": {
                    current_step: {
                        "success": False,
                        "error": str(e)
                    }
                }
            })
            break

        next_step = get_next_step(current_step)
        if next_step is None:
            break

        current_step = next_step

    return state

def agent_orchestrator(state: AgentState) -> AgentState:
    """Agent orchestrator node for managing workflow execution."""
    logger.info("Agent Orchestrator managing workflow")
    return orchestrate_workflow(state)
