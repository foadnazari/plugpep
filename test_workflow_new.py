#!/usr/bin/env python3
"""
Test script for running the full protein binder design workflow.
Usage:
    python test_workflow_new.py <query_file>  # Read query from file
    python test_workflow_new.py --query "your query here"  # Direct query string
"""

import os
import sys
import json
import uuid
import argparse
from datetime import datetime
from pathlib import Path
from typing import cast
from plugpep import AgentConfig
from plugpep.agent_graph import AgentState
from plugpep.nodes.orchestrator_node import agent_orchestrator
from plugpep.nodes.utils import initialize_workflow_state, create_workflow_dirs

def test_full_workflow(query: str):
    # Get current directory
    current_dir = os.path.abspath(os.path.dirname(__file__))

    # Create a unique workflow ID
    workflow_id = f"test_workflow_{uuid.uuid4().hex[:8]}"
    workflow_dir = os.path.join(current_dir, workflow_id)

    # Create configuration with absolute paths
    config = AgentConfig(
        output_dir=os.path.join(current_dir, "test_output"),
        log_dir=os.path.join(current_dir, "test_logs"),
        debug=True
    )

    # Save configuration
    config.save(os.path.join(current_dir, "test_config.json"))

    # Initialize workflow state with default structure
    state = initialize_workflow_state()

    # Add our custom fields
    state.update({
        "workflow_id": workflow_id,
        "workflow_dir": workflow_dir,
        "timestamp": datetime.now().isoformat(),
        "config": config.to_dict(),  # Use to_dict() method for serialization
        "input": {
            "query": query,
            "target_name": None  # Will be determined by LLM planning
        },
        "orchestrator": {
            "workflow_status": "initialized",
            "current_step": "llm_planning",  # Start with LLM planning
            "next_step": "alphafold_retrieve",
            "completed_steps": [],
            "pending_steps": ["llm_planning", "alphafold_retrieve", "extract_backbone", "llm_report"],
            "last_error": None
        }
    })

    try:
        # Create workflow directory
        os.makedirs(workflow_dir, exist_ok=True)

        # Create workflow directory structure
        create_workflow_dirs(workflow_dir)

        # Save initial state
        state_file_path = os.path.join(workflow_dir, "state.json")
        with open(state_file_path, "w") as f:
            json.dump(state, f, indent=2)

        print(f"Initial state saved to: {state_file_path}")

        # Run orchestrator to execute workflow steps
        print("\nExecuting workflow steps...")
        print(f"Query: {query}")
        agent_state = agent_orchestrator(cast(AgentState, state))

        # Save final state
        with open(state_file_path, "w") as f:
            json.dump(agent_state, f, indent=2)

        print(f"Final state saved to: {state_file_path}")

        # Print workflow information
        print(f"\nWorkflow ID: {workflow_id}")
        print(f"Workflow directory: {workflow_dir}")

        # Check if directories were created
        assert os.path.exists(workflow_dir), "Workflow directory not created"
        assert os.path.exists(config.output_dir), "Output directory not created"
        assert os.path.exists(config.log_dir), "Log directory not created"

        print("\nWorkflow started successfully!")
        print("Check the output and log directories for results.")

    except Exception as e:
        print(f"Error in workflow: {str(e)}")
        raise

def main():
    parser = argparse.ArgumentParser(description='Run protein binder design workflow with a query.')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('query_file', nargs='?', help='Path to the file containing the query')
    group.add_argument('--query', '-q', help='Direct query string')
    args = parser.parse_args()

    if args.query_file:
        try:
            with open(args.query_file, "r") as f:
                query = f.read().strip()
        except FileNotFoundError:
            print(f"Error: Query file '{args.query_file}' not found.")
            sys.exit(1)
        except Exception as e:
            print(f"Error reading query file: {str(e)}")
            sys.exit(1)
    else:
        query = args.query

    test_full_workflow(query)

if __name__ == "__main__":
    main()
