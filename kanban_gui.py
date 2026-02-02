"""
Kanban GUI - Streamlit web interface for the Kanban board
Improved version with dark theme, drag-and-drop, and better UX
"""

import streamlit as st
from datetime import datetime
from typing import Optional, List, Dict, Any
import json

st.set_page_config(
    page_title="Kanban Board",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Force dark theme
def set_dark_theme():
    st.markdown("""
        <style>
        /* Force dark theme */
        .stApp {
            background-color: #0d1117 !important;
            color: #c9d1d9 !important;
        }
        
        /* Main title */
        h1 {
            color: #58a6ff !important;
            font-weight: 700 !important;
            text-shadow: 0 0 20px rgba(88, 166, 255, 0.3);
        }
        
        /* Subtitle */
        .subtitle {
            color: #8b949e !important;
            font-size: 1.1rem;
            margin-bottom: 2rem;
        }
        
        /* Column headers */
        .column-header {
            background: linear-gradient(135deg, #1f6feb 0%, #388bfd 100%);
            color: #ffffff !important;
            padding: 16px 20px;
            border-radius: 12px;
            text-align: center;
            font-weight: 700;
            font-size: 1.1rem;
            margin-bottom: 16px;
            box-shadow: 0 4px 15px rgba(31, 111, 235, 0.4);
            text-shadow: 0 2px 4px rgba(0,0,0,0.3);
            border: 1px solid rgba(255,255,255,0.1);
        }
        
        /* Column container */
        .column-container {
            background-color: #161b22;
            border-radius: 12px;
            padding: 12px;
            min-height: 500px;
            border: 2px solid #30363d;
            transition: all 0.3s ease;
        }
        
        .column-container:hover {
            border-color: #58a6ff;
        }
        
        /* Task cards */
        .task-card {
            background-color: #21262d;
            border-radius: 10px;
            padding: 14px;
            margin: 10px 0;
            border-left: 4px solid;
            box-shadow: 0 2px 8px rgba(0,0,0,0.3);
            cursor: grab;
            transition: all 0.2s ease;
            border: 1px solid #30363d;
        }
        
        .task-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 20px rgba(0,0,0,0.4);
            border-color: #58a6ff;
        }
        
        .task-card.dragging {
            opacity: 0.5;
            cursor: grabbing;
        }
        
        /* Priority colors */
        .priority-low { border-left-color: #8b949e; }
        .priority-medium { border-left-color: #58a6ff; }
        .priority-high { border-left-color: #f0883e; }
        .priority-critical { border-left-color: #f85149; }
        
        /* Priority badge */
        .priority-badge {
            display: inline-block;
            padding: 3px 10px;
            border-radius: 20px;
            font-size: 0.7rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        /* Tags */
        .tag-badge {
            display: inline-block;
            background-color: rgba(88, 166, 255, 0.15);
            color: #58a6ff;
            padding: 3px 10px;
            border-radius: 20px;
            font-size: 0.75rem;
            margin: 3px;
            font-weight: 500;
            border: 1px solid rgba(88, 166, 255, 0.3);
        }
        
        /* Agent context */
        .agent-context-badge {
            display: inline-block;
            background-color: rgba(210, 153, 34, 0.15);
            color: #d29922;
            padding: 3px 10px;
            border-radius: 20px;
            font-size: 0.75rem;
            margin-top: 8px;
            font-weight: 500;
            border: 1px solid rgba(210, 153, 34, 0.3);
        }
        
        /* Empty column state */
        .empty-column {
            text-align: center;
            color: #8b949e;
            padding: 60px 20px;
            border: 2px dashed #30363d;
            border-radius: 10px;
            cursor: pointer;
            transition: all 0.3s ease;
            background-color: rgba(48, 54, 61, 0.3);
        }
        
        .empty-column:hover {
            border-color: #58a6ff;
            background-color: rgba(88, 166, 255, 0.1);
            color: #58a6ff;
        }
        
        /* Drag drop zone */
        .drop-zone {
            min-height: 100px;
            border: 2px dashed transparent;
            border-radius: 8px;
            transition: all 0.3s ease;
        }
        
        .drop-zone.drag-over {
            border-color: #58a6ff;
            background-color: rgba(88, 166, 255, 0.1);
        }
        
        /* Buttons */
        .stButton button {
            background-color: #238636 !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            padding: 12px 24px !important;
            font-size: 1rem !important;
            box-shadow: 0 4px 12px rgba(35, 134, 54, 0.3) !important;
            transition: all 0.2s ease !important;
        }
        
        .stButton button:hover {
            background-color: #2ea043 !important;
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(35, 134, 54, 0.4) !important;
        }
        
        /* Secondary buttons */
        button[kind="secondary"] {
            background-color: #21262d !important;
            color: #c9d1d9 !important;
            border: 1px solid #30363d !important;
        }
        
        /* Dialog/Modal */
        [data-testid="stDialog"] {
            background-color: #161b22 !important;
        }
        
        /* Form styling */
        div[data-testid="stForm"] {
            background-color: #161b22;
            padding: 24px;
            border-radius: 12px;
            border: 1px solid #30363d;
        }
        
        /* Input fields */
        .stTextInput input, .stTextArea textarea, .stSelectbox select {
            background-color: #0d1117 !important;
            color: #c9d1d9 !important;
            border: 1px solid #30363d !important;
            border-radius: 8px !important;
        }
        
        .stTextInput input:focus, .stTextArea textarea:focus {
            border-color: #58a6ff !important;
            box-shadow: 0 0 0 3px rgba(88, 166, 255, 0.1);
        }
        
        /* WIP warning */
        .wip-warning {
            background-color: rgba(210, 153, 34, 0.15);
            color: #d29922;
            padding: 10px 16px;
            border-radius: 8px;
            border-left: 4px solid #d29922;
            font-size: 0.9rem;
            margin-bottom: 12px;
            font-weight: 500;
        }
        
        /* Stats card */
        .stats-card {
            background-color: #161b22;
            border: 1px solid #30363d;
            border-radius: 10px;
            padding: 16px;
            margin-bottom: 12px;
        }
        
        .stats-label {
            color: #8b949e;
            font-size: 0.85rem;
        }
        
        .stats-value {
            color: #58a6ff;
            font-size: 1.5rem;
            font-weight: 700;
        }
        
        /* Drag handle */
        .drag-handle {
            float: right;
            color: #484f58;
            cursor: grab;
            padding: 4px 8px;
            border-radius: 4px;
            transition: all 0.2s;
        }
        
        .drag-handle:hover {
            color: #58a6ff;
            background-color: rgba(88, 166, 255, 0.1);
        }
        
        /* Task title */
        .task-title {
            font-weight: 600;
            font-size: 1rem;
            color: #c9d1d9;
            margin-bottom: 6px;
        }
        
        /* Task description */
        .task-desc {
            color: #8b949e;
            font-size: 0.9rem;
            line-height: 1.4;
            margin-top: 8px;
        }
        
        /* Action bar */
        .action-bar {
            display: flex;
            gap: 8px;
            margin-top: 12px;
        }
        
        .action-btn {
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 0.8rem;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s;
            border: none;
        }
        
        .view-btn {
            background-color: rgba(88, 166, 255, 0.15);
            color: #58a6ff;
        }
        
        .view-btn:hover {
            background-color: rgba(88, 166, 255, 0.25);
        }
        
        .delete-btn {
            background-color: rgba(248, 81, 73, 0.15);
            color: #f85149;
        }
        
        .delete-btn:hover {
            background-color: rgba(248, 81, 73, 0.25);
        }
        
        /* Sidebar */
        [data-testid="stSidebar"] {
            background-color: #161b22;
            border-right: 1px solid #30363d;
        }
        
        /* Selectbox in sidebar */
        [data-testid="stSidebar"] .stSelectbox {
            margin-bottom: 16px;
        }
        
        /* Divider */
        hr {
            border-color: #30363d !important;
            margin: 24px 0 !important;
        }
        
        /* Success message */
        .stSuccess {
            background-color: rgba(35, 134, 54, 0.15) !important;
            color: #3fb950 !important;
            border: 1px solid rgba(35, 134, 54, 0.3) !important;
            border-radius: 8px !important;
        }
        
        /* Error message */
        .stError {
            background-color: rgba(248, 81, 73, 0.15) !important;
            color: #f85149 !important;
            border: 1px solid rgba(248, 81, 73, 0.3) !important;
            border-radius: 8px !important;
        }
        
        /* Warning message */
        .stWarning {
            background-color: rgba(210, 153, 34, 0.15) !important;
            color: #d29922 !important;
            border: 1px solid rgba(210, 153, 34, 0.3) !important;
            border-radius: 8px !important;
        }
        </style>
    """, unsafe_allow_html=True)

set_dark_theme()

# Import after setting theme
from models import KanbanData, Board, Task, Column, Priority, now_utc
from storage import KanbanStorage

# Initialize session state
if 'show_add_dialog' not in st.session_state:
    st.session_state.show_add_dialog = False
if 'selected_column_for_add' not in st.session_state:
    st.session_state.selected_column_for_add = 'todo'
if 'viewing_task' not in st.session_state:
    st.session_state.viewing_task = None
if 'deleting_task' not in st.session_state:
    st.session_state.deleting_task = None
if 'drag_task_id' not in st.session_state:
    st.session_state.drag_task_id = None
if 'drag_target_column' not in st.session_state:
    st.session_state.drag_target_column = None

@st.cache_data(ttl=1)
def load_data() -> KanbanData:
    storage = KanbanStorage()
    return storage.load()

def save_data(data: KanbanData):
    storage = KanbanStorage()
    storage.save(data)
    st.cache_data.clear()

def get_priority_style(priority: Priority):
    styles = {
        Priority.LOW: ("#8b949e", "rgba(139, 148, 158, 0.15)"),
        Priority.MEDIUM: ("#58a6ff", "rgba(88, 166, 255, 0.15)"),
        Priority.HIGH: ("#f0883e", "rgba(240, 136, 62, 0.15)"),
        Priority.CRITICAL: ("#f85149", "rgba(248, 81, 73, 0.15)")
    }
    return styles.get(priority, ("#8b949e", "rgba(139, 148, 158, 0.15)"))

def render_task_card(task: Task, board: Board, data: KanbanData):
    text_color, bg_color = get_priority_style(task.priority)
    priority_class = f"priority-{task.priority.value}"
    
    tags_html = ""
    if task.tags:
        tags_html = " ".join([f'<span class="tag-badge">{tag}</span>' for tag in task.tags])
    
    agent_html = ""
    if task.agent_context:
        agent_html = '<div class="agent-context-badge">🤖 Agent Context</div>'
    
    desc_html = ""
    if task.description:
        desc = task.description[:80] + "..." if len(task.description) > 80 else task.description
        desc_html = f'<div class="task-desc">{desc}</div>'
    
    st.markdown(f"""
        <div class="task-card {priority_class}" draggable="true" data-task-id="{task.id}">
            <div style="display: flex; justify-content: space-between; align-items: start;">
                <div class="task-title">#{task.id}: {task.title}</div>
                <div class="drag-handle">⋮⋮</div>
            </div>
            <div style="margin-top: 4px;">
                <span class="priority-badge" style="background-color: {bg_color}; color: {text_color}; border: 1px solid {text_color}40;">
                    {task.priority.value.upper()}
                </span>
            </div>
            {desc_html}
            {f'<div style="margin-top: 8px;">{tags_html}</div>' if tags_html else ""}
            {agent_html}
        </div>
    """, unsafe_allow_html=True)
    
    # Action buttons using Streamlit
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("👁️ View", key=f"view_{task.id}", use_container_width=True):
            st.session_state.viewing_task = task.id
            st.rerun()
    with col2:
        # Quick move dropdown
        other_cols = [c for c in board.columns if c.id != task.column_id]
        if other_cols:
            options = ["Move to..."] + [c.name for c in other_cols]
            selected = st.selectbox(
                "Move",
                options=options,
                key=f"move_{task.id}",
                label_visibility="collapsed"
            )
            if selected != "Move to...":
                target_col = next(c for c in other_cols if c.name == selected)
                can_move, error = board.can_add_to_column(target_col.id)
                if can_move:
                    task.move_to(target_col.id)
                    save_data(data)
                    st.success(f"✓ Moved to {selected}")
                    st.rerun()
                else:
                    st.error(error)
    with col3:
        if st.button("🗑️ Delete", key=f"del_{task.id}", use_container_width=True):
            st.session_state.deleting_task = task.id
            st.rerun()

def render_add_task_dialog(board: Board, data: KanbanData, default_column: str = 'todo'):
    """Render the add task form in a dialog-like container"""
    with st.container():
        st.markdown("### ➕ Add New Task")
        
        with st.form("add_task_form"):
            title = st.text_input("Title*", max_chars=200, placeholder="Enter task title...")
            description = st.text_area("Description", height=100, placeholder="Optional description...")
            
            col1, col2 = st.columns(2)
            with col1:
                priority = st.selectbox("Priority", options=[p.value for p in Priority], index=1)
            with col2:
                col_options = [(c.name, c.id) for c in sorted(board.columns, key=lambda x: x.order)]
                default_idx = next((i for i, (_, cid) in enumerate(col_options) if cid == default_column), 0)
                column = st.selectbox(
                    "Column",
                    options=col_options,
                    format_func=lambda x: x[0],
                    index=default_idx
                )
            
            tags_input = st.text_input("Tags (comma-separated)", placeholder="e.g., urgent, backend, bug")
            
            col_submit, col_cancel = st.columns(2)
            with col_submit:
                submitted = st.form_submit_button("✓ Add Task", use_container_width=True)
            with col_cancel:
                cancelled = st.form_submit_button("✕ Cancel", use_container_width=True)
            
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
                        st.session_state.show_add_dialog = False
                        st.success(f"✓ Created task #{task.id}")
                        st.rerun()
            
            if cancelled:
                st.session_state.show_add_dialog = False
                st.rerun()

def render_task_details(task: Task, board: Board, data: KanbanData):
    st.markdown(f"## Task #{task.id}: {task.title}")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        col = board.get_column(task.column_id)
        st.markdown(f"**Column:** {col.name if col else task.column_id}")
    with col2:
        st.markdown(f"**Priority:** {task.priority.value.upper()}")
    with col3:
        st.markdown(f"**Created:** {task.created_at.strftime('%Y-%m-%d')}")
    
    if task.description:
        st.markdown("### Description")
        st.markdown(task.description)
    
    if task.tags:
        st.markdown("### Tags")
        tags_html = " ".join([f'<span class="tag-badge">{tag}</span>' for tag in task.tags])
        st.markdown(tags_html, unsafe_allow_html=True)
    
    if task.agent_context:
        st.markdown("### 🤖 Agent Context")
        for key, value in task.agent_context.items():
            st.markdown(f"**{key}:** {value}")
        
        with st.expander("Update Context"):
            ctx_key = st.text_input("Key", key=f"ctx_key_{task.id}")
            ctx_value = st.text_input("Value", key=f"ctx_value_{task.id}")
            if st.button("Update", key=f"ctx_update_{task.id}"):
                if ctx_key:
                    task.agent_context[ctx_key] = ctx_value
                    task.updated_at = now_utc()
                    save_data(data)
                    st.success("✓ Context updated")
                    st.rerun()
    
    if task.history:
        st.markdown("### 📜 History")
        for entry in reversed(task.history[-10:]):
            ts = entry.get('timestamp', 'Unknown')[:16]
            action = entry.get('action', 'Unknown')
            reason = entry.get('reason', '')
            st.markdown(f"- **{ts}**: {action}" + (f" — {reason}" if reason else ""))
    
    st.markdown("---")
    if st.button("← Back to Board", use_container_width=True):
        del st.session_state.viewing_task
        st.rerun()

def render_delete_confirmation(task: Task, board: Board, data: KanbanData):
    st.markdown(f"### ⚠️ Delete Task #{task.id}?")
    st.markdown(f"Are you sure you want to delete **'{task.title}'**?")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✓ Yes, Delete", use_container_width=True, type="primary"):
            board.tasks = [t for t in board.tasks if t.id != task.id]
            save_data(data)
            del st.session_state.deleting_task
            st.success("✓ Task deleted")
            st.rerun()
    with col2:
        if st.button("✕ Cancel", use_container_width=True):
            del st.session_state.deleting_task
            st.rerun()

def main():
    data = load_data()
    board = data.get_board()
    
    if not board:
        st.error("No board found. Initialize using CLI: `python3 kanban.py init-board --name 'My Board'`")
        return
    
    # Header with dark theme styling
    st.markdown(f"<h1>📋 {board.name}</h1>", unsafe_allow_html=True)
    st.markdown(f"<div class='subtitle'>Total tasks: {len(board.tasks)} | Drag and drop to organize</div>", unsafe_allow_html=True)
    
    # Handle viewing/deleting states
    if st.session_state.viewing_task:
        task = data.get_task(st.session_state.viewing_task)
        if task:
            render_task_details(task, board, data)
        else:
            st.error("Task not found")
            del st.session_state.viewing_task
        return
    
    if st.session_state.deleting_task:
        task = data.get_task(st.session_state.deleting_task)
        if task:
            render_delete_confirmation(task, board, data)
        else:
            del st.session_state.deleting_task
        return
    
    # Main action button - Add Task
    col_add, col_spacer = st.columns([1, 4])
    with col_add:
        if st.button("➕ Add New Task", use_container_width=True):
            st.session_state.show_add_dialog = True
    
    # Show add task dialog if triggered
    if st.session_state.show_add_dialog:
        st.markdown("---")
        render_add_task_dialog(board, data, st.session_state.selected_column_for_add)
        st.markdown("---")
    
    # Sidebar with filters and stats
    with st.sidebar:
        st.markdown("### 📊 Statistics")
        for col in sorted(board.columns, key=lambda x: x.order):
            count = len(board.get_tasks_in_column(col.id))
            limit_text = f" / {col.limit}" if col.limit else ""
            st.markdown(f"""
                <div class="stats-card">
                    <div class="stats-label">{col.name}</div>
                    <div class="stats-value">{count}{limit_text}</div>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("### 🔍 Filters")
        search = st.text_input("Search", placeholder="Search tasks...")
        priority_filter = st.selectbox("Priority", options=["All"] + [p.value for p in Priority])
        
        all_tags = set()
        for task in board.tasks:
            all_tags.update(task.tags)
        if all_tags:
            tag_filter = st.selectbox("Tag", options=["All"] + sorted(list(all_tags)))
        else:
            tag_filter = "All"
        
        if st.button("🔄 Refresh", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    
    # Apply filters
    search_filter = search if search else None
    priority_filter_val = priority_filter if priority_filter != "All" else None
    tag_filter_val = tag_filter if tag_filter != "All" else None
    
    # Kanban board - three columns
    cols = st.columns(len(board.columns))
    
    for idx, col in enumerate(sorted(board.columns, key=lambda x: x.order)):
        with cols[idx]:
            # Column header
            count = len(board.get_tasks_in_column(col.id))
            limit_text = f" ({count}/{col.limit})" if col.limit else f" ({count})"
            
            st.markdown(f"""
                <div class="column-header">
                    {col.name}{limit_text}
                </div>
            """, unsafe_allow_html=True)
            
            # WIP warning
            if col.limit and count >= col.limit:
                st.markdown("""
                    <div class="wip-warning">
                        ⚠️ WIP limit reached
                    </div>
                """, unsafe_allow_html=True)
            
            # Get filtered tasks
            tasks = board.get_tasks_in_column(col.id)
            if search_filter:
                tasks = [t for t in tasks if search_filter.lower() in t.title.lower()]
            if priority_filter_val:
                tasks = [t for t in tasks if t.priority.value == priority_filter_val]
            if tag_filter_val and tag_filter_val != "All":
                tasks = [t for t in tasks if tag_filter_val in t.tags]
            
            # Render tasks or empty state
            if tasks:
                for task in tasks:
                    render_task_card(task, board, data)
            else:
                # Clickable empty state
                empty_clicked = st.button(
                    f"+ Add task to {col.name}", 
                    key=f"empty_{col.id}",
                    use_container_width=True
                )
                if empty_clicked:
                    st.session_state.show_add_dialog = True
                    st.session_state.selected_column_for_add = col.id
                    st.rerun()
                
                st.markdown(f"""
                    <div class="empty-column">
                        <div style="font-size: 2rem; margin-bottom: 8px;">📭</div>
                        <div>No tasks yet</div>
                        <div style="font-size: 0.85rem; margin-top: 8px;">Click above to add one</div>
                    </div>
                """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
