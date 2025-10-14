#!/usr/bin/env python3
"""
Personal AI Agent - Main Entry Point

A fully functional personal AI agent with no restrictions.
"""

import sys
import argparse
import logging
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent))

from agent.personal_agent import PersonalAgent
from utils.config import load_config
from utils.logger import setup_logger


def main():
    """Main entry point for the personal AI agent."""
    parser = argparse.ArgumentParser(description="Personal AI Agent")
    parser.add_argument(
        "--config", 
        type=str, 
        default="config/config.json",
        help="Path to configuration file"
    )
    parser.add_argument(
        "--debug", 
        action="store_true",
        help="Enable debug logging"
    )
    parser.add_argument(
        "--interactive", 
        action="store_true",
        help="Run in interactive mode"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    setup_logger(level=log_level)
    logger = logging.getLogger(__name__)
    
    try:
        # Load configuration
        config = load_config(args.config)
        logger.info("Configuration loaded successfully")
        
        # Initialize the agent
        agent = PersonalAgent(config)
        logger.info("Personal AI Agent initialized")
        
        if args.interactive:
            run_interactive_mode(agent)
        else:
            # Default behavior - can be extended
            print("Personal AI Agent is ready!")
            print("Use --interactive flag to start interactive mode")
            
    except Exception as e:
        logger.error(f"Failed to start agent: {e}")
        sys.exit(1)


def run_interactive_mode(agent):
    """Run the agent in interactive mode."""
    print("=== Personal AI Agent - Interactive Mode ===")
    print("Type 'quit' or 'exit' to stop the agent")
    print("=" * 45)
    
    while True:
        try:
            user_input = input("\nYou: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("Agent: Goodbye! Have a great day!")
                break
                
            if not user_input:
                continue
                
            # Get response from agent
            response = agent.chat(user_input)
            print(f"Agent: {response}")
            
        except KeyboardInterrupt:
            print("\n\nAgent: Goodbye! Have a great day!")
            break
        except Exception as e:
            print(f"Agent: Sorry, I encountered an error: {e}")


if __name__ == "__main__":
    main()