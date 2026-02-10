#!/usr/bin/env python3
"""
Kanban CLI - Terminal-based Kanban board for AI agent collaboration
"""

import json
import os
import sys
from typing import Optional, List
from datetime import datetime
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

from models import KanbanData, Board, Task, Column, Priority, DEFAULT_COLUMNS, now_utc
from models import KanbanError, BoardNotFoundError, TaskNotFoundError, ColumnError
from storage import KanbanStorage, KanbanStorageLocked


app = typer.Typer(help="Kanban CLI - Personal task board for AI agent collaboration")
console = Console()

DEFAULT_DATA_PATH = Path.home() / ".kanban" / "data.json"


def get_storage() -> KanbanStorage:
    data_path = os.environ.get("KANBAN_DATA_PATH")
    return KanbanStorage(data_path)


def get_data() -> KanbanData:
    storage = get_storage()
    return storage.load()


def save_data(data: KanbanData) -> None:
    storage = get_storage()
    storage.save(data)


@app.command()
def add(
    title: str = typer.Argument(..., help="Task title"),
    description: Optional[str] = typer.Option(None, "--description", "-d", help="Task description"),
    priority: Priority = typer.Option(Priority.MEDIUM, "--priority", "-p", help="Task priority"),
    tags: Optional[List[str]] = typer.Option(None, "--tag", "-t", help="Task tags (can be used multiple times)"),
    column: str = typer.Option("todo", "--column", "-c", help="Initial column (default: todo)"),
    board_id: Optional[str] = typer.Option(None, "--board", "-b", help="Board ID (uses default if not specified)")
):
    """Add a new task to the board"""
    data = get_data()
    board = data.get_board(board_id)
    
    if not board:
        raise BoardNotFoundError(f"Board '{board_id}' not found")
    
    can_add, error_msg = board.can_add_to_column(column)
    if not can_add:
        raise ColumnError(error_msg)
    
    task = Task(
        id=board.get_next_task_id(data),
        board_id=board.id,
        column_id=column,
        title=title,
        description=description,
        priority=priority,
        tags=tags or []
    )
    
    board.tasks.append(task)
    save_data(data)
    
    console.print(f"[green]Created task #{task.id}: {title}[/green]")


@app.command()
def move(
    task_id: int = typer.Argument(..., help="Task ID to move"),
    column: str = typer.Argument(..., help="Target column"),
    reason: Optional[str] = typer.Option(None, "--reason", "-r", help="Reason for moving"),
    board_id: Optional[str] = typer.Option(None, "--board", "-b", help="Board ID (uses default if not specified)")
):
    """Move a task to a different column"""
    data = get_data()
    board = data.get_board(board_id)
    
    if not board:
        raise BoardNotFoundError(f"Board '{board_id}' not found")
    
    task = data.get_task(task_id)
    if not task:
        raise TaskNotFoundError(f"Task #{task_id} not found")
    
    if task.column_id == column:
        console.print(f"[yellow]Task #{task_id} is already in '{column}'[/yellow]")
        return
    
    can_add, error_msg = board.can_add_to_column(column)
    if not can_add:
        raise ColumnError(error_msg)
    
    old_column = task.column_id
    task.move_to(column, reason)
    save_data(data)
    
    console.print(f"[green]Moved task #{task_id} from '{old_column}' to '{column}'[/green]")


@app.command()
def delete(
    task_id: int = typer.Argument(..., help="Task ID to delete"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
    board_id: Optional[str] = typer.Option(None, "--board", "-b", help="Board ID (uses default if not specified)")
):
    """Delete a task from the board"""
    data = get_data()
    board = data.get_board(board_id)
    
    if not board:
        raise BoardNotFoundError(f"Board '{board_id}' not found")
    
    task = data.get_task(task_id, board_id)
    if not task:
        raise TaskNotFoundError(f"Task #{task_id} not found")
    
    if not force:
        confirm = typer.confirm(f"Delete task #{task_id}: '{task.title}'?")
        if not confirm:
            console.print("Cancelled")
            return
    
    board.tasks = [t for t in board.tasks if t.id != task_id]
    save_data(data)
    
    console.print(f"[green]Deleted task #{task_id}[/green]")


@app.command()
def show(
    board_id: Optional[str] = typer.Option(None, "--board", "-b", help="Board ID"),
    json_output: bool = typer.Option(False, "--json", "-j", help="Output as JSON (for AI agents)")
):
    """Display the Kanban board"""
    data = get_data()
    board = data.get_board(board_id)
    
    if not board:
        raise BoardNotFoundError(f"Board '{board_id}' not found")
    
    if json_output:
        output = {
            "board": board.model_dump(mode='json'),
            "tasks_by_column": {
                col.id: [t.model_dump(mode='json') for t in board.get_tasks_in_column(col.id)]
                for col in board.columns
            }
        }
        print(json.dumps(output, indent=2))
        return
    
    table = Table(
        title=f"📋 {board.name}",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold"
    )
    
    for col in sorted(board.columns, key=lambda c: c.order):
        col_tasks = board.get_tasks_in_column(col.id)
        count = len(col_tasks)
        limit_text = f"/{col.limit}" if col.limit else ""
        table.add_column(f"{col.name} ({count}{limit_text})", no_wrap=False)
    
    max_rows = max(
        len(board.get_tasks_in_column(col.id))
        for col in board.columns
    ) if board.columns else 0
    
    for row_idx in range(max_rows):
        row_cells = []
        for col in sorted(board.columns, key=lambda c: c.order):
            tasks = board.get_tasks_in_column(col.id)
            if row_idx < len(tasks):
                task = tasks[row_idx]
                priority_color = {
                    Priority.LOW: "dim",
                    Priority.MEDIUM: "white",
                    Priority.HIGH: "yellow",
                    Priority.CRITICAL: "red bold"
                }.get(task.priority, "white")
                
                tags_str = f" [dim]({', '.join(task.tags)})[/dim]" if task.tags else ""
                cell = f"[{priority_color}]#{task.id}: {task.title}[/]{tags_str}"
                row_cells.append(cell)
            else:
                row_cells.append("")
        table.add_row(*row_cells)
    
    console.print(table)
    
    if board.tasks:
        console.print(f"\n[dim]Total tasks: {len(board.tasks)}[/dim]")


@app.command()
def list_tasks(
    column: Optional[str] = typer.Option(None, "--column", "-c", help="Filter by column"),
    priority: Optional[Priority] = typer.Option(None, "--priority", "-p", help="Filter by priority"),
    tag: Optional[str] = typer.Option(None, "--tag", "-t", help="Filter by tag"),
    json_output: bool = typer.Option(False, "--json", "-j", help="Output as JSON")
):
    """List all tasks with optional filters"""
    data = get_data()
    board = data.get_board()
    
    if not board:
        raise BoardNotFoundError("No board found")
    
    tasks = board.tasks
    
    if column:
        tasks = [t for t in tasks if t.column_id == column]
    if priority:
        tasks = [t for t in tasks if t.priority == priority]
    if tag:
        tasks = [t for t in tasks if tag in t.tags]
    
    if json_output:
        print(json.dumps([t.model_dump(mode='json') for t in tasks], indent=2))
        return
    
    if not tasks:
        console.print("[dim]No tasks found[/dim]")
        return
    
    for task in tasks:
        priority_color = {
            Priority.LOW: "dim",
            Priority.MEDIUM: "white",
            Priority.HIGH: "yellow",
            Priority.CRITICAL: "red bold"
        }.get(task.priority, "white")
        
        col = board.get_column(task.column_id)
        col_display = col.name if col else task.column_id
        
        tags_str = f" [dim]({', '.join(task.tags)})[/dim]" if task.tags else ""
        console.print(f"[{priority_color}]#{task.id}[/] [{task.column_id}]{col_display}[/{task.column_id}] - {task.title}{tags_str}")


@app.command()
def info(
    task_id: int = typer.Argument(..., help="Task ID"),
    json_output: bool = typer.Option(False, "--json", "-j", help="Output as JSON")
):
    """Show detailed information about a task"""
    data = get_data()
    task = data.get_task(task_id)
    
    if not task:
        raise TaskNotFoundError(f"Task #{task_id} not found")
    
    if json_output:
        print(json.dumps(task.model_dump(mode='json'), indent=2))
        return
    
    board = data.get_board()
    col = board.get_column(task.column_id) if board else None
    col_name = col.name if col else task.column_id
    
    content = f"""
[bold]Task #{task.id}:[/bold] {task.title}

[dim]Column:[/dim] {col_name}
[dim]Priority:[/dim] {task.priority.value}
[dim]Tags:[/dim] {', '.join(task.tags) if task.tags else 'None'}
[dim]Created:[/dim] {task.created_at.strftime('%Y-%m-%d %H:%M')}
[dim]Updated:[/dim] {task.updated_at.strftime('%Y-%m-%d %H:%M')}
"""
    
    if task.description:
        content += f"\n[bold]Description:[/bold]\n{task.description}\n"
    
    if task.agent_context:
        content += f"\n[bold]Agent Context:[/bold]\n"
        for key, value in task.agent_context.items():
            content += f"  [dim]{key}:[/dim] {value}\n"
    
    if task.history:
        content += f"\n[bold]History:[/bold]\n"
        for entry in task.history[-5:]:
            content += f"  [dim]{entry.get('timestamp', 'unknown')}:[/dim] {entry.get('action', 'unknown')}\n"
    
    console.print(Panel(content.strip(), title=f"Task #{task.id}"))


@app.command()
def edit(
    task_id: int = typer.Argument(..., help="Task ID"),
    title: Optional[str] = typer.Option(None, "--title", help="New title"),
    description: Optional[str] = typer.Option(None, "--description", "-d", help="New description"),
    priority: Optional[Priority] = typer.Option(None, "--priority", "-p", help="New priority"),
    add_tags: Optional[List[str]] = typer.Option(None, "--add-tag", help="Add tags"),
    remove_tags: Optional[List[str]] = typer.Option(None, "--remove-tag", help="Remove tags")
):
    """Edit a task's properties"""
    data = get_data()
    task = data.get_task(task_id)
    
    if not task:
        raise TaskNotFoundError(f"Task #{task_id} not found")
    
    if title:
        task.title = title
    if description is not None:
        task.description = description
    if priority:
        task.priority = priority
    if add_tags:
        task.tags = list(set(task.tags + add_tags))
    if remove_tags:
        task.tags = [t for t in task.tags if t not in remove_tags]
    
    task.updated_at = now_utc()
    save_data(data)
    
    console.print(f"[green]Updated task #{task_id}[/green]")


@app.command()
def agent_context(
    task_id: int = typer.Argument(..., help="Task ID"),
    key: str = typer.Argument(..., help="Context key"),
    value: str = typer.Argument(..., help="Context value")
):
    """Set agent context for a task (AI agent integration)"""
    data = get_data()
    task = data.get_task(task_id)
    
    if not task:
        raise TaskNotFoundError(f"Task #{task_id} not found")
    
    task.agent_context[key] = value
    task.updated_at = now_utc()
    save_data(data)
    
    console.print(f"[green]Set agent context for task #{task_id}: {key} = {value}[/green]")


@app.command()
def init_board(
    name: str = typer.Option("Main Board", "--name", "-n", help="Board name"),
    data_path: Optional[str] = typer.Option(None, "--path", help="Custom data path")
):
    """Initialize a new Kanban board"""
    storage = KanbanStorage(data_path)
    
    board = Board(
        id="main",
        name=name,
        columns=DEFAULT_COLUMNS
    )
    
    kanban_data = KanbanData(
        boards=[board],
        default_board="main"
    )
    
    storage.save(kanban_data)
    console.print(f"[green]Created new board: {name}[/green]")
    console.print(f"[dim]Data stored at: {storage.data_path}[/dim]")


@app.command()
def backup(
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Backup file path")
):
    """Create a backup of the Kanban data"""
    storage = get_storage()
    backup_path = storage.backup(output)
    console.print(f"[green]Backup created: {backup_path}[/green]")


@app.command()
def status(
    json_output: bool = typer.Option(False, "--json", "-j", help="Output as JSON")
):
    """Show Kanban system status and data file info"""
    storage = get_storage()
    data = get_data()
    
    if json_output:
        output = {
            "data_path": str(storage.data_path),
            "data_file_exists": storage.data_path.exists(),
            "boards_count": len(data.boards),
            "default_board": data.default_board,
            "total_tasks": sum(len(b.tasks) for b in data.boards)
        }
        print(json.dumps(output, indent=2))
        return
    
    console.print(f"[bold]Kanban Status[/bold]")
    console.print(f"Data file: {storage.data_path}")
    console.print(f"File exists: {'[green]Yes[/green]' if storage.data_path.exists() else '[red]No[/red]'}")
    console.print(f"Boards: {len(data.boards)}")
    console.print(f"Default board: {data.default_board}")
    console.print(f"Total tasks: {sum(len(b.tasks) for b in data.boards)}")


@app.command()
def create_board(
    name: str = typer.Argument(..., help="Board name"),
    set_default: bool = typer.Option(True, "--default/--no-default", help="Set as default board")
):
    """Create a new Kanban board"""
    data = get_data()
    
    # Generate unique board ID
    base_id = name.lower().replace(" ", "-")[:20]
    board_id = base_id
    counter = 1
    while any(b.id == board_id for b in data.boards):
        board_id = f"{base_id}-{counter}"
        counter += 1
    
    new_board = Board(
        id=board_id,
        name=name,
        columns=DEFAULT_COLUMNS.copy()
    )
    data.boards.append(new_board)
    
    if set_default or len(data.boards) == 1:
        data.default_board = board_id
    
    save_data(data)
    console.print(f"[green]Created board: {name} ({board_id})[/green]")
    if set_default:
        console.print(f"[dim]Set as default board[/dim]")


@app.command()
def list_boards(
    json_output: bool = typer.Option(False, "--json", "-j", help="Output as JSON")
):
    """List all Kanban boards"""
    data = get_data()
    
    if json_output:
        output = {
            "boards": [b.model_dump(mode='json') for b in data.boards],
            "default_board": data.default_board
        }
        print(json.dumps(output, indent=2))
        return
    
    table = Table(title="📋 Boards", box=box.ROUNDED)
    table.add_column("ID", style="dim")
    table.add_column("Name")
    table.add_column("Tasks", justify="right")
    table.add_column("Default", justify="center")
    
    for board in data.boards:
        is_default = "✓" if board.id == data.default_board else ""
        task_count = len(board.tasks)
        table.add_row(board.id, board.name, str(task_count), is_default)
    
    console.print(table)


@app.command()
def switch_board(
    board_id: str = typer.Argument(..., help="Board ID to switch to")
):
    """Set the default board"""
    data = get_data()
    
    board = data.get_board(board_id)
    if not board:
        raise BoardNotFoundError(f"Board '{board_id}' not found")
    
    data.default_board = board_id
    save_data(data)
    console.print(f"[green]Switched to board: {board.name} ({board_id})[/green]")


@app.command()
def delete_board(
    board_id: str = typer.Argument(..., help="Board ID to delete"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation")
):
    """Delete a Kanban board and all its tasks"""
    data = get_data()
    
    board = data.get_board(board_id)
    if not board:
        raise BoardNotFoundError(f"Board '{board_id}' not found")
    
    if len(data.boards) <= 1:
        raise KanbanError("Cannot delete the only board. Create another board first.")
    
    if not force:
        task_count = len(board.tasks)
        warning = f" with {task_count} tasks" if task_count > 0 else ""
        confirm = typer.confirm(f"Delete board '{board.name}'{warning}? This cannot be undone.")
        if not confirm:
            console.print("Cancelled")
            return
    
    data.boards = [b for b in data.boards if b.id != board_id]
    
    # If we deleted the default board, set a new default
    if data.default_board == board_id and data.boards:
        data.default_board = data.boards[0].id
    
    save_data(data)
    console.print(f"[green]Deleted board: {board.name} ({board_id})[/green]")


def handle_exception(exc: Exception) -> None:
    """Handle Kanban exceptions with user-friendly messages"""
    if isinstance(exc, BoardNotFoundError):
        console.print(f"[red]Error: {exc}[/red]")
    elif isinstance(exc, TaskNotFoundError):
        console.print(f"[red]Error: {exc}[/red]")
    elif isinstance(exc, ColumnError):
        console.print(f"[red]Error: {exc}[/red]")
    elif isinstance(exc, KanbanError):
        console.print(f"[red]Error: {exc}[/red]")
    elif isinstance(exc, KanbanStorageLocked):
        console.print(f"[red]Error: {exc}[/red]")
    else:
        console.print(f"[red]Unexpected error: {exc}[/red]")
    raise typer.Exit(1)


@app.callback()
def main(
    version: Optional[bool] = typer.Option(None, "--version", "-v", help="Show version")
):
    """Kanban CLI - Personal task board for AI agent collaboration"""
    if version:
        console.print("Kanban CLI v1.0.0")
        raise typer.Exit()
    
    # Add exception handler for all commands
    from typing import get_type_hints
    app.registered_commands = getattr(app, 'registered_commands', [])
    
    # Register exception handling wrapper
    pass


if __name__ == "__main__":
    app()
