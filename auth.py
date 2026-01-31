import streamlit as st
from database import Database
import re

class AuthManager:
    def __init__(self):
        self.db = Database()
        
        # Initialize session state
        if 'user' not in st.session_state:
            st.session_state.user = None
        if 'page' not in st.session_state:
            st.session_state.page = 'login'
    
    def is_valid_email(self, email):
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def is_valid_mobile(self, mobile):
        """Validate mobile number (Indian format)"""
        pattern = r'^[6-9]\d{9}$'
        return re.match(pattern, mobile) is not None
    
    def show_login_page(self):
        """Display login page"""
        st.markdown("""
        <style>
        .auth-container {
            max-width: 400px;
            margin: 0 auto;
            padding: 2rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        .auth-title {
            text-align: center;
            color: white;
            margin-bottom: 2rem;
            font-size: 2rem;
            font-weight: bold;
        }
        .auth-input {
            margin-bottom: 1rem;
        }
        </style>
        """, unsafe_allow_html=True)
        
        with st.container():
            st.markdown('<div class="auth-container">', unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([1, 3, 1])
            with col2:
                st.markdown('<h1 class="auth-title">AGRIVISION</h1>', unsafe_allow_html=True)
                st.markdown('<p style="text-align: center; color: white; margin-bottom: 2rem;">Smart Agriculture Decision Support System</p>', unsafe_allow_html=True)
                
                with st.form("login_form"):
                    st.markdown('<h3 style="color: white; text-align: center; margin-bottom: 1.5rem;">Farmer Login</h3>', unsafe_allow_html=True)
                    
                    email_mobile = st.text_input("Email or Mobile Number", placeholder="Enter email or mobile")
                    password = st.text_input("Password", type="password", placeholder="Enter password")
                    
                    submit_button = st.form_submit_button("Login", use_container_width=True)
                    
                    if submit_button:
                        if not email_mobile or not password:
                            st.error("Please fill all fields")
                        else:
                            user = self.db.authenticate_user(email_mobile, password)
                            if user:
                                st.session_state.user = {
                                    'id': user[0],
                                    'name': user[1],
                                    'email': user[2],
                                    'language': user[3]
                                }
                                st.success("Login successful!")
                                st.rerun()
                            else:
                                st.error("Invalid email/mobile or password")
                
                st.markdown('<div style="text-align: center; margin-top: 1.5rem;">', unsafe_allow_html=True)
                st.markdown('<p style="color: white;">New farmer? <a href="#" style="color: #FFD700;">Create Account</a></p>', unsafe_allow_html=True)
                if st.button("Create New Account", use_container_width=True):
                    st.session_state.page = 'signup'
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    def show_signup_page(self):
        """Display signup page"""
        st.markdown("""
        <style>
        .auth-container {
            max-width: 400px;
            margin: 0 auto;
            padding: 2rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        </style>
        """, unsafe_allow_html=True)
        
        with st.container():
            st.markdown('<div class="auth-container">', unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([1, 3, 1])
            with col2:
                st.markdown('<h1 class="auth-title">AGRIVISION</h1>', unsafe_allow_html=True)
                st.markdown('<p style="text-align: center; color: white; margin-bottom: 2rem;">Create Your Account</p>', unsafe_allow_html=True)
                
                with st.form("signup_form"):
                    st.markdown('<h3 style="color: white; text-align: center; margin-bottom: 1.5rem;">Farmer Registration</h3>', unsafe_allow_html=True)
                    
                    name = st.text_input("Full Name", placeholder="Enter your full name")
                    email = st.text_input("Email Address", placeholder="Enter email address")
                    mobile = st.text_input("Mobile Number", placeholder="Enter 10-digit mobile number")
                    password = st.text_input("Password", type="password", placeholder="Create password")
                    confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm password")
                    
                    submit_button = st.form_submit_button("Create Account", use_container_width=True)
                    
                    if submit_button:
                        # Validation
                        if not all([name, email, mobile, password, confirm_password]):
                            st.error("Please fill all fields")
                        elif not self.is_valid_email(email):
                            st.error("Please enter a valid email address")
                        elif not self.is_valid_mobile(mobile):
                            st.error("Please enter a valid 10-digit mobile number")
                        elif len(password) < 6:
                            st.error("Password must be at least 6 characters long")
                        elif password != confirm_password:
                            st.error("Passwords do not match")
                        else:
                            # Create user
                            if self.db.create_user(name, email, mobile, password):
                                st.success("Account created successfully! Please login.")
                                st.session_state.page = 'login'
                                st.rerun()
                            else:
                                st.error("Email or mobile number already registered")
                
                st.markdown('<div style="text-align: center; margin-top: 1.5rem;">', unsafe_allow_html=True)
                if st.button("Back to Login", use_container_width=True):
                    st.session_state.page = 'login'
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    def logout(self):
        """Logout user"""
        st.session_state.user = None
        st.session_state.page = 'login'
        st.rerun()
    
    def get_current_user(self):
        """Get current logged-in user"""
        return st.session_state.get('user')
    
    def require_auth(self):
        """Check if user is authenticated, show login page if not"""
        if not st.session_state.get('user'):
            if st.session_state.get('page') == 'signup':
                self.show_signup_page()
            else:
                self.show_login_page()
            return False
        return True
    
    def show_auth_sidebar(self):
        """Show authentication info in sidebar"""
        # Removed logout button - moved to profile section
        pass
