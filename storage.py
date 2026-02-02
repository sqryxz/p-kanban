"""
Storage layer for Kanban data - JSON file with atomic writes
"""

import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Optional
from datetime import datetime

from models import KanbanData, Board, Task, Column, DEFAULT_COLUMNS, now_utc


class KanbanStorage:
    """Handles JSON file storage with atomic write operations"""
    
    def __init__(self, data_path: Optional[str] = None):
        if data_path:
            self.data_path = Path(data_path)
        else:
            home = Path.home()
            self.data_path = home / ".kanban" / "data.json"
        
        self._ensure_directory()
    
    def _ensure_directory(self):
        """Ensure the data directory exists"""
        self.data_path.parent.mkdir(parents=True, exist_ok=True)
    
    def load(self) -> KanbanData:
        """Load Kanban data from JSON file"""
        if not self.data_path.exists():
            return self._create_default_data()
        
        try:
            with open(self.data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return KanbanData.model_validate(data)
        except (json.JSONDecodeError, Exception):
            return self._create_default_data()
    
    def save(self, data: KanbanData) -> None:
        """Save Kanban data atomically to JSON file"""
        temp_fd, temp_path = tempfile.mkstemp(
            dir=self.data_path.parent,
            prefix='.kanban_tmp_'
        )
        
        try:
            with os.fdopen(temp_fd, 'w', encoding='utf-8') as f:
                json.dump(
                    data.model_dump(mode='json'),
                    f,
                    indent=2,
                    ensure_ascii=False,
                    default=str
                )
            
            shutil.move(temp_path, self.data_path)
            
        except Exception:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            raise
    
    def _create_default_data(self) -> KanbanData:
        """Create default Kanban data with initial board"""
        board = Board(
            id="main",
            name="pODV - progress tracker",
            columns=DEFAULT_COLUMNS
        )
        
        data = KanbanData(
            boards=[board],
            default_board="main"
        )
        
        self.save(data)
        return data
    
    def backup(self, backup_path: Optional[str] = None) -> str:
        """Create a backup of the current data file"""
        if backup_path is None:
            timestamp = now_utc().strftime("%Y%m%d_%H%M%S")
            target_path: Path = self.data_path.parent / f"backup_{timestamp}.json"
        else:
            target_path = Path(backup_path)
        
        shutil.copy2(self.data_path, target_path)
        return str(target_path)
