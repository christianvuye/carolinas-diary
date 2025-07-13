# MCP (Model Context Protocol) Integration Guide for Carolina's Diary

## Overview

This guide outlines how to integrate Model Context Protocol (MCP) servers with the Carolina's Diary project to provide AI agents with comprehensive context about the codebase, data, and development environment. MCP enables standardized access to external data sources and tools, transforming your development workflow into an AI-native environment.

## What is MCP?

Model Context Protocol (MCP) is an open standard developed by Anthropic for connecting AI agents to external data sources and tools. It provides a unified interface that replaces fragmented custom integrations with a standardized protocol.

### Key Benefits
- [ ] **Unified Context Access**: Single protocol for all external integrations
- [ ] **Rich Project Understanding**: AI agents access database schemas, code structure, git history
- [ ] **Standardized Interface**: Consistent way to access different types of context
- [ ] **Enhanced AI Assistance**: More informed recommendations and code generation
- [ ] **Reduced Integration Complexity**: No need for custom integrations per data source

## Essential MCP Servers for Carolina's Diary

### 1. Database & Storage Context

#### SQLite MCP Server ⭐ **PRIORITY**
**Purpose**: Direct access to your `carolinas_diary.db` database
**Benefits**:
- [ ] Query journal entries, users, and metadata in natural language
- [ ] Schema inspection and relationship mapping
- [ ] Safe read-only access with query validation
- [ ] Understanding of data patterns and relationships

**Installation**:
```bash
uvx mcp-server-sqlite --db-path ./backend/carolinas_diary.db
```

**Configuration**:
```json
{
  "sqlite": {
    "command": "uvx",
    "args": ["mcp-server-sqlite", "--db-path", "./backend/carolinas_diary.db", "--readonly"]
  }
}
```

#### PostgreSQL MCP Server
**Purpose**: Future-proofing for database migration
**Benefits**:
- [ ] When you eventually scale beyond SQLite
- [ ] Advanced querying capabilities
- [ ] Schema inspection for complex relationships

**Installation**:
```bash
npx @modelcontextprotocol/server-postgres
```

### 2. Codebase Understanding

#### Filesystem MCP Server ⭐ **PRIORITY**
**Purpose**: Secure access to project files and structure
**Benefits**:
- [ ] Read configuration files, documentation, and code
- [ ] Understand project structure and dependencies
- [ ] Access to both frontend and backend codebases
- [ ] Configurable access controls for security

**Installation**:
```bash
npx @modelcontextprotocol/server-filesystem /path/to/carolinas-diary
```

**Configuration**:
```json
{
  "filesystem": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/carolinas-diary"],
    "env": {
      "ALLOWED_EXTENSIONS": ".py,.ts,.tsx,.js,.json,.md,.yml,.yaml"
    }
  }
}
```

#### Git MCP Server ⭐ **PRIORITY**
**Purpose**: Version control context and development history
**Benefits**:
- [ ] Access commit history and branch information
- [ ] Understand recent changes and development patterns
- [ ] Track architectural decisions over time
- [ ] Analyze development velocity and patterns

**Installation**:
```bash
uvx mcp-server-git --repository /path/to/carolinas-diary
```

**Configuration**:
```json
{
  "git": {
    "command": "uvx",
    "args": ["mcp-server-git", "--repository", "/path/to/carolinas-diary"]
  }
}
```

#### GitHub MCP Server
**Purpose**: Repository management and collaboration context
**Benefits**:
- [ ] Access issues, pull requests, and project metadata
- [ ] Understand development workflow and collaboration patterns
- [ ] Integration with CI/CD pipeline context
- [ ] Project management insights

**Installation**:
```bash
npx @modelcontextprotocol/server-github
```

**Configuration**:
```json
{
  "github": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-github"],
    "env": {
      "GITHUB_PERSONAL_ACCESS_TOKEN": "<YOUR_TOKEN>"
    }
  }
}
```

### 3. Development Environment Context

#### Memory MCP Server ⭐ **PRIORITY**
**Purpose**: Persistent knowledge graph for project-specific information
**Benefits**:
- [ ] Store and retrieve project-specific knowledge
- [ ] Build institutional memory across development sessions
- [ ] Track decisions and their rationale
- [ ] Maintain context between AI interactions

**Installation**:
```bash
npx @modelcontextprotocol/server-memory
```

**Configuration**:
```json
{
  "memory": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-memory"]
  }
}
```

#### Code Analysis MCP Server
**Purpose**: Deep codebase understanding and analysis
**Benefits**:
- [ ] Natural language exploration of code relationships
- [ ] Data flow analysis and architectural insights
- [ ] Pattern recognition across the codebase
- [ ] Understanding of business logic and dependencies

**Installation**:
```bash
git clone https://github.com/saiprashanths/code-analysis-mcp.git
cd code-analysis-mcp
```

**Configuration**:
```json
{
  "code-analysis": {
    "command": "uv",
    "args": ["--directory", "/path/to/code-analysis-mcp", "run", "code_analysis.py"]
  }
}
```

### 4. API & Backend Context

#### FastAPI Integration MCP Server (Custom)
**Purpose**: Backend API context and monitoring
**Benefits**:
- [ ] Understand API endpoints and their relationships
- [ ] Access request/response schemas
- [ ] Monitor API usage patterns and performance
- [ ] Real-time backend status and metrics

**Implementation Strategy**:
```python
# Custom MCP server for FastAPI integration
from fastmcp import FastMCP
from backend.main import app as fastapi_app

mcp_server = FastMCP("Carolina's Diary API Context")

@mcp_server.tool
def get_api_endpoints() -> dict:
    """Get all available API endpoints with their schemas"""
    routes = []
    for route in fastapi_app.routes:
        if hasattr(route, 'methods'):
            routes.append({
                'path': route.path,
                'methods': list(route.methods),
                'name': route.name
            })
    return {"endpoints": routes}

@mcp_server.tool
def get_database_schema() -> dict:
    """Get current database schema information"""
    from backend.models import Base
    tables = {}
    for table in Base.metadata.tables.values():
        tables[table.name] = {
            'columns': [str(col) for col in table.columns],
            'relationships': [str(rel) for rel in table.foreign_keys]
        }
    return {"schema": tables}
```

#### OpenAPI MCP Server
**Purpose**: API documentation and contract context
**Benefits**:
- [ ] Auto-generate and access OpenAPI specifications
- [ ] Understand API contracts and dependencies
- [ ] Validate API changes against specifications
- [ ] Frontend-backend interface documentation

**Installation**:
```bash
# Community-maintained OpenAPI MCP servers
npm install -g mcp-server-openapi
```

## MCP Server Configuration

### Claude Desktop Configuration
Create or update `claude_desktop_config.json`:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "sqlite": {
      "command": "uvx",
      "args": ["mcp-server-sqlite", "--db-path", "./backend/carolinas_diary.db", "--readonly"]
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/Users/username/Projects/carolinas-diary"],
      "env": {
        "ALLOWED_EXTENSIONS": ".py,.ts,.tsx,.js,.json,.md,.yml,.yaml"
      }
    },
    "git": {
      "command": "uvx",
      "args": ["mcp-server-git", "--repository", "/Users/username/Projects/carolinas-diary"]
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "<YOUR_TOKEN>"
      }
    },
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"]
    },
    "code-analysis": {
      "command": "uv",
      "args": ["--directory", "/Users/username/Projects/code-analysis-mcp", "run", "code_analysis.py"]
    }
  }
}
```

### Cursor MCP Configuration
Create or update `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "carolina-diary-sqlite": {
      "command": "uvx",
      "args": ["mcp-server-sqlite", "--db-path", "./backend/carolinas_diary.db", "--readonly"]
    },
    "carolina-diary-filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/carolinas-diary"]
    },
    "carolina-diary-git": {
      "command": "uvx",
      "args": ["mcp-server-git", "--repository", "/path/to/carolinas-diary"]
    }
  }
}
```

### Custom MCP Server for Project-Specific Context
Create `mcp_server.py` in the project root:

```python
#!/usr/bin/env python3
"""
Custom MCP Server for Carolina's Diary
Provides project-specific context and tools
"""

from fastmcp import FastMCP
import json
import os
from pathlib import Path
from typing import Dict, Any

# Initialize the MCP server
mcp = FastMCP("Carolina's Diary Context")

@mcp.tool
def get_project_structure() -> Dict[str, Any]:
    """Get the overall project structure and key files"""
    structure = {
        "backend": {
            "main_files": ["main.py", "models.py", "schemas.py", "auth.py"],
            "database": "carolinas_diary.db",
            "tests": "tests/",
            "migrations": "migrate_database.py"
        },
        "frontend": {
            "main_files": ["App.tsx", "index.tsx"],
            "components": "src/components/",
            "services": "src/services/",
            "hooks": "src/hooks/"
        },
        "deployment": {
            "ci_cd": ".github/workflows/",
            "docker": "Containerization ready",
            "netlify": "netlify.toml"
        }
    }
    return structure

@mcp.tool
def get_backend_api_info() -> Dict[str, Any]:
    """Get information about the FastAPI backend"""
    return {
        "framework": "FastAPI",
        "database": "SQLite with SQLAlchemy",
        "authentication": "Firebase Auth",
        "main_endpoints": [
            "POST /journal-entry",
            "GET /journal-entry/{date}",
            "GET /journal-entries",
            "GET /users/me",
            "POST /users/register"
        ],
        "models": ["User", "JournalEntry", "EmotionQuestion", "GratitudeQuestion", "Quote"]
    }

@mcp.tool
def get_frontend_tech_stack() -> Dict[str, Any]:
    """Get information about the React frontend"""
    return {
        "framework": "React 19.1.0",
        "language": "TypeScript",
        "routing": "React Router DOM",
        "http_client": "Axios",
        "authentication": "Firebase",
        "key_components": [
            "JournalEntry", "EmotionSection", "GratitudeSection",
            "CustomizationPanel", "AllEntries", "Header"
        ],
        "pwa": "Progressive Web App with offline support"
    }

@mcp.tool
def get_development_workflow() -> Dict[str, Any]:
    """Get information about the development workflow and CI/CD"""
    return {
        "ci_cd": "GitHub Actions",
        "backend_ci": "Python testing, linting (flake8, black, isort), security scans",
        "frontend_ci": "Node.js testing, TypeScript checking, ESLint, Prettier",
        "security": "CodeQL, dependency scanning, Trivy, Gitleaks",
        "deployment": "Netlify for frontend, Backend containerization ready",
        "testing": "pytest for backend, React Testing Library for frontend"
    }

@mcp.resource
def project_readme() -> str:
    """Get the project README content"""
    readme_path = Path("README.md")
    if readme_path.exists():
        return readme_path.read_text()
    return "README.md not found"

if __name__ == "__main__":
    mcp.run()
```

## Implementation Roadmap

### Phase 1: Essential Context Setup (Week 1)
- [ ] **Install and configure SQLite MCP Server**
  - Test database queries and schema inspection
  - Verify read-only access and security
  - Document common query patterns

- [ ] **Set up Filesystem MCP Server**
  - Configure allowed file extensions
  - Test code reading and navigation
  - Verify security boundaries

- [ ] **Deploy Git MCP Server**
  - Access commit history and branch info
  - Test development pattern analysis
  - Verify repository access permissions

- [ ] **Initialize Memory MCP Server**
  - Set up persistent knowledge storage
  - Create initial project knowledge base
  - Test knowledge retrieval and updates

### Phase 2: Development Context Enhancement (Week 2)
- [ ] **Integrate GitHub MCP Server**
  - Connect to repository management
  - Access issues and pull requests
  - Analyze development collaboration patterns

- [ ] **Deploy Code Analysis MCP Server**
  - Set up codebase exploration tools
  - Test natural language code queries
  - Verify architectural analysis capabilities

- [ ] **Create Custom Project MCP Server**
  - Implement project-specific tools
  - Add business logic context
  - Test custom tool functionality

### Phase 3: Advanced Integration (Week 3)
- [ ] **Build FastAPI Integration MCP Server**
  - Connect to backend API context
  - Monitor endpoint usage and performance
  - Integrate with database schema information

- [ ] **Set up OpenAPI MCP Server**
  - Generate API documentation context
  - Validate frontend-backend contracts
  - Test API specification access

- [ ] **Implement CI/CD Context Integration**
  - Connect to GitHub Actions workflows
  - Monitor build and deployment status
  - Integrate with code quality metrics

## Security Implementation

### Authentication & Authorization
- [ ] **Environment Variable Management**
  ```bash
  # .env file for MCP configuration
  GITHUB_TOKEN=your_github_token_here
  MCP_SQLITE_DB_PATH=./backend/carolinas_diary.db
  MCP_ALLOWED_PATHS=/path/to/project,/path/to/docs
  ```

- [ ] **Read-Only Database Access**
  ```bash
  # Always use readonly flag for database servers
  uvx mcp-server-sqlite --db-path ./backend/carolinas_diary.db --readonly
  ```

- [ ] **File System Access Controls**
  ```json
  {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/project"],
      "env": {
        "ALLOWED_EXTENSIONS": ".py,.ts,.tsx,.js,.json,.md,.yml,.yaml",
        "DENIED_PATHS": "node_modules,venv,.git,*.log"
      }
    }
  }
  ```

### Network Security
- [ ] **Local-Only Servers**: Use stdio transport for local development
- [ ] **Token-Based Auth**: For remote MCP servers
- [ ] **HTTPS Only**: For production SSE servers
- [ ] **Rate Limiting**: Prevent abuse of MCP endpoints

### Audit & Monitoring
- [ ] **Request Logging**: Log all MCP server interactions
- [ ] **Access Auditing**: Track what data is accessed by AI agents
- [ ] **Performance Monitoring**: Monitor MCP server response times
- [ ] **Error Tracking**: Capture and analyze MCP server errors

## Testing MCP Integration

### Basic Functionality Tests
```python
# test_mcp_integration.py
import pytest
from mcp import Client

@pytest.mark.asyncio
async def test_sqlite_mcp_server():
    """Test SQLite MCP server functionality"""
    async with Client(server_command=["uvx", "mcp-server-sqlite", "--db-path", "./test.db"]) as client:
        # Test database query
        result = await client.call_tool("query", {"sql": "SELECT COUNT(*) FROM journal_entries"})
        assert "result" in result

@pytest.mark.asyncio
async def test_filesystem_mcp_server():
    """Test Filesystem MCP server functionality"""
    async with Client(server_command=["npx", "-y", "@modelcontextprotocol/server-filesystem", "."]) as client:
        # Test file reading
        result = await client.call_tool("read_file", {"path": "README.md"})
        assert "content" in result

@pytest.mark.asyncio
async def test_git_mcp_server():
    """Test Git MCP server functionality"""
    async with Client(server_command=["uvx", "mcp-server-git", "--repository", "."]) as client:
        # Test commit history
        result = await client.call_tool("get_commit_history", {"limit": 5})
        assert "commits" in result
```

### Integration Tests
```python
# test_ai_agent_context.py
import pytest
from your_ai_agent import CarolinaDiaryAgent

@pytest.mark.asyncio
async def test_agent_understands_database_schema():
    """Test that AI agent can understand and query database schema"""
    agent = CarolinaDiaryAgent()

    response = await agent.query("What tables exist in the database?")
    assert "journal_entries" in response.lower()
    assert "users" in response.lower()

@pytest.mark.asyncio
async def test_agent_understands_codebase_structure():
    """Test that AI agent can navigate and understand codebase"""
    agent = CarolinaDiaryAgent()

    response = await agent.query("What are the main components in the React frontend?")
    assert "journalentry" in response.lower()
    assert "emotionsection" in response.lower()
```

## Monitoring & Observability

### MCP Server Health Monitoring
```python
# mcp_health_monitor.py
import asyncio
import logging
from datetime import datetime
from typing import Dict, List

class MCPHealthMonitor:
    def __init__(self, server_configs: Dict[str, Dict]):
        self.server_configs = server_configs
        self.health_status = {}

    async def check_server_health(self, server_name: str, config: Dict) -> Dict:
        """Check the health of a specific MCP server"""
        try:
            # Test basic connectivity
            async with Client(server_command=config["command"], args=config["args"]) as client:
                # Try a simple operation
                tools = await client.list_tools()
                return {
                    "status": "healthy",
                    "tools_count": len(tools),
                    "last_check": datetime.now().isoformat()
                }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "last_check": datetime.now().isoformat()
            }

    async def monitor_all_servers(self):
        """Monitor health of all configured MCP servers"""
        while True:
            for server_name, config in self.server_configs.items():
                health = await self.check_server_health(server_name, config)
                self.health_status[server_name] = health

                if health["status"] == "unhealthy":
                    logging.error(f"MCP Server {server_name} is unhealthy: {health['error']}")

            await asyncio.sleep(60)  # Check every minute
```

### Usage Analytics
```python
# mcp_analytics.py
from collections import defaultdict
from datetime import datetime
import json

class MCPUsageAnalytics:
    def __init__(self):
        self.usage_stats = defaultdict(int)
        self.tool_usage = defaultdict(int)
        self.response_times = defaultdict(list)

    def record_tool_usage(self, server_name: str, tool_name: str, response_time: float):
        """Record usage of an MCP tool"""
        self.usage_stats[server_name] += 1
        self.tool_usage[f"{server_name}.{tool_name}"] += 1
        self.response_times[f"{server_name}.{tool_name}"].append(response_time)

    def get_usage_report(self) -> Dict:
        """Generate usage analytics report"""
        return {
            "server_usage": dict(self.usage_stats),
            "tool_usage": dict(self.tool_usage),
            "average_response_times": {
                tool: sum(times) / len(times)
                for tool, times in self.response_times.items()
            },
            "generated_at": datetime.now().isoformat()
        }
```

## Troubleshooting Common Issues

### Installation Problems
```bash
# Common MCP server installation issues and solutions

# Issue: uvx not found
# Solution: Install uv first
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc

# Issue: npx permission errors
# Solution: Fix npm permissions
npm config set prefix ~/.npm-global
export PATH=~/.npm-global/bin:$PATH

# Issue: SQLite database access
# Solution: Check file permissions
chmod 644 ./backend/carolinas_diary.db
```

### Configuration Issues
```json
// Common configuration problems and solutions

// Issue: Relative paths not working
// Solution: Use absolute paths
{
  "filesystem": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-filesystem", "/absolute/path/to/project"]
  }
}

// Issue: Environment variables not loading
// Solution: Explicitly set in configuration
{
  "github": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-github"],
    "env": {
      "GITHUB_PERSONAL_ACCESS_TOKEN": "your_token_here"
    }
  }
}
```

### Runtime Issues
```python
# Common runtime problems and debugging

# Issue: MCP server not responding
# Solution: Check server logs and restart
import subprocess
import logging

def restart_mcp_server(server_name: str, config: Dict):
    """Restart an unresponsive MCP server"""
    try:
        # Kill existing process if any
        subprocess.run(["pkill", "-f", server_name], check=False)

        # Wait and restart
        time.sleep(2)
        process = subprocess.Popen(
            [config["command"]] + config["args"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        logging.info(f"Restarted MCP server {server_name} with PID {process.pid}")
        return process

    except Exception as e:
        logging.error(f"Failed to restart MCP server {server_name}: {e}")
        return None
```

## Next Steps

### Immediate Actions (This Week)
1. [ ] **Install essential MCP servers**: SQLite, Filesystem, Git, Memory
2. [ ] **Configure Claude Desktop** with basic MCP server setup
3. [ ] **Test basic functionality** with simple queries and file access
4. [ ] **Set up security boundaries** with read-only access and path restrictions

### Short-term Goals (Next 2 Weeks)
1. [ ] **Add GitHub integration** for repository management context
2. [ ] **Deploy code analysis tools** for deeper codebase understanding
3. [ ] **Create custom project-specific MCP server** with business logic
4. [ ] **Implement monitoring and health checks** for all MCP servers

### Long-term Vision (Next Month)
1. [ ] **Build comprehensive AI development environment** with full context access
2. [ ] **Implement automated context refresh** to keep information current
3. [ ] **Create context-aware CI/CD pipelines** that understand project changes
4. [ ] **Develop project-specific AI agents** that can autonomously work on development tasks

---

*This MCP integration transforms Carolina's Diary from a traditional development project into an AI-native environment where agents have comprehensive understanding of the codebase, data, and development context. The standardized MCP interface enables seamless integration of multiple context sources, creating a unified foundation for advanced AI-assisted development.*
