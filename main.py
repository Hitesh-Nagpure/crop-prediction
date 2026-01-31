import streamlit as st
import sys
import os

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from auth import AuthManager
from dashboard import Dashboard
from ml_modules import MLModules
from additional_features import AdditionalFeatures
from admin_panel import AdminPanel
from language_utils import get_text, get_current_language, render_voice_controls, speak_text_response, is_voice_assistant_available
from voice_assistant import VoiceAssistant
from crop_disease_detection import render_disease_detection_ui
from pesticide_shops_map import render_pesticide_shops_map

# Page configuration
st.set_page_config(
    page_title="AGRIVISION - Smart Agriculture System",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for responsive design and mobile support
st.markdown("""
<style>
/* Mobile Responsive Design */
@media (max-width: 768px) {
    .stSidebar {
        width: 100% !important;
    }
    
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }
    
    .element-container {
        width: 100% !important;
    }
}

/* Desktop styles only, removed mobile bottom nav styles */
@media (min-width: 769px) {
    /* Styles here if needed */
}

/* General styling */
.metric-card {
    background: white;
    padding: 1rem;
    border-radius: 10px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    margin-bottom: 1rem;
}

.gradient-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 2rem;
    border-radius: 15px;
    margin-bottom: 2rem;
    text-align: center;
    color: white;
}

/* Loading animation */
.loading {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 200px;
}

/* Responsive tables */
@media (max-width: 768px) {
    .dataframe {
        font-size: 0.8rem;
    }
}

/* Responsive charts */
@media (max-width: 768px) {
    .js-plotly-plot {
        width: 100% !important;
    }
}
</style>
""", unsafe_allow_html=True)

def show_voice_assistant():
    """Display the AI Voice Assistant page"""
    from voice_assistant import render_voice_controls
    render_voice_controls()

def main():
    """Main application entry point"""
    
    # Initialize managers
    auth_manager = AuthManager()
    dashboard = Dashboard()
    ml_modules = MLModules()
    additional_features = AdditionalFeatures()
    admin_panel = AdminPanel()
    
    # Check if accessing admin panel
    query_params = st.query_params
    if 'admin' in query_params and query_params['admin'] == 'true':
        admin_panel.show_admin_dashboard()
        return
    
    # Authentication check
    if not auth_manager.require_auth():
        return
    
    # Get current user
    user = auth_manager.get_current_user()
    if not user:
        return
    
    # Sidebar navigation with dropdown menus
    with st.sidebar:
        # Dashboard as standalone item
        current_lang = get_current_language()
        
        if st.button(f"{get_text('Dashboard', current_lang)}", use_container_width=True, key="dashboard_btn"):
            st.session_state.selected_page = "dashboard"
            st.rerun()
        
        st.markdown("---")
        
        # AI Predictions Dropdown
        with st.expander(f"AI Predictions", expanded=True):
            ai_options = [
                f"{get_text('Crop Recommendation', current_lang)}",
                f"{get_text('Yield Prediction', current_lang)}",
                f"{get_text('Disease Detection', current_lang)}"
            ]
            
            # Add navigation buttons for AI options
            for option in ai_options:
                if st.button(option, key=f"ai_btn_{option}", use_container_width=True):
                    st.session_state.selected_page = option
                    st.rerun()
        
        # Resources Dropdown
        with st.expander(f"Resources", expanded=False):
            resource_options = [
                f"{get_text('Government Schemes', current_lang)}",
                f"{get_text('Pesticide Information', current_lang)}",
                f"{get_text('Nearby Pesticide Shops', current_lang)}"
            ]
            
            # Add navigation buttons for resource options
            for option in resource_options:
                if st.button(option, key=f"resource_btn_{option}", use_container_width=True):
                    st.session_state.selected_page = option
                    st.rerun()
        
        # Account Dropdown
        with st.expander(f"Account", expanded=False):
            account_options = [
                f"{get_text('Profile & AI Chatbot', current_lang)}",
                "Voice Assistant"
            ]
            
            # Add navigation buttons for account options
            for option in account_options:
                if st.button(option, key=f"account_btn_{option}", use_container_width=True):
                    if option == "Voice Assistant":
                        st.session_state.selected_page = "voice_assistant"
                    else:
                        st.session_state.selected_page = option
                    st.rerun()
        
        # Admin access (if user is admin)
        if user['email'] == 'admin@agrivision.com':
            with st.expander("Admin Panel", expanded=False):
                if st.button("Admin Dashboard", key="admin_btn", use_container_width=True):
                    st.query_params.admin = "true"
                    st.rerun()
        
        # Determine selected menu item
        menu = None
        if 'selected_page' in st.session_state:
            if st.session_state.selected_page == "dashboard":
                menu = f"{get_text('Dashboard', current_lang)}"
            else:
                menu = st.session_state.selected_page
        else:
            # Default to dashboard if nothing selected
            menu = f"{get_text('Dashboard', current_lang)}"
            st.session_state.selected_page = "dashboard"
        
        # Show authentication info
        auth_manager.show_auth_sidebar()
    
    # Main content area
    current_lang = get_current_language()
    
    # Map menu options to their English keys for comparison
    menu_mapping = {
        f"{get_text('Dashboard', current_lang)}": "dashboard",
        f"{get_text('Crop Recommendation', current_lang)}": "crop",
        f"{get_text('Yield Prediction', current_lang)}": "yield",
        f"{get_text('Disease Detection', current_lang)}": "disease_detection",
        f"{get_text('Government Schemes', current_lang)}": "schemes",
        f"{get_text('Pesticide Information', current_lang)}": "pesticide",
        f"{get_text('Nearby Pesticide Shops', current_lang)}": "shops",
        f"{get_text('Profile & AI Chatbot', current_lang)}": "profile",
        "Admin Panel": "admin"
    }
    
    # Handle voice assistant directly from session state
    if st.session_state.get('selected_page') == "voice_assistant":
        selected_page = "voice_assistant"
    else:
        selected_page = menu_mapping.get(menu, "dashboard")
    
    if selected_page == "dashboard":
        dashboard.show_dashboard()
    elif selected_page == "crop":
        ml_modules.show_crop_recommendation()
    elif selected_page == "yield":
        ml_modules.show_yield_prediction()
    elif selected_page == "disease_detection":
        render_disease_detection_ui()
    elif selected_page == "schemes":
        additional_features.show_government_schemes()
    elif selected_page == "pesticide":
        additional_features.show_pesticide_information()
    elif selected_page == "shops":
        render_pesticide_shops_map()
    elif selected_page == "profile":
        additional_features.show_profile()
    elif selected_page == "voice_assistant":
        show_voice_assistant()
    elif selected_page == "admin":
        # Redirect to admin panel
        st.query_params.admin = "true"
        st.rerun()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p>AGRIVISION - Smart Agriculture Decision Support System</p>
        <p>© 2024 All rights reserved | Empowering farmers with AI technology</p>
        <p>
            <a href='#' style='color: #667eea;'>Privacy Policy</a> | 
            <a href='#' style='color: #667eea;'>Terms of Service</a> | 
            <a href='#' style='color: #667eea;'>Contact Us</a>
        </p>
    </div>
    """, unsafe_allow_html=True)



if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.markdown("Please refresh the page and try again. If the problem persists, contact support.")
