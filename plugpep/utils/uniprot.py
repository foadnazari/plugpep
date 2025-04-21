"""UniProt API utilities."""

import requests
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

def search_uniprot(query: str) -> Optional[Dict[str, Any]]:
    """Search UniProt for a protein and return its information.

    Args:
        query: Protein name or description to search for

    Returns:
        Dictionary containing UniProt ID, name, and organism if found, None otherwise
    """
    try:
        # Clean up the query
        query = query.replace("Receptor", "").strip()  # Remove "Receptor" as it's too generic

        # Construct the search URL
        base_url = "https://rest.uniprot.org/uniprotkb/search"
        params = {
            "query": f"{query} AND reviewed:true AND organism_id:9606",  # Human proteins only, reviewed
            "format": "json",
            "fields": "accession,id,protein_name,organism_name,gene_names,length,sequence",
            "size": 1
        }

        # Make the request
        response = requests.get(base_url, params=params)
        response.raise_for_status()

        # Parse the response
        data = response.json()

        # Check if we got any results
        if data["results"]:
            result = data["results"][0]
            return {
                "uniprot_id": result["primaryAccession"],
                "target_name": result["proteinName"],
                "organism": result["organismName"],
                "gene_names": result.get("geneNames", ""),
                "length": result.get("length", 0),
                "sequence": result.get("sequence", {}).get("value", "")
            }

        # If no results with human proteins, try without organism filter
        params["query"] = f"{query} AND reviewed:true"
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()

        if data["results"]:
            result = data["results"][0]
            return {
                "uniprot_id": result["primaryAccession"],
                "target_name": result["proteinName"],
                "organism": result["organismName"],
                "gene_names": result.get("geneNames", ""),
                "length": result.get("length", 0),
                "sequence": result.get("sequence", {}).get("value", "")
            }

        return None

    except Exception as e:
        logger.error(f"Error searching UniProt: {str(e)}")
        return None
