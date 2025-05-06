import os
import logging
from typing import List, Optional, Dict, Any

def extract_backbone(input_pdb: str, output_pdb: Optional[str] = None) -> Dict[str, Any]:
    """
    Extract backbone atoms (N, CA, C, O) from a PDB file.

    Args:
        input_pdb (str): Path to the input PDB file
        output_pdb (Optional[str]): Path to the output PDB file. If None, will use input filename with '_backbone' suffix.

    Returns:
        Dict[str, Any]: A dictionary containing:
            - success (bool): Whether the operation was successful
            - output_pdb (str): Path to the output PDB file (if successful)
            - error (str): Error message (if unsuccessful)
    """
    # Initialize response dictionary
    response = {
        "success": False,
        "output_pdb": None,
        "error": None
    }

    # Validate input file
    if not os.path.exists(input_pdb):
        response["error"] = f"Input PDB file not found: {input_pdb}"
        return response

    # Set default output path if not provided
    if output_pdb is None:
        base_name = os.path.splitext(input_pdb)[0]
        output_pdb = f"{base_name}_backbone.pdb"

    # Backbone atom names to keep
    backbone_atoms = {'N', 'CA', 'C', 'O'}

    try:
        # First pass: validate PDB format
        has_valid_atom = False
        with open(input_pdb, 'r') as infile:
            for line in infile:
                if line.startswith(('ATOM', 'HETATM')):
                    if len(line) >= 16:  # Minimum length for atom name field
                        has_valid_atom = True
                        break

        if not has_valid_atom:
            response["error"] = "Invalid PDB format: no valid ATOM records found"
            return response

        # Second pass: extract backbone atoms
        with open(input_pdb, 'r') as infile, open(output_pdb, 'w') as outfile:
            # Copy header lines (REMARK, TITLE, etc.)
            for line in infile:
                if line.startswith(('REMARK', 'TITLE', 'EXPDTA', 'AUTHOR', 'REVDAT', 'JRNL', 'SEQRES')):
                    outfile.write(line)
                elif line.startswith('ATOM') or line.startswith('HETATM'):
                    # Check if this is a backbone atom
                    atom_name = line[12:16].strip()
                    if atom_name in backbone_atoms:
                        outfile.write(line)
                elif line.startswith('END'):
                    outfile.write(line)
                    break

        logging.info(f"Backbone atoms extracted to: {output_pdb}")
        response["success"] = True
        response["output_pdb"] = output_pdb
        return response

    except Exception as e:
        error_msg = f"Failed to extract backbone: {str(e)}"
        logging.error(error_msg)
        response["error"] = error_msg
        if os.path.exists(output_pdb):
            try:
                os.remove(output_pdb)
            except:
                pass
        return response

def main():
    """Command line interface for extract_backbone."""
    import argparse

    parser = argparse.ArgumentParser(description='Extract backbone atoms from a PDB file')
    parser.add_argument('input_pdb', help='Path to input PDB file')
    parser.add_argument('-o', '--output', help='Path to output PDB file (optional)')

    args = parser.parse_args()

    result = extract_backbone(args.input_pdb, args.output)
    if result["success"]:
        print(f"Successfully extracted backbone to: {result['output_pdb']}")
        return 0
    else:
        print(f"Error: {result['error']}")
        return 1

if __name__ == '__main__':
    main()