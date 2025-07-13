# Context Engineering for AI-Driven Development

This document outlines comprehensive context engineering recommendations to make Carolina's Diary more amenable to fully automated software development using AI agents and LLM tools.

## Context Engineering Recommendations

### 1. Root-Level CLAUDE.md Configuration

Create `/Carolina's Diary/CLAUDE.md` with comprehensive project context:

```markdown
# Carolina's Diary - AI Development Context

## Tech Stack
- Backend: Python 3.x, FastAPI, SQLite, pytest
- Frontend: React 18, TypeScript, CSS3
- Deployment: Netlify
- Testing: pytest (backend), React Testing Library (frontend)

## Project Structure
- `/backend/` - FastAPI server with SQLite database
- `/frontend/` - React TypeScript SPA
- `/landing/` - Static landing page
- `/local_docs/` - Project documentation
- `/testing/` - Test plans and checklists

## Essential Commands
- Backend: `cd backend && python main.py`
- Frontend: `cd frontend && npm start`
- Backend tests: `cd backend && pytest`
- Frontend tests: `cd frontend && npm test`
- Type checking: `cd frontend && npx tsc --noEmit`
- Backend linting: `cd backend && mypy .`

## Code Conventions
- Python: PEP 8, type hints required
- TypeScript: Strict mode, functional components with hooks
- CSS: BEM naming, custom properties for themes
- Database: SQLAlchemy models in models.py

## Authentication & Security
- Firebase Authentication integration
- CORS configured for localhost development
- No API keys in code (use environment variables)

## Known Issues & Context
- Cold Turkey Blocker interferes with Playwright automation
- PWA functionality implemented for offline use
- Emotion tracking with 13 supported emotions
```

### 2. Component-Specific Context Files

**Backend Context** (`/backend/CLAUDE.md`):
```markdown
# Backend Development Context

## Database Schema
- Users: Firebase UID integration
- Entries: Journal entries with emotions/gratitude
- Customizations: User preferences storage

## API Endpoints
- GET /entries - Fetch user entries
- POST /entries - Create new entry
- Authentication via Firebase tokens

## Development Workflow
1. Always run tests after changes: `pytest`
2. Type check with mypy: `mypy .`
3. Database migrations: `python migrate_database.py`
```

**Frontend Context** (`/frontend/CLAUDE.md`):
```markdown
# Frontend Development Context

## Component Architecture
- AuthContext for Firebase authentication
- Service layer in /services/ for API calls
- Custom hooks in /hooks/ for reusable logic

## Styling Conventions
- CSS modules for component-specific styles
- Global themes in App.css
- Responsive design: mobile-first approach

## State Management
- React Context for auth state
- Local state with useState/useReducer
- API state with custom hooks
```

### 3. Task-Oriented Documentation

**Feature Specifications** (`/specs/`):
```
/specs/
  ├── emotion-tracking.md
  ├── gratitude-practice.md
  ├── customization-system.md
  └── authentication-flow.md
```

**Development Tasks** (`/tasks/`):
```
/tasks/
  ├── current-sprint.md
  ├── technical-debt.md
  └── bug-fixes.md
```

### 4. Enhanced Testing Context

**Comprehensive Test Documentation** (`/testing/CLAUDE.md`):
```markdown
# Testing Strategy Context

## Test Commands
- Backend unit tests: `cd backend && pytest --cov=.`
- Frontend tests: `cd frontend && npm test -- --coverage`
- E2E tests: Configure Playwright with headless mode

## Test Patterns
- Mock Firebase auth in tests
- Use factories for test data
- Isolate database state between tests

## Coverage Requirements
- Backend: >90% coverage
- Frontend: >85% coverage
- Critical paths: 100% coverage
```

### 5. Autonomous Development Workflows

**Development Context** (`/development/CLAUDE.md`):
```markdown
# Autonomous Development Guidelines

## Pre-Development Checklist
1. Read relevant CLAUDE.md files
2. Check current branch status
3. Review recent commits for context
4. Understand the specific feature/bug

## Development Process
1. Write tests first (TDD approach)
2. Implement minimal viable solution
3. Run all tests and type checking
4. Update documentation if needed

## Definition of Done
- [ ] Tests pass (backend and frontend)
- [ ] Type checking passes
- [ ] No linting errors
- [ ] Feature tested manually
- [ ] Documentation updated
```

### 6. Context Memory System

**Session Context** (`/context/current-session.md`):
```markdown
# Current Development Session

## Active Tasks
- [Track current work items]

## Recent Decisions
- [Document architectural decisions]

## Known Constraints
- [Current limitations or blockers]

## Next Steps
- [Planned upcoming work]
```

### 7. AI Agent Optimization Patterns

**Agent Instructions** (`/ai-context/agent-instructions.md`):
```markdown
# AI Agent Operating Instructions

## Context Priority
1. Read project-specific CLAUDE.md first
2. Check current git status and recent commits
3. Review related test files before implementing
4. Understand existing patterns before extending

## Error Handling
- Always run tests after changes
- Check for type errors before considering complete
- Verify API endpoints work with curl/Postman equivalent

## Communication Style
- Be explicit about assumptions
- Explain complex decisions in comments
- Update context files with new patterns
```

### 8. Integration with External Tools

**MCP Server Configuration** (`.claude/mcp-settings.json`):
```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp@latest"],
      "env": {
        "HEADLESS": "true"
      }
    },
    "filesystem": {
      "command": "mcp-filesystem",
      "args": ["/Users/christianvuye/Projects_Programming/claude_autonomous_tools/Carolina's Diary"]
    }
  }
}
```

## Implementation Strategy

1. **Start with Root CLAUDE.md** - Create comprehensive project context
2. **Add Component Contexts** - Create specific contexts for backend/frontend
3. **Implement Memory System** - Track decisions and session state
4. **Enhance Testing Context** - Detailed test strategies and requirements
5. **Create Development Workflows** - Standardized processes for AI agents

This structure provides AI agents with rich, contextual information to understand your project deeply, make informed decisions, and work autonomously while maintaining code quality and project consistency.

## Key Benefits

- **Reduced Context Switching** - All relevant information available in structured format
- **Consistent Development Patterns** - Standardized approaches across the project
- **Autonomous Decision Making** - AI agents can work independently with clear guidelines
- **Quality Assurance** - Built-in testing and validation requirements
- **Project Continuity** - Session memory and decision tracking for long-term development

## Next Steps

1. Create the root-level CLAUDE.md file with project-wide context
2. Add component-specific CLAUDE.md files in backend and frontend directories
3. Set up the recommended directory structure for specs, tasks, and contexts
4. Implement the testing documentation framework
5. Configure MCP settings for optimal AI agent integration
