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
</style>
""", unsafe_allow_html=True)

from models import KanbanData, Board, Task, Column, Priority, now_utc
from storage import KanbanStorage

@st.cache_data(ttl=1)
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
if 'selected_column' not in st.session_state:
    st.session_state.selected_column = 'backlog'
if 'viewing_task' not in st.session_state:
    st.session_state.viewing_task = None
if 'show_move_menu' not in st.session_state:
    st.session_state.show_move_menu = None

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
                board.tasks = [t for t in board.tasks if t.id != task.id]
                save_data(data)
                st.rerun()
        
        # Show move menu if this task is selected
        if st.session_state.show_move_menu == task.id:
            st.markdown("<div style='margin:4px 0;font-size:0.65rem;color:#666'>move to:</div>", unsafe_allow_html=True)
            other_cols = [c for c in board.columns if c.id != task.column_id]
            move_cols = st.columns(len(other_cols))
            for idx, col_dest in enumerate(other_cols):
                with move_cols[idx]:
                    if st.button(col_dest.name.lower()[:3], key=f"to_{task.id}_{col_dest.id}"):
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
                    id=board.get_next_task_id(),
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

def main():
    data = load_data()
    board = data.get_board()
    
    if not board:
        st.error("no board found")
        return
    
    # Update board name for this session
    board.name = "pODV - progress tracker"
    
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
        st.markdown("**stats**")
        for col in sorted(board.columns, key=lambda x: x.order):
            count = len(board.get_tasks_in_column(col.id))
            limit = f"/{col.limit}" if col.limit else ""
            st.markdown(f"<div style='font-size:0.7rem;color:#666'>{col.name.lower()}: <span style='color:#888'>{count}{limit}</span></div>", unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("**filters**")
        search = st.text_input("search", placeholder="...", label_visibility="collapsed")
        
        all_tags = set()
        for t in board.tasks:
            all_tags.update(t.tags)
        if all_tags:
            tag_filter = st.selectbox("tag", ["all"] + sorted(list(all_tags)), label_visibility="collapsed")
        else:
            tag_filter = "all"
    
    # Kanban columns - 5 columns
    cols = st.columns(5)
    
    for idx, col in enumerate(sorted(board.columns, key=lambda x: x.order)):
        with cols[idx]:
            # Header
            count = len(board.get_tasks_in_column(col.id))
            limit_text = f" ({count}/{col.limit})" if col.limit else f" ({count})"
            
            st.markdown(f"""
                <div class="column-header {col.id}">
                    {col.name.lower()}{limit_text}
                </div>
            """, unsafe_allow_html=True)
            
            # Filter tasks
            tasks = board.get_tasks_in_column(col.id)
            if search:
                tasks = [t for t in tasks if search.lower() in t.title.lower()]
            if tag_filter != "all":
                tasks = [t for t in tasks if tag_filter in t.tags]
            
            # Render tasks
            if tasks:
                for task in tasks:
                    render_task_card(task, board, data)
            else:
                # Empty state
                if st.button(f"+ add", key=f"e_{col.id}"):
                    st.session_state.selected_column = col.id
                    st.session_state.show_add = True
                    st.rerun()
                
                st.markdown("""
                    <div class="empty-state">
                        empty
                    </div>
                """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
