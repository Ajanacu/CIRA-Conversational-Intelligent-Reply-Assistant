"""
Reply Assistant Page
"""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from api_client import api_post, api_get

RELATIONSHIPS = {
    "👫 Friend": "friend",
    "👨‍👩‍👧 Family": "family",
    "💼 Client": "client",
    "🏢 Manager": "manager",
    "🤝 Colleague": "colleague",
    "❤️ Partner": "partner",
    "🎓 Teacher / Mentor": "mentor",
    "🧑‍🤝‍🧑 Acquaintance": "acquaintance",
}

TONES = {
    "😊 Casual": "casual",
    "😄 Friendly": "friendly",
    "💼 Professional": "professional",
    "😂 Humorous": "humorous",
    "🤝 Formal": "formal",
    "💕 Warm": "warm",
    "⚡ Direct": "direct",
}


def show():
    st.markdown("""
    <div style='margin-bottom:1.5rem;'>
        <span style='font-size:1.6rem; font-weight:700; color:#25D366'>💬 Reply Assistant</span>
    </div>
    """, unsafe_allow_html=True)

    # Check if chat has been analyzed
    analysis_resp = api_get("/chat/analysis")
    has_analysis = analysis_resp and analysis_resp.status_code == 200

    if not has_analysis:
        st.warning("⚠️ No chat analyzed yet. Please upload and analyze your chat first.")
        return

    col_main, col_history = st.columns([1.7, 1])

    with col_main:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-header'>📨 Incoming Message</div>", unsafe_allow_html=True)

        incoming = st.text_area(
            "incoming",
            placeholder="Paste the message you received here...",
            height=100,
            label_visibility="collapsed",
            key="incoming_msg"
        )

        # Relationship and tone row
        col_r, col_t = st.columns(2)
        with col_r:
            rel_label = st.selectbox(
                "Relationship",
                options=list(RELATIONSHIPS.keys()),
                key="relationship_select"
            )
        with col_t:
            tone_label = st.selectbox(
                "Tone",
                options=list(TONES.keys()),
                key="tone_select"
            )

        sender = st.text_input("Sender name (optional)", placeholder="e.g. Rahul, Amma, Boss...")

        generate_btn = st.button("✨ Generate Replies", type="primary", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        if generate_btn:
            if not incoming.strip():
                st.error("Please enter the incoming message.")
            else:
                with st.spinner("Generating replies..."):
                    resp = api_post("/reply/generate", {
                        "incoming_message": incoming,
                        "sender_name": sender or None,
                        "relationship": RELATIONSHIPS[rel_label],
                        "tone": TONES[tone_label],
                    })

                if resp and resp.status_code == 200:
                    data = resp.json()
                    replies = data.get("replies", [])
                    similar_found = data.get("similar_found", False)

                    st.markdown("<div class='card'>", unsafe_allow_html=True)

                    st.markdown(f"""
                    <div class='incoming-msg'>
                        <span style='color:#25D366; font-size:0.75rem; font-weight:600'>
                            {'📨 ' + sender if sender else '📨 Incoming'} &nbsp;·&nbsp;
                            {rel_label} &nbsp;·&nbsp; {tone_label}
                        </span><br>
                        {incoming}
                    </div>
                    """, unsafe_allow_html=True)

                    if similar_found:
                        st.markdown("<span class='badge badge-green'>✓ Based on your past similar replies</span>", unsafe_allow_html=True)

                    st.markdown("<div class='section-header' style='margin-top:1rem'>💬 Choose a Reply</div>", unsafe_allow_html=True)

                    icons = ["⭐ Option 1", "💡 Option 2", "🔄 Option 3"]
                    for i, (reply_text, icon) in enumerate(zip(replies, icons)):
                        st.markdown(f"<div style='color:#9ca3af; font-size:0.75rem; margin-top:0.8rem'>{icon}</div>", unsafe_allow_html=True)

                        edited = st.text_area(
                            f"reply_{i}",
                            value=reply_text,
                            key=f"edit_{i}",
                            height=80,
                            label_visibility="collapsed"
                        )
                        c1, c2 = st.columns([1, 1])
                        with c1:
                            if st.button("📋 Copy", key=f"copy_{i}", use_container_width=True):
                                st.session_state["selected_reply"] = edited
                                st.toast("Copied to clipboard area!", icon="✅")
                        with c2:
                            if st.button("✅ Use this", key=f"use_{i}", use_container_width=True):
                                st.session_state["selected_reply"] = edited
                                st.toast("Reply selected!", icon="✅")

                    if st.session_state.get("selected_reply"):
                        st.divider()
                        st.markdown("<div class='section-header'>✅ Selected Reply</div>", unsafe_allow_html=True)
                        st.code(st.session_state["selected_reply"], language=None)

                    st.markdown("</div>", unsafe_allow_html=True)

                elif resp:
                    st.error(f"❌ {resp.json().get('detail', 'Error generating replies')}")

    with col_history:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-header'>🕐 Recent History</div>", unsafe_allow_html=True)

        resp = api_get("/reply/history")
        if resp and resp.status_code == 200:
            history = resp.json().get("history", [])
            if not history:
                st.markdown("<div style='color:#6b7280; font-size:0.85rem'>No history yet.</div>", unsafe_allow_html=True)
            else:
                for item in history[:8]:
                    incoming_preview = item.get("incoming_message", "")[:55]
                    reply_preview = (item.get("replies") or [""])[0][:45]
                    st.markdown(f"""
                    <div style='border-bottom: 1px solid #374151; padding: 0.6rem 0;'>
                        <div style='color:#9ca3af; font-size:0.72rem'>{item.get('created_at','')[:16]}</div>
                        <div style='color:#d1fae5; font-size:0.83rem; margin-top:2px'>📨 {incoming_preview}…</div>
                        <div style='color:#6ee7b7; font-size:0.8rem; margin-top:2px'>💬 {reply_preview}…</div>
                    </div>
                    """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

