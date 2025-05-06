
from google.adk.agents import Agent
from . import alphafold_retrieve
from . import extract_backbone


root_agent = Agent(
    name="uniprot_id_identifier",
    model="gemini-2.0-flash",
    description=(
        "Agent to identify the uniprot id from the given protein name/information, retrieve the alphafold files and generate the backbone of the protein."
    ),
    instruction=(
        "You are a helpful agent who can identify the uniprot id from the given protein name/information."
        "You will be given a protein name/information and you will need to identify the specific protein being referenced and return the uniprot id."
        "You will use the uniprot id that you have identified to fetch the alphafold files from the alphafold database and save them to the output folder."
        "You will also use the alphafold pdb files to generate the backbone of the protein."
        "you should save the backbone pdb file to the output folder."
    ),
    tools=[alphafold_retrieve.fetch_alphafold_files, extract_backbone.extract_backbone],
)
