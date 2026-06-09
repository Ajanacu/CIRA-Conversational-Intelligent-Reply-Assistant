"""
Upload Chat Page - Step 1: Upload, Step 2: Analyze
"""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from api_client import api_post, api_get


def show():
    st.markdown("""
    <div style='margin-bottom:1.5rem;'>
        <span style='font-size:1.6rem; font-weight:700; color:#25D366'>📁 Upload & Analyze</span>
    </div>
    """, unsafe_allow_html=True)

    # Get current status
    status_resp = api_get("/chat/status")
    status = status_resp.json() if status_resp and status_resp.status_code == 200 else {}
    has_messages = status.get("has_messages", False)
    message_count = status.get("message_count", 0)
    has_analysis = status.get("has_analysis", False)

    col1, col2 = st.columns([1.5, 1])

    with col1:
        # Step 1: Upload
        step1_color = "#059669" if has_messages else "#374151"
        st.markdown(f"""
        <div class='card' style='border-color:{step1_color};'>
            <div class='section-header'>
                {'✅' if has_messages else '1️⃣'} Upload WhatsApp Chat
            </div>
            {f"<div style='color:#6ee7b7; font-size:0.85rem; margin-bottom:0.75rem;'>✓ {message_count:,} messages loaded</div>" if has_messages else ""}
        """, unsafe_allow_html=True)

        uploaded = st.file_uploader("Choose .txt file", type=["txt"], label_visibility="collapsed")

        if uploaded:
            st.success(f"File ready: **{uploaded.name}** ({uploaded.size / 1024:.1f} KB)")
            if st.button("📤 Upload Chat", type="primary", use_container_width=True):
                with st.spinner("Uploading and parsing..."):
                    files = {"file": (uploaded.name, uploaded.getvalue(), "text/plain")}
                    resp = api_post("/chat/upload", files=files)

                if resp and resp.status_code == 200:
                    count = resp.json().get("count", 0)
                    if count == 0:
                        st.error("⚠️ No messages parsed. Make sure the file is a WhatsApp .txt export (without media).")
                    else:
                        st.success(f"✅ {count:,} messages uploaded!")
                        st.rerun()
                elif resp:
                    st.error(f"❌ {resp.json().get('detail', 'Upload failed')}")

        st.markdown("</div>", unsafe_allow_html=True)

        # Step 2: Analyze
        step2_color = "#059669" if has_analysis else ("#1e40af" if has_messages else "#374151")
        st.markdown(f"""
        <div class='card' style='border-color:{step2_color}; margin-top:0.5rem;'>
            <div class='section-header'>
                {'✅' if has_analysis else '2️⃣'} Analyze Messaging Style
            </div>
            <div style='color:#9ca3af; font-size:0.85rem; margin-bottom:0.75rem;'>
                {'Analysis saved. Re-analyze only after uploading a new chat.' if has_analysis
                 else 'Learns your writing style from the uploaded chat.' if has_messages
                 else 'Upload a chat first.'}
            </div>
        """, unsafe_allow_html=True)

        if has_messages:
            btn_label = "🔄 Re-analyze" if has_analysis else "🔍 Analyze My Chat"
            if st.button(btn_label, type="primary" if not has_analysis else "secondary", use_container_width=True):
                with st.spinner("Analyzing your messaging style..."):
                    resp = api_post("/chat/analyze", {})
                if resp and resp.status_code == 200:
                    pattern = resp.json().get("user_pattern", {})
                    st.success("✅ Analysis complete!")
                    if pattern.get("style_summary"):
                        st.info(f"🎨 *{pattern['style_summary']}*")
                    st.rerun()
                elif resp:
                    st.error(f"❌ {resp.json().get('detail', 'Analysis failed')}")
        else:
            st.button("🔍 Analyze My Chat", disabled=True, use_container_width=True)

        st.markdown("</div>", unsafe_allow_html=True)

        # Style profile preview after analysis
        if has_analysis:
            analysis_resp = api_get("/chat/analysis")
            if analysis_resp and analysis_resp.status_code == 200:
                pattern = analysis_resp.json().get("user_pattern", {})
                if pattern:
                    summary = pattern.get("style_summary", "")
                    st.markdown(f"""
                    <div class='card card-green'>
                        <div class='section-header'>🎨 Your Style Profile</div>
                        <div style='color:#a7f3d0; margin-top:0.5rem; line-height:2;'>
                            <strong>Language:</strong> {pattern.get('language_style','—').title()}<br>
                            <strong>Manglish:</strong> {pattern.get('manglish_level','none').title()}<br>
                            <strong>Avg length:</strong> {pattern.get('avg_message_length','—').title()}<br>
                            <strong>Emoji:</strong> {'Yes 😊' if pattern.get('uses_emoji') else 'No'}<br>
                            <strong>Punctuation:</strong> {pattern.get('punctuation_style','—').title()}
                        </div>
                        {f'<div style="color:#6ee7b7;font-size:0.85rem;margin-top:0.5rem;font-style:italic;">"{summary}"</div>' if summary else ''}
                    </div>
                    """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class='card'>
            <div class='section-header'>📱 How to Export Chat</div>
            <div style='color:#9ca3af; font-size:0.85rem; line-height:2.2;'>
                <div>1️⃣ Open WhatsApp</div>
                <div>2️⃣ Open the chat</div>
                <div>3️⃣ Tap ⋮ → <strong>More</strong></div>
                <div>4️⃣ Tap <strong>Export Chat</strong></div>
                <div>5️⃣ Choose <strong>Without Media</strong></div>
                <div>6️⃣ Save the <strong>.txt</strong> file</div>
                <div>7️⃣ Upload it here ✅</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class='card' style='margin-top:1rem;'>
            <div class='section-header'>📊 Status</div>
            <div style='line-height:2.4; font-size:0.9rem;'>
                <div>{'✅' if has_messages else '⬜'} Chat uploaded
                    {f'<span style="color:#6b7280"> · {message_count:,} msgs</span>' if has_messages else ''}
                </div>
                <div>{'✅' if has_analysis else '⬜'} Style analyzed</div>
                <div>{'✅' if has_analysis else '⬜'} Ready to generate replies</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
