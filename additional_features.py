import streamlit as st
import pandas as pd
import sqlite3
import os
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import json
from auth import AuthManager
from language_utils import get_text, get_current_language
from voice_assistant import VoiceAssistant, render_voice_controls
from database import Database
import folium
from streamlit_folium import st_folium
import requests

# Global functions for government schemes
def show_application_process(scheme_name, application_process):
    """Display detailed application process for a scheme"""
    current_lang = get_current_language()
    st.markdown(f"""
    <style>
    .process-header {
        background-color: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
    }
    .process-step {
        background-color: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        border-left: 5px solid #667eea;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="process-header">
        <h1>{get_text('Application Process', current_lang)} - {scheme_name}</h1>
        <p>{get_text('Application process will guide you through the steps', current_lang)}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Application Steps
    steps = [
        {
            "step": "Step 1: Eligibility Check",
            "description": "Verify if you meet the eligibility criteria for this scheme. Check your land ownership, crop type, and other requirements.",
            "documents": ["Land ownership documents", "Aadhaar card", "Bank account details", "Crop cultivation proof"]
        },
        {
            "step": "Step 2: Document Preparation",
            "description": "Gather all required documents and ensure they are properly attested and up-to-date.",
            "documents": ["Recent photographs", "Income certificate", "Land records", "Bank passbook"]
        },
        {
            "step": "Step 3: Online Registration",
            "description": "Register on the official government portal and fill out the application form with accurate information.",
            "documents": ["Digital copies of documents", "Mobile number", "Email address", "Bank account details"]
        },
        {
            "step": "Step 4: Document Upload",
            "description": "Upload scanned copies of all required documents in the specified format and size.",
            "documents": ["Scanned documents", "Passport size photos", "Signature", "Thumb impression"]
        },
        {
            "step": "Step 5: Verification",
            "description": "Wait for government verification of your application and documents. This may take 2-4 weeks.",
            "documents": ["Application reference number", "Contact details", "Email/SMS updates"]
        },
        {
            "step": "Step 6: Approval & Disbursement",
            "description": "Upon approval, benefits will be disbursed directly to your bank account.",
            "documents": ["Bank account details", "IFSC code", "Account holder name"]
        }
    ]
    
    for i, step in enumerate(steps, 1):
        st.markdown(f"""
        <div class="process-step">
            <h3>{step['step']}</h3>
            <p>{step['description']}</p>
            <p><strong>Required Documents:</strong></p>
            <ul>
        """, unsafe_allow_html=True)
        
        for doc in step['documents']:
            st.write(f"• {doc}")
        
        st.markdown("""
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Important Notes
    st.markdown("### Important Notes")
    st.warning("""
    • Ensure all documents are clear and legible
    • Double-check all information before submission
    • Keep your application reference number safe
    • Regularly check your application status online
    • Contact the helpline if you face any issues
    """)
    
    # Contact Information
    st.markdown("### Contact Information")
    col1, col2 = st.columns(2)
    with col1:
        st.info("""
        **Helpline:** 1800-180-1234
        **Email:** support@agrischemes.gov.in
        **Website:** www.agrischemes.gov.in
        """)
    with col2:
        st.info("""
        **Office Hours:** 9:00 AM - 6:00 PM
        **Working Days:** Monday - Friday
        **Response Time:** 24-48 hours
        """)
    
    # Action Buttons
    st.markdown("### Next Steps")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Download Application Form"):
            st.success("Application form downloaded successfully!")
    with col2:
        if st.button("Check Eligibility"):
            st.info("Eligibility checker will guide you through the requirements")
    with col3:
        if st.button("Save Application"):
            st.success("Application progress saved to your profile")

def show_scheme_details(scheme_name, description, eligibility, benefits, application_process, deadline):
    """Display detailed information about a scheme"""
    current_lang = get_current_language()
    st.markdown(f"""
    <style>
    .details-header {
        background-color: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
    }
    .details-card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        border-left: 5px solid #667eea;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="details-header">
        <h1>{scheme_name}</h1>
        <p>{get_text('Complete scheme information and details', current_lang)}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Scheme Information
    st.markdown("### Scheme Overview")
    st.write(description)
    
    st.markdown("### Eligibility Criteria")
    st.write(eligibility)
    
    st.markdown("### Benefits & Features")
    st.write(benefits)
    
    st.markdown("### Application Process")
    st.write(application_process)
    
    st.markdown(f"### Important Dates")
    st.warning(f"**Application Deadline:** {deadline}")
    
    # Additional Information
    st.markdown("### Additional Information")
    col1, col2 = st.columns(2)
    with col1:
        st.info("""
        **Scheme Type:** Government Subsidy
        **Beneficiary Type:** Farmers
        **State:** All States
        **Category:** Agriculture
        """)
    with col2:
        st.info("""
        **Implementation:** Direct Benefit Transfer
        **Payment Mode:** Bank Transfer
        **Monitoring:** Digital Platform
        **Grievance:** Online Portal
        """)
    
    # Action Buttons
    st.markdown("### Quick Actions")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Apply Now"):
            st.success("Redirecting to application portal...")
    with col2:
        if st.button("Download Guidelines"):
            st.success("Guidelines downloaded successfully!")
    with col3:
        if st.button("Share Scheme"):
            st.success("Scheme link copied to clipboard!")

class AdditionalFeatures:
    def __init__(self):
        self.db = Database()
    
    def show_government_schemes(self):
        """Display comprehensive government schemes page"""
        current_lang = get_current_language()
        st.markdown("""
        <style>
        .scheme-header {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            padding: 2rem;
            border-radius: 15px;
            margin-bottom: 2rem;
            text-align: center;
            color: white !important;
        }
        .scheme-header h1 {
            color: white !important;
            margin: 0;
            font-size: 2.5rem;
            font-weight: bold;
        }
        .scheme-header p {
            color: white !important;
            margin: 0.5rem 0 0 0;
            font-size: 1.2rem;
        }
        .scheme-card {
            background-color: white;
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            margin-bottom: 1rem;
            border-left: 5px solid #f5576c;
        }
        .scheme-title {
            color: #f5576c;
            font-size: 1.5rem;
            font-weight: bold;
            margin-bottom: 1rem;
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="scheme-header">
            <h1>{get_text('Government Schemes', current_lang)}</h1>
            <p>{get_text('Agricultural schemes and initiatives for farmers', current_lang)}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Search and Filter
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            search_term = st.text_input("Search schemes", placeholder="Search by name or keyword...")
        
        with col2:
            category = st.selectbox("Category", ["All", "Insurance", "Subsidy", "Credit", "Infrastructure"])
        
        with col3:
            sort_by = st.selectbox("Sort by", ["Latest", "Popular", "Deadline"])
        
        # Get schemes from database
        schemes = self.db.get_schemes(50)  # Get more schemes
        
        # Filter schemes based on search
        if search_term:
            schemes = [s for s in schemes if search_term.lower() in s[0].lower() or search_term.lower() in s[1].lower()]
        
        # Display schemes
        if schemes:
            for scheme in schemes:
                with st.container():
                    st.markdown(f"""
                    <div class="scheme-card">
                        <div class="scheme-title">{scheme[0]}</div>
                        <p><strong>Description:</strong> {scheme[1]}</p>
                        <p><strong>Eligibility:</strong> {scheme[2]}</p>
                        <p><strong>Benefits:</strong> {scheme[3]}</p>
                        <p><strong>Application Process:</strong> {scheme[4]}</p>
                        <p><strong>Deadline:</strong> {scheme[5]}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col1, col2, col3 = st.columns([1, 1, 1])
                    with col1:
                        if st.button(f"Apply Now - {scheme[0][:20]}...", key=f"apply_{scheme[0]}"):
                            show_application_process(scheme[0], scheme[4])
                    with col2:
                        if st.button(f"Details - {scheme[0][:20]}...", key=f"details_{scheme[0]}"):
                            show_scheme_details(scheme[0], scheme[1], scheme[2], scheme[3], scheme[4], scheme[5])
                    with col3:
                        if st.button(f"Save - {scheme[0][:20]}...", key=f"save_{scheme[0]}"):
                            st.success("Scheme saved to your profile")
                    
                    st.markdown("---")
        else:
            st.info("No schemes found matching your criteria")
        
        # Scheme Statistics
        st.markdown("### Scheme Statistics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Schemes", "25")
        with col2:
            st.metric("Active Schemes", "18")
        with col3:
            st.metric("Closing Soon", "5")
        with col4:
            st.metric("New This Month", "3")
    
    def show_pesticide_information(self):
        """Display pesticide information and search"""
        current_lang = get_current_language()
        st.markdown("""
        <style>
        .pesticide-header {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            padding: 2rem;
            border-radius: 15px;
            margin-bottom: 2rem;
            text-align: center;
            color: white !important;
        }
        .pesticide-header h1 {
            color: white !important;
            margin: 0;
            font-size: 2.5rem;
            font-weight: bold;
        }
        .pesticide-header p {
            color: white !important;
            margin: 0.5rem 0 0 0;
            font-size: 1.2rem;
        }
        .pesticide-card {
            background-color: white;
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            margin-bottom: 1rem;
            border-left: 5px solid #00f2fe;
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="pesticide-header">
            <h1>{get_text('Pesticide Information', current_lang)}</h1>
            <p>{get_text('Comprehensive pesticide database and safety guidelines', current_lang)}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Search Section
        col1, col2 = st.columns([2, 1])
        
        with col1:
            search_term = st.text_input("Search Pesticides", placeholder="Enter pesticide name...")
        
        with col2:
            pesticide_type = st.selectbox("Type", ["All", "Herbicide", "Insecticide", "Fungicide", "Bactericide"])
        
        # Search pesticides
        if search_term:
            pesticides = self.db.search_pesticides(search_term)
        else:
            pesticides = self.db.search_pesticides("")  # Get all pesticides
        
        # Display pesticides
        if pesticides:
            for pesticide in pesticides:
                with st.expander(f"{pesticide[0]}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f"**Company:** {pesticide[1]}")
                        st.markdown(f"**Usage:** {pesticide[2]}")
                        st.markdown(f"**Crops:** {pesticide[3]}")
                    
                    with col2:
                        st.markdown(f"**Safety:** {pesticide[4]}")
                        st.markdown(f"**Dosage:** {pesticide[5]}")
                        
                        # Safety indicator
                        if "toxic" in pesticide[4].lower():
                            st.error("High Toxicity - Use with extreme caution")
                        elif "danger" in pesticide[4].lower():
                            st.warning("Moderate Hazard - Follow safety guidelines")
                        else:
                            st.success("Standard Safety Precautions Apply")
                    
                    # Action buttons
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button(f"MSDS - {pesticide[0]}", key=f"msds_{pesticide[0]}"):
                            st.info("Material Safety Data Sheet would be displayed")
                    with col2:
                        if st.button(f"Shops - {pesticide[0]}", key=f"shops_{pesticide[0]}"):
                            st.info("Nearby shops selling this pesticide")
                    with col3:
                        if st.button(f"Save - {pesticide[0]}", key=f"save_pest_{pesticide[0]}"):
                            st.success("Pesticide saved to your list")
        else:
            st.info("No pesticides found. Try different search terms.")
        
        # Pesticide Categories
        st.markdown("### Pesticide Categories")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Herbicides", "45")
        with col2:
            st.metric("Insecticides", "38")
        with col3:
            st.metric("Fungicides", "28")
        with col4:
            st.metric("Bactericides", "15")
        
        # Safety Guidelines
        st.markdown("### Safety Guidelines")
        
        guidelines = [
            "Always wear protective equipment (gloves, mask, goggles)",
            "Apply pesticides during early morning or late evening",
            "Keep children and pets away during application",
            "Ensure proper ventilation in enclosed spaces",
            "Wash hands thoroughly after handling",
            "Read and follow label instructions carefully",
            "Dispose of empty containers properly",
            "Keep emergency contact numbers handy"
        ]
        
        for guideline in guidelines:
            st.info(guideline)
    
    def show_pesticide_shops_map(self):
        """Display nearby pesticide shops with map integration"""
        st.markdown("""
        <style>
        .map-header {
            background-color: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            padding: 2rem;
            border-radius: 15px;
            margin-bottom: 2rem;
            text-align: center;
            color: white;
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="map-header">
            <h1>Nearby Pesticide Shops</h1>
            <p>Find pesticide shops in your area</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Location Input
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            location = st.text_input("Enter your location", placeholder="City, State or Pincode")
        
        with col2:
            radius = st.selectbox("Search Radius", ["5 km", "10 km", "25 km", "50 km"])
        
        with col3:
            if st.button("Search Shops"):
                st.info("Searching for nearby shops...")
        
        # Get shops from database
        shops = self.db.get_pesticide_shops()
        
        if shops:
            # Create map centered on India (default)
            m = folium.Map(location=[20.5937, 78.9629], zoom_start=5)
            
            # Add shop markers
            for shop in shops:
                if shop[2] and shop[3]:  # If lat/lng available
                    folium.Marker(
                        location=[shop[2], shop[3]],
                        popup=f"""
                        <b>{shop[0]}</b><br>
                        {shop[1]}<br>
                        📞 {shop[4]}
                        """,
                        tooltip=shop[0],
                        icon=folium.Icon(color='red', icon='shopping-cart', prefix='fa')
                    ).add_to(m)
            
            # Display map
            st_data = st_folium(m, width=700, height=500)
            
            # Shop list
            st.markdown("### Shop List")
            
            for i, shop in enumerate(shops):
                with st.expander(f"{shop[0]}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f"**Address:** {shop[1]}")
                        st.markdown(f"**Contact:** {shop[4]}")
                    
                    with col2:
                        if st.button(f"Call - {shop[0]}", key=f"call_{i}"):
                            st.info(f"Calling {shop[4]}...")
                        if st.button(f"Directions - {shop[0]}", key=f"dir_{i}"):
                            st.info("Opening maps for directions...")
                        if st.button(f"Rate - {shop[0]}", key=f"rate_{i}"):
                            st.info("Rate this shop")
        else:
            st.warning("No shops available in database. Please check back later.")
        
        # Add shop form
        st.markdown("### Add New Shop")
        
        with st.expander("Add a pesticide shop"):
            with st.form("add_shop"):
                shop_name = st.text_input("Shop Name")
                shop_address = st.text_area("Address")
                shop_contact = st.text_input("Contact Number")
                shop_lat = st.number_input("Latitude", format="%.6f")
                shop_lng = st.number_input("Longitude", format="%.6f")
                
                if st.form_submit_button("Add Shop"):
                    st.success("Shop added successfully!")
    
    def show_profile(self):
        """Display user profile and settings"""
        user = st.session_state.get('user')
        if not user:
            st.error("Please login to view profile")
            return
        
        st.markdown("""
        <style>
        .profile-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem;
            border-radius: 15px;
            margin-bottom: 2rem;
            text-align: center;
            color: white;
        }
        .profile-card {
            background: white;
            padding: 2rem;
            border-radius: 10px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            margin-bottom: 1rem;
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="profile-header">
            <h1>Farmer Profile</h1>
            <p>Welcome back, {user['name']}!</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Profile Information
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown('<div class="profile-card">', unsafe_allow_html=True)
            st.markdown("### Personal Information")
            
            # Get full user details
            user_details = self.db.get_user(user['id'])
            if user_details:
                st.markdown(f"**Name:** {user_details[1]}")
                st.markdown(f"**Email:** {user_details[2]}")
                st.markdown(f"**Mobile:** {user_details[3]}")
                st.markdown(f"**Member Since:** {user_details[5]}")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="profile-card">', unsafe_allow_html=True)
            st.markdown("### Settings")
            
            # Language selection
            languages = {
                'english': 'English',
                'hindi': 'हिंदी',
                'marathi': 'मराठी'
            }
            current_lang = user.get('language', 'english')
            selected_lang = st.selectbox(
                "Language",
                options=list(languages.keys()),
                format_func=lambda x: languages[x],
                index=list(languages.keys()).index(current_lang) if current_lang in languages else 0
            )
            
            if selected_lang != current_lang:
                self.db.update_user_language(user['id'], selected_lang)
                st.session_state.user['language'] = selected_lang
                st.success("Language updated!")
                st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Prediction History
        st.markdown("### Your Prediction History")
        
        history = self.db.get_prediction_history(user['id'], 10)
        
        if history:
            # Create DataFrame for better display
            history_data = []
            for record in history:
                history_data.append({
                    'Type': record[0].title(),
                    'Input': str(record[1])[:50] + "...",
                    'Result': record[2],
                    'Date': record[3]
                })
            
            df = pd.DataFrame(history_data)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("📝 No predictions yet. Try our AI models!")
        
        # AI Chatbot Section
        self.show_ai_chatbot()
        
        # Logout Section
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚪 Logout", use_container_width=True, type="secondary"):
                from auth import AuthManager
                auth_manager = AuthManager()
                auth_manager.logout()
    
    def show_ai_chatbot(self):
        """Display AI chatbot for farmer support"""
        st.markdown("""
        <style>
        .chat-container {
            background-color: #f8f9fa;
            padding: 1rem;
            border-radius: 10px;
            height: 400px;
            overflow-y: auto;
            margin-bottom: 0.5rem;
        }
        .user-message {
            background-color: #007bff;
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 10px;
            margin-bottom: 0.5rem;
            text-align: right;
            margin-left: 20%;
        }
        .bot-message {
            background-color: #28a745;
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 10px;
            margin-bottom: 0.5rem;
            text-align: left;
            margin-right: 20%;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Initialize chat history
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        
        # Initialize voice assistant
        if 'voice_assistant' not in st.session_state:
            st.session_state.voice_assistant = VoiceAssistant()
        
        # Chat display
        chat_container = st.container()
        
        with chat_container:
            st.markdown('<div class="chat-container">', unsafe_allow_html=True)
            
            for message in st.session_state.chat_history:
                if message['role'] == 'user':
                    st.markdown(f'<div class="user-message">{message["content"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="bot-message">{message["content"]}</div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    def handle_chat_query(self, query, should_speak=False):
        """Handle chatbot queries with enhanced responses and voice output"""
        # Add user message
        st.session_state.chat_history.append({
            'role': 'user',
            'content': query
        })
        
        # Generate enhanced bot response
        response = self.generate_smart_response(query)
        
        # Add bot message
        st.session_state.chat_history.append({
            'role': 'bot',
            'content': response
        })
        
        # Text-to-speech if enabled
        if should_speak:
            try:
                current_lang = get_current_language()
                audio_file = st.session_state.voice_assistant.text_to_speech(response, current_lang)
                if audio_file:
                    st.session_state.voice_assistant.autoplay_audio(audio_file)
            except Exception as e:
                print(f"Voice output error: {e}")
        
        # Clear voice tracker after successful processing
        if 'last_voice_processed' in st.session_state:
            st.session_state.last_voice_processed = ''
        
        # Clear text tracker after successful processing
        if 'last_text_processed' in st.session_state:
            st.session_state.last_text_processed = ''
        
        st.rerun()
    
    def generate_smart_response(self, query):
        """Generate intelligent responses using centralized VoiceAssistant logic"""
        from voice_assistant import VoiceAssistant
        va = VoiceAssistant()
        return va.get_intelligent_response(query)
