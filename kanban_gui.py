"""
Kanban GUI - Streamlit web interface for the Kanban board
"""

import streamlit as st
from datetime import datetime
from typing import Optional, List, Dict, Any
import json

from models import KanbanData, Board, Task, Column, Priority, now_utc
from storage import KanbanStorage

# Page configuration
st.set_page_config(
    page_title="Kanban Board",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling with proper contrast
st.markdown("""
<style>
    /* Main app background */
    .stApp {
        background-color: #f5f5f5;
    }
    
    /* Task card styling */
    .task-card {
        background-color: #ffffff;
        border-radius: 8px;
        padding: 12px;
        margin: 8px 0;
        border-left: 4px solid #dee2e6;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        cursor: grab;
        transition: all 0.2s ease;
    }
    .task-card:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        transform: translateY(-2px);
    }
    .task-card:active {
        cursor: grabbing;
    }
    .priority-low { border-left-color: #6c757d; }
    .priority-medium { border-left-color: #007bff; }
    .priority-high { border-left-color: #fd7e14; }
    .priority-critical { border-left-color: #dc3545; }
    
    /* Column header with dark text for readability */
    .column-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: #ffffff !important;
        padding: 16px;
        border-radius: 12px;
        text-align: center;
        font-weight: bold;
        font-size: 1.2rem;
        margin-bottom: 16px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-shadow: 0 1px 2px rgba(0,0,0,0.2);
    }
    
    /* Column container */
    .column-container {
        background-color: #e8eaf6;
        border-radius: 12px;
        padding: 16px;
        min-height: 400px;
        border: 2px dashed transparent;
        transition: all 0.3s ease;
    }
    .column-container.drag-over {
        border-color: #667eea;
        background-color: #c5cae9;
    }
    
    /* Tag badge */
    .tag-badge {
        display: inline-block;
        background-color: #e3f2fd;
        color: #1976d2;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.75rem;
        margin: 2px;
        font-weight: 500;
    }
    
    /* Agent context badge */
    .agent-context-badge {
        display: inline-block;
        background-color: #fff3e0;
        color: #e65100;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.75rem;
        margin-top: 4px;
        font-weight: 500;
    }
    
    /* Priority badge */
    .priority-badge {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.7rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Drag handle */
    .drag-handle {
        cursor: grab;
        color: #999;
        float: right;
        padding: 4px;
    }
    .drag-handle:hover {
        color: #667eea;
    }
    
    /* Button styling */
    .stButton button {
        width: 100%;
        border-radius: 6px;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    
    /* Form styling */
    div[data-testid="stForm"] {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    /* WIP limit warning */
    .wip-warning {
        background-color: #fff3cd;
        color: #856404;
        padding: 8px 12px;
        border-radius: 6px;
        border-left: 4px solid #ffc107;
        font-size: 0.9rem;
        margin-bottom: 12px;
    }
    
    /* Empty column state */
    .empty-column {
        text-align: center;
        color: #9e9e9e;
        padding: 40px 20px;
        border: 2px dashed #c5cae9;
        border-radius: 8px;
        font-style: italic;
    }
</style>
""", unsafe_allow_html=True)

# JavaScript for drag-and-drop functionality
st.markdown("""
<script>
// Drag and drop functionality
let draggedElement = null;

function initDragAndDrop() {
    const cards = document.querySelectorAll('.task-card');
    const columns = document.querySelectorAll('.column-container');
    
    cards.forEach(card => {
        card.draggable = true;
        
        card.addEventListener('dragstart', (e) => {
            draggedElement = card;
            card.style.opacity = '0.5';
            e.dataTransfer.effectAllowed = 'move';
            e.dataTransfer.setData('text/html', card.innerHTML);
        });
        
        card.addEventListener('dragend', () => {
            card.style.opacity = '1';
            draggedElement = null;
            columns.forEach(col => col.classList.remove('drag-over'));
        });
    });
    
    columns.forEach(column => {
        column.addEventListener('dragover', (e) => {
            e.preventDefault();
            column.classList.add('drag-over');
        });
        
        column.addEventListener('dragleave', () => {
            column.classList.remove('drag-over');
        });
        
        column.addEventListener('drop', (e) => {
            e.preventDefault();
            column.classList.remove('drag-over');
            
            if (draggedElement) {
                const taskId = draggedElement.getAttribute('data-task-id');
                const targetColumn = column.getAttribute('data-column-id');
                
                // Send to Streamlit
                window.parent.postMessage({
                    type: 'kanban-move',
                    taskId: taskId,
                    targetColumn: targetColumn
                }, '*');
            }
        });
    });
}

// Initialize on load
document.addEventListener('DOMContentLoaded', initDragAndDrop);
// Re-initialize on Streamlit re-render
setInterval(initDragAndDrop, 1000);
</script>
""", unsafe_allow_html=True)


def load_data() -> KanbanData:
    """Load kanban data from storage"""
    storage = KanbanStorage()
    return storage.load()


def save_data(data: KanbanData):
    """Save kanban data to storage"""
    storage = KanbanStorage()
    storage.save(data)


def get_priority_class(priority: Priority) -> str:
    """Get CSS class for priority level"""
    return f"priority-{priority.value}"


def get_priority_color(priority: Priority) -> tuple[str, str]:
    """Get color for priority badge (text_color, bg_color)"""
    colors: dict[Priority, tuple[str, str]] = {
        Priority.LOW: ("#6c757d", "#f8f9fa"),
        Priority.MEDIUM: ("#007bff", "#e7f3ff"),
        Priority.HIGH: ("#fd7e14", "#fff3e0"),
        Priority.CRITICAL: ("#dc3545", "#ffe7e7")
    }
    return colors.get(priority, ("#6c757d", "#f8f9fa"))


def render_task_card_html(task: Task, board: Board) -> str:
    """Render a single task card as HTML for drag-and-drop"""
    priority_class = get_priority_class(task.priority)
    text_color, bg_color = get_priority_color(task.priority)
    
    tags_html = ""
    if task.tags:
        tags_html = " ".join([f'<span class="tag-badge">{tag}</span>' for tag in task.tags])
    
    agent_context_html = ""
    if task.agent_context:
        agent_context_html = '<div class="agent-context-badge">🤖 Agent Context</div>'
    
    desc_html = ""
    if task.description:
        desc = task.description[:100] + "..." if len(task.description) > 100 else task.description
        desc_html = f'<div style="margin-top: 8px; font-size: 0.9rem; color: #666; line-height: 1.4;">{desc}</div>'
    
    return f"""
    <div class="task-card {priority_class}" data-task-id="{task.id}" draggable="true">
        <div style="display: flex; justify-content: space-between; align-items: start;">
            <div style="font-weight: bold; font-size: 1rem; color: #212529; flex: 1;">
                #{task.id}: {task.title}
            </div>
            <div style="font-size: 0.7rem; color: #999; margin-left: 8px;">
                ⋮⋮
            </div>
        </div>
        <div style="margin-top: 6px;">
            <span class="priority-badge" style="background-color: {bg_color}; color: {text_color};">
                {task.priority.value.upper()}
            </span>
        </div>
        {desc_html}
        {f'<div style="margin-top: 8px;">{tags_html}</div>' if tags_html else ""}
        {agent_context_html}
    </div>
    """


def render_task_card_native(task: Task, board: Board, data: KanbanData):
    """Render a task card using native Streamlit components with move functionality"""
    priority_class = get_priority_class(task.priority)
    text_color, bg_color = get_priority_color(task.priority)
    
    # Card container with custom styling
    with st.container():
        st.markdown(f"""
        <div class="task-card {priority_class}">
            <div style="display: flex; justify-content: space-between; align-items: start;">
                <div style="font-weight: bold; font-size: 1rem; color: #212529; flex: 1;">
                    #{task.id}: {task.title}
                </div>
            </div>
            <div style="margin-top: 6px;">
                <span class="priority-badge" style="background-color: {bg_color}; color: {text_color};">
                    {task.priority.value.upper()}
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if task.description:
            desc = task.description[:100] + "..." if len(task.description) > 100 else task.description
            st.markdown(f"<div style='font-size: 0.9rem; color: #666; margin: 8px 0;'>{desc}</div>", unsafe_allow_html=True)
        
        if task.tags:
            tags_html = " ".join([f'<span class="tag-badge">{tag}</span>' for tag in task.tags])
            st.markdown(f"<div>{tags_html}</div>", unsafe_allow_html=True)
        
        if task.agent_context:
            st.markdown("<div class='agent-context-badge'>🤖 Agent Context</div>", unsafe_allow_html=True)
        
        # Action buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📖 View", key=f"view_{task.id}", use_container_width=True):
                st.session_state.viewing_task = task.id
                st.rerun()
        
        with col2:
            # Quick move buttons to adjacent columns
            other_columns = [c for c in board.columns if c.id != task.column_id]
            if other_columns:
                move_options = {c.name: c.id for c in other_columns}
                selected = st.selectbox(
                    "Move to",
                    options=[""] + list(move_options.keys()),
                    key=f"move_select_{task.id}",
                    label_visibility="collapsed"
                )
                if selected and selected != "":
                    target_col_id = move_options[selected]
                    can_move, error = board.can_add_to_column(target_col_id)
                    if can_move:
                        task.move_to(target_col_id)
                        save_data(data)
                        st.success(f"Moved to {selected}")
                        st.rerun()
                    else:
                        st.error(error)
        
        with col3:
            if st.button("🗑️ Delete", key=f"delete_{task.id}", use_container_width=True):
                st.session_state.deleting_task = task.id
                st.rerun()


def render_add_task_form(board: Board, data: KanbanData):
    """Render form to add new task"""
    st.subheader("➕ Add New Task")
    
    with st.form("add_task_form"):
        title = st.text_input("Title*", max_chars=200)
        description = st.text_area("Description", height=100)
        
        col1, col2 = st.columns(2)
        with col1:
            priority = st.selectbox(
                "Priority",
                options=[p.value for p in Priority],
                index=1
            )
        with col2:
            column = st.selectbox(
                "Column",
                options=[(c.name, c.id) for c in sorted(board.columns, key=lambda x: x.order)],
                format_func=lambda x: x[0]
            )
        
        tags_input = st.text_input("Tags (comma-separated)", placeholder="e.g., backend, urgent, bug")
        
        submitted = st.form_submit_button("Add Task", use_container_width=True)
        
        if submitted:
            if not title:
                st.error("Title is required")
            else:
                column_id = column[1]
                can_add, error = board.can_add_to_column(column_id)
                
                if not can_add:
                    st.error(error)
                else:
                    tags = [t.strip() for t in tags_input.split(",") if t.strip()]
                    
                    task = Task(
                        id=board.get_next_task_id(),
                        board_id=board.id,
                        column_id=column_id,
                        title=title,
                        description=description if description else None,
                        priority=Priority(priority),
                        tags=tags
                    )
                    
                    board.tasks.append(task)
                    save_data(data)
                    st.success(f"Created task #{task.id}")
                    st.rerun()


def render_task_details(task: Task, board: Board, data: KanbanData):
    """Render detailed task view"""
    st.subheader(f"Task #{task.id}: {task.title}")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        col = board.get_column(task.column_id)
        st.markdown(f"**Column:** {col.name if col else task.column_id}")
    with col2:
        st.markdown(f"**Priority:** {task.priority.value.upper()}")
    with col3:
        st.markdown(f"**Created:** {task.created_at.strftime('%Y-%m-%d %H:%M')}")
    
    if task.description:
        st.markdown("**Description:**")
        st.markdown(task.description)
    
    if task.tags:
        st.markdown("**Tags:** " + ", ".join(task.tags))
    
    # Agent Context
    if task.agent_context:
        st.markdown("---")
        st.markdown("### 🤖 Agent Context")
        for key, value in task.agent_context.items():
            st.markdown(f"**{key}:** {value}")
        
        # Add agent context
        with st.expander("Update Agent Context"):
            ctx_key = st.text_input("Key", key=f"ctx_key_{task.id}")
            ctx_value = st.text_input("Value", key=f"ctx_value_{task.id}")
            if st.button("Update Context", key=f"ctx_update_{task.id}"):
                if ctx_key:
                    task.agent_context[ctx_key] = ctx_value
                    task.updated_at = now_utc()
                    save_data(data)
                    st.success("Context updated")
                    st.rerun()
    
    # History
    if task.history:
        st.markdown("---")
        st.markdown("### 📜 History")
        for entry in reversed(task.history[-10:]):
            ts = entry.get('timestamp', 'Unknown')
            action = entry.get('action', 'Unknown')
            reason = entry.get('reason', '')
            st.markdown(f"- **{ts}**: {action}" + (f" ({reason})" if reason else ""))
    
    if st.button("← Back to Board"):
        del st.session_state.viewing_task
        st.rerun()


def render_delete_confirmation(task: Task, board: Board, data: KanbanData):
    """Render delete confirmation dialog"""
    st.warning(f"Are you sure you want to delete task #{task.id}: '{task.title}'?")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Yes, Delete", use_container_width=True):
            board.tasks = [t for t in board.tasks if t.id != task.id]
            save_data(data)
            del st.session_state.deleting_task
            st.success("Task deleted")
            st.rerun()
    
    with col2:
        if st.button("❌ Cancel", use_container_width=True):
            del st.session_state.deleting_task
            st.rerun()


def render_filters(board: Board) -> tuple[Optional[str], Optional[str], Optional[str]]:
    """Render filter controls and return filter values"""
    st.sidebar.header("🔍 Filters")
    
    search = st.sidebar.text_input("Search tasks", placeholder="Search by title...")
    
    priority_filter = st.sidebar.selectbox(
        "Filter by Priority",
        options=["All"] + [p.value for p in Priority]
    )
    
    all_tags = set()
    for task in board.tasks:
        all_tags.update(task.tags)
    
    tag_filter = None
    if all_tags:
        tag_filter = st.sidebar.selectbox(
            "Filter by Tag",
            options=["All"] + sorted(list(all_tags))
        )
    
    return (
        search if search else None,
        priority_filter if priority_filter != "All" else None,
        tag_filter if tag_filter != "All" else None
    )


def filter_tasks(tasks: list[Task], search: Optional[str], priority: Optional[str], tag: Optional[str]) -> list[Task]:
    """Apply filters to task list"""
    filtered = tasks
    
    if search:
        search_lower = search.lower()
        filtered = [t for t in filtered if search_lower in t.title.lower()]
    
    if priority:
        filtered = [t for t in filtered if t.priority.value == priority]
    
    if tag:
        filtered = [t for t in filtered if tag in t.tags]
    
    return filtered


def main():
    """Main application"""
    # Load data
    data = load_data()
    board = data.get_board()
    
    if not board:
        st.error("No board found. Please initialize using the CLI first.")
        st.code("python3 kanban.py init-board --name 'My Board'")
        return
    
    # Header
    st.title(f"📋 {board.name}")
    st.markdown(f"*Total tasks: {len(board.tasks)}*")
    
    # Sidebar - Add Task Form
    with st.sidebar:
        render_add_task_form(board, data)
        
        st.markdown("---")
        st.markdown("### 📊 Statistics")
        for col in sorted(board.columns, key=lambda x: x.order):
            count = len(board.get_tasks_in_column(col.id))
            limit_text = f" / {col.limit}" if col.limit else ""
            st.markdown(f"**{col.name}:** {count}{limit_text}")
    
    # Check for viewing or deleting state
    if "viewing_task" in st.session_state:
        task = data.get_task(st.session_state.viewing_task)
        if task:
            render_task_details(task, board, data)
        else:
            st.error("Task not found")
            del st.session_state.viewing_task
        return
    
    if "deleting_task" in st.session_state:
        task = data.get_task(st.session_state.deleting_task)
        if task:
            render_delete_confirmation(task, board, data)
        else:
            del st.session_state.deleting_task
        return
    
    # Filters
    search, priority_filter, tag_filter = render_filters(board)
    
    # Main board view - Three columns
    columns = st.columns(len(board.columns))
    
    for idx, col in enumerate(sorted(board.columns, key=lambda x: x.order)):
        with columns[idx]:
            # Column header with gradient
            count = len(board.get_tasks_in_column(col.id))
            limit_text = f" ({count}/{col.limit})" if col.limit else f" ({count})"
            
            st.markdown(f"""
                <div class="column-header">
                    {col.name}{limit_text}
                </div>
            """, unsafe_allow_html=True)
            
            # WIP limit warning
            if col.limit and count >= col.limit:
                st.markdown(f"""
                    <div class="wip-warning">
                        ⚠️ WIP limit reached ({col.limit})
                    </div>
                """, unsafe_allow_html=True)
            
            # Get and filter tasks for this column
            tasks = board.get_tasks_in_column(col.id)
            tasks = filter_tasks(tasks, search, priority_filter, tag_filter)
            
            # Render tasks with drag-and-drop support
            if tasks:
                # Sortable list for drag-and-drop
                task_items = []
                for task in tasks:
                    task_items.append({
                        "id": task.id,
                        "title": f"#{task.id}: {task.title}",
                        "priority": task.priority.value,
                        "description": task.description or "",
                        "tags": task.tags,
                        "has_agent_context": bool(task.agent_context)
                    })
                
                # Display each task
                for task in tasks:
                    render_task_card_native(task, board, data)
                    st.markdown("---")
            else:
                st.markdown("""
                    <div class="empty-column">
                        No tasks<br>
                        <span style="font-size: 0.8rem;">Drag tasks here or add new ones</span>
                    </div>
                """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
