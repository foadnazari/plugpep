# Protein Structure Analysis Agent

This project implements an AI agent that helps identify UniProt IDs from protein names/information, retrieves AlphaFold structure files, and generates protein backbone structures.

## Features

- **UniProt ID Identification**: Automatically identifies UniProt IDs from protein names or descriptions
- **AlphaFold Structure Retrieval**: Downloads protein structure files from the AlphaFold database
- **Backbone Extraction**: Generates simplified backbone structures from full protein models

## Prerequisites

- Python 3.9 or higher
- Google Cloud account with access to Gemini API
- Internet connection for AlphaFold database access

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Create and activate a virtual environment:
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/MacOS
python -m venv .venv
source .venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file in the project root with your Google API key:
```
GOOGLE_API_KEY=your_api_key_here
```

## Project Structure

```
.
├── multi_tool_agent/
│   ├── __init__.py
│   ├── agent.py              # Main agent implementation
│   ├── alphafold_retrieve.py # AlphaFold file retrieval module
│   └── extract_backbone.py   # Backbone extraction module
├── alphafold_output/         # Directory for downloaded AlphaFold files
├── backbone_output/          # Directory for generated backbone structures
├── requirements.txt
└── .env                      # Environment variables (not tracked in git)
```

## Usage

1. Run the agent:
```bash
adk run multi_tool_agent
```

2. Interact with the agent by providing protein names or descriptions. For example:
```
> What is the UniProt ID for human insulin?
```

The agent will:
1. Identify the UniProt ID
2. Download the corresponding AlphaFold structure
3. Generate the backbone structure
4. Save the files in their respective output directories

## Output Files

- **AlphaFold Files**: Saved in `alphafold_output/`
  - Full protein structure files in PDB format
  - Additional metadata files

- **Backbone Files**: Saved in `backbone_output/`
  - Simplified backbone structures in PDB format
  - Contains only the main chain atoms

## Development

### Adding New Features

1. Create new tool functions in the appropriate module
2. Add the function to the `tools` list in `agent.py`
3. Update the agent's instruction to include the new capability

### Testing

To test the agent:
1. Ensure all dependencies are installed
2. Set up your API key in `.env`
3. Run the agent and test with various protein queries

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[Add your license information here]

## Acknowledgments

- Google ADK for the agent framework
- AlphaFold team for the protein structure database
- UniProt for protein information 