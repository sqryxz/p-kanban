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
        border: 1px solid #333 !important;
        color: #888 !important;
        font-size: 0.7rem !important;
        padding: 6px 12px !important;
        font-weight: 400 !important;
        border-radius: 3px !important;
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }
    
    .stButton button:hover {
        border-color: #555 !important;
        color: #aaa !important;
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
        margin-top: 8px;
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
    
    /* Select boxes */
    .stSelectbox {
        font-size: 0.75rem;
    }
    
    /* Move selector */
    .move-select {
        opacity: 0;
        transition: opacity 0.2s;
    }
    
    .task-card:hover .move-select {
        opacity: 1;
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
if 'selected_column' not in st.session_state:
    st.session_state.selected_column = 'backlog'
if 'viewing_task' not in st.session_state:
    st.session_state.viewing_task = None

def render_task_card(task: Task, board: Board, data: KanbanData):
    """Render minimal task card"""
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
        
        # Actions row
        c1, c2, c3 = st.columns([1, 2, 1])
        
        with c1:
            if st.button("view", key=f"v_{task.id}"):
                st.session_state.viewing_task = task.id
                st.rerun()
        
        with c2:
            # Move dropdown - shows on hover via CSS
            other_cols = [c for c in board.columns if c.id != task.column_id]
            if other_cols:
                opts = ["→ move"] + [c.name.lower() for c in other_cols]
                dest = st.selectbox(
                    "",
                    options=opts,
                    key=f"m_{task.id}",
                    label_visibility="collapsed"
                )
                if dest != "→ move":
                    target = next(c for c in other_cols if c.name.lower() == dest)
                    ok, err = board.can_add_to_column(target.id)
                    if ok:
                        task.move_to(target.id)
                        save_data(data)
                        st.rerun()
        
        with c3:
            if st.button("del", key=f"d_{task.id}"):
                board.tasks = [t for t in board.tasks if t.id != task.id]
                save_data(data)
                st.rerun()

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
        
        submitted = st.form_submit_button("add task")
        
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

def render_task_detail(task: Task, board: Board, data: KanbanData):
    """Render minimal task detail view"""
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
        
        with st.expander("edit context"):
            k = st.text_input("key")
            v = st.text_input("value")
            if st.button("update") and k:
                task.agent_context[k] = v
                task.updated_at = now_utc()
                save_data(data)
                st.rerun()
    
    if st.button("← back"):
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
    
    # View task detail if selected
    if st.session_state.viewing_task:
        task = data.get_task(st.session_state.viewing_task)
        if task:
            render_task_detail(task, board, data)
            return
    
    # Header actions
    c1, c2, c3 = st.columns([1, 4, 1])
    with c1:
        if st.button("+ new task"):
            st.session_state.show_add = True
            st.rerun()
    with c3:
        if st.button("refresh"):
            st.cache_data.clear()
            st.rerun()
    
    # Show add form
    if st.session_state.show_add:
        st.markdown("---")
        render_add_form(board, data)
        if st.button("cancel"):
            st.session_state.show_add = False
            st.rerun()
        st.markdown("---")
    
    # Sidebar filters
    with st.sidebar:
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
            limit_indicator = f" <span class='wip-badge'>limit</span>" if col.limit and count >= col.limit else ""
            
            st.markdown(f"""
                <div class="column-header {col.id}">
                    {col.name.lower()} {count}{limit_indicator}
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
