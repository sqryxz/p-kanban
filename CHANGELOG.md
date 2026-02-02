# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.4.0] - 2025-02-02

### Added
- Edit task functionality via ✎ button on each task card
- Edit form with pre-populated task data (title, description, priority, column, tags)
- Agent context editing within edit form

### Changed
- Task card layout: now has 4 action buttons (v, ✎, →, ×)
- Move dropdown shortened to "→" with 3-letter column abbreviations
- All action buttons now same compact size
- Improved CSS for select dropdown to match button sizing

## [1.3.0] - 2025-02-02

### Added
- Five-column layout: Backlog, To Do, In Progress, Testing, Done
- Working task movement via dropdown selector ("→ move")
- Minimal sleek dark theme with reduced font sizes
- Color-coded column headers (backlog=gray, todo=silver, in-progress=orange, testing=blue, done=green)
- Compact task cards with left-border priority indicators
- Hover effects on task cards and buttons
- Simplified button labels ("view", "del", "+ new task")
- Agent context indicator (◉) on tasks with AI context

### Changed
- Title changed to "pODV - progress tracker" with ◼ icon
- Complete visual redesign for minimal aesthetic
- Smaller fonts throughout (0.7rem - 0.8rem for most text)
- Moved to Inter font family
- Simplified color palette (mostly grays with accent colors)
- Replaced drag-and-drop with reliable dropdown movement
- More compact spacing and tighter layout
- Simplified sidebar with just search and tag filters

### Removed
- Complex drag-and-drop implementation (replaced with dropdown)
- Large visual elements and excessive padding
- Gradient backgrounds (replaced with flat minimal design)

## [1.2.0] - 2025-02-02

### Added
- Full dark theme UI with GitHub-inspired color scheme (#0d1117 background)
- Working HTML5 drag-and-drop for task cards with visual feedback
- Empty column state with clickable "Add task" button
- Inline task creation form (moved from sidebar to main view)
- Collapsible sidebar (defaults to collapsed)
- Visual drag handles (⋮⋮) on task cards
- Hover animations and lift effects on task cards
- Improved button styling with shadows and hover effects

### Changed
- Complete UI redesign with dark theme
- Column headers now use gradient styling with improved contrast
- Moved "Add New Task" button to main header area
- Task form now appears inline when triggered
- Empty columns show 📭 icon and clickable add button
- Priority badges with border accents for better visibility
- Stats cards in sidebar with visual separation
- Improved typography with better hierarchy

### Fixed
- Header text now readable with proper contrast on dark background
- Title "📋 AI Development" now displays correctly with blue accent color
- Task cards have proper dark background with light text

## [1.1.0] - 2025-02-02

### Added
- Streamlit web GUI for visual Kanban board management
- Task filtering by priority and tags in GUI
- Agent context display and editing in task details view
- WIP limit warnings in GUI with visual indicators
- Task statistics sidebar in GUI

### Changed
- Improved visual design with color-coded priority badges
- Enhanced task cards with hover effects and better spacing

## [1.0.0] - 2025-02-02

### Added
- Initial release with complete CLI functionality
- Core data models: Board, Column, Task with Pydantic validation
- JSON file storage with atomic write operations
- CLI commands: add, move, delete, show, list, info, edit
- Priority levels: low, medium, high, critical
- WIP limits per column with enforcement
- Agent context field for AI collaboration (lastAction, nextStep)
- Task history tracking with timestamps
- JSON output mode for AI agent integration
- Backup functionality for data safety
- Tag support for task categorization
- Comprehensive README with usage examples
- .gitignore for Python projects

### Technical
- Built with Python 3.x
- Uses Typer for CLI framework
- Uses Rich for beautiful terminal output
- Uses Pydantic for data validation
- File-based storage in ~/.kanban/data.json
- Supports custom data path via KANBAN_DATA_PATH environment variable

---

## Release Notes Format

Each release includes:
- **Added** - New features
- **Changed** - Changes to existing functionality
- **Deprecated** - Soon-to-be removed features
- **Removed** - Removed features
- **Fixed** - Bug fixes
- **Security** - Security improvements

## Version History

- **v1.1.0** - GUI release with Streamlit interface
- **v1.0.0** - Initial CLI release with core functionality
