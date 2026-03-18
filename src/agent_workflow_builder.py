"""
Agent Workflow Builder - CLI Tool
Auto-generate AI agent workflows from YAML configuration.
Supports web automation, data processing, API integrations, and more.
"""

import argparse
import os
import sys
import yaml
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

VERSION = "1.0.0"

# ─────────────────────────────────────────────────────────────────────
# AGENT TYPE TEMPLATES
# ─────────────────────────────────────────────────────────────────────

AGENT_TEMPLATES = {
    "web_automation": {
        "description": "Web scraping, form filling, browser automation",
        "required_tools": ["playwright", "selenium"],
        "docker_base": "python:3.11-slim",
        "extra_packages": ["playwright", "selenium", "beautifulsoup4", "requests"],
        "env_vars": ["HEADLESS=1", "PROXY_URL="],
    },
    "data_processing": {
        "description": "ETL pipelines, data transformation, file processing",
        "required_tools": ["pandas", "pyarrow"],
        "docker_base": "python:3.11-slim",
        "extra_packages": ["pandas", "pyarrow", "openpyxl", "requests"],
        "env_vars": ["INPUT_DIR=/data/input", "OUTPUT_DIR=/data/output"],
    },
    "api_integration": {
        "description": "REST/GraphQL API integration, webhook handling",
        "required_tools": ["httpx", "fastapi"],
        "docker_base": "python:3.11-slim",
        "extra_packages": ["httpx", "fastapi", "uvicorn", "pydantic", "python-dotenv"],
        "env_vars": ["API_KEY=", "BASE_URL=", "WEBHOOK_PORT=8000"],
    },
    "llm_orchestration": {
        "description": "LLM chaining, prompt management, RAG pipelines",
        "required_tools": ["langchain", "openai"],
        "docker_base": "python:3.11-slim",
        "extra_packages": ["langchain", "openai", "chromadb", "sentence-transformers"],
        "env_vars": ["OPENAI_API_KEY=", "LLM_MODEL=gpt-4"],
    },
    "security_scanner": {
        "description": "Vulnerability scanning, security auditing",
        "required_tools": ["nmap", "bandit"],
        "docker_base": "python:3.11-slim",
        "extra_packages": ["bandit", "requests", "beautifulsoup4", "python-nmap"],
        "env_vars": ["SCAN_TARGET=", "REPORT_DIR=/data/reports"],
    },
    "telegram_bot": {
        "description": "Telegram bot for notifications and automation",
        "required_tools": ["python-telegram-bot"],
        "docker_base": "python:3.11-slim",
        "extra_packages": ["python-telegram-bot", "requests", "python-dotenv"],
        "env_vars": ["TELEGRAM_BOT_TOKEN=", "TELEGRAM_CHAT_ID="],
    },
}

WORKFLOW_TYPES = {
    "sequential": "Execute steps in order, one after another",
    "parallel": "Execute steps simultaneously",
    "conditional": "Execute based on condition evaluation",
    "cron": "Schedule-based execution (cron-like)",
    "event_driven": "Trigger-based execution via webhooks",
}

# ─────────────────────────────────────────────────────────────────────
# WORKFLOW STEP CLASS
# ─────────────────────────────────────────────────────────────────────

class WorkflowStep:
    """Represents a single step in an agent workflow."""
    
    def __init__(self, name: str, agent_type: str, config: Dict[str, Any]):
        self.name = name
        self.agent_type = agent_type
        self.config = config
        self.output_dir = f"output/{name}"
    
    def generate_dockerfile(self) -> str:
        """Generate Dockerfile for this step."""
        template = AGENT_TEMPLATES.get(self.agent_type, AGENT_TEMPLATES["api_integration"])
        base = template["docker_base"]
        packages = " ".join(template["extra_packages"])
        
        dockerfile = f"""FROM {base}

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    curl \\
    git \\
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir {packages}

# Copy application files
COPY . .

# Create output directory
RUN mkdir -p /app/output

# Set environment variables
ENV PYTHONUNBUFFERED=1
"""
        for env_var in template["env_vars"]:
            dockerfile += f"ENV {env_var}\n"
        
        dockerfile += f"""
# Health check
HEALTHCHECK --interval=30s --timeout=10s \\
    CMD curl -f http://localhost:8000/health || exit 1

CMD [\"python\", \"main.py\"]
"""
        return dockerfile

    def generate_main_py(self) -> str:
        """Generate main.py for this step."""
        template = AGENT_TEMPLATES.get(self.agent_type, AGENT_TEMPLATES["api_integration"])
        tools = template["required_tools"]
        
        main_py = f"""#!/usr/bin/env python3
\"\"\"{self.name} - {template['description']}\"\"\"\n\nimport os\nimport json\nimport logging\nfrom datetime import datetime\n\nlogging.basicConfig(level=logging.INFO)\nlogger = logging.getLogger(__name__)\n\n"""
        # Add tool imports
        for tool in tools:
            main_py += f"# {tool} integration\n"
        
        main_py += f"""\nSTEP_NAME = \"{self.name}\"\nSTEP_TYPE = \"{self.agent_type}\"\n\ndef health_check():\n    \"\"\"Health check endpoint.\"\"\"\n    return {{\"status\": \"healthy\", \"step\": STEP_NAME}}\n\ndef process():\n    \"\"\"Main processing logic.\"\"\"\n    logger.info(f\"Starting {{STEP_NAME}}...\")\n    
    # Get configuration from environment
    config = os.environ.get(f\"{{STEP_NAME.upper()}}_CONFIG\", \"{{}}\")\n    config = json.loads(config) if config else {{}}\n    
    # TODO: Implement step-specific logic\n    logger.info(f\"Configuration: {{config}}\")\n    
    # Save output
    output_dir = os.path.join(\"/app/output\", STEP_NAME)\n    os.makedirs(output_dir, exist_ok=True)\n    
    output_file = os.path.join(output_dir, f\"result_{{datetime.now().strftime('%Y%m%d_%H%M%S')}}.json\")\n    with open(output_file, \"w\") as f:\n        json.dump({{"step\": STEP_NAME, \"status\": \"completed\", \"timestamp\": datetime.now().isoformat()}}, f, indent=2)\n    
    logger.info(f\"Output saved to {{output_file}}\")\n    return {{\"status\": \"completed\"}}\n\nif __name__ == \"__main__\":\n    process()\n"""
        return main_py

# ─────────────────────────────────────────────────────────────────────
# WORKFLOW CLASS
# ─────────────────────────────────────────────────────────────────────

class Workflow:
    """Represents a complete agent workflow with multiple steps."""
    
    def __init__(self, name: str, workflow_type: str, steps: List[WorkflowStep]):
        self.name = name
        self.workflow_type = workflow_type
        self.steps = steps
    
    def generate_docker_compose(self) -> str:
        """Generate docker-compose.yml for the entire workflow."""
        services = {}
        
        for i, step in enumerate(self.steps):
            services[step.name] = {
                "build": f"./steps/{step.name}",
                "container_name": f"{self.name}_{step.name}",
                "restart": "unless-stopped",
                "volumes": [f"./{self.name}_output/{step.name}:/app/output"],
                "healthcheck": {
                    "test": ["CMD", "curl", "-f", "http://localhost:8000/health"],
                    "interval": "30s",
                    "timeout": "10s",
                    "retries": 3
                }
            }
            
            if self.workflow_type == "parallel":
                services[step.name]["deploy"] = {
                    "resources": {
                        "limits": {"cpus": "0.5", "memory": "512M"}
                    }
                }
        
        compose = {
            "version": "3.8",
            "services": services,
            "networks": {f"{self.name}_net": {"driver": "bridge"}}
        }
        return yaml.dump(compose, default_flow_style=False, sort_keys=Fa
                         
                             def build(self, output_dir: str) -> Path:
        """Build the complete workflow project in the given directory."""
        base = Path(output_dir)
        base.mkdir(parents=True, exist_ok=True)
        
        logger = logging.getLogger(__name__)
        logger.info(f"Building workflow '{self.name}' in {base}")
        
        # Create directory structure
        for step in self.steps:
            step_dir = base / "steps" / step.name
            step_dir.mkdir(parents=True, exist_ok=True)
            
            # Write Dockerfile
            (step_dir / "Dockerfile").write_text(step.generate_dockerfile())
            
            # Write main.py
            (step_dir / "main.py").write_text(step.generate_main_py())
            
            # Write .env.example
            env_example = "# Environment variables for " + step.name + "\n"
            template = AGENT_TEMPLATES.get(step.agent_type, {})
            for env in template.get("env_vars", []):
                env_example += env + "\n"
            (step_dir / ".env.example").write_text(env_example)
        
        # Write docker-compose.yml
        (base / "docker-compose.yml").write_text(self.generate_docker_compose())
        
        # Write workflow.json (metadata)
        metadata = {
            "name": self.name,
            "type": self.workflow_type,
            "created": datetime.now().isoformat(),
            "steps": [
                {"name": s.name, "type": s.agent_type, "config": s.config}
                for s in self.steps
            ]
        }
        (base / "workflow.json").write_text(json.dumps(metadata, indent=2))
        
        # Write README
        readme = f"""# {self.name} - Agent Workflow

Generated by **agent-workflow-builder** v{VERSION}

## Workflow Type: {self.workflow_type}

## Steps
"""
        for step in self.steps:
            template = AGENT_TEMPLATES.get(step.agent_type, {})
            desc = template.get("description", "Custom agent")
            readme += f"\n### {step.name} ({step.agent_type})\n{desc}\n"
        readme += "\n## Quick Start\n\n```bash\n# Build and start all services\ndocker-compose up --build -d\n\n# View logs\ndocker-compose logs -f\n\n# Stop services\ndocker-compose down\n```\n"
        (base / "README.md").write_text(readme)
        
        logger.info(f"Workflow built successfully in {base}")
        return baselse)

# ─────────────────────────────────────────────────────────────────────
# WORKFLOW BUILDER (MAIN CLASS)
# ─────────────────────────────────────────────────────────────────────

class WorkflowBuilder:
    """Main class for parsing config and building workflows."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def parse_config(self, config_path: str) -> Workflow:
        """Parse YAML config and return Workflow object."""
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        name = config.get('name', 'my-workflow')
        workflow_type = config.get('workflow_type', 'sequential')
        
        if workflow_type not in WORKFLOW_TYPES:
            raise ValueError(f"Unknown workflow type: {workflow_type}. "
                           f"Available: {list(WORKFLOW_TYPES.keys())}")
        
        steps = []
        for step_config in config.get('steps', []):
            step_name = step_config.get('name')
            agent_type = step_config.get('type')
            step_config_data = step_config.get('config', {})
            
            if agent_type not in AGENT_TEMPLATES:
                self.logger.warning(
                    f"Unknown agent type '{agent_type}' for step '{step_name}'. "
                    f"Falling back to api_integration template."
                )
            
            steps.append(WorkflowStep(step_name, agent_type, step_config_data))
        
        if not steps:
            raise ValueError("No steps defined in workflow config")
        
        return Workflow(name, workflow_type, steps)

    def build_from_config(self, config_path: str, output_dir: str) -> Path:
        """Parse config and build workflow in one step."""
        workflow = self.parse_config(config_path)
        return workflow.build(output_dir)
    
    def list_agents(self) -> Dict[str, Dict[str, Any]]:
        """Return available agent types and their templates."""
        result = {}
        for name, template in AGENT_TEMPLATES.items():
            result[name] = {
                "description": template["description"],
                "tools": template["required_tools"],
                "packages": template["extra_packages"]
            }
        return result
    
    def generate_sample_config(self, agent_types: List[str], output_path: str):
        """Generate a sample YAML config file."""
        config = {
            "name": "my-agent-workflow",
            "workflow_type": "sequential",
            "version": VERSION,
            "steps": []
        }
        
        for i, agent_type in enumerate(agent_types):
            step = {
                "name": f"step_{i+1}_{agent_type}",
                "type": agent_type,
                "config": {
                    "enabled": True,
                    "timeout": 300,
                    "retry": 3
                }
            }
            config["steps"].append(step)
        
        with open(output_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)
        
        return output_path

# ─────────────────────────────────────────────────────────────────────
# CLI MAIN
# ─────────────────────────────────────────────────────────────────────

def list_workflow_types():
    """Print available workflow types."""
    print("\nAvailable Workflow Types:\n" + "="*50)
    for wtype, desc in WORKFLOW_TYPES.items():
        print(f"  {wtype:20} - {desc}")
    print()

def list_agent_types():
    """Print available agent types."""
    builder = WorkflowBuilder()
    agents = builder.list_agents()
    print("\nAvailable Agent Types:\n" + "="*50)
    for name, info in agents.items():
        print(f"  {name:20} - {info['description']}")
        print(f"    Tools: {', '.join(info['tools'])}")
        print(f"    Packages: {', '.join(info['packages'])}")
        print()

def create_sample(args):
    """Create a sample config file."""
    agent_types = args.types.split(',')
    builder = WorkflowBuilder()
    output = builder.generate_sample_config(agent_types, args.output)
    print(f"Sample config created: {output}")

def build_workflow(args):
    """Build workflow from config."""
    builder = WorkflowBuilder()
    output_dir = builder.build_from_config(args.config, args.output)
    print(f"\nWorkflow built successfully in: {output_dir}")
    print("\nTo run the workflow:")
    print(f"  cd {output_dir}")
    print("  docker-compose up --build -d")
    print("\nTo view logs:")
    print("  docker-compose logs -f")

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog='agent-workflow-builder',
        description='Auto-generate AI agent workflows from YAML configuration.'
    )
    parser.add_argument('-v', '--version', action='version', version=f'%(prog)s {VERSION}')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # List agents
    subparsers.add_parser('agents', help='List available agent types')
    subparsers.add_parser('types', help='List available workflow types')
    
    # Sample config
    sample = subparsers.add_parser('sample', help='Generate sample config file')
    sample.add_argument('-t', '--types', required=True,
                       help='Comma-separated agent types (e.g., web_automation,api_integration)')
    sample.add_argument('-o', '--output', default='workflow.yaml',
                       help='Output file path (default: workflow.yaml)')
    sample.set_defaults(func=create_sample)
    
    # Build
    build = subparsers.add_parser('build', help='Build workflow from config')
    build.add_argument('-c', '--config', required=True,
                      help='Path to YAML config file')
    build.add_argument('-o', '--output', default='workflow-project',
                      help='Output directory (default: workflow-project)')
    build.set_defaults(func=build_workflow)
    
    # Init - creates sample config and project structure
    init = subparsers.add_parser('init', help='Initialize new workflow project')
    init.add_argument('-n', '--name', required=True, help='Project name')
    init.add_argument('-o', '--output', default='.', help='Output directory')
    init.add_argument('-t', '--types', help='Agent types (comma-separated)')
    init.set_defaults(func=init_project)
    
    args = parser.parse_args()
    
    if args.command == 'agents':
        list_agent_types()
    elif args.command == 'types':
        list_workflow_types()
    elif hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()

def init_project(args):
    """Initialize a new workflow project with sample config."""
    output_dir = Path(args.output) / args.name
    
    builder = WorkflowBuilder()
    
    # Default types if not specified
    types = args.types.split(',') if args.types else ['api_integration', 'web_automation']
    
    # Generate sample config
    config_path = output_dir / 'workflow.yaml'
    builder.generate_sample_config(types, str(config_path))
    
    # Build the workflow
    builder.build_from_config(str(config_path), str(output_dir / 'project'))
    
    print(f"\nProject initialized: {output_dir}")
    print("\nNext steps:")
    print(f"  1. Edit the config: {config_path}")
    print(f"  2. Build: python src/agent_workflow_builder.py build -c {config_path}")
    print(f"  3. Run: cd {output_dir}/project && docker-compose up -d")

if __name__ == '__main__':
    main()
