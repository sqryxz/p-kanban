"""
Kanban GUI - Streamlit web interface for the Kanban board
"""

import streamlit as st
from datetime import datetime
from typing import Optional

from models import KanbanData, Board, Task, Column, Priority, now_utc
from storage import KanbanStorage

# Page configuration
st.set_page_config(
    page_title="Kanban Board",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .task-card {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 12px;
        margin: 8px 0;
        border-left: 4px solid #dee2e6;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .task-card:hover {
        box-shadow: 0 2px 8px rgba(0,0,0,0.15);
    }
    .priority-low { border-left-color: #6c757d; }
    .priority-medium { border-left-color: #007bff; }
    .priority-high { border-left-color: #fd7e14; }
    .priority-critical { border-left-color: #dc3545; }
    
    .column-header {
        background-color: #e9ecef;
        padding: 12px;
        border-radius: 8px;
        text-align: center;
        font-weight: bold;
        margin-bottom: 16px;
    }
    
    .tag-badge {
        display: inline-block;
        background-color: #e3f2fd;
        color: #1976d2;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.75rem;
        margin: 2px;
    }
    
    .agent-context-badge {
        display: inline-block;
        background-color: #fff3e0;
        color: #e65100;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.75rem;
        margin-top: 4px;
    }
    
    .stButton button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=1)
def load_data() -> KanbanData:
    """Load kanban data from storage"""
    storage = KanbanStorage()
    return storage.load()


def save_data(data: KanbanData):
    """Save kanban data to storage"""
    storage = KanbanStorage()
    storage.save(data)
    st.cache_data.clear()


def get_priority_class(priority: Priority) -> str:
    """Get CSS class for priority level"""
    return f"priority-{priority.value}"


def get_priority_color(priority: Priority) -> str:
    """Get color for priority badge"""
    colors = {
        Priority.LOW: "#6c757d",
        Priority.MEDIUM: "#007bff",
        Priority.HIGH: "#fd7e14",
        Priority.CRITICAL: "#dc3545"
    }
    return colors.get(priority, "#6c757d")


def render_task_card(task: Task, board: Board, data: KanbanData):
    """Render a single task card"""
    priority_class = get_priority_class(task.priority)
    priority_color = get_priority_color(task.priority)
    
    with st.container():
        st.markdown(f"""
        <div class="task-card {priority_class}">
            <div style="font-weight: bold; font-size: 1rem; margin-bottom: 4px;">
                #{task.id}: {task.title}
            </div>
        """, unsafe_allow_html=True)
        
        # Priority badge
        st.markdown(f"""
            <span style="
                background-color: {priority_color}20;
                color: {priority_color};
                padding: 2px 8px;
                border-radius: 4px;
                font-size: 0.75rem;
                font-weight: 500;
            ">{task.priority.value.upper()}</span>
        """, unsafe_allow_html=True)
        
        # Description
        if task.description:
            desc = task.description[:100] + "..." if len(task.description) > 100 else task.description
            st.markdown(f"<div style='margin-top: 8px; font-size: 0.9rem; color: #666;'>{desc}</div>", unsafe_allow_html=True)
        
        # Tags
        if task.tags:
            tags_html = " ".join([f'<span class="tag-badge">{tag}</span>' for tag in task.tags])
            st.markdown(f"<div style='margin-top: 8px;'>{tags_html}</div>", unsafe_allow_html=True)
        
        # Agent context indicator
        if task.agent_context:
            st.markdown("""
                <div class="agent-context-badge">🤖 Agent Context</div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Action buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📖 View", key=f"view_{task.id}"):
                st.session_state.viewing_task = task.id
                st.rerun()
        
        with col2:
            # Move dropdown
            other_columns = [c for c in board.columns if c.id != task.column_id]
            if other_columns:
                move_to = st.selectbox(
                    "Move to",
                    options=[c.name for c in other_columns],
                    key=f"move_{task.id}",
                    label_visibility="collapsed"
                )
                if st.button("➡️ Move", key=f"move_btn_{task.id}"):
                    target_col = next(c for c in other_columns if c.name == move_to)
                    can_move, error = board.can_add_to_column(target_col.id)
                    if can_move:
                        task.move_to(target_col.id)
                        save_data(data)
                        st.success(f"Moved to {target_col.name}")
                        st.rerun()
                    else:
                        st.error(error)
        
        with col3:
            if st.button("🗑️ Delete", key=f"delete_{task.id}"):
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
        for entry in reversed(task.history[-10:]):  # Show last 10 entries
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
            # Column header
            count = len(board.get_tasks_in_column(col.id))
            limit_text = f" ({count}/{col.limit})" if col.limit else f" ({count})"
            
            st.markdown(f"""
                <div class="column-header">
                    {col.name}{limit_text}
                </div>
            """, unsafe_allow_html=True)
            
            # WIP limit warning
            if col.limit and count >= col.limit:
                st.warning(f"⚠️ WIP limit reached ({col.limit})")
            
            # Get and filter tasks for this column
            tasks = board.get_tasks_in_column(col.id)
            tasks = filter_tasks(tasks, search, priority_filter, tag_filter)
            
            # Render tasks
            if tasks:
                for task in tasks:
                    render_task_card(task, board, data)
                    st.markdown("---")
            else:
                st.markdown("""
                    <div style="text-align: center; color: #999; padding: 20px;">
                        No tasks
                    </div>
                """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
