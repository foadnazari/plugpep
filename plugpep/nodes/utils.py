"""
Utility functions for node implementations.
"""

import os
import json
import logging
from typing import Dict, Any, Optional, cast
from datetime import datetime
from pathlib import Path
from ..agent_graph import AgentState

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def update_node_state(
    state: AgentState,
    node_name: str,
    success: bool,
    error: Optional[str] = None,
    input_path: Optional[str] = None,
    output_path: Optional[str] = None,
    output_data: Optional[Dict[str, Any]] = None,
    **additional_data: Any
) -> AgentState:
    """Update node state with common fields.

    Args:
        state: Current workflow state
        node_name: Name of the node being updated
        success: Whether the node execution was successful
        error: Error message if execution failed
        input_path: Path to input file(s)
        output_path: Path to output file(s)
        output_data: Output data from the node
        **additional_data: Additional data to store in node state

    Returns:
        Updated state dictionary
    """
    # Create new state dictionary
    new_state: StepState = {
        "success": success,
        "error": error,
        "status": "completed" if success else "failed",
        "input_path": input_path,
        "output_path": output_path,
        "output": output_data
    }

    # Add any additional data
    new_state.update(additional_data)

    # Update state
    state["steps"][node_name] = new_state

    # Update logs
    if success:
        if input_path:
            state["logs"]["file_paths"].append(input_path)
        if output_path:
            state["logs"]["file_paths"].append(output_path)
        state["logs"]["timestamps"][node_name] = datetime.now().isoformat()
    else:
        state["logs"]["errors"].append(f"{node_name} error: {error}")

    return cast(AgentState, state)

def save_json_result(
    workflow_dir: str,
    node_name: str,
    result: Dict[str, Any],
    filename: str = "result.json"
) -> str:
    """Save node results to a JSON file.

    Args:
        workflow_dir: Base workflow directory
        node_name: Name of the node
        result: Result data to save
        filename: Name of the output file

    Returns:
        Path to the saved file
    """
    output_dir = Path(workflow_dir) / node_name
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / filename
    with open(output_path, "w") as f:
        json.dump(result, f, indent=2)

    return str(output_path)

def create_workflow_dirs(workflow_dir: str) -> None:
    """Create standard workflow directory structure.

    Args:
        workflow_dir: Base workflow directory
    """
    dirs = [
        "input",
        "alphafold",
        "backbone",
        "llm"
    ]

    for dir_name in dirs:
        os.makedirs(os.path.join(workflow_dir, dir_name), exist_ok=True)

def initialize_workflow_state() -> Dict[str, Any]:
    """Initialize standard workflow state structure.

    Returns:
        Initialized state dictionary
    """
    return {
        "steps": {
            "llm_planning": {"success": False, "error": None},
            "alphafold_retrieve": {"success": False, "error": None},
            "extract_backbone": {"success": False, "error": None},
            "llm_report": {"success": False, "error": None}
        },
        "logs": {
            "file_paths": [],
            "timestamps": {},
            "errors": []
        }
    }
