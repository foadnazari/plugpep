from dataclasses import dataclass, field
from typing import Optional, Dict, List, Any
from pathlib import Path

@dataclass
class AgentConfig:
    """Main configuration for the protein binder design agent."""
    # Paths
    output_dir: str = "output"
    log_dir: str = "logs"

    # Agent-specific settings
    max_retries: int = 3
    timeout: int = 300
    debug: bool = False

    def __post_init__(self):
        """Initialize paths."""
        # Create output and log directories
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        Path(self.log_dir).mkdir(parents=True, exist_ok=True)

    @classmethod
    def from_dict(cls, config_dict: Dict) -> 'AgentConfig':
        """Create configuration from a dictionary."""
        return cls(
            output_dir=config_dict.get('output_dir', 'output'),
            log_dir=config_dict.get('log_dir', 'logs'),
            max_retries=config_dict.get('max_retries', 3),
            timeout=config_dict.get('timeout', 300),
            debug=config_dict.get('debug', False)
        )

    def to_dict(self) -> Dict:
        """Convert configuration to dictionary."""
        return {
            'output_dir': self.output_dir,
            'log_dir': self.log_dir,
            'max_retries': self.max_retries,
            'timeout': self.timeout,
            'debug': self.debug
        }

    def save(self, path: str) -> None:
        """Save configuration to a JSON file."""
        import json
        with open(path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load(cls, path: str) -> 'AgentConfig':
        """Load configuration from a JSON file."""
        import json
        with open(path) as f:
            config_dict = json.load(f)
        return cls.from_dict(config_dict)
