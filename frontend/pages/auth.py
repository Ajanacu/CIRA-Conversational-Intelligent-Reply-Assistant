"""
Authentication Page - Login & Register
"""
import streamlit as st
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from api_client import api_post


def show():
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("""
        <div style='text-align:center; padding: 3rem 0 1rem 0;'>
            <div style='font-size:3.5rem'>💬</div>
            <div class='login-title'>CIRA</div>
            <div class='login-sub'>Conversational Intelligent Reply Assistant</div>
        </div>
        """, unsafe_allow_html=True)

        tab_login, tab_register = st.tabs(["🔐 Login", "✨ Register"])

        with tab_login:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            username = st.text_input("Username", key="login_user", placeholder="Enter username")
            password = st.text_input("Password", type="password", key="login_pass", placeholder="Enter password")

            if st.button("Login", use_container_width=True, type="primary"):
                if not username or not password:
                    st.error("Please fill all fields")
                else:
                    resp = api_post("/auth/login", {"username": username, "password": password}, authenticated=False)
                    if resp and resp.status_code == 200:
                        data = resp.json()
                        st.session_state.logged_in = True
                        st.session_state.token = data["token"]
                        st.session_state.username = data["username"]
                        st.session_state.display_name = data["display_name"]
                        st.success("✅ Login successful!")
                        st.rerun()
                    elif resp:
                        st.error(f"❌ {resp.json().get('detail', 'Login failed')}")
            st.markdown("</div>", unsafe_allow_html=True)

        with tab_register:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            new_display = st.text_input("Display Name", key="reg_display", placeholder="Your name")
            new_user = st.text_input("Username", key="reg_user", placeholder="Choose a username")
            new_pass = st.text_input("Password", type="password", key="reg_pass", placeholder="Choose a password")
            new_pass2 = st.text_input("Confirm Password", type="password", key="reg_pass2", placeholder="Confirm password")

            if st.button("Create Account", use_container_width=True, type="primary"):
                if not all([new_display, new_user, new_pass, new_pass2]):
                    st.error("Please fill all fields")
                elif new_pass != new_pass2:
                    st.error("Passwords do not match")
                elif len(new_pass) < 4:
                    st.error("Password must be at least 4 characters")
                else:
                    resp = api_post("/auth/register",
                                    {"username": new_user, "password": new_pass, "display_name": new_display},
                                    authenticated=False)
                    if resp and resp.status_code == 200:
                        data = resp.json()
                        st.session_state.logged_in = True
                        st.session_state.token = data["token"]
                        st.session_state.username = data["username"]
                        st.session_state.display_name = data["display_name"]
                        st.success("✅ Account created!")
                        st.rerun()
                    elif resp:
                        st.error(f"❌ {resp.json().get('detail', 'Registration failed')}")
            st.markdown("</div>", unsafe_allow_html=True)
