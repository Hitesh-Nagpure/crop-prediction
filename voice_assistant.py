"""
Voice Assistant Module for AgriVision
Enhanced with intelligent response generation and database integration
"""

import streamlit as st
import speech_recognition as sr
from gtts import gTTS
import os
import tempfile
import base64
import json
import sqlite3
import requests
from datetime import datetime
from database import Database

class VoiceAssistant:
    """Handle voice input and output for the chatbot with intelligent responses"""
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.temp_dir = tempfile.gettempdir()
        self.db = Database()
        
        # Agricultural knowledge base for intelligent responses
        self.agricultural_responses = {
            'crop': {
                'wheat': {
                    'general': "For wheat cultivation, I recommend sowing in October-November. Use certified seeds, apply balanced NPK fertilizer, and irrigate at critical stages. Yield potential: 3-4 quintals per acre.",
                    'irrigation': "Wheat needs irrigation at crown root initiation (21-25 days), tillering (45-50 days), flowering (70-80 days), and grain filling (90-100 days). Stop irrigation 15 days before harvest.",
                    'fertilizer': "Apply NPK 150:60:40 kg/ha. Apply all P&K + 50% N basal, remaining N in 2 splits at crown root and boot leaf stages. Add micronutrients as needed.",
                    'pest': "For wheat aphids, use Imidacloprid or acetamiprid. For rust, use Propiconazole or Tebuconazole. Follow IPM practices and ETL levels.",
                    'harvest': "Harvest when grains turn golden yellow and moisture content is 12-14%. Use proper combine harvester and store at 12% moisture.",
                },
                'rice': {
                    'general': "For rice cultivation, I recommend Kharif season sowing with first monsoon rains. Use high-yielding varieties and maintain proper water management.",
                    'irrigation': "Rice needs continuous flooding (2-5 cm) during vegetative stage. Use Alternate Wetting & Drying (AWD) to save 25-30% water.",
                    'fertilizer': "Apply NPK 120:60:40 kg/ha. Apply 50% N + all P&K basal, remaining N in 2 equal splits at tillering and panicle initiation.",
                    'pest': "For rice stem borer, use Cartap Hydrochloride. For leaf folder, Chlorpyrifos. For blast disease, Tricyclazole. Follow IPM practices.",
                    'harvest': "Drain field 15 days before harvest. Harvest when 80% grains turn golden. Use proper combine harvester and dry to 14% moisture.",
                },
                'cotton': {
                    'general': "For cotton cultivation, I recommend Kharif season sowing with Bt cotton varieties. Maintain proper spacing and pest management.",
                    'irrigation': "Cotton needs irrigation at critical stages: square formation, flowering, and boll development. Use drip irrigation for efficiency.",
                    'fertilizer': "Apply NPK 120:60:40 kg/ha. Apply 25% N + all P&K basal, remaining N in 3 splits at square formation, flowering, and boll development.",
                    'pest': "For cotton bollworms, use Spinosad or Chlorantraniliprole. For aphids, Imidacloprid. For whitefly, Thiamethoxam. Follow IPM.",
                    'harvest': "Pick cotton in 2-3 rounds when 60% bolls open. Use proper picking methods to maintain fiber quality.",
                }
            },
            'farming': {
                'general': "For successful farming, I recommend an integrated approach combining traditional wisdom with modern technology for sustainable agriculture.",
                'sustainability': "Practice crop rotation, organic farming, water conservation, and biodiversity for long-term farm health.",
                'technology': "Use precision agriculture, IoT sensors, drones, and AI for data-driven decision making.",
                'organic': "Consider organic certification for premium prices and export markets. Use FYM and vermicompost.",
                'soil': "Maintain soil health through regular testing and organic matter addition. Use Soil Health Cards."
            }
        }
    
    def get_intelligent_response(self, query):
        """Generate intelligent agricultural response based on query, database, and optional OpenAI API"""
        query_lower = query.lower()
        
        # 1. Try OpenAI if API Key is available
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            try:
                from openai import OpenAI
                client = OpenAI(api_key=api_key)
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are Agrivision, an expert agricultural AI assistant for Indian farmers. Provide helpful, accurate, and concise farming advice in a friendly tone."},
                        {"role": "user", "content": query}
                    ],
                    max_tokens=300
                )
                return response.choices[0].message.content
            except Exception as e:
                st.error(f"OpenAI Error: {e}")
                # Fall through to pattern matching
        
        # 2. Try Ollama if local server is running
        try:
            ollama_url = "http://localhost:11434/api/generate"
            payload = {
                "model": "llama3", # Defaulting to llama3, can be changed
                "prompt": f"You are Agrivision, an expert agricultural AI assistant. User asks: {query}",
                "stream": False
            }
            response = requests.post(ollama_url, json=payload, timeout=10)
            if response.status_code == 200:
                return response.json().get('response', '')
        except Exception:
            # If Ollama is not running, silently fall through
            pass
        
        # 3. Search Database for schemes, pesticides, or shops
        db_response = self._search_database(query_lower)
        if db_response:
            return db_response
        
        # 3. Hardcoded Pattern Matching
        crop_keywords = {
            'wheat': ['wheat', 'gehu', 'gandum'],
            'rice': ['rice', 'chawal', 'dhan'],
            'cotton': ['cotton', 'kapas', 'kapaas'],
            'maize': ['maize', 'makka', 'corn']
        }
        
        topic_keywords = {
            'irrigation': ['irrigate', 'water', 'irrigation', 'pani', 'jal'],
            'fertilizer': ['fertilizer', 'khad', 'manure', 'npk'],
            'pest': ['pest', 'insect', 'disease', 'pesticide', 'keet', 'bimari'],
            'harvest': ['harvest', 'katni', 'katai'],
        }
        
        # Check for crop + topic
        for crop, keywords in crop_keywords.items():
            if any(k in query_lower for k in keywords):
                crop_data = self.agricultural_responses['crop'].get(crop, {})
                for topic, t_keywords in topic_keywords.items():
                    if any(tk in query_lower for tk in t_keywords):
                        if topic in crop_data:
                            return f"🌾 **{crop.title()} {topic.title()}**: {crop_data[topic]}"
                
                return f"🌾 **{crop.title()} Information**: {crop_data.get('general', 'I recommend certified seeds and proper soil testing.')}"

        # Check for general farming topics
        for topic, keywords in topic_keywords.items():
            if any(k in query_lower for k in keywords):
                return f"🌱 **Farming Tip**: {self.agricultural_responses['farming'].get(topic, self.agricultural_responses['farming']['general'])}"

        # 4. Final Fallback
        return self._get_default_response(query)

    def _search_database(self, query):
        """Search database for schemes, pesticides, or shops"""
        # Search Schemes
        if any(w in query for w in ['scheme', 'government', 'yojana', 'help', 'support']):
            schemes = self.db.get_schemes(limit=3)
            if schemes:
                res = "🏛️ **Top Government Schemes for You:**\n\n"
                for s in schemes:
                    res += f"🔹 **{s[0]}**: {s[1][:100]}...\n"
                return res
        
        # Search Pesticides
        if any(w in query for w in ['pesticide', 'medicine', 'spray', 'fungicide', 'herbicide']):
            # Try to extract pesticide name if possible, otherwise search general
            pesticides = self.db.search_pesticides("")
            if pesticides:
                res = "🧪 **Commonly Used Pesticides:**\n\n"
                for p in pesticides[:3]:
                    res += f"🔹 **{p[0]}**: {p[2]}\n"
                return res
        
        # Search Shops
        if any(w in query for w in ['shop', 'store', 'market', 'buy']):
            shops = self.db.get_pesticide_shops()
            if shops:
                res = "🏠 **Nearby Pesticide Shops:**\n\n"
                for s in shops[:3]:
                    res += f"🔹 **{s[1]}**: {s[3]}\n"
                return res
        
        return None

    def _get_default_response(self, query):
        """Get default response when no specific topic is matched"""
        if any(keyword in query.lower() for keyword in ['hello', 'hi', 'help']):
            return "👋 Namaste! I'm Agrivision AI. I can help with: 🌾 Crops, 💧 Irrigation, 🌿 Pest control, 🏛️ Schemes, and more. Ask me anything!"
        
        return f"🤖 I'm here to support your farming! I don't have a specific answer for '{query}' yet, but you can try our AI prediction models in the sidebar for personalized recommendations on crops, irrigation, and yield."

    def speech_to_text(self, audio_data=None, language='en-IN'):
        """Convert speech to text using speech_recognition library"""
        try:
            if audio_data:
                text = self.recognizer.recognize_google(audio_data, language=language)
                return text
            else:
                with sr.Microphone() as source:
                    st.info("🎤 Listening... Speak now!")
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                
                st.info("🔄 Processing...")
                text = self.recognizer.recognize_google(audio, language=language)
                return text
        except Exception as e:
            return f"❌ Error: {str(e)}"

    def text_to_speech(self, text, language='en', slow=False):
        """Convert text to speech using gTTS"""
        try:
            tts = gTTS(text=text, lang=language, slow=slow)
            audio_file = os.path.join(self.temp_dir, "response_audio.mp3")
            tts.save(audio_file)
            return audio_file
        except Exception as e:
            st.error(f"Speech error: {e}")
            return None

    def autoplay_audio(self, file_path):
        """Auto-play audio file in Streamlit"""
        try:
            with open(file_path, "rb") as audio_file:
                audio_bytes = audio_file.read()
            audio_base64 = base64.b64encode(audio_bytes).decode()
            audio_html = f'<audio autoplay><source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3"></audio>'
            st.markdown(audio_html, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Playback error: {e}")

def render_voice_controls():
    """Render voice control UI and Chat History"""
    st.markdown("---")
    st.subheader("🎙️ AgriVision AI Voice Assistant")
    
    if 'voice_assistant' not in st.session_state:
        st.session_state.voice_assistant = VoiceAssistant()
        if 'voice_chat_history' not in st.session_state:
            st.session_state.voice_chat_history = []
    
    va = st.session_state.voice_assistant
    
    # 1. Action Buttons for Voice
    col1, col2, col3 = st.columns([2, 1, 1])
    voice_input_text = None
    
    with col1:
        if st.button("🎤 Click to Speak (Voice Input)", use_container_width=True, type="primary"):
            voice_input_text = va.speech_to_text()
            if voice_input_text and not voice_input_text.startswith('❌'):
                st.session_state.voice_chat_history.append({"role": "user", "content": voice_input_text})
                response = va.get_intelligent_response(voice_input_text)
                st.session_state.voice_chat_history.append({"role": "bot", "content": response})
                st.session_state.last_response = response
                st.rerun()
            elif voice_input_text and voice_input_text.startswith('❌'):
                st.error(voice_input_text)
                
    with col2:
        should_speak = st.checkbox("🔊 Speak Response", value=True)
    
    with col3:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.voice_chat_history = []
            st.session_state.last_response = None
            st.rerun()

    # 2. Text Input Option
    user_query = st.chat_input("Type your farming question here...")
    if user_query:
        st.session_state.voice_chat_history.append({"role": "user", "content": user_query})
        response = va.get_intelligent_response(user_query)
        st.session_state.voice_chat_history.append({"role": "bot", "content": response})
        st.session_state.last_response = response
        st.rerun()

    # 3. Display Chat History
    st.markdown("### 💬 Chat History")
    for msg in st.session_state.voice_chat_history:
        if msg["role"] == "user":
            st.chat_message("user").write(msg["content"])
        else:
            st.chat_message("assistant", avatar="🤖").write(msg["content"])

    # 4. Handle Voice Output for latest response
    if 'last_response' in st.session_state and st.session_state.last_response and should_speak:
        audio = va.text_to_speech(st.session_state.last_response)
        if audio:
            va.autoplay_audio(audio)
        st.session_state.last_response = None # Prevent repeating

    return voice_input_text, should_speak

def create_voice_input_component():
    """Browser-based voice input (fallback)"""
    return "<div>Voice recognition requires microphone permissions.</div>"
