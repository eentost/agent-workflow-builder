# Agent Workflow Builder

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A command-line tool for automatically setting up and generating AI agent workflows using YAML configuration files.

## Features

- **YAML-based Configuration** - Define complex agent workflows in simple YAML files
- **Multiple Agent Types** - Support for Web Scraper, Security Scanner, LLM Agent, and Data Pipeline agents
- **Docker-ready** - Auto-generate Dockerfile and docker-compose.yml for containerized deployment
- **Template System** - Built-in templates for common use cases
- **Validation** - Validate workflow configurations before deployment
- **CLI Tool** - Easy-to-use command-line interface with install via pip

## Installation

### From Source

```bash
git clone https://github.com/eentost/agent-workflow-builder.git
cd agent-workflow-builder
pip install -e .
```

### From PyPI (coming soon)

```bash
pip install agent-workflow-builder
```

### Requirements

- Python 3.8+
- pip
- (Optional) Docker for containerized deployment

## Quick Start

```bash
# Initialize a new workflow project
awb init my_project

# Generate a workflow from config
awb generate examples/web_scraper_pipeline.yaml --output ./my_project

# Validate a workflow configuration
awb validate examples/web_scraper_pipeline.yaml

# Generate Docker configuration
awb dockerize my_project/
```

## CLI Commands

| Command | Description |
|---------|-------------|
| `awb init <project_name>` | Initialize a new agent workflow project |
| `awb generate <config.yaml> --output <dir>` | Generate workflow from YAML config |
| `awb validate <config.yaml>` | Validate a workflow configuration file |
| `awb dockerize <project_dir>` | Generate Dockerfile and docker-compose for a project |
| `awb list-templates` | List available workflow templates |
| `awb new-config <type>` | Create a new config from a template |

## Configuration

Workflows are defined in YAML files. Here's the structure:

```yaml
name: my-agent-workflow
version: "1.0"
description: Description of your workflow
agents:
  - name: scraper
    type: web_scraper
    config:
      target_url: https://example.com
      output_format: json
  - name: analyzer
    type: security_scanner
    config:
      scan_type: port_scan
      target: localhost
output:
  format: json
  path: ./results
```

## Available Agent Types

### 1. Web Scraper Agent
Extract data from websites automatically.

```yaml
agents:
  - name: scraper
    type: web_scraper
    config:
      target_url: https://target-site.com
      output_format: json
      rate_limit: 10
      follow_links: true
```

### 2. Security Scanner Agent
Run security scans on targets.

```yaml
agents:
  - name: scanner
    type: security_scanner
    config:
      scan_type: port_scan
      target: 192.168.1.1
      ports: "1-1000"
      output: nmap
```

### 3. LLM Agent
Run large language model tasks.

```yaml
agents:
  - name: llm
    type: llm_agent
    config:
      model: gpt-4
      task: text_analysis
      input_source: ./data/input.txt
```

### 4. Data Pipeline Agent
Process and transform data.

```yaml
agents:
  - name: pipeline
    type: data_pipeline
    config:
      input_path: ./data/raw
      output_path: ./data/processed
      operations:
        - type: filter
        - type: transform
```

## Project Structure

```
agent-workflow-builder/
├── src/
│   └── agent_workflow_builder.py  # Main CLI tool
├── examples/
│   ├── web_scraper_pipeline.yaml  # Web scraper example
│   └── security_scanner_pipeline.yaml
├── pyproject.toml                  # Project configuration
├── requirements.txt                # Dependencies
├── README.md                       # This file
├── LICENSE                         # MIT License
└── .gitignore                      # Git ignore rules
```

## Development

```bash
# Install in development mode
pip install -e ".[dev]"

# Run linter
pylint src/

# Run security checks
bandit -r src/
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## Author

**eentost** - [GitHub](https://github.com/eentost)

## Support

- Create an issue on [GitHub](https://github.com/eentost/agent-workflow-builder/issues)
- Star the repo if you find it useful!
