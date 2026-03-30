"""
Authentication UI module for login and signup.
"""

import streamlit as st
from models.user_model import UserModel


class AuthUI:
    """Handle authentication UI components."""
    
    @staticmethod
    def login_form() -> bool:
        """Display login form."""
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login", use_container_width=True)
            
            if submitted:
                user = UserModel.authenticate(username, password)
                if user:
                    st.session_state.user_id = user['user_id']
                    st.session_state.username = user['username']
                    UserModel.update_last_login(user['user_id'])
                    st.success(f"Welcome back, {username}!")
                    st.rerun()
                    return True
                else:
                    st.error("Invalid username or password")
        
        return False
    
    @staticmethod
    def signup_form() -> bool:
        """Display signup form."""
        with st.form("signup_form"):
            username = st.text_input("Username")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            submitted = st.form_submit_button("Sign Up", use_container_width=True)
            
            if submitted:
                if password != confirm_password:
                    st.error("Passwords don't match")
                elif not username or not email:
                    st.error("Please fill all fields")
                else:
                    user_id = UserModel.create_user(username, password, email)
                    if user_id:
                        st.session_state.user_id = user_id
                        st.session_state.username = username
                        st.success("Account created successfully!")
                        st.rerun()
                        return True
                    else:
                        st.error("Username already exists")
        
        return False
    
    @staticmethod
    def render():
        """Render authentication UI in sidebar."""
        st.sidebar.title("Authentication")
        
        # Initialize session state
        if 'user_id' not in st.session_state:
            st.session_state.user_id = None
            st.session_state.username = None
        
        # Show login/signup if not logged in
        if st.session_state.user_id is None:
            tab1, tab2 = st.sidebar.tabs(["Login", "Sign Up"])
            
            with tab1:
                AuthUI.login_form()
            
            with tab2:
                AuthUI.signup_form()
            
            return False
        
        # Show user info if logged in
        else:
            st.sidebar.success(f"Logged in as: {st.session_state.username}")
            
            if st.sidebar.button("Logout", use_container_width=True):
                st.session_state.user_id = None
                st.session_state.username = None
                st.session_state.clients = {}
                st.rerun()
            
            return True