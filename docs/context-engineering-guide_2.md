# Context Engineering Guide for Carolina's Diary

Based on research into context engineering and automated software development, here are comprehensive recommendations for making the Carolina's Diary project more amenable to fully automated AI/LLM agent development:

## 1. **Implement Context Engineering Architecture**

### Context Layers to Establish:

**a) Instructional Context**
- Create an `AGENTS.md` file at the root with:
  - Project overview and goals
  - Architecture decisions and patterns used
  - Development workflow and standards
  - Testing requirements and procedures
  - Deployment process

**b) Semantic Documentation**
```markdown
# .cursor/agents/project-context.md
## Project Overview
- Purpose: Personal journaling app with emotion tracking
- Stack: React/TypeScript frontend, FastAPI/Python backend
- Key Features: Authentication, journal entries, emotion tracking

## Architecture Patterns
- Frontend: Component-based with context providers
- Backend: Layered architecture (routes → services → models)
- Database: SQLite with SQLAlchemy ORM

## Coding Standards
- TypeScript: Strict mode, explicit types
- Python: Type hints, PEP 8 compliance
- Testing: Unit tests for all business logic
```

**c) Dynamic Context Management**
```typescript
// frontend/src/context/AgentContext.tsx
interface AgentContext {
  currentTask: string;
  relevantFiles: string[];
  recentChanges: GitCommit[];
  testResults: TestResult[];
  dependencies: DependencyMap;
}
```

## 2. **Enhance Observability Infrastructure**

### Add Comprehensive Tracing:
```python
# backend/observability.py
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

tracer = trace.get_tracer(__name__)

class AgentObservability:
    @staticmethod
    def trace_operation(operation_name: str):
        def decorator(func):
            def wrapper(*args, **kwargs):
                with tracer.start_as_current_span(operation_name) as span:
                    # Add context about the operation
                    span.set_attribute("args", str(args))
                    span.set_attribute("kwargs", str(kwargs))

                    result = func(*args, **kwargs)

                    # Log the result for agent learning
                    span.set_attribute("result", str(result))
                    return result
            return wrapper
        return decorator
```

### Implement Decision Logging:
```typescript
// frontend/src/services/agentLogger.ts
class AgentLogger {
  logDecision(context: {
    task: string;
    options: string[];
    chosen: string;
    reasoning: string;
    outcome: 'success' | 'failure';
  }) {
    // Send to observability platform
    this.sendToLangfuse({
      type: 'agent_decision',
      timestamp: new Date(),
      ...context
    });
  }
}
```

## 3. **Create Agent-Friendly Documentation**

### Component Documentation:
```typescript
/**
 * @agent-context This component handles user emotion selection
 * @dependencies EmotionSection.css, api.service
 * @state-management Uses React hooks for local state
 * @api-calls GET /emotion-questions/{emotion}, GET /quote/{emotion}
 * @test-coverage Unit tests in EmotionSection.test.tsx
 * @common-modifications Adding new emotions, changing UI layout
 */
export const EmotionSection: React.FC<EmotionSectionProps> = ({ ... }) => {
```

### API Documentation:
```python
@app.post("/journal-entry")
async def create_journal_entry(
    entry: JournalEntryCreate,
    user_data: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    @agent-context Creates or updates journal entry for current date
    @database-operations INSERT/UPDATE on journal_entries table
    @authentication Required (Firebase auth)
    @common-errors 401 (unauthorized), 422 (validation error)
    @test-scenarios
      - New entry creation
      - Existing entry update
      - Invalid emotion handling
    """
```

## 4. **Implement Context-Aware Testing Framework**

```python
# backend/tests/agent_test_framework.py
class AgentTestFramework:
    """Framework for AI agents to understand and run tests"""

    def __init__(self):
        self.test_catalog = self._build_test_catalog()

    def _build_test_catalog(self):
        """Build a semantic catalog of all tests"""
        return {
            "authentication": {
                "description": "Tests for user authentication flow",
                "files": ["test_auth.py"],
                "dependencies": ["Firebase", "JWT"],
                "common_failures": ["Token expiration", "Invalid credentials"]
            },
            "journal_operations": {
                "description": "Tests for CRUD operations on journal entries",
                "files": ["test_journal.py"],
                "dependencies": ["SQLAlchemy", "Pydantic"],
                "common_failures": ["Date format issues", "Missing fields"]
            }
        }

    @agent_observable
    def run_relevant_tests(self, changed_files: List[str]) -> TestResults:
        """Intelligently select and run tests based on changes"""
        relevant_tests = self._select_tests(changed_files)
        return self._execute_tests(relevant_tests)
```

## 5. **Build Knowledge Graph of Codebase**

```python
# tools/build_knowledge_graph.py
import ast
import networkx as nx

class CodebaseKnowledgeGraph:
    def __init__(self):
        self.graph = nx.DiGraph()

    def analyze_codebase(self):
        """Build relationships between code components"""
        # Analyze imports
        self._analyze_dependencies()

        # Analyze function calls
        self._analyze_call_graph()

        # Analyze data flow
        self._analyze_data_flow()

    def export_for_agents(self):
        """Export graph in agent-friendly format"""
        return {
            "components": self._get_component_map(),
            "dependencies": self._get_dependency_tree(),
            "data_flows": self._get_data_flow_paths(),
            "test_coverage": self._get_test_coverage_map()
        }
```

## 6. **Create Agent Interaction Points**

```yaml
# .github/agent-tasks.yml
tasks:
  add_new_emotion:
    description: "Add a new emotion to the journaling system"
    steps:
      - name: "Update emotion enum"
        file: "backend/schemas.py"
        pattern: "class Emotion"
      - name: "Add emotion questions"
        file: "backend/emotion_data.py"
        pattern: "EMOTION_QUESTIONS"
      - name: "Add emotion quotes"
        file: "backend/emotion_data.py"
        pattern: "QUOTES_DATA"
      - name: "Update frontend emotion list"
        file: "frontend/src/components/EmotionSection.tsx"
        pattern: "getEmotionColor"
      - name: "Add tests"
        files:
          - "backend/tests/test_emotions.py"
          - "frontend/src/components/EmotionSection.test.tsx"
    validation:
      - "All tests pass"
      - "Emotion appears in UI"
      - "Questions and quotes load correctly"
```

## 7. **Implement Feedback Loop System**

```typescript
// frontend/src/agents/FeedbackCollector.ts
class AgentFeedbackCollector {
  async collectFeedback(agentAction: AgentAction) {
    const feedback = await this.promptUserFeedback(agentAction);

    // Store feedback for agent learning
    await this.store({
      action: agentAction,
      feedback: feedback,
      context: this.getCurrentContext(),
      outcome: this.measureOutcome(agentAction)
    });
  }

  private getCurrentContext() {
    return {
      openFiles: this.getOpenFiles(),
      recentCommits: this.getRecentCommits(),
      testStatus: this.getTestStatus(),
      performanceMetrics: this.getPerformanceMetrics()
    };
  }
}
```

## 8. **Add Semantic Search and Retrieval**

```python
# backend/agent_tools/semantic_search.py
from sentence_transformers import SentenceTransformer
import faiss

class CodebaseSemanticSearch:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.index = self._build_index()

    def _build_index(self):
        """Build FAISS index of codebase semantics"""
        documents = self._extract_semantic_documents()
        embeddings = self.model.encode(documents)

        index = faiss.IndexFlatL2(embeddings.shape[1])
        index.add(embeddings)
        return index

    def search(self, query: str, k: int = 5):
        """Find semantically similar code sections"""
        query_vector = self.model.encode([query])
        distances, indices = self.index.search(query_vector, k)
        return self._get_documents(indices[0])
```

## 9. **Create Development Environment Profiles**

```json
// .agents/environments.json
{
  "environments": {
    "testing": {
      "setup": [
        "cd backend && pip install -r requirements-dev.txt",
        "cd frontend && npm install"
      ],
      "test_commands": {
        "backend": "cd backend && pytest",
        "frontend": "cd frontend && npm test"
      },
      "validation": {
        "backend": "mypy . && flake8 .",
        "frontend": "npm run lint && npm run type-check"
      }
    },
    "development": {
      "start_commands": {
        "backend": "cd backend && python main.py",
        "frontend": "cd frontend && npm start"
      },
      "watch_patterns": ["**/*.py", "**/*.tsx", "**/*.ts"]
    }
  }
}
```

## 10. **Implement Progressive Context Loading**

```python
# backend/agent_tools/context_manager.py
class ProgressiveContextManager:
    """Manages context window efficiently for AI agents"""

    def __init__(self, max_tokens: int = 128000):
        self.max_tokens = max_tokens
        self.context_layers = {
            "critical": [],      # Always included
            "important": [],     # Included if space
            "supplementary": []  # Included if lots of space
        }

    def build_context(self, task: str):
        """Build optimal context for specific task"""
        context = []

        # Always include critical context
        context.extend(self.context_layers["critical"])

        # Add task-specific context
        task_context = self._get_task_context(task)
        context.append(task_context)

        # Fill remaining space with important/supplementary
        remaining_tokens = self._calculate_remaining_tokens(context)

        if remaining_tokens > 10000:
            context.extend(self.context_layers["important"])

        if remaining_tokens > 20000:
            context.extend(self.context_layers["supplementary"])

        return self._format_context(context)
```

## Implementation Roadmap:

1. **Phase 1**: Add semantic documentation and AGENTS.md files
2. **Phase 2**: Implement observability with Langfuse or similar
3. **Phase 3**: Create agent task definitions and test framework
4. **Phase 4**: Build knowledge graph and semantic search
5. **Phase 5**: Implement feedback loops and progressive context

These enhancements will create an environment where AI agents can:
- Understand the codebase deeply through semantic documentation
- Make informed decisions based on comprehensive context
- Learn from their actions through observability
- Navigate complex tasks with clear guidance
- Adapt to the specific patterns and standards of your project

The key is to make the implicit knowledge explicit and machine-readable, while maintaining human readability and developer experience.
