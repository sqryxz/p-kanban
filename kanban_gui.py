"""
Kanban GUI - Minimal sleek interface for the Kanban board
"""

import streamlit as st
from datetime import datetime
from typing import Optional, List

st.set_page_config(
    page_title="pODV - Progress Tracker",
    page_icon="◼",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Minimal sleek dark theme
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');
    
    * {
        font-family: 'Inter', sans-serif !important;
    }
    
    .stApp {
        background-color: #0a0a0a;
        color: #e0e0e0;
    }
    
    /* Title */
    h1 {
        color: #fff !important;
        font-weight: 300 !important;
        font-size: 1.5rem !important;
        letter-spacing: 0.05em;
        margin-bottom: 0.5rem !important;
        padding-bottom: 1rem;
        border-bottom: 1px solid #222;
    }
    
    /* Column headers - minimal */
    .column-header {
        background: transparent;
        border: 1px solid #333;
        color: #888;
        padding: 8px 12px;
        border-radius: 4px;
        text-align: left;
        font-weight: 500;
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: 12px;
    }
    
    .column-header.backlog { border-color: #4a4a4a; color: #666; }
    .column-header.todo { border-color: #5a5a5a; color: #888; }
    .column-header.inprogress { border-color: #f0a030; color: #f0a030; }
    .column-header.testing { border-color: #30a0f0; color: #30a0f0; }
    .column-header.done { border-color: #30f080; color: #30f080; }
    
    /* Task cards - minimal */
    .task-card {
        background-color: #141414;
        border: 1px solid #222;
        border-radius: 3px;
        padding: 10px 12px;
        margin: 6px 0;
        font-size: 0.8rem;
        transition: all 0.15s ease;
        cursor: pointer;
    }
    
    .task-card:hover {
        border-color: #444;
        background-color: #1a1a1a;
    }
    
    /* Priority indicators - left border */
    .priority-low { border-left: 2px solid #666; }
    .priority-medium { border-left: 2px solid #888; }
    .priority-high { border-left: 2px solid #f0a030; }
    .priority-critical { border-left: 2px solid #f03030; }
    
    /* Task title */
    .task-title {
        font-weight: 400;
        color: #ccc;
        margin-bottom: 4px;
        font-size: 0.8rem;
    }
    
    /* Task meta */
    .task-meta {
        font-size: 0.65rem;
        color: #555;
        display: flex;
        gap: 8px;
        align-items: center;
    }
    
    /* Tags */
    .tag {
        background: #1f1f1f;
        padding: 1px 6px;
        border-radius: 2px;
        color: #666;
    }

    /* Task actions list styling */
    .task-actions-card {
        background-color: #141414;
        border: 1px solid #222;
        border-radius: 3px;
        padding: 10px 12px;
        margin: 6px 0;
    }

    .task-actions-title {
        font-weight: 400;
        color: #ccc;
        margin-bottom: 6px;
        font-size: 0.8rem;
    }

    .task-actions-meta {
        font-size: 0.65rem;
        color: #555;
        display: flex;
        gap: 8px;
        align-items: center;
    }

    .task-actions-buttons {
        margin-top: 4px;
    }
    
    /* Agent indicator */
    .agent-indicator {
        color: #d4a030;
    }
    
    /* Buttons - minimal */
    .stButton button {
        background: transparent !important;
        border: 1px solid #2a2a2a !important;
        color: #666 !important;
        font-size: 0.6rem !important;
        padding: 2px 6px !important;
        font-weight: 400 !important;
        border-radius: 2px !important;
        letter-spacing: 0.03em;
        text-transform: lowercase;
        height: auto !important;
        min-height: 20px !important;
        line-height: 1.2 !important;
    }
    
    .stButton button:hover {
        border-color: #444 !important;
        color: #888 !important;
        background: #1a1a1a !important;
    }
    
    /* Primary action button */
    button[kind="primary"] {
        background: #1a1a1a !important;
        border-color: #444 !important;
        color: #fff !important;
    }
    
    /* Empty state */
    .empty-state {
        text-align: center;
        padding: 40px 20px;
        color: #333;
        font-size: 0.7rem;
        border: 1px dashed #222;
        border-radius: 3px;
        cursor: pointer;
        transition: all 0.3s ease;
        background-color: rgba(48, 54, 61, 0.3);
    }
    
    .empty-state:hover {
        border-color: #444;
        color: #555;
        cursor: pointer;
    }
    
    /* Forms */
    div[data-testid="stForm"] {
        background: #0f0f0f;
        border: 1px solid #222;
        border-radius: 4px;
        padding: 16px;
    }
    
    /* Inputs */
    .stTextInput input, .stTextArea textarea, .stSelectbox select {
        background: #141414 !important;
        border: 1px solid #222 !important;
        color: #aaa !important;
        font-size: 0.8rem !important;
        border-radius: 3px !important;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: #0a0a0a;
        border-right: 1px solid #1a1a1a;
    }
    
    /* WIP indicator */
    .wip-badge {
        font-size: 0.6rem;
        color: #f0a030;
        margin-left: auto;
    }
    
    /* Divider */
    hr {
        border-color: #1a1a1a !important;
        margin: 1rem 0 !important;
    }
    
    /* Column containers */
    .column-container {
        min-height: 60vh;
        padding: 4px;
    }
    
    /* Fix sidebar toggle icon - hide text and show proper icon */
    /* Multiple selector strategies for different Streamlit versions */
    button[data-testid="baseButton-header"],
    button[kind="header"],
    section[data-testid="stSidebar"] button[data-testid="stBaseButton-header"],
    section[data-testid="stSidebar"] button[data-testid="baseButton-header"] {
        font-size: 0 !important;
        color: transparent !important;
        position: relative !important;
    }
    
    button[data-testid="baseButton-header"]::before,
    button[kind="header"]::before,
    section[data-testid="stSidebar"] button[data-testid="stBaseButton-header"]::before,
    section[data-testid="stSidebar"] button[data-testid="baseButton-header"]::before {
        content: "☰";
        font-size: 16px !important;
        color: #666 !important;
        position: absolute !important;
        left: 50% !important;
        top: 50% !important;
        transform: translate(-50%, -50%) !important;
        visibility: visible !important;
        display: block !important;
    }
    
    /* Hide any text/span inside the button */
    button[data-testid="baseButton-header"] span,
    button[kind="header"] span {
        display: none !important;
    }
</style>
""", unsafe_allow_html=True)

from models import KanbanData, Board, Task, Column, Priority, now_utc
from storage import KanbanStorage
from streamlit_sortables import sort_items


# Custom CSS for drag-and-drop visual feedback (in-component)
DRAG_DROP_CSS = """
.sortable-component {
    display: flex;
    gap: 12px;
    align-items: flex-start;
}

/* Drop zone highlighting */
.sortable-container.droppable-hover {
    background-color: rgba(240, 160, 48, 0.1) !important;
    border: 2px dashed #f0a030 !important;
}

/* Dragging item styling */
.sortable-item.dragging {
    background-color: #2a2a2a !important;
    border: 2px solid #f0a030 !important;
    opacity: 0.9 !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5) !important;
}

/* Container styling to match dark theme */
.sortable-container {
    background-color: #0a0a0a !important;
    border: 1px solid #222 !important;
    border-radius: 4px !important;
    min-width: 200px !important;
    flex: 1 1 0 !important;
}

.sortable-container-header {
    background-color: #141414 !important;
    border-bottom: 1px solid #222 !important;
    padding: 8px 12px !important;
    font-family: 'Inter', sans-serif !important;
}

.sortable-container-body {
    background-color: #0a0a0a !important;
    padding: 4px !important;
    min-height: 100px !important;
}

    .sortable-item {
    background-color: #141414 !important;
    border: 1px solid #222 !important;
    border-radius: 3px !important;
    padding: 10px 12px !important;
    margin: 6px 0 !important;
    font-family: 'Inter', sans-serif !important;
    color: #ccc !important;
    font-size: 0.8rem !important;
    transition: all 0.15s ease !important;
    cursor: grab !important;
}

    .sortable-item:hover {
    border-color: #444 !important;
    background-color: #1a1a1a !important;
}

.sortable-item:active {
    cursor: grabbing !important;
}
"""


def build_sortable_items(board: Board, search: str = "", tag_filter: str = "all") -> list:
    """Build items structure for streamlit-sortables from board tasks"""
    # Ensure we have strings, not None
    search = search or ""
    tag_filter = tag_filter or "all"
    items = []
    
    for col in sorted(board.columns, key=lambda x: x.order):
        # Filter tasks for this column
        tasks = board.get_tasks_in_column(col.id)
        
        if search:
            tasks = [t for t in tasks if search.lower() in t.title.lower()]
        if tag_filter != "all":
            tasks = [t for t in tasks if tag_filter in t.tags]
        
        # Build task items with display info
        task_items = []
        for task in tasks:
            item_str = f"#{task.id} {task.title}"
            task_items.append(item_str)
        
        items.append({
            'header': f"{col.name.lower()} ({len(tasks)})",
            'items': task_items,
            'column_id': col.id  # Track which column this is
        })
    
    return items


def _parse_task_id(item_str: str) -> Optional[int]:
    if not item_str:
        return None
    if not item_str.startswith("#"):
        return None
    token = item_str.split()[0].lstrip("#")
    try:
        return int(token)
    except ValueError:
        return None


def process_sortable_movement(original_items: list, sorted_items: list, board: Board, data: KanbanData) -> tuple:
    """Process drag-and-drop movements and update task positions
    
    Returns: (moved_tasks_count, updated_board)
    """
    moved_count = 0
    
    if not sorted_items or len(original_items) != len(sorted_items):
        return moved_count, board
    
    # Build original column mapping
    original_mapping = {}  # task_id -> column_id
    for container in original_items:
        column_id = container.get('column_id')
        for item in container.get('items', []):
            task_id = _parse_task_id(item)
            if task_id is not None:
                original_mapping[task_id] = column_id
    
    # Check for movements in sorted result
    for container in sorted_items:
        column_id = container.get('column_id')
        for item in container.get('items', []):
            task_id = _parse_task_id(item)
            if task_id is None:
                continue
            original_column = original_mapping.get(task_id)
            
            # Task moved to a different column
            if original_column and original_column != column_id:
                task = data.get_task(task_id)
                if task:
                    ok, err = board.can_add_to_column(column_id)
                    if ok:
                        task.move_to(column_id)
                        moved_count += 1
                    else:
                        # Log warning but don't fail
                        pass
    
    return moved_count, board

@st.cache_data
def load_data() -> KanbanData:
    storage = KanbanStorage()
    return storage.load()

def save_data(data: KanbanData):
    storage = KanbanStorage()
    storage.save(data)
    st.cache_data.clear()

# Initialize session state
if 'show_add' not in st.session_state:
    st.session_state.show_add = False
if 'show_edit' not in st.session_state:
    st.session_state.show_edit = False
if 'editing_task_id' not in st.session_state:
    st.session_state.editing_task_id = None
if 'current_board_id' not in st.session_state:
    st.session_state.current_board_id = None
if 'show_create_board' not in st.session_state:
    st.session_state.show_create_board = False
if 'selected_column' not in st.session_state:
    st.session_state.selected_column = 'backlog'
if 'viewing_task' not in st.session_state:
    st.session_state.viewing_task = None
if 'show_move_menu' not in st.session_state:
    st.session_state.show_move_menu = None
if 'sortable_key' not in st.session_state:
    st.session_state.sortable_key = "kanban_sortable"
if 'delete_confirm' not in st.session_state:
    st.session_state.delete_confirm = None  # Task ID pending confirmation

def render_task_card(task: Task, board: Board, data: KanbanData):
    """Render minimal task card with click-to-edit"""
    priority_class = f"priority-{task.priority.value}"
    
    # Build meta line
    meta_parts = []
    if task.tags:
        meta_parts.extend([f'<span class="tag">{t}</span>' for t in task.tags[:2]])
    if task.agent_context:
        meta_parts.append('<span class="agent-indicator">◉</span>')
    
    meta_html = ' '.join(meta_parts) if meta_parts else '<span style="color:#333">—</span>'
    
    # Card container
    with st.container():
        st.markdown(f"""
            <div class="task-card {priority_class}">
                <div class="task-title">#{task.id} {task.title}</div>
                <div class="task-meta">{meta_html}</div>
            </div>
        """, unsafe_allow_html=True)
        
        # Actions row - all compact and same size
        cols = st.columns([1, 1, 1, 1])
        
        with cols[0]:
            if st.button("v", key=f"v_{task.id}"):
                st.session_state.viewing_task = task.id
                st.rerun()
        
        with cols[1]:
            if st.button("✎", key=f"e_{task.id}"):
                st.session_state.show_edit = True
                st.session_state.editing_task_id = task.id
                st.rerun()
        
        with cols[2]:
            # Move button - opens menu
            if st.button("→", key=f"mv_{task.id}"):
                st.session_state.show_move_menu = task.id
                st.rerun()
        
        with cols[3]:
            if st.button("×", key=f"d_{task.id}"):
                st.session_state.delete_confirm = task.id
                st.rerun()
        
        # Show delete confirmation dialog
        if st.session_state.delete_confirm == task.id:
            c_confirm, c_cancel = st.columns(2)
            with c_confirm:
                if st.button("✓ delete", key=f"del_yes_{task.id}", type="primary"):
                    board.tasks = [t for t in board.tasks if t.id != task.id]
                    save_data(data)
                    st.session_state.delete_confirm = None
                    st.rerun()
            with c_cancel:
                if st.button("✕ cancel", key=f"del_no_{task.id}"):
                    st.session_state.delete_confirm = None
                    st.rerun()
            st.markdown(f"<div style='color:#f03030;font-size:0.7rem'>delete '{task.title}'?</div>", unsafe_allow_html=True)
        
        # Show move menu if this task is selected
        if st.session_state.show_move_menu == task.id:
            st.markdown("<div style='margin:4px 0 2px 0;font-size:0.65rem;color:#666'>move to:</div>", unsafe_allow_html=True)
            other_cols = [c for c in board.columns if c.id != task.column_id]
            # Use more columns for tighter layout
            move_cols = st.columns(len(other_cols) * 2)
            for idx, col_dest in enumerate(other_cols):
                with move_cols[idx * 2]:
                    # Use abbreviated column names for compact display
                    col_name = col_dest.name.lower().replace(" ", "")
                    col_label = col_name[:3] if len(col_name) > 5 else col_name
                    if st.button(col_label, key=f"to_{task.id}_{col_dest.id}", use_container_width=True):
                        ok, err = board.can_add_to_column(col_dest.id)
                        if ok:
                            task.move_to(col_dest.id)
                            st.session_state.show_move_menu = None
                            save_data(data)
                            st.rerun()
                        else:
                            st.error(err)

def render_add_form(board: Board, data: KanbanData):
    """Render minimal add form"""
    with st.form("add"):
        st.markdown("**new task**")
        
        title = st.text_input("title", placeholder="task name...", label_visibility="collapsed")
        desc = st.text_area("desc", placeholder="description (optional)...", height=60, label_visibility="collapsed")
        
        c1, c2 = st.columns(2)
        with c1:
            pri = st.selectbox("priority", [p.value for p in Priority], index=1, label_visibility="collapsed")
        with c2:
            col_opts = [(c.name, c.id) for c in sorted(board.columns, key=lambda x: x.order)]
            default = next((i for i, (_, cid) in enumerate(col_opts) if cid == st.session_state.selected_column), 0)
            col = st.selectbox("column", options=col_opts, format_func=lambda x: x[0], index=default, label_visibility="collapsed")
        
        tags = st.text_input("tags", placeholder="tags, separated, by, commas", label_visibility="collapsed")
        
        c_submit, c_cancel = st.columns(2)
        with c_submit:
            submitted = st.form_submit_button("✓ add", use_container_width=True)
        with c_cancel:
            cancelled = st.form_submit_button("✕ cancel", use_container_width=True)
        
        if submitted and title:
            cid = col[1]
            ok, err = board.can_add_to_column(cid)
            if ok:
                task = Task(
                    id=board.get_next_task_id(data),
                    board_id=board.id,
                    column_id=cid,
                    title=title,
                    description=desc if desc else None,
                    priority=Priority(pri),
                    tags=[t.strip() for t in tags.split(",") if t.strip()]
                )
                board.tasks.append(task)
                save_data(data)
                st.session_state.show_add = False
                st.rerun()
            else:
                st.error(err)
        
        if cancelled:
            st.session_state.show_add = False
            st.rerun()

def render_edit_form(task: Task, board: Board, data: KanbanData):
    """Render edit form for existing task"""
    with st.form("edit"):
        st.markdown(f"**edit task #{task.id}**")
        
        title = st.text_input("title", value=task.title, label_visibility="collapsed")
        desc = st.text_area("desc", value=task.description or "", height=60, label_visibility="collapsed")
        
        c1, c2 = st.columns(2)
        with c1:
            pri = st.selectbox("priority", [p.value for p in Priority], index=[p.value for p in Priority].index(task.priority.value), label_visibility="collapsed")
        with c2:
            col_opts = [(c.name, c.id) for c in sorted(board.columns, key=lambda x: x.order)]
            current_idx = next((i for i, (_, cid) in enumerate(col_opts) if cid == task.column_id), 0)
            col = st.selectbox("column", options=col_opts, format_func=lambda x: x[0], index=current_idx, label_visibility="collapsed")
        
        tags = st.text_input("tags", value=", ".join(task.tags), label_visibility="collapsed")
        
        # Agent context editor
        if task.agent_context:
            st.markdown("<div style='font-size:0.7rem;color:#666;margin-top:8px;'>agent context</div>", unsafe_allow_html=True)
            for key in list(task.agent_context.keys()):
                c_key, c_val = st.columns([1, 3])
                with c_key:
                    st.markdown(f"<span style='font-size:0.7rem;color:#888;'>{key}</span>", unsafe_allow_html=True)
                with c_val:
                    new_val = st.text_input(f"ctx_{key}", value=task.agent_context[key], label_visibility="collapsed")
                    task.agent_context[key] = new_val
        
        c_save, c_cancel = st.columns(2)
        with c_save:
            submitted = st.form_submit_button("✓ save", use_container_width=True)
        with c_cancel:
            cancelled = st.form_submit_button("✕ cancel", use_container_width=True)
        
        if submitted:
            task.title = title
            task.description = desc if desc else None
            task.priority = Priority(pri)
            task.column_id = col[1]
            task.tags = [t.strip() for t in tags.split(",") if t.strip()]
            task.updated_at = now_utc()
            save_data(data)
            st.session_state.show_edit = False
            st.session_state.editing_task_id = None
            st.rerun()
        
        if cancelled:
            st.session_state.show_edit = False
            st.session_state.editing_task_id = None
            st.rerun()

def render_create_board_form(data: KanbanData):
    """Render form to create a new board"""
    with st.form("create_board"):
        st.markdown("**create new board**")
        
        name = st.text_input("board name", placeholder="my project...", label_visibility="collapsed")
        
        c_create, c_cancel = st.columns(2)
        with c_create:
            submitted = st.form_submit_button("✓ create", use_container_width=True)
        with c_cancel:
            cancelled = st.form_submit_button("✕ cancel", use_container_width=True)
        
        if submitted and name:
            # Generate unique board ID
            base_id = name.lower().replace(" ", "-")[:20]
            board_id = base_id
            counter = 1
            while any(b.id == board_id for b in data.boards):
                board_id = f"{base_id}-{counter}"
                counter += 1
            
            from models import DEFAULT_COLUMNS
            new_board = Board(
                id=board_id,
                name=name,
                columns=DEFAULT_COLUMNS.copy()
            )
            data.boards.append(new_board)
            data.default_board = board_id
            save_data(data)
            
            st.session_state.current_board_id = board_id
            st.session_state.show_create_board = False
            st.rerun()
        
        if cancelled:
            st.session_state.show_create_board = False
            st.rerun()

def render_task_detail(task: Task, board: Board, data: KanbanData):
    st.markdown(f"### #{task.id}")
    st.markdown(f"**{task.title}**")
    
    col = board.get_column(task.column_id)
    st.markdown(f"<span style='color:#666;font-size:0.75rem'>{col.name if col else task.column_id} • {task.priority.value}</span>", unsafe_allow_html=True)
    
    if task.description:
        st.markdown(f"<div style='color:#888;font-size:0.8rem;margin:1rem 0'>{task.description}</div>", unsafe_allow_html=True)
    
    if task.tags:
        st.markdown(" ".join([f'<span style="background:#1f1f1f;padding:2px 8px;border-radius:2px;font-size:0.7rem;color:#666">{t}</span>' for t in task.tags]))
    
    if task.agent_context:
        st.markdown("<div style='margin-top:1rem;color:#d4a030;font-size:0.75rem'>◉ agent context</div>", unsafe_allow_html=True)
        for k, v in task.agent_context.items():
            st.markdown(f"<div style='font-size:0.75rem;color:#888;margin-left:1rem'>{k}: {v}</div>", unsafe_allow_html=True)
    
    if st.button("← back", use_container_width=True):
        del st.session_state.viewing_task
        st.rerun()


def render_task_actions_list(board: Board, data: KanbanData):
    cols = st.columns(len(board.columns))
    for idx, col in enumerate(sorted(board.columns, key=lambda x: x.order)):
        tasks = board.get_tasks_in_column(col.id)
        with cols[idx]:
            for task in tasks:
                meta_parts = []
                if task.tags:
                    meta_parts.extend([f'<span class="tag">{t}</span>' for t in task.tags[:2]])
                if task.agent_context:
                    meta_parts.append('<span class="agent-indicator">◉</span>')
                meta_html = ' '.join(meta_parts) if meta_parts else '<span style="color:#333">—</span>'

                st.markdown(f"""
                    <div class="task-actions-card">
                        <div class="task-actions-title">#{task.id} {task.title}</div>
                        <div class="task-actions-meta">{meta_html}</div>
                    </div>
                """, unsafe_allow_html=True)

                c_view, c_edit, c_delete = st.columns([1, 1, 1])
                with c_view:
                    if st.button("v", key=f"act_view_{task.id}", use_container_width=True):
                        st.session_state.viewing_task = task.id
                        st.rerun()
                with c_edit:
                    if st.button("✎", key=f"act_edit_{task.id}", use_container_width=True):
                        st.session_state.show_edit = True
                        st.session_state.editing_task_id = task.id
                        st.rerun()
                with c_delete:
                    if st.button("×", key=f"act_del_{task.id}"):
                        st.session_state.delete_confirm = task.id
                        st.rerun()
                
                # Show delete confirmation dialog
                if st.session_state.delete_confirm == task.id:
                    c_del_yes, c_del_no = st.columns([1, 1])
                    with c_del_yes:
                        if st.button("✓", key=f"act_del_yes_{task.id}", type="primary"):
                            board.tasks = [t for t in board.tasks if t.id != task.id]
                            save_data(data)
                            st.session_state.delete_confirm = None
                            st.rerun()
                    with c_del_no:
                        if st.button("✕", key=f"act_del_no_{task.id}"):
                            st.session_state.delete_confirm = None
                            st.rerun()

def ensure_five_columns(board: Board):
    """Ensure board has all 5 columns with correct order"""
    expected_columns = {
        "backlog": ("Backlog", 0),
        "todo": ("To Do", 1),
        "inprogress": ("In Progress", 2),
        "testing": ("Testing", 3),
        "done": ("Done", 4),
    }
    
    existing_ids = {c.id for c in board.columns}
    changed = False
    
    # Update existing columns to have correct order
    for col in board.columns:
        if col.id in expected_columns:
            correct_name, correct_order = expected_columns[col.id]
            if col.order != correct_order:
                col.order = correct_order
                changed = True
            if col.name != correct_name:
                col.name = correct_name
                changed = True
    
    # Add missing columns
    for col_id, (col_name, order) in expected_columns.items():
        if col_id not in existing_ids:
            board.columns.append(Column(
                id=col_id,
                name=col_name,
                limit=3 if col_id == "inprogress" else None,
                order=order
            ))
            changed = True
    
    # Sort by order
    board.columns.sort(key=lambda x: x.order)
    
    return changed

def main():
    data = load_data()
    
    # Get current board (from session state or default)
    current_board_id = st.session_state.current_board_id or data.default_board
    board = data.get_board(current_board_id)
    
    if not board:
        st.error("no board found")
        return
    
    # Ensure board has all 5 columns with correct order, save if changed
    if ensure_five_columns(board):
        save_data(data)
    
    # Title
    st.markdown(f"<h1>◼ {board.name}</h1>", unsafe_allow_html=True)
    
    # Handle viewing task detail
    if st.session_state.viewing_task:
        task = data.get_task(st.session_state.viewing_task)
        if task:
            render_task_detail(task, board, data)
            return
        else:
            del st.session_state.viewing_task
    
    # Handle editing task
    if st.session_state.show_edit and st.session_state.editing_task_id:
        task = data.get_task(st.session_state.editing_task_id)
        if task:
            st.markdown("---")
            render_edit_form(task, board, data)
            st.markdown("---")
            return
        else:
            st.session_state.show_edit = False
            st.session_state.editing_task_id = None
    
    # Handle add new task
    if st.session_state.show_add:
        st.markdown("---")
        render_add_form(board, data)
        st.markdown("---")
    
    # Handle create new board
    if st.session_state.show_create_board:
        st.markdown("---")
        render_create_board_form(data)
        st.markdown("---")
        return
    
    # Header actions
    if not st.session_state.show_add and not st.session_state.show_edit:
        c1, c2, c3 = st.columns([1, 4, 1])
        with c1:
            if st.button("+ new task"):
                st.session_state.show_add = True
                st.rerun()
        with c3:
            if st.button("refresh"):
                st.cache_data.clear()
                st.rerun()
    
    # Sidebar filters
    with st.sidebar:
        # Board selector (only show if multiple boards exist)
        if len(data.boards) > 1:
            st.markdown("**board**")
            board_options = [(b.name, b.id) for b in data.boards]
            # Determine which board to select
            current_id = st.session_state.current_board_id or data.default_board
            current_idx = next((i for i, (_, bid) in enumerate(board_options) if bid == current_id), 0)
            
            selected_board = st.selectbox(
                "select board",
                options=board_options,
                format_func=lambda x: x[0],
                index=current_idx,
                label_visibility="collapsed"
            )
            
            # Update current board if changed
            if selected_board[1] != st.session_state.current_board_id:
                st.session_state.current_board_id = selected_board[1]
                # Clear viewing/editing states when switching boards
                st.session_state.viewing_task = None
                st.session_state.show_edit = False
                st.session_state.editing_task_id = None
                st.session_state.show_add = False
                st.rerun()
            
            st.markdown("---")
        
        st.markdown("**stats**")
        for col in sorted(board.columns, key=lambda x: x.order):
            count = len(board.get_tasks_in_column(col.id))
            limit = f"/{col.limit}" if col.limit else ""
            st.markdown(f"<div style='font-size:0.7rem;color:#666'>{col.name.lower()}: <span style='color:#888'>{count}{limit}</span></div>", unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Board management
        st.markdown("**boards**")
        if st.button("+ new board", use_container_width=True):
            st.session_state.show_create_board = True
            st.rerun()
        
        st.markdown("---")
        st.markdown("**filters**")
    
    # Get sidebar filter values (outside sidebar context)
    search = st.session_state.get('search_filter', '')
    tag_filter = st.session_state.get('tag_filter', 'all')
    
    with st.sidebar:
        # We need to get the actual values from the sidebar inputs
        # Re-create inputs to capture values
        search = st.text_input("search", value=search, placeholder="...", label_visibility="collapsed")
        st.session_state.search_filter = search
        
        all_tags = set()
        for t in board.tasks:
            all_tags.update(t.tags)
        if all_tags:
            tag_filter = st.selectbox("tag", ["all"] + sorted(list(all_tags)), index=0 if tag_filter == "all" else sorted(list(all_tags)).index(tag_filter) + 1 if tag_filter in all_tags else 0, label_visibility="collapsed")
        else:
            tag_filter = "all"
        st.session_state.tag_filter = tag_filter
    
    # Build sortable items from current board state
    original_items = build_sortable_items(board, str(search) if search else "", str(tag_filter) if tag_filter else "all")
    
    # Render draggable columns
    sorted_items = sort_items(
        original_items,
        multi_containers=True,
        direction='horizontal',
        custom_style=DRAG_DROP_CSS,
        key=st.session_state.sortable_key
    )
    
    # Process any drag-and-drop movements
    if sorted_items != original_items:
        moved_count, board = process_sortable_movement(original_items, sorted_items, board, data)
        if moved_count > 0:
            save_data(data)
            st.cache_data.clear()
        # Increment key to force re-render with fresh state
            st.session_state.sortable_key = f"kanban_sortable_{hash(str(sorted_items))}"
            st.rerun()

    # Actions list for view/edit/delete
    render_task_actions_list(board, data)

if __name__ == "__main__":
    main()
