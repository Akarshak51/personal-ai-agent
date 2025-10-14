"""
Configuration utilities for the Personal AI Agent.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional


def load_config(config_path: str) -> Dict[str, Any]:
    """
    Load configuration from JSON file.
    
    Args:
        config_path: Path to the configuration file
        
    Returns:
        Configuration dictionary
        
    Raises:
        FileNotFoundError: If config file doesn't exist
        json.JSONDecodeError: If config file is invalid JSON
    """
    config_file = Path(config_path)
    
    if not config_file.exists():
        # Try to use example config if main config doesn't exist
        example_config = config_file.parent / 'config.example.json'
        if example_config.exists():
            logging.warning(f"Config file {config_path} not found. Using example config.")
            config_file = example_config
        else:
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
            
        # Apply default values if needed
        config = apply_defaults(config)
        
        logging.info(f"Configuration loaded from {config_file}")
        return config
        
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(f"Invalid JSON in config file {config_file}: {e}")


def apply_defaults(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Apply default values to configuration.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Configuration with defaults applied
    """
    defaults = {
        'agent': {
            'name': 'Personal AI Agent',
            'version': '1.0.0',
            'personality': {
                'style': 'helpful',
                'tone': 'friendly',
                'verbosity': 'balanced'
            }
        },
        'memory': {
            'memory_dir': 'data/memory',
            'max_context_length': 10,
            'memory_retention_days': 30
        },
        'nlp': {
            'language': 'en',
            'sentiment_analysis': True,
            'intent_recognition': True
        },
        'logging': {
            'level': 'INFO',
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        }
    }
    
    # Merge defaults with provided config
    merged_config = merge_dict(defaults, config)
    return merged_config


def merge_dict(default: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recursively merge two dictionaries.
    
    Args:
        default: Default dictionary
        override: Override dictionary
        
    Returns:
        Merged dictionary
    """
    result = default.copy()
    
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dict(result[key], value)
        else:
            result[key] = value
            
    return result


def save_config(config: Dict[str, Any], config_path: str) -> None:
    """
    Save configuration to JSON file.
    
    Args:
        config: Configuration dictionary
        config_path: Path to save the configuration
    """
    config_file = Path(config_path)
    config_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
        
    logging.info(f"Configuration saved to {config_file}")


def get_config_value(config: Dict[str, Any], key_path: str, default: Any = None) -> Any:
    """
    Get configuration value using dot notation.
    
    Args:
        config: Configuration dictionary
        key_path: Dot-separated key path (e.g., 'agent.personality.style')
        default: Default value if key not found
        
    Returns:
        Configuration value or default
    """
    keys = key_path.split('.')
    value = config
    
    try:
        for key in keys:
            value = value[key]
        return value
    except (KeyError, TypeError):
        return default