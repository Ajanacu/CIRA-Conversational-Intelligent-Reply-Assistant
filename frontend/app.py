"""
CIRA Reply Assistant 
"""
import streamlit as st

st.set_page_config(
    page_title="CIRA",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

* { font-family: 'Inter', sans-serif; }

/* Hide sidebar toggle and default streamlit chrome */
[data-testid="collapsedControl"] { display: none; }
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stSidebar"] { display: none; }
.stApp { background-color: #0b0f14; }
.block-container { padding: 0 !important; max-width: 100% !important; }

/* ── Top navbar ── */
.navbar {
    background: #111820;
    border-bottom: 1px solid #1e2d3d;
    padding: 0.7rem 2rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    position: sticky;
    top: 0;
    z-index: 100;
}
.navbar-brand { font-size: 1.2rem; font-weight: 700; color: #25D366; display:flex; align-items:center; gap:0.5rem; }
.navbar-user  { font-size: 0.82rem; color: #6b7280; }

/* ── Layout grid ── */
.main-grid {
    display: grid;
    grid-template-columns: 300px 1fr 320px;
    grid-template-rows: auto;
    gap: 0;
    height: calc(100vh - 52px);
    overflow: hidden;
}
.panel-left   { background: #0f1923; border-right: 1px solid #1e2d3d; overflow-y: auto; padding: 1rem; }
.panel-center { background: #0b0f14; overflow-y: auto; padding: 1.2rem 1.5rem; }
.panel-right  { background: #0f1923; border-left:  1px solid #1e2d3d; overflow-y: auto; padding: 1rem; }

/* ── Cards ── */
.card {
    background: #151f2b;
    border: 1px solid #1e2d3d;
    border-radius: 10px;
    padding: 1rem 1.1rem;
    margin-bottom: 0.8rem;
}
.card-title {
    font-size: 0.7rem;
    font-weight: 600;
    color: #4b6280;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 0.6rem;
}
.card-green { background: #0a1f16; border-color: #065f46; }
.card-blue  { background: #0d1b2e; border-color: #1e3a5f; }

/* ── Metrics ── */
.metric-row { display: flex; gap: 0.5rem; margin-bottom: 0.8rem; }
.metric-box {
    flex: 1;
    background: #0f1923;
    border: 1px solid #1e2d3d;
    border-radius: 8px;
    padding: 0.6rem 0.5rem;
    text-align: center;
}
.metric-val   { font-size: 1.4rem; font-weight: 700; color: #25D366; line-height: 1.2; }
.metric-label { font-size: 0.65rem; color: #4b6280; text-transform: uppercase; letter-spacing:0.05em; margin-top:2px; }

/* ── Relationship icon grid ── */
.rel-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 0.4rem; margin-bottom: 0.6rem; }
.rel-btn {
    background: #0f1923;
    border: 1px solid #1e2d3d;
    border-radius: 8px;
    padding: 0.5rem 0.2rem;
    text-align: center;
    cursor: pointer;
    transition: all 0.15s;
    font-size: 0.6rem;
    color: #6b7280;
    line-height: 1.4;
    word-break: break-word;
}
.rel-btn:hover  { border-color: #25D366; color: #25D366; }
.rel-btn.active { border-color: #25D366; background: #0a1f16; color: #25D366; }
.rel-icon { font-size: 1.2rem; display: block; margin-bottom: 2px; }

/* ── Tone pills ── */
.tone-row { display: flex; flex-wrap: wrap; gap: 0.35rem; margin-bottom: 0.6rem; }
.tone-pill {
    background: #0f1923;
    border: 1px solid #1e2d3d;
    border-radius: 999px;
    padding: 0.25rem 0.7rem;
    font-size: 0.72rem;
    color: #6b7280;
    cursor: pointer;
    transition: all 0.15s;
}
.tone-pill:hover  { border-color: #25D366; color: #25D366; }
.tone-pill.active { border-color: #25D366; background: #0a1f16; color: #25D366; font-weight: 600; }

/* ── Incoming message bubble ── */
.incoming-bubble {
    background: #151f2b;
    border: 1px solid #1e2d3d;
    border-left: 3px solid #25D366;
    border-radius: 4px 12px 12px 12px;
    padding: 0.8rem 1rem;
    color: #e2e8f0;
    font-size: 0.9rem;
    margin-bottom: 1rem;
    line-height: 1.5;
}

/* ── Reply bubbles ── */
.reply-wrap { margin-bottom: 0.7rem; }
.reply-label { font-size: 0.68rem; color: #4b6280; text-transform:uppercase; letter-spacing:0.06em; margin-bottom:0.3rem; }
.reply-bubble {
    background: #0a1f16;
    border: 1px solid #065f46;
    border-radius: 12px 12px 12px 4px;
    padding: 0.75rem 1rem;
    color: #d1fae5;
    font-size: 0.88rem;
    line-height: 1.5;
}

/* ── History items ── */
.hist-item {
    border-bottom: 1px solid #1e2d3d;
    padding: 0.55rem 0;
    font-size: 0.78rem;
}
.hist-time { color: #4b6280; font-size: 0.68rem; }
.hist-in   { color: #94a3b8; margin-top: 2px; }
.hist-out  { color: #6ee7b7; margin-top: 2px; }

/* ── Upload area ── */
.upload-hint {
    text-align: center;
    padding: 1.5rem;
    border: 1px dashed #1e2d3d;
    border-radius: 10px;
    color: #4b6280;
    font-size: 0.82rem;
    line-height: 2;
}

/* ── Step indicator ── */
.step-row { display:flex; align-items:center; gap:0.5rem; margin-bottom:0.5rem; }
.step-dot { width:20px; height:20px; border-radius:50%; background:#1e2d3d; color:#4b6280; font-size:0.65rem; font-weight:700; display:flex; align-items:center; justify-content:center; flex-shrink:0; }
.step-dot.done { background:#065f46; color:#6ee7b7; }
.step-text { font-size:0.78rem; color:#6b7280; }

/* ── Status badge ── */
.status-ok  { color:#6ee7b7; font-size:0.72rem; font-weight:600; }
.status-no  { color:#4b6280; font-size:0.72rem; }

/* ── Streamlit overrides ── */
.stTextArea textarea {
    background: #0f1923 !important;
    border: 1px solid #1e2d3d !important;
    border-radius: 8px !important;
    color: #e2e8f0 !important;
    font-size: 0.88rem !important;
    resize: none !important;
}
.stTextArea textarea:focus { border-color: #25D366 !important; box-shadow: none !important; }
.stTextInput input {
    background: #0f1923 !important;
    border: 1px solid #1e2d3d !important;
    border-radius: 8px !important;
    color: #e2e8f0 !important;
    font-size: 0.85rem !important;
}
.stButton > button {
    border-radius: 8px !important;
    font-size: 0.72rem !important;
    font-weight: 600 !important;
    border: none !important;
    transition: all 0.15s !important;
}
.stButton > button[kind="primary"] {
    background: #25D366 !important;
    color: #000 !important;
}
.stButton > button[kind="primary"]:hover { background: #1faa52 !important; }
.stButton > button[kind="secondary"] {
    background: #151f2b !important;
    color: #94a3b8 !important;
    border: 1px solid #1e2d3d !important;
}
[data-testid="stFileUploader"] {
    background: #0f1923;
    border: 1px dashed #1e2d3d;
    border-radius: 10px;
    padding: 0.5rem;
}
.stFileUploader label { color: #6b7280 !important; }
div[data-testid="stExpander"] {
    background: #151f2b;
    border: 1px solid #1e2d3d;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

import requests as _req
from pages import auth

# ── Session state ─────────────────────────────────────────────────────────────
for k, v in [("logged_in", False), ("token", None), ("username", None),
              ("display_name", None), ("relationship", "friend"), ("tone", "casual"),
              ("replies", []), ("incoming", ""), ("selected_reply", "")]:
    if k not in st.session_state:
        st.session_state[k] = v

# ── Auth gate ─────────────────────────────────────────────────────────────────
if not st.session_state.logged_in:
    auth.show()
    st.stop()

# ── Helper: API call with token ───────────────────────────────────────────────
BASE = "http://localhost:8000"

def api(method, endpoint, **kwargs):
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    try:
        return getattr(_req, method)(f"{BASE}{endpoint}", headers=headers, timeout=30, **kwargs)
    except Exception:
        return None

# ── Fetch status ──────────────────────────────────────────────────────────────
status_r = api("get", "/chat/status")
status   = status_r.json() if status_r and status_r.status_code == 200 else {}
has_msgs = status.get("has_messages", False)
msg_cnt  = status.get("message_count", 0)
has_an   = status.get("has_analysis", False)

analysis = {}
if has_an:
    ar = api("get", "/chat/analysis")
    if ar and ar.status_code == 200:
        analysis = ar.json()

pattern = analysis.get("user_pattern", {})

# ── Navbar ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class='navbar'>
    <div class='navbar-brand'>💬 CIRA</div>
    <div class='navbar-user'>👤 {st.session_state.display_name}</div>
</div>
""", unsafe_allow_html=True)

# ── Three-panel layout via columns ───────────────────────────────────────────
left, center, right = st.columns([2.2, 3.8, 2.4], gap="small")

# ═══════════════════════════════════════════════════════════════════════════════
# LEFT PANEL — Upload + Dashboard stats
# ═══════════════════════════════════════════════════════════════════════════════
with left:
    st.markdown("<div style='padding:0.2rem 0.2rem;'>", unsafe_allow_html=True)

    # ── Setup steps ──────────────────────────────────────────────────────────
    st.markdown(f"""
    <div class='card'>
        <div class='card-title'>Setup</div>
        <div class='step-row'>
            <div class='step-dot {"done" if has_msgs else ""}'>{"✓" if has_msgs else "1"}</div>
            <div class='step-text'>{"Chat uploaded · " + f"{msg_cnt:,} msgs" if has_msgs else "Upload WhatsApp chat"}</div>
        </div>
        <div class='step-row'>
            <div class='step-dot {"done" if has_an else ""}'>{"✓" if has_an else "2"}</div>
            <div class='step-text'>{"Style analyzed" if has_an else "Analyze messaging style"}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Upload ────────────────────────────────────────────────────────────────
    with st.expander("📁 Upload Chat" + (" ✅" if has_msgs else ""), expanded=not has_msgs):
        uploaded = st.file_uploader("WhatsApp .txt export", type=["txt"], label_visibility="collapsed")
        if uploaded:
            if st.button("📤 Upload", type="primary", use_container_width=True):
                with st.spinner("Parsing..."):
                    r = api("post", "/chat/upload", files={"file": (uploaded.name, uploaded.getvalue(), "text/plain")})
                if r and r.status_code == 200:
                    cnt = r.json().get("count", 0)
                    if cnt == 0:
                        st.error("No messages found. Use WhatsApp → Export Chat → Without Media.")
                    else:
                        st.success(f"✅ {cnt:,} messages uploaded")
                        st.rerun()
                else:
                    st.error("Upload failed")
        else:
            st.markdown("""
            <div class='upload-hint'>
                WhatsApp → Chat → ⋮ → More<br>
                → Export Chat → Without Media<br>
                → Upload the .txt file here
            </div>
            """, unsafe_allow_html=True)

        if has_msgs:
            btn = "🔄 Re-analyze" if has_an else "🔍 Analyze Style"
            if st.button(btn, type="primary" if not has_an else "secondary", use_container_width=True):
                with st.spinner("Analyzing..."):
                    r = api("post", "/chat/analyze", json={})
                if r and r.status_code == 200:
                    st.success("✅ Done!")
                    st.rerun()
                else:
                    st.error(r.json().get("detail", "Failed") if r else "Error")

    # ── Dashboard stats ───────────────────────────────────────────────────────
    if has_an and analysis:
        total    = analysis.get("total_messages", 0)
        senders  = analysis.get("senders", [])
        moods    = analysis.get("mood_distribution", {})
        top_mood = max(moods, key=moods.get) if moods else "neutral"
        mood_emoji = {"happy":"😊","excited":"🎉","sad":"😢","angry":"😡","neutral":"😐"}.get(top_mood,"😐")
        msg_types = analysis.get("message_type_distribution", {})
        media_pct = round(msg_types.get("media", 0) / max(total,1) * 100)

        st.markdown(f"""
        <div class='card'>
            <div class='card-title'>Chat Overview</div>
            <div class='metric-row'>
                <div class='metric-box'>
                    <div class='metric-val'>{mood_emoji}</div>
                    <div class='metric-label'>{top_mood.title()} Mood</div>
                </div>
            </div>
            <div class='metric-row'>
                <div class='metric-box' style='flex:2'>
                    <div class='metric-val' style='font-size:1rem'>{max(analysis.get("sender_stats",{}), key=lambda s: analysis["sender_stats"][s]["total_messages"]) if analysis.get("sender_stats") else "—"}</div>
                    <div class='metric-label'>Most Active</div>
                </div>
                <div class='metric-box'>
                    <div class='metric-val'>{int(max(analysis.get("hourly_distribution",{}), key=lambda k: analysis["hourly_distribution"][k])) if analysis.get("hourly_distribution") else "—"}:00</div>
                    <div class='metric-label'>Peak Hour</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Hourly activity mini bar
        hourly = analysis.get("hourly_distribution", {})
        if hourly:
            import plotly.graph_objects as go
            hours  = list(range(24))
            counts = [hourly.get(str(h), hourly.get(h, 0)) for h in hours]
            mx = max(counts) or 1
            fig = go.Figure(go.Bar(
                x=[f"{h:02d}" for h in hours], y=counts,
                marker_color=[f"rgba(37,211,102,{0.2+c/mx*0.8:.2f})" for c in counts],
                hovertemplate="%{x}:00 · %{y} msgs<extra></extra>"
            ))
            fig.update_layout(
                template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)", margin=dict(t=4,b=4,l=4,r=4),
                height=90, showlegend=False,
                xaxis=dict(tickfont=dict(size=7), tickvals=[0,6,12,18,23],
                           ticktext=["12am","6am","12pm","6pm","11pm"]),
                yaxis=dict(visible=False),
            )
            st.markdown("<div class='card'><div class='card-title'>Activity by Hour</div>", unsafe_allow_html=True)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
            st.markdown("</div>", unsafe_allow_html=True)

        # Top words
        top_words = analysis.get("top_words", [])
        if top_words:
            words_html = " ".join(
                f"<span style='background:#0f1923;border:1px solid #1e2d3d;border-radius:999px;"
                f"padding:2px 8px;font-size:0.68rem;color:#94a3b8;display:inline-block;margin:2px'>"
                f"{w}</span>"
                for w, _ in top_words[:10]
            )
            st.markdown(f"""
            <div class='card'>
                <div class='card-title'>Top Words</div>
                <div style='line-height:2'>{words_html}</div>
            </div>
            """, unsafe_allow_html=True)

        # Style profile
        if pattern:
            st.markdown(f"""
            <div class='card card-green'>
                <div class='card-title'>Your Style</div>
                <div style='color:#a7f3d0; font-size:0.78rem; line-height:2;'>
                    <b>Lang:</b> {pattern.get("language_style","—").title()}&nbsp;&nbsp;
                    <b>Manglish:</b> {pattern.get("manglish_level","none").title()}<br>
                    <b>Length:</b> {pattern.get("avg_message_length","—").title()}&nbsp;&nbsp;
                    <b>Emoji:</b> {"Yes" if pattern.get("uses_emoji") else "No"}
                </div>
                {f'<div style="color:#6ee7b7;font-size:0.75rem;margin-top:0.4rem;font-style:italic;">"{pattern["style_summary"]}"</div>' if pattern.get("style_summary") else ""}
            </div>
            """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # Logout at bottom
    if st.button("🚪 Logout", use_container_width=True):
        for k in ["logged_in","token","username","display_name","replies","incoming","selected_reply"]:
            st.session_state[k] = False if k == "logged_in" else ([] if k == "replies" else (None if k not in ["incoming","selected_reply"] else ""))
        st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# CENTER PANEL — Relationship + Tone + Incoming + Replies
# ═══════════════════════════════════════════════════════════════════════════════
with center:
    st.markdown("<div style='padding:0.2rem 0.4rem;'>", unsafe_allow_html=True)

    if not has_an:
        st.markdown("""
        <div style='text-align:center; padding:4rem 2rem; color:#4b6280;'>
            <div style='font-size:3rem; margin-bottom:1rem;'>💬</div>
            <div style='font-size:1rem; font-weight:600; color:#6b7280; margin-bottom:0.5rem;'>
                Upload & analyze your chat to get started
            </div>
            <div style='font-size:0.82rem;'>Use the panel on the left → Upload Chat → Analyze Style</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # ── Relationship icons ────────────────────────────────────────────────
        RELATIONSHIPS = [
            ("👫", "Friend",      "friend"),
            ("👨‍👩‍👧", "Family",    "family"),
            ("💼", "Client",      "client"),
            ("🏢", "Manager",     "manager"),
            ("❤️", "Partner",     "partner"),
            ("🎓", "Mentor",      "mentor"),
        ]

        st.markdown("<div class='card'><div class='card-title'>Relationship</div>", unsafe_allow_html=True)
        rel_cols = st.columns(6, gap="small")
        for i, (icon, label, val) in enumerate(RELATIONSHIPS):
            with rel_cols[i % 6]:
                is_active = st.session_state.relationship == val
                if st.button(
                    f"{icon}\n{label}",
                    key=f"rel_{val}",
                    help=label,
                    use_container_width=True,
                    type="primary" if is_active else "secondary"
                ):
                    st.session_state.relationship = val
                    st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

        # ── Tone pills ────────────────────────────────────────────────────────
        TONES = [
            ("😊 Casual",       "casual"),
            ("🤝 Formal",     "formal")
        ]

        st.markdown("<div class='card'><div class='card-title'>Tone</div>", unsafe_allow_html=True)
        tone_cols = st.columns(2, gap="small")
        for i, (label, val) in enumerate(TONES):
            with tone_cols[i % 2]:
                is_active = st.session_state.tone == val
                if st.button(
                    label,
                    key=f"tone_{val}",
                    use_container_width=True,
                    type="primary" if is_active else "secondary"
                ):
                    st.session_state.tone = val
                    st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

        # ── Incoming message ──────────────────────────────────────────────────
        st.markdown("<div class='card'><div class='card-title'>Incoming Message</div>", unsafe_allow_html=True)

        c_in, c_name = st.columns([3, 1])
        with c_in:
            incoming = st.text_area(
                "msg", placeholder="Paste the message you received...",
                height=90, label_visibility="collapsed", key="incoming_text"
            )
        with c_name:
            sender = st.text_input("Sender", placeholder="Name (optional)", label_visibility="collapsed")

        gen_col, _ = st.columns([1, 2])
        with gen_col:
            generate = st.button("✨ Generate Replies", type="primary", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # ── Generate ──────────────────────────────────────────────────────────
        if generate:
            if not incoming.strip():
                st.error("Please paste a message first.")
            else:
                with st.spinner("Generating..."):
                    r = api("post", "/reply/generate", json={
                        "incoming_message": incoming,
                        "sender_name": sender or None,
                        "relationship": st.session_state.relationship,
                        "tone": st.session_state.tone,
                    })
                if r and r.status_code == 200:
                    st.session_state.replies   = r.json().get("replies", [])
                    st.session_state.incoming  = incoming
                    st.session_state.sender    = sender
                    st.session_state.selected_reply = ""
                elif r:
                    st.error(r.json().get("detail", "Error generating replies"))

        # ── Show replies ──────────────────────────────────────────────────────
        if st.session_state.replies:
            st.markdown(f"""
            <div class='incoming-bubble'>
                <span style='color:#25D366; font-size:0.7rem; font-weight:600'>
                    📨 {st.session_state.get("sender","") or "Incoming"}
                    &nbsp;·&nbsp; {st.session_state.relationship.title()}
                    &nbsp;·&nbsp; {st.session_state.tone.title()}
                </span><br>
                {st.session_state.incoming}
            </div>
            """, unsafe_allow_html=True)

            labels = ["⭐ Option 1", "💡 Option 2", "🔄 Option 3"]
            for i, (reply_text, label) in enumerate(zip(st.session_state.replies, labels)):
                st.markdown(f"<div class='reply-label'>{label}</div>", unsafe_allow_html=True)
                edited = st.text_area(
                    f"r{i}", value=reply_text,
                    height=70, label_visibility="collapsed", key=f"r_edit_{i}"
                )
                ca, cb = st.columns(2)
                with ca:
                    if st.button("✅ Use this", key=f"use_{i}", use_container_width=True, type="primary"):
                        st.session_state.selected_reply = edited
                        st.toast("Reply selected!", icon="✅")
                with cb:
                    if st.button("📋 Copy", key=f"copy_{i}", use_container_width=True):
                        st.session_state.selected_reply = edited
                        st.toast("Copied!", icon="📋")

            if st.session_state.selected_reply:
                st.markdown("<div class='card card-green'><div class='card-title'>Selected Reply</div>", unsafe_allow_html=True)
                st.code(st.session_state.selected_reply, language=None)
                st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# RIGHT PANEL — Reply history + mood chart
# ═══════════════════════════════════════════════════════════════════════════════
with right:
    st.markdown("<div style='padding:0.2rem 0.2rem;'>", unsafe_allow_html=True)

    # Mood pie
    if has_an and analysis:
        moods = analysis.get("mood_distribution", {})
        if moods:
            import plotly.graph_objects as go
            MOOD_COLORS = {"happy":"#10b981","neutral":"#374151","excited":"#f59e0b",
                           "sad":"#3b82f6","angry":"#ef4444"}
            fig = go.Figure(go.Pie(
                labels=[m.title() for m in moods],
                values=list(moods.values()),
                marker_colors=[MOOD_COLORS.get(m,"#374151") for m in moods],
                hole=0.6,
                hovertemplate="%{label}: %{value}<extra></extra>",
                textinfo="none",
            ))
            fig.update_layout(
                template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
                margin=dict(t=4,b=4,l=4,r=4), height=140, showlegend=True,
                legend=dict(font=dict(size=9), orientation="v", x=0.75),
            )
            st.markdown("<div class='card'><div class='card-title'>Mood Distribution</div>", unsafe_allow_html=True)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
            st.markdown("</div>", unsafe_allow_html=True)

        

    # Reply history
    st.markdown("<div class='card'><div class='card-title'>Reply History</div>", unsafe_allow_html=True)
    hr = api("get", "/reply/history")
    if hr and hr.status_code == 200:
        history = hr.json().get("history", [])
        if not history:
            st.markdown("<div style='color:#4b6280; font-size:0.78rem;'>No replies yet.</div>", unsafe_allow_html=True)
        else:
            for item in history[:10]:
                inc  = (item.get("incoming_message") or "")[:50]
                rep  = ((item.get("replies") or [""])[0])[:45]
                time = (item.get("created_at") or "")[:16]
                st.markdown(f"""
                <div class='hist-item'>
                    <div class='hist-time'>{time}</div>
                    <div class='hist-in'>📨 {inc}…</div>
                    <div class='hist-out'>💬 {rep}…</div>
                </div>
                """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
