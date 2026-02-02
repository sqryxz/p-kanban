# Kanban Board

A simple, file-based Kanban board for personal task tracking and AI agent collaboration.

## Features

- **CLI Interface**: Easy-to-use command line interface with beautiful terminal output
- **Web GUI**: Streamlit-based web interface with drag-and-drop feel
- **AI-Agent Friendly**: JSON output mode for programmatic interaction
- **File-Based Storage**: JSON file storage (human-readable, git-friendly)
- **WIP Limits**: Set work-in-progress limits per column
- **Agent Context**: Special field for AI agents to store reasoning and next steps
- **Atomic Writes**: Safe file operations prevent data corruption

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Web GUI (Streamlit)

Launch the web interface for a visual Kanban board experience:

```bash
streamlit run kanban_gui.py
```

The GUI provides:
- **Visual Board Layout**: Three columns (To Do, In Progress, Done) with task cards
- **Task Cards**: Show priority (color-coded), tags, description, and agent context
- **Add Tasks**: Form in sidebar to create new tasks
- **Move Tasks**: Dropdown selector to move tasks between columns
- **View Details**: Click "View" to see full task info, agent context, and history
- **Delete Tasks**: With confirmation dialog
- **Filters**: Search by text, filter by priority or tag
- **Statistics**: Task counts per column in sidebar

Access the GUI at `http://localhost:8501` after starting.

### CLI Interface

### Initialize a new board
```bash
python kanban.py init-board --name "My Project"
```

### Add tasks
```bash
python kanban.py add "Implement authentication" --priority high --tag backend
python kanban.py add "Write tests" --description "Add unit tests for API endpoints" --tag testing
```

### View board
```bash
python kanban.py show
```

### Move tasks between columns
```bash
python kanban.py move 1 inprogress
python kanban.py move 1 done --reason "Code reviewed and merged"
```

### List tasks with filters
```bash
python kanban.py list-tasks --column todo
python kanban.py list-tasks --priority high
python kanban.py list-tasks --tag backend
```

### Get task details
```bash
python kanban.py info 1
```

### Edit tasks
```bash
python kanban.py edit 1 --priority critical --add-tag urgent
python kanban.py edit 1 --description "Updated requirements..."
```

### Set agent context (AI integration)
```bash
python kanban.py agent-context 1 lastAction "reviewed codebase"
python kanban.py agent-context 1 nextStep "implement middleware"
```

### JSON output (for AI agents)
```bash
python kanban.py show --json
python kanban.py list-tasks --json
python kanban.py info 1 --json
```

### Delete tasks
```bash
python kanban.py delete 1
python kanban.py delete 1 --force  # Skip confirmation
```

### Backup
```bash
python kanban.py backup
python kanban.py backup --output /path/to/backup.json
```

## Using CLI and GUI Together

Both interfaces work with the same data file, so you can seamlessly switch between them:

```bash
# Add tasks via CLI
python3 kanban.py add "Fix bug" --priority high

# View and manage in GUI
streamlit run kanban_gui.py

# Or continue with CLI
python3 kanban.py move 1 done
```

## Data Storage

Data is stored in `~/.kanban/data.json` by default. You can customize this:

```bash
export KANBAN_DATA_PATH=/path/to/custom/data.json
python kanban.py show
```

## Default Columns

- **To Do**: Unlimited capacity
- **In Progress**: WIP limit of 3 tasks
- **Done**: Unlimited capacity

## AI Agent Integration

The Kanban CLI is designed to work seamlessly with AI agents:

1. **JSON Mode**: All list/show commands support `--json` for structured output
2. **Agent Context**: Special field to store AI reasoning and planned next steps
3. **Atomic Operations**: Safe concurrent access from multiple agents
4. **History Tracking**: All moves are logged with timestamps and reasons

Example agent workflow:
```bash
# Agent reads current state
python kanban.py show --json

# Agent adds a new task
python kanban.py add "Fix bug in auth" --priority high

# Agent updates context
python kanban.py agent-context 5 lastAction "identified root cause"
python kanban.py agent-context 5 nextStep "implement fix"

# Agent moves task when complete
python kanban.py move 5 done --reason "Bug fixed and tested"
```

## License

MIT
