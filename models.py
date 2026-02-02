"""
Kanban Tracker - Personal Kanban Board for AI Agent Collaboration
"""

from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


def now_utc() -> datetime:
    """Return current UTC time with timezone info"""
    return datetime.now(timezone.utc)


class Priority(str, Enum):
    """Task priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Column(BaseModel):
    """A Kanban column (e.g., To Do, In Progress, Done)"""
    id: str = Field(..., description="Unique identifier for the column")
    name: str = Field(..., description="Display name")
    limit: Optional[int] = Field(None, description="WIP limit (None = unlimited)")
    order: int = Field(0, description="Display order")


class Task(BaseModel):
    """A Kanban task/card"""
    id: int = Field(..., description="Unique task ID")
    board_id: str = Field(default="main", description="Board this task belongs to")
    column_id: str = Field(..., description="Current column")
    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(None, description="Detailed description")
    priority: Priority = Field(default=Priority.MEDIUM, description="Task priority")
    tags: List[str] = Field(default_factory=list, description="Task tags")
    created_at: datetime = Field(default_factory=now_utc)
    updated_at: datetime = Field(default_factory=now_utc)
    agent_context: Dict[str, Any] = Field(
        default_factory=dict,
        description="Context for AI agents (lastAction, nextStep, notes)"
    )
    
    # History log for tracking changes
    history: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Change history"
    )

    def move_to(self, column_id: str, reason: Optional[str] = None):
        """Move task to a different column and log the change"""
        old_column = self.column_id
        self.column_id = column_id
        self.updated_at = now_utc()
        
        self.history.append({
            "action": "moved",
            "from_column": old_column,
            "to_column": column_id,
            "timestamp": now_utc().isoformat(),
            "reason": reason
        })


class Board(BaseModel):
    """A Kanban board containing columns and tasks"""
    id: str = Field(default="main", description="Board identifier")
    name: str = Field(default="Main Board", description="Board name")
    columns: List[Column] = Field(default_factory=list)
    tasks: List[Task] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=now_utc)
    updated_at: datetime = Field(default_factory=now_utc)

    def get_next_task_id(self) -> int:
        """Generate next available task ID"""
        if not self.tasks:
            return 1
        return max(t.id for t in self.tasks) + 1

    def get_tasks_in_column(self, column_id: str) -> List[Task]:
        """Get all tasks in a specific column"""
        return [t for t in self.tasks if t.column_id == column_id]

    def get_column(self, column_id: str) -> Optional[Column]:
        """Get column by ID"""
        for col in self.columns:
            if col.id == column_id:
                return col
        return None

    def can_add_to_column(self, column_id: str) -> tuple[bool, Optional[str]]:
        """Check if a task can be added to a column (WIP limit)"""
        col = self.get_column(column_id)
        if not col:
            return False, f"Column '{column_id}' not found"
        
        if col.limit is None:
            return True, None
        
        current_count = len(self.get_tasks_in_column(column_id))
        if current_count >= col.limit:
            return False, f"WIP limit ({col.limit}) reached for '{col.name}'"
        
        return True, None


class KanbanData(BaseModel):
    """Root data structure for the Kanban tracker"""
    version: str = Field(default="1.0", description="Data format version")
    boards: List[Board] = Field(default_factory=list)
    default_board: str = Field(default="main", description="Default board ID")
    
    def get_board(self, board_id: Optional[str] = None) -> Optional[Board]:
        """Get board by ID (or default if not specified)"""
        target_id = board_id or self.default_board
        for board in self.boards:
            if board.id == target_id:
                return board
        return None
    
    def get_task(self, task_id: int, board_id: Optional[str] = None) -> Optional[Task]:
        """Get task by ID"""
        board = self.get_board(board_id)
        if not board:
            return None
        for task in board.tasks:
            if task.id == task_id:
                return task
        return None


DEFAULT_COLUMNS = [
    Column(id="todo", name="To Do", limit=None, order=0),
    Column(id="inprogress", name="In Progress", limit=3, order=1),
    Column(id="done", name="Done", limit=None, order=2),
]
