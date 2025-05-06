import os
import requests
import json
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class AlphaFoldError(Exception):
    """Base exception for AlphaFold-related errors."""
    pass

class InvalidUniProtIDError(AlphaFoldError):
    """Exception raised when UniProt ID is invalid."""
    pass

class UniProtIDNotFoundError(AlphaFoldError):
    """Exception raised when UniProt ID is not found in AlphaFold DB."""
    pass

def validate_uniprot_id(uniprot_id: str) -> bool:
    """
    Validate UniProt ID format.

    Args:
        uniprot_id: UniProt ID to validate

    Returns:
        True if valid, False otherwise
    """
    # UniProt IDs are 6-10 characters long
    if not (6 <= len(uniprot_id) <= 10):
        return False

    # First character is a letter
    if not uniprot_id[0].isalpha():
        return False

    # Remaining characters are alphanumeric
    if not all(c.isalnum() for c in uniprot_id[1:]):
        return False

    return True

def check_uniprot_exists(uniprot_id: str) -> bool:
    """
    Check if a UniProt ID exists in the AlphaFold database.

    Args:
        uniprot_id: UniProt ID to check

    Returns:
        True if exists, False otherwise
    """
    url = f"https://alphafold.ebi.ac.uk/api/prediction/{uniprot_id}"
    response = requests.get(url)
    return response.status_code == 200

def fetch_alphafold_files(uniprot_id: str, output_dir: Optional[str] = None) -> Dict[str, Any]:
    """
    Fetch PDB, CIF, and PAE JSON files from AlphaFold database.

    Args:
        uniprot_id: UniProt ID to fetch files for
        output_dir: Directory to save files in. If None, uses current directory.

    Returns:
        Dictionary containing:
        - success: bool indicating if fetch was successful
        - pdb_path: Path to saved PDB file
        - cif_path: Path to saved CIF file
        - pae_path: Path to saved PAE JSON file
        - confidence_score: Confidence score from PAE data
        - error: error message if fetch failed
    """
    try:
        logger.info(f"Starting AlphaFold retrieval for UniProt ID: {uniprot_id}")

        # Validate UniProt ID
        if not validate_uniprot_id(uniprot_id):
            error_msg = f"Invalid UniProt ID format: {uniprot_id}"
            logger.error(error_msg)
            raise InvalidUniProtIDError(error_msg)

        # Check if UniProt ID exists
        logger.info(f"Checking if UniProt ID exists in AlphaFold database: {uniprot_id}")
        if not check_uniprot_exists(uniprot_id):
            error_msg = f"UniProt ID not found in AlphaFold database: {uniprot_id}"
            logger.error(error_msg)
            raise UniProtIDNotFoundError(error_msg)

        # Create output directory if needed
        if output_dir is None:
            output_dir = os.path.join(os.getcwd(), "alphafold_output")
        os.makedirs(output_dir, exist_ok=True)
        logger.info(f"Using output directory: {output_dir}")

        # Fetch and save PDB file
        pdb_url = f"https://alphafold.ebi.ac.uk/files/AF-{uniprot_id}-F1-model_v4.pdb"
        logger.info(f"Fetching PDB file from: {pdb_url}")
        pdb_response = requests.get(pdb_url)
        if pdb_response.status_code != 200:
            error_msg = f"Failed to fetch PDB file: {pdb_response.status_code} - {pdb_response.text}"
            logger.error(error_msg)
            raise AlphaFoldError(error_msg)
        pdb_path = os.path.join(output_dir, f"{uniprot_id}.pdb")
        with open(pdb_path, "w") as f:
            f.write(pdb_response.text)
        logger.info(f"Saved PDB file to: {pdb_path}")

        # Fetch and save CIF file
        cif_url = f"https://alphafold.ebi.ac.uk/files/AF-{uniprot_id}-F1-model_v4.cif"
        logger.info(f"Fetching CIF file from: {cif_url}")
        cif_response = requests.get(cif_url)
        if cif_response.status_code != 200:
            error_msg = f"Failed to fetch CIF file: {cif_response.status_code} - {cif_response.text}"
            logger.error(error_msg)
            raise AlphaFoldError(error_msg)
        cif_path = os.path.join(output_dir, f"{uniprot_id}.cif")
        with open(cif_path, "w") as f:
            f.write(cif_response.text)
        logger.info(f"Saved CIF file to: {cif_path}")

        # Fetch and save PAE JSON
        pae_url = f"https://alphafold.ebi.ac.uk/files/AF-{uniprot_id}-F1-predicted_aligned_error_v4.json"
        logger.info(f"Fetching PAE JSON from: {pae_url}")
        pae_response = requests.get(pae_url)
        if pae_response.status_code != 200:
            error_msg = f"Failed to fetch PAE JSON: {pae_response.status_code} - {pae_response.text}"
            logger.error(error_msg)
            raise AlphaFoldError(error_msg)
        pae_path = os.path.join(output_dir, f"{uniprot_id}_pae.json")
        with open(pae_path, "w") as f:
            json.dump(pae_response.json(), f, indent=2)
        logger.info(f"Saved PAE JSON to: {pae_path}")

        # Calculate confidence score from PAE data
        pae_data = pae_response.json()
        try:
            if isinstance(pae_data, dict) and "predicted_aligned_error" in pae_data:
                pae_matrix = pae_data["predicted_aligned_error"]
                if isinstance(pae_matrix, list) and all(isinstance(row, list) for row in pae_matrix):
                    max_pae = max(max(float(val) for val in row) for row in pae_matrix)
                    confidence_score = 1.0 - (max_pae / 31.0)  # Normalize PAE to [0,1]
                else:
                    confidence_score = 0.0  # Default if matrix structure is invalid
            else:
                confidence_score = 0.0  # Default if expected keys not found
            logger.info(f"Calculated confidence score: {confidence_score}")
        except (TypeError, ValueError) as e:
            logger.warning(f"Error calculating confidence score: {e}. Using default value.")
            confidence_score = 0.0

        return {
            "success": True,
            "pdb_path": pdb_path,
            "cif_path": cif_path,
            "pae_path": pae_path,
            "confidence_score": confidence_score
        }

    except (InvalidUniProtIDError, UniProtIDNotFoundError, AlphaFoldError) as e:
        logger.error(f"AlphaFold retrieval failed: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }
    except Exception as e:
        logger.error(f"Unexpected error during AlphaFold retrieval: {str(e)}")
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }