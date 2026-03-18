# Agent Workflow Builder
# A CLI tool for automatically setting up AI agent workflows
# Package initialization

__version__ = "1.0.0"
__author__ = "eentost"
__all__ = ["main", "init_project", "generate_workflow", "validate_config", "dockerize"]

from .agent_workflow_builder import main
