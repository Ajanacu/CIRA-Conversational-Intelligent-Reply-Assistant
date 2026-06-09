"""
Dashboard Page - WhatsApp Chat Analytics
"""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from api_client import api_get, api_post
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd


MOOD_COLORS = {
    "happy": "#10b981",
    "neutral": "#6b7280",
    "excited": "#f59e0b",
    "sad": "#3b82f6",
    "angry": "#ef4444",
}

DAY_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def show():
    st.markdown("""
    <div style='margin-bottom:1.5rem;'>
        <span style='font-size:1.6rem; font-weight:700; color:#25D366'>📊 Chat Dashboard</span>
        <span style='color:#6b7280; margin-left:0.75rem; font-size:0.9rem'>Insights from your WhatsApp conversations</span>
    </div>
    """, unsafe_allow_html=True)

    # Check if we have analysis
    resp = api_get("/chat/analysis")

    if resp is None:
        return

    if resp.status_code == 404:
        st.info("📁 No analysis found. Upload a WhatsApp chat and run analysis first.")
        col1, col2 = st.columns(2)
        with col2:
            if st.button("🔍 Analyze Chat", use_container_width=True, type="primary"):
                with st.spinner("Analyzing..."):
                    r = api_post("/chat/analyze", {})
                if r and r.status_code == 200:
                    st.success("Analysis complete!")
                    st.rerun()
        return

    if resp.status_code != 200:
        st.error("Error loading analysis")
        return

    analysis = resp.json()

    # ── Top metrics ───────────────────────────────────────────────────────────
    m1, m2, m3, m4 = st.columns(4)

    total = analysis.get("total_messages", 0)
    senders = analysis.get("senders", [])
    top_mood = max(analysis.get("mood_distribution", {"neutral": 1}), key=analysis.get("mood_distribution", {}).get)
    date_range = analysis.get("date_range", {})

    with m1:
        st.markdown(f"""
        <div class='card card-green' style='text-align:center;'>
            <div class='metric-big'>{total:,}</div>
            <div class='metric-label'>Total Messages</div>
        </div>""", unsafe_allow_html=True)
    with m2:
        st.markdown(f"""
        <div class='card card-blue' style='text-align:center;'>
            <div class='metric-big'>{len(senders)}</div>
            <div class='metric-label'>Participants</div>
        </div>""", unsafe_allow_html=True)
    with m3:
        mood_emoji = {"happy": "😊", "excited": "🎉", "sad": "😢", "angry": "😡", "neutral": "😐"}.get(top_mood, "😐")
        st.markdown(f"""
        <div class='card' style='text-align:center;'>
            <div class='metric-big'>{mood_emoji}</div>
            <div class='metric-label'>Dominant Mood: {top_mood.title()}</div>
        </div>""", unsafe_allow_html=True)
    with m4:
        msg_types = analysis.get("message_type_distribution", {})
        media_pct = round(msg_types.get("media", 0) / max(total, 1) * 100)
        st.markdown(f"""
        <div class='card' style='text-align:center;'>
            <div class='metric-big'>{media_pct}%</div>
            <div class='metric-label'>Media Messages</div>
        </div>""", unsafe_allow_html=True)

    if date_range.get("first"):
        st.markdown(f"""
        <div style='color:#6b7280; font-size:0.8rem; margin-bottom:1rem;'>
            📅 Chat period: {date_range.get('first', '')[:10]} → {date_range.get('last', '')[:10]}
        </div>""", unsafe_allow_html=True)

    # ── Charts Row 1 ──────────────────────────────────────────────────────────
    c1, c2 = st.columns(2)

    with c1:
        # Hourly activity heatmap
        hourly = analysis.get("hourly_distribution", {})
        if hourly:
            hours = list(range(24))
            counts = [hourly.get(str(h), hourly.get(h, 0)) for h in hours]
            labels = [f"{h:02d}:00" for h in hours]

            fig = go.Figure(go.Bar(
                x=labels, y=counts,
                marker_color=[
                    f"rgba(37, 211, 102, {min(1.0, 0.2 + c / max(counts, default=1) * 0.8)})"
                    for c in counts
                ],
                hovertemplate="%{x}<br>Messages: %{y}<extra></extra>"
            ))
            fig.update_layout(
                title="⏰ Activity by Hour",
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(t=40, b=20, l=20, r=20),
                height=280,
                xaxis=dict(tickangle=-45, tickfont=dict(size=9)),
                yaxis_title=None,
            )
            st.plotly_chart(fig, use_container_width=True)

    with c2:
        # Day of week distribution
        daily = analysis.get("daily_distribution", {})
        if daily:
            days = [d for d in DAY_ORDER if d in daily]
            vals = [daily[d] for d in days]

            fig = go.Figure(go.Bar(
                x=days, y=vals,
                marker_color="#25D366",
                hovertemplate="%{x}<br>Messages: %{y}<extra></extra>"
            ))
            fig.update_layout(
                title="📅 Activity by Day",
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(t=40, b=20, l=20, r=20),
                height=280,
            )
            st.plotly_chart(fig, use_container_width=True)

    # ── Charts Row 2 ──────────────────────────────────────────────────────────
    c3, c4, c5 = st.columns([1.2, 1, 1])

    with c3:
        # Mood distribution
        moods = analysis.get("mood_distribution", {})
        if moods:
            mood_labels = list(moods.keys())
            mood_vals = list(moods.values())
            mood_colors = [MOOD_COLORS.get(m, "#6b7280") for m in mood_labels]

            fig = go.Figure(go.Pie(
                labels=[m.title() for m in mood_labels],
                values=mood_vals,
                marker_colors=mood_colors,
                hole=0.5,
                hovertemplate="%{label}: %{value} msgs<extra></extra>"
            ))
            fig.update_layout(
                title="😊 Mood Distribution",
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                margin=dict(t=40, b=10, l=10, r=10),
                height=280,
                legend=dict(font=dict(size=10)),
            )
            st.plotly_chart(fig, use_container_width=True)

    with c4:
        # Message type distribution
        msg_types = analysis.get("message_type_distribution", {})
        if msg_types and sum(msg_types.values()) > 0:
            fig = go.Figure(go.Pie(
                labels=["Text 📝", "Media 📸", "Links 🔗"],
                values=[msg_types.get("text", 0), msg_types.get("media", 0), msg_types.get("link", 0)],
                marker_colors=["#25D366", "#3b82f6", "#f59e0b"],
                hole=0.5,
            ))
            fig.update_layout(
                title="📂 Message Types",
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                margin=dict(t=40, b=10, l=10, r=10),
                height=280,
                legend=dict(font=dict(size=10)),
            )
            st.plotly_chart(fig, use_container_width=True)

    with c5:
        # Per-sender message count
        sender_stats = analysis.get("sender_stats", {})
        if sender_stats:
            names = list(sender_stats.keys())[:6]
            counts = [sender_stats[n]["total_messages"] for n in names]

            fig = go.Figure(go.Bar(
                x=counts, y=names,
                orientation="h",
                marker_color="#25D366",
                hovertemplate="%{y}: %{x} messages<extra></extra>"
            ))
            fig.update_layout(
                title="👥 Messages per Person",
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(t=40, b=20, l=20, r=20),
                height=280,
            )
            st.plotly_chart(fig, use_container_width=True)

    # ── Per-Sender Details ────────────────────────────────────────────────────
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-header'>👤 Per-Participant Stats</div>", unsafe_allow_html=True)

    sender_stats = analysis.get("sender_stats", {})
    if sender_stats:
        rows = []
        for name, stats in sender_stats.items():
            mood_dist = stats.get("mood_distribution", {})
            top_mood = max(mood_dist, key=mood_dist.get) if mood_dist else "neutral"
            rows.append({
                "Name": name,
                "Messages": stats.get("total_messages", 0),
                "Avg Length": stats.get("avg_length", 0),
                "Media": stats.get("media_count", 0),
                "Links": stats.get("link_count", 0),
                "Top Mood": top_mood.title(),
                "Peak Hour": f"{stats.get('most_active_hour', '?')}:00",
                "Peak Day": stats.get("most_active_day", "?"),
            })
        df = pd.DataFrame(rows).sort_values("Messages", ascending=False)
        st.dataframe(df, use_container_width=True, hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Top Words ─────────────────────────────────────────────────────────────
    top_words = analysis.get("top_words", [])
    if top_words:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-header'>🔤 Most Used Words</div>", unsafe_allow_html=True)
        words_html = ""
        for word, count in top_words[:15]:
            opacity = 0.4 + (count / (top_words[0][1] if top_words else 1)) * 0.6
            size = 0.85 + (count / (top_words[0][1] if top_words else 1)) * 0.6
            words_html += f"""<span style='
                background: rgba(37,211,102,{opacity:.2f});
                color: white;
                border-radius: 999px;
                padding: 4px 14px;
                margin: 4px;
                display: inline-block;
                font-size: {size:.2f}rem;
                font-weight: 600;
            '>{word} <span style='opacity:0.7; font-size:0.75rem'>({count})</span></span>"""
        st.markdown(f"<div style='line-height:2.5'>{words_html}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Re-analyze button ─────────────────────────────────────────────────────
    st.divider()
    col_a, col_b = st.columns([3, 1])
    with col_b:
        if st.button("🔄 Re-analyze Chat", use_container_width=True):
            with st.spinner("Re-analyzing..."):
                r = api_post("/chat/analyze", {})
            if r and r.status_code == 200:
                st.success("Analysis updated!")
                st.rerun()
