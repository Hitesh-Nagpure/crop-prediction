"""
Language utilities for AGRIVISION multi-language support
"""

# Voice assistant imports
from voice_assistant import VoiceAssistant, render_voice_controls as new_render_voice_controls, create_voice_input_component
import streamlit as st
import threading
import time

# Translation dictionary for the application
TRANSLATIONS = {
    'english': {
        # Navigation
        'Dashboard': 'Dashboard',
        'Crop Recommendation': 'Crop Recommendation',
        'Irrigation Recommendation': 'Irrigation Recommendation',
        'Yield Prediction': 'Yield Prediction',
        'Disease Detection': 'Disease Detection',
        'Government Schemes': 'Government Schemes',
        'Pesticide Information': 'Pesticide Information',
        'Nearby Pesticide Shops': 'Nearby Pesticide Shops',
        'Profile & AI Chatbot': 'Profile',
        'Admin Panel': 'Admin Panel',
        
        # Section Headers
        'Application Process': 'Application Process',
        'Application process will guide you through the steps': 'Application process will guide you through the steps',
        'Complete scheme information and details': 'Complete scheme information and details',
        'Agricultural schemes and initiatives for farmers': 'Agricultural schemes and initiatives for farmers',
        'Comprehensive pesticide database and safety guidelines': 'Comprehensive pesticide database and safety guidelines',
        
        # Common
        'Welcome': 'Welcome',
        'Login': 'Login',
        'Logout': 'Logout',
        'Signup': 'Signup',
        'Name': 'Name',
        'Email': 'Email',
        'Mobile': 'Mobile',
        'Password': 'Password',
        'Language': 'Language',
        'Settings': 'Settings',
        
        # Dashboard
        'AGRIVISION Dashboard': 'AGRIVISION Dashboard',
        'Smart Agriculture Decision Support System': 'Smart Agriculture Decision Support System',
        'Crops Analyzed': 'Crops Analyzed',
        'Water Saved': 'Water Saved',
        'Yield Increase': 'Yield Increase',
        'Farmers Helped': 'Farmers Helped',
        
        # Crop Recommendation
        'Crop Recommendation System': 'Crop Recommendation System',
        'AI-powered crop selection based on soil and environmental conditions': 'AI-powered crop selection based on soil and environmental conditions',
        'Soil Nutrients': 'Soil Nutrients',
        'Environmental Conditions': 'Environmental Conditions',
        'Nitrogen (N)': 'Nitrogen (N)',
        'Phosphorus (P)': 'Phosphorus (P)',
        'Potassium (K)': 'Potassium (K)',
        'Temperature': 'Temperature',
        'Humidity': 'Humidity',
        'pH Value': 'pH Value',
        'Rainfall': 'Rainfall',
        'Recommend Crop': 'Recommend Crop',
        'Recommended Crop': 'Recommended Crop',
        
        # Irrigation
        'Irrigation Recommendation System': 'Irrigation Recommendation System',
        'Smart irrigation decisions based on soil and crop conditions': 'Smart irrigation decisions based on soil and crop conditions',
        'Soil Conditions': 'Soil Conditions',
        'Environmental Factors': 'Environmental Factors',
        'Crop Information': 'Crop Information',
        'Soil Moisture': 'Soil Moisture',
        'Soil Type': 'Soil Type',
        'Crop Type': 'Crop Type',
        'Growth Stage': 'Growth Stage',
        'Check Irrigation Need': 'Check Irrigation Need',
        'Irrigation Required': 'Irrigation Required',
        'No Irrigation Needed': 'No Irrigation Needed',
        
        # Yield Prediction
        'Yield Prediction System': 'Yield Prediction System',
        'AI-powered crop yield prediction based on multiple factors': 'AI-powered crop yield prediction based on multiple factors',
        'Farm Details': 'Farm Details',
        'Area (hectares)': 'Area (hectares)',
        'State': 'State',
        'Crop Details': 'Crop Details',
        'Season': 'Season',
        'Crop Year': 'Crop Year',
        'Environmental Factors': 'Environmental Factors',
        'Predict Yield': 'Predict Yield',
        'Predicted Yield': 'Predicted Yield',
        
        # Profile
        'Farmer Profile': 'Farmer Profile',
        'Personal Information': 'Personal Information',
        'Member Since': 'Member Since',
        'Prediction History': 'Prediction History',
        'AI Agriculture Assistant': 'AI Agriculture Assistant',
        'Ask your agriculture question': 'Ask your agriculture question',
        'Send': 'Send',
        'Clear Chat': 'Clear Chat',
    },
    
    'hindi': {
        # Navigation
        'Dashboard': 'डैशबोर्ड',
        'Crop Recommendation': 'फसल सिफारिश',
        'Irrigation Recommendation': 'सिंचाई सिफारिश',
        'Yield Prediction': 'उपज भविष्यवाणी',
        'Disease Detection': 'रोग पहचान',
        'Government Schemes': 'सरकारी योजनाएं',
        'Pesticide Information': 'कीटनाशक जानकारी',
        'Nearby Pesticide Shops': 'नजदीकी कीटनाशक दुकान',
        'Profile & AI Chatbot': 'प्रोफाइल',
        'Admin Panel': 'व्यवस्थापक पैनल',
        
        # Section Headers
        'Application Process': 'आवेदन प्रक्रिया',
        'Application process will guide you through the steps': 'आवेदन प्रक्रिया आपको चरणों के माध्यम से मार्गदर्शन करेगी',
        'Complete scheme information and details': 'पूर्ण योजना जानकारी और विवरण',
        'Agricultural schemes and initiatives for farmers': 'किसानों के लिए कृषि योजनाएं और पहल',
        'Comprehensive pesticide database and safety guidelines': 'व्यापक कीटनाशक डेटाबेस और सुरक्षा दिशानिर्देश',
        
        # Common
        'Welcome': 'स्वागत है',
        'Login': 'लॉगिन',
        'Logout': 'लॉगआउट',
        'Signup': 'साइनअप',
        'Name': 'नाम',
        'Email': 'ईमेल',
        'Mobile': 'मोबाइल',
        'Password': 'पासवर्ड',
        'Language': 'भाषा',
        'Settings': 'सेटिंग्स',
        
        # Dashboard
        'AGRIVISION Dashboard': 'एग्रीविजन डैशबोर्ड',
        'Smart Agriculture Decision Support System': 'स्मार्ट एग्रीकल्चर डिसीजन सपोर्ट सिस्टम',
        'Crops Analyzed': 'विश्लेषित फसलें',
        'Water Saved': 'बचाया गया पानी',
        'Yield Increase': 'उपज में वृद्धि',
        'Farmers Helped': 'मदद पाए किसान',
        
        # Crop Recommendation
        'Crop Recommendation System': 'फसल सिफारिश प्रणाली',
        'AI-powered crop selection based on soil and environmental conditions': 'मिट्टी और पर्यावरणीय स्थितियों के आधार पर AI-संचालित फसल चयन',
        'Soil Nutrients': 'मिट्टी के पोषक तत्व',
        'Environmental Conditions': 'पर्यावरणीय स्थितियां',
        'Nitrogen (N)': 'नाइट्रोजन (N)',
        'Phosphorus (P)': 'फास्फोरस (P)',
        'Potassium (K)': 'पोटेशियम (K)',
        'Temperature': 'तापमान',
        'Humidity': 'नमी',
        'pH Value': 'pH मान',
        'Rainfall': 'वर्षा',
        'Recommend Crop': 'फसल की सिफारिश करें',
        'Recommended Crop': 'अनुशंसित फसल',
        
        # Irrigation
        'Irrigation Recommendation System': 'सिंचाई सिफारिश प्रणाली',
        'Smart irrigation decisions based on soil and crop conditions': 'मिट्टी और फसल की स्थितियों के आधार पर स्मार्ट सिंचाई निर्णय',
        'Soil Conditions': 'मिट्टी की स्थितियां',
        'Environmental Factors': 'पर्यावरणीय कारक',
        'Crop Information': 'फसल की जानकारी',
        'Soil Moisture': 'मिट्टी की नमी',
        'Soil Type': 'मिट्टी का प्रकार',
        'Crop Type': 'फसल का प्रकार',
        'Growth Stage': 'विकास चरण',
        'Check Irrigation Need': 'सिंचाई की आवश्यकता जांचें',
        'Irrigation Required': 'सिंचाई आवश्यक',
        'No Irrigation Needed': 'सिंचाई की आवश्यकता नहीं',
        
        # Yield Prediction
        'Yield Prediction System': 'उपज भविष्यवाणी प्रणाली',
        'AI-powered crop yield prediction based on multiple factors': 'कई कारकों के आधार पर AI-संचालित फसल उपज भविष्यवाणी',
        'Farm Details': 'खेत का विवरण',
        'Area (hectares)': 'क्षेत्रफल (हेक्टेयर)',
        'State': 'राज्य',
        'Crop Details': 'फसल का विवरण',
        'Season': 'सीजन',
        'Crop Year': 'फसल वर्ष',
        'Environmental Factors': 'पर्यावरणीय कारक',
        'Predict Yield': 'उपज का अनुमान लगाएं',
        'Predicted Yield': 'अनुमानित उपज',
        
        # Profile
        'Farmer Profile': 'किसान प्रोफाइल',
        'Personal Information': 'व्यक्तिगत जानकारी',
        'Member Since': 'सदस्य तब से',
        'Prediction History': 'भविष्यवाणी इतिहास',
        'AI Agriculture Assistant': 'AI कृषि सहायक',
        'Ask your agriculture question': 'अपना कृषि प्रश्न पूछें',
        'Send': 'भेजें',
        'Clear Chat': 'चैट साफ करें',
    },
    
    'marathi': {
        # Navigation
        'Dashboard': 'डॅशबोर्ड',
        'Crop Recommendation': 'पीक शिफारस',
        'Irrigation Recommendation': 'सिंचन शिफारस',
        'Yield Prediction': 'उत्पादन अंदाज',
        'Disease Detection': 'रोग ओळख',
        'Government Schemes': 'सरकारी योजना',
        'Pesticide Information': 'कीटकनाशक माहिती',
        'Nearby Pesticide Shops': 'जवळचे कीटकनाशक दुकाने',
        'Profile & AI Chatbot': 'प्रोफाइल',
        'Admin Panel': 'अॅडमिन पॅनेल',
        
        # Section Headers
        'Application Process': 'अर्ज प्रक्रिया',
        'Application process will guide you through the steps': 'अर्ज प्रक्रिया तुम्हाला टप्प्यांमधून मार्गदर्शन करेल',
        'Complete scheme information and details': 'पूर्ण योजना माहिती आणि तपशील',
        'Agricultural schemes and initiatives for farmers': 'शेतकऱ्यांसाठी कृषी योजना आणि उपक्रम',
        'Comprehensive pesticide database and safety guidelines': 'व्यापक कीटकनाशक डेटाबेस आणि सुरक्षा मार्गदर्शक तत्त्वे',
        
        # Common
        'Welcome': 'स्वागत',
        'Login': 'लॉगिन',
        'Logout': 'लॉगआउट',
        'Signup': 'साइनअप',
        'Name': 'नाव',
        'Email': 'ईमेल',
        'Mobile': 'मोबाइल',
        'Password': 'पासवर्ड',
        'Language': 'भाषा',
        'Settings': 'सेटिंग्स',
        
        # Dashboard
        'AGRIVISION Dashboard': 'एग्रीव्हिजन डॅशबोर्ड',
        'Smart Agriculture Decision Support System': 'स्मार्ट अॅग्रिकल्चर डिसीजन सपोर्ट सिस्टम',
        'Crops Analyzed': 'विश्लेषित पिके',
        'Water Saved': 'वाचलेले पाणी',
        'Yield Increase': 'उत्पादन वाढ',
        'Farmers Helped': 'मदत केलेले शेतकरी',
        
        # Crop Recommendation
        'Crop Recommendation System': 'पीक शिफारस प्रणाली',
        'AI-powered crop selection based on soil and environmental conditions': 'माती आणि पर्यावरणीय परिस्थितींच्या आधारावर AI-चालित पीक निवड',
        'Soil Nutrients': 'मातीतील पोषक घटक',
        'Environmental Conditions': 'पर्यावरणीय परिस्थिती',
        'Nitrogen (N)': 'नायट्रोजन (N)',
        'Phosphorus (P)': 'फॉस्फरस (P)',
        'Potassium (K)': 'पोटॅशियम (K)',
        'Temperature': 'तापमान',
        'Humidity': 'आर्द्रता',
        'pH Value': 'pH मूल्य',
        'Rainfall': 'पाऊस',
        'Recommend Crop': 'पीकाची शिफारस करा',
        'Recommended Crop': 'शिफारस केलेले पीक',
        
        # Irrigation
        'Irrigation Recommendation System': 'सिंचन शिफारस प्रणाली',
        'Smart irrigation decisions based on soil and crop conditions': 'माती आणि पिकाच्या परिस्थितींच्या आधारावर स्मार्ट सिंचन निर्णय',
        'Soil Conditions': 'मातीच्या परिस्थिती',
        'Environmental Factors': 'पर्यावरणीय घटक',
        'Crop Information': 'पिकाची माहिती',
        'Soil Moisture': 'मातीची आर्द्रता',
        'Soil Type': 'मातीचा प्रकार',
        'Crop Type': 'पिकाचा प्रकार',
        'Growth Stage': 'वाढीचा टप्पा',
        'Check Irrigation Need': 'सिंचनाची गरज तपासा',
        'Irrigation Required': 'सिंचन आवश्यक',
        'No Irrigation Needed': 'सिंचनाची गरज नाही',
        
        # Yield Prediction
        'Yield Prediction System': 'उत्पादन अंदाज प्रणाली',
        'AI-powered crop yield prediction based on multiple factors': 'अनेक घटकांच्या आधारावर AI-चालित पीक उत्पादन अंदाज',
        'Farm Details': 'शेताचे तपशील',
        'Area (hectares)': 'क्षेत्रफळ (हेक्टर)',
        'State': 'राज्य',
        'Crop Details': 'पिकाचे तपशील',
        'Season': 'हंगाम',
        'Crop Year': 'पीक वर्ष',
        'Environmental Factors': 'पर्यावरणीय घटक',
        'Predict Yield': 'उत्पादनाचा अंदाज लावा',
        'Predicted Yield': 'अंदाजित उत्पादन',
        
        # Profile
        'Farmer Profile': 'शेतकरी प्रोफाइल',
        'Personal Information': 'वैयक्तिक माहिती',
        'Member Since': 'सदस्य तेव्हापासून',
        'Prediction History': 'अंदाज इतिहास',
        'AI Agriculture Assistant': 'AI शेती सहाय्यक',
        'Ask your agriculture question': 'आपले शेती प्रश्न विचारा',
        'Send': 'पाठवा',
        'Clear Chat': 'चॅट साफ करा',
    }
}

def get_text(text_key, language='english'):
    """
    Get translated text for the given key and language
    """
    if language not in TRANSLATIONS:
        language = 'english'
    
    return TRANSLATIONS[language].get(text_key, text_key)

def get_current_language():
    """
    Get current user's language preference from session state
    """
    try:
        import streamlit as st
        user = st.session_state.get('user', {})
        return user.get('language', 'english')
    except:
        # Fallback if streamlit is not available
        return 'english'

def translate_ui_elements(element_dict, language=None):
    """
    Translate a dictionary of UI elements
    """
    if language is None:
        language = get_current_language()
    
    translated = {}
    for key, value in element_dict.items():
        if isinstance(value, str):
            translated[key] = get_text(value, language)
        else:
            translated[key] = value
    
    return translated

def get_language_display_name(language_code):
    """
    Get display name for language code
    """
    language_names = {
        'english': 'English',
        'hindi': 'हिंदी',
        'marathi': 'मराठी'
    }
    return language_names.get(language_code, language_code.title())

def render_voice_controls():
    """
    Render voice input and output controls for the chatbot
    
    Returns:
        tuple: (voice_input_text, should_speak_response)
    """
    # Use the new voice assistant controls
    voice_input_text, should_speak = new_render_voice_controls()
    return voice_input_text, should_speak

def speak_text_response(text, language='en'):
    """
    Speak text response using voice assistant
    
    Args:
        text: Text to speak
        language: Language code for speech
    """
    try:
        # Create voice assistant instance
        va = VoiceAssistant()
        
        # Map language codes to gTTS language codes
        lang_mapping = {
            'english': 'en',
            'hindi': 'hi',
            'marathi': 'mr'
        }
        
        tts_lang = lang_mapping.get(language, 'en')
        
        # Generate speech file
        audio_file = va.text_to_speech(text, tts_lang)
        
        if audio_file:
            # Auto-play the audio
            va.autoplay_audio(audio_file)
        
    except Exception as e:
        print(f"Error speaking text: {e}")

def is_voice_assistant_available():
    """
    Check if voice assistant is available and working
    
    Returns:
        bool: True if voice assistant is available
    """
    try:
        va = VoiceAssistant()
        return True  # New implementation doesn't have explicit availability check
    except:
        return False
