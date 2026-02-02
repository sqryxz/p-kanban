# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Drag-and-drop support for moving tasks between columns in GUI
- Visual hover effects and improved card styling
- Streamlit-sortables dependency for enhanced drag-and-drop functionality

### Changed
- Improved column header styling with gradient background and white text for better readability
- Enhanced task card design with better contrast and visual hierarchy
- Updated priority badges with proper color contrast

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
