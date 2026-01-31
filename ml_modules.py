import streamlit as st
import pandas as pd
import numpy as np
import joblib
import plotly.express as px
import plotly.graph_objects as go
from database import Database
from language_utils import get_text, get_current_language

class MLModules:
    def __init__(self):
        self.db = Database()
        
        # Load models
        try:
            self.crop_model = joblib.load("models/crop_recommendation_model.pkl")
            self.crop_encoder = joblib.load("models/crop_encoder.pkl")
            self.irrigation_model = joblib.load("models/irrigation_model.pkl")
            self.irrigation_preprocessor = joblib.load("models/irrigation_preprocessor.pkl")
            self.yield_model = joblib.load("models/yield_prediction_model.pkl")
            self.yield_preprocessor = joblib.load("models/yield_preprocessor.pkl")
        except Exception as e:
            st.error(f"Error loading models: {e}")
            self.crop_model = None
            self.crop_encoder = None
            self.irrigation_model = None
            self.irrigation_preprocessor = None
            self.yield_model = None
            self.yield_preprocessor = None
    
    def show_crop_recommendation(self):
        """Enhanced crop recommendation module"""
        current_lang = get_current_language()
        
        st.markdown("""
        <style>
        .module-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem;
            border-radius: 15px;
            margin-bottom: 2rem;
            text-align: center;
            color: white;
        }
        .input-section {
            background: white;
            padding: 2rem;
            border-radius: 10px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            margin-bottom: 2rem;
        }
        .result-section {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            padding: 2rem;
            border-radius: 10px;
            margin-bottom: 2rem;
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="module-header">
            <h1>{get_text('Crop Recommendation System', current_lang)}</h1>
            <p>{get_text('AI-powered crop selection based on soil and environmental conditions', current_lang)}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Input Section
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown('<div class="input-section">', unsafe_allow_html=True)
            st.markdown(f"### {get_text('Soil Nutrients', current_lang)}")
            
            N = st.slider(f"{get_text('Nitrogen (N)', current_lang)} - kg/ha", 0, 140, 50, help="Nitrogen content in soil")
            P = st.slider(f"{get_text('Phosphorus (P)', current_lang)} - kg/ha", 0, 145, 50, help="Phosphorus content in soil")
            K = st.slider(f"{get_text('Potassium (K)', current_lang)} - kg/ha", 0, 205, 50, help="Potassium content in soil")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="input-section">', unsafe_allow_html=True)
            st.markdown(f"### {get_text('Environmental Conditions', current_lang)}")
            
            temp = st.slider(f"{get_text('Temperature', current_lang)} (°C)", 0, 50, 25, help="Average temperature")
            humidity = st.slider(f"{get_text('Humidity', current_lang)} (%)", 0, 100, 65, help="Relative humidity")
            ph = st.slider(f"{get_text('pH Value', current_lang)}", 0.0, 14.0, 6.5, 0.1, help="Soil pH level")
            rainfall = st.slider(f"{get_text('Rainfall', current_lang)} (mm)", 0, 500, 100, help="Annual rainfall")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Prediction Button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button(f"🚀 {get_text('Recommend Crop', current_lang)}", width='stretch', type="primary"):
                if self.crop_model and self.crop_encoder:
                    try:
                        # Prepare input data
                        input_data = pd.DataFrame([[N, P, K, temp, humidity, ph, rainfall]])
                        
                        # Make prediction
                        crop_encoded = self.crop_model.predict(input_data)[0]
                        crop_name = self.crop_encoder.inverse_transform([crop_encoded])[0]
                        
                        # Save prediction
                        user = st.session_state.get('user')
                        if user:
                            self.db.save_prediction(
                                user['id'], 
                                'crop',
                                {'N': N, 'P': P, 'K': K, 'temp': temp, 'humidity': humidity, 'ph': ph, 'rainfall': rainfall},
                                crop_name
                            )
                        
                        # Display result
                        st.markdown(f"""
                        <div class="result-section">
                            <h2>{get_text('Recommended Crop', current_lang)}: {crop_name}</h2>
                            <p>Based on your soil and environmental conditions, {crop_name} is the most suitable crop for cultivation.</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Show crop details
                        self.show_crop_details(crop_name)
                        
                        # Show confidence scores
                        self.show_prediction_confidence(input_data, crop_name)
                        
                    except Exception as e:
                        st.error(f"Prediction error: {str(e)}")
                else:
                    st.error("Model not available")
        
        # Statistics Section
        st.markdown(f"### {get_text('Crop Statistics & Analysis', current_lang)}")
        self.show_crop_statistics()
    
    def show_crop_details(self, crop_name):
        """Show detailed information about recommended crop"""
        current_lang = get_current_language()
        
        crop_info = {
            'Rice': {
                'growing_season': 'Kharif (June-November)',
                'water_requirement': 'High (1200-1500mm)',
                'soil_type': 'Clay loam, well-drained',
                'fertilizer': 'NPK 120:60:40 kg/ha',
                'yield_potential': '4-6 tons/ha'
            },
            'Wheat': {
                'growing_season': 'Rabi (October-March)',
                'water_requirement': 'Medium (450-650mm)',
                'soil_type': 'Well-drained loamy soil',
                'fertilizer': 'NPK 150:60:40 kg/ha',
                'yield_potential': '3-4 tons/ha'
            },
            'Maize': {
                'growing_season': 'Kharif & Rabi',
                'water_requirement': 'Medium (500-800mm)',
                'soil_type': 'Well-drained fertile soil',
                'fertilizer': 'NPK 120:60:40 kg/ha',
                'yield_potential': '3-5 tons/ha'
            }
        }
        
        info = crop_info.get(crop_name, {
            'growing_season': 'Varies by region',
            'water_requirement': 'Medium',
            'soil_type': 'Well-drained soil',
            'fertilizer': 'As per soil test',
            'yield_potential': 'Depends on conditions'
        })
        
        # Display crop details with improved formatting
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); 
                    padding: 2rem; border-radius: 15px; margin: 1rem 0; 
                    box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
            <h3 style="color: #2c3e50; margin-bottom: 1.5rem; text-align: center; font-size: 1.5rem;">
                {get_text('Crop Information', current_lang)}
            </h3>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); 
                        gap: 1.5rem;">
        """, unsafe_allow_html=True)
        
        # Crop information cards
        crop_info_items = [
            ("", get_text('Growing Season', current_lang), info['growing_season'], "#28a745"),
            ("", get_text('Water Requirement', current_lang), info['water_requirement'], "#17a2b8"),
            ("", get_text('Soil Type', current_lang), info['soil_type'], "#6f42c1"),
            ("", get_text('Fertilizer', current_lang), info['fertilizer'], "#fd7e14"),
            ("", get_text('Yield Potential', current_lang), info['yield_potential'], "#20c997"),
            ("", get_text('Temperature Range', current_lang), "20-30°C", "#dc3545")
        ]
        
        for icon, label, value, color in crop_info_items:
            st.markdown(f"""
            <div style="background: white; padding: 1.5rem; border-radius: 10px; 
                       border-left: 5px solid {color}; box-shadow: 0 2px 8px rgba(0,0,0,0.05);
                       transition: transform 0.3s ease, box-shadow 0.3s ease;"
                   onmouseover="this.style.transform='translateY(-3px)'; this.style.boxShadow='0 4px 15px rgba(0,0,0,0.1)'"
                   onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 2px 8px rgba(0,0,0,0.05)'">
                <h4 style="color: {color}; margin-bottom: 0.5rem; font-size: 1.1rem; font-weight: 600;">
                    {icon} {label}
                </h4>
                <p style="color: #495057; font-size: 1rem; margin: 0; font-weight: 500;">
                    {value}
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div></div>", unsafe_allow_html=True)
    
    def show_prediction_confidence(self, input_data, predicted_crop):
        """Show prediction confidence scores"""
        try:
            # Get prediction probabilities if available
            if hasattr(self.crop_model, 'predict_proba'):
                probabilities = self.crop_model.predict_proba(input_data)[0]
                crop_names = self.crop_encoder.classes_
                
                # Create confidence chart
                fig = px.bar(
                    x=crop_names[:10],  # Show top 10
                    y=probabilities[:10],
                    title="Prediction Confidence Scores",
                    labels={'x': 'Crop', 'y': 'Confidence'},
                    color=probabilities[:10],
                    color_continuous_scale='Viridis'
                )
                st.plotly_chart(fig, width='stretch')
        except:
            pass
    
    def show_crop_statistics(self):
        """Show crop statistics and trends"""
        col1, col2 = st.columns(2)
        
        with col1:
            # Crop suitability heatmap
            crops = ['Rice', 'Wheat', 'Maize', 'Cotton', 'Pulses']
            conditions = ['Soil', 'Climate', 'Water', 'Fertilizer']
            
            # Sample data
            suitability_data = [
                [85, 90, 95, 80],  # Rice
                [80, 85, 70, 85],  # Wheat
                [75, 80, 75, 80],  # Maize
                [70, 75, 65, 75],  # Cotton
                [80, 70, 70, 85],  # Pulses
            ]
            
            fig = go.Figure(data=go.Heatmap(
                z=suitability_data,
                x=conditions,
                y=crops,
                colorscale='RdYlBu',
                hoverongaps=False
            ))
            fig.update_layout(title="Crop Suitability Analysis")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Historical crop performance
            years = ['2019', '2020', '2021', '2022', '2023']
            crop_performance = {
                'Rice': [4.2, 4.5, 4.8, 5.0, 5.2],
                'Wheat': [3.0, 3.2, 3.4, 3.6, 3.8],
                'Maize': [2.8, 3.0, 3.2, 3.4, 3.6]
            }
            
            fig = go.Figure()
            for crop, yields in crop_performance.items():
                fig.add_trace(go.Scatter(
                    x=years,
                    y=yields,
                    mode='lines+markers',
                    name=crop,
                    line=dict(width=3)
                ))
            
            fig.update_layout(
                title="Historical Crop Yield Trends",
                xaxis_title="Year",
                yaxis_title="Yield (tons/ha)"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    def show_irrigation_recommendation(self):
        """Enhanced irrigation recommendation module"""
        current_lang = get_current_language()
        
        st.markdown("""
        <style>
        .module-header {
            background: linear-gradient(135deg, #00b4db 0%, #0083b0 100%);
            padding: 2rem;
            border-radius: 15px;
            margin-bottom: 2rem;
            text-align: center;
            color: white;
        }
        .input-section {
            background: white;
            padding: 2rem;
            border-radius: 10px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            margin-bottom: 2rem;
        }
        .result-section {
            background: linear-gradient(135deg, #56ccf2 0%, #2f80ed 100%);
            color: white;
            padding: 2rem;
            border-radius: 10px;
            margin-bottom: 2rem;
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="module-header">
            <h1>{get_text('Irrigation Recommendation System', current_lang)}</h1>
            <p>{get_text('Smart irrigation decisions based on soil and crop conditions', current_lang)}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Input Section
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown('<div class="input-section">', unsafe_allow_html=True)
            st.markdown(f"### {get_text('Soil Conditions', current_lang)}")
            
            soil_moisture = st.slider(f"{get_text('Soil Moisture', current_lang)} (%)", 0, 100, 60, help="Current soil moisture level")
            soil_type = st.selectbox(f"{get_text('Soil Type', current_lang)}", 
                ["Sandy", "Loamy", "Clay", "Silt", "Peat"], 
                help="Type of soil in your field"
            )
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="input-section">', unsafe_allow_html=True)
            st.markdown(f"### {get_text('Environmental Factors', current_lang)}")
            
            temp = st.slider(f"{get_text('Temperature', current_lang)} (°C)", 10, 45, 25, help="Current temperature")
            rainfall = st.number_input(f"Recent {get_text('Rainfall', current_lang)} (mm)", 0, 200, 10, help="Rainfall in last 7 days")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Crop Information
        st.markdown('<div class="input-section">', unsafe_allow_html=True)
        st.markdown(f"### {get_text('Crop Information', current_lang)}")
        
        col1, col2 = st.columns(2)
        with col1:
            crop = st.selectbox(f"{get_text('Crop Type', current_lang)}", 
                ["Rice", "Maize", "Wheat", "Cotton", "Sugarcane", "Pulses", "Vegetables"],
                help="Current crop in field"
            )
        with col2:
            growth_stage = st.selectbox(f"{get_text('Growth Stage', current_lang)}", 
                ["Early", "Mid", "Late", "Harvest"],
                help="Current growth stage of crop"
            )
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Prediction Button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button(f"🚀 {get_text('Check Irrigation Need', current_lang)}", width='stretch', type="primary"):
                if self.irrigation_model and self.irrigation_preprocessor:
                    try:
                        # Prepare input data
                        input_df = pd.DataFrame([{
                            "soil_moisture": soil_moisture,
                            "Temperature": temp,
                            "Humidity": 70,  # Default value
                            "Rainfall": rainfall,
                            "soil_type": soil_type,
                            "Crop": crop,
                            "growth_stage": growth_stage,
                            "water_required_mm": 0  # Default value
                        }])
                        
                        # Preprocess and predict
                        input_processed = self.irrigation_preprocessor.transform(input_df)
                        probabilities = self.irrigation_model.predict_proba(input_processed)[0]
                        
                        # Use threshold for decision
                        threshold = 0.15
                        result = 1 if probabilities[1] >= threshold else 0
                        
                        # Save prediction
                        user = st.session_state.get('user')
                        if user:
                            self.db.save_prediction(
                                user['id'],
                                'irrigation',
                                {
                                    'soil_moisture': soil_moisture,
                                    'temperature': temp,
                                    'rainfall': rainfall,
                                    'soil_type': soil_type,
                                    'crop': crop,
                                    'growth_stage': growth_stage
                                },
                                "Irrigation Required" if result == 1 else "No Irrigation Needed"
                            )
                        
                        # Display result
                        if result == 1:
                            st.markdown(f"""
                            <div class="result-section" style="background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);">
                                <h2>🚨 {get_text('Irrigation Required', current_lang)}</h2>
                                <p>Current conditions indicate that irrigation is needed for optimal crop growth.</p>
                                <p><strong>Confidence:</strong> {probabilities[1]:.1%}</p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Show irrigation recommendations
                            self.show_irrigation_recommendations(crop, growth_stage, soil_type, current_lang)
                        else:
                            st.markdown(f"""
                            <div class="result-section" style="background: linear-gradient(135deg, #56ab2f 0%, #a8e063 100%);">
                                <h2>✅ {get_text('No Irrigation Needed', current_lang)}</h2>
                                <p>Current soil moisture and environmental conditions are adequate.</p>
                                <p><strong>{get_text('Irrigation Probability', current_lang)}:</strong> {probabilities[1]:.1%}</p>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        # Show moisture trend
                        self.show_moisture_trend(soil_moisture)
                        
                    except Exception as e:
                        st.error(f"Prediction error: {str(e)}")
                else:
                    st.error("Model not available")
        
        # Statistics Section
        st.markdown(f"### {get_text('Irrigation Statistics', current_lang)}")
        self.show_irrigation_statistics()
    
    def show_irrigation_recommendations(self, crop, growth_stage, soil_type, current_lang):
        """Show specific irrigation recommendations"""
        st.markdown(f"#### 💡 {get_text('Irrigation Recommendations', current_lang)}")
        
        recommendations = {
            'Rice': {
                'Early': 'Maintain 2-5 cm standing water',
                'Mid': 'Maintain 5-10 cm standing water',
                'Late': 'Gradually reduce water before harvest'
            },
            'Wheat': {
                'Early': 'Light irrigation at crown root initiation',
                'Mid': 'Critical irrigation at flowering stage',
                'Late': 'Stop irrigation 2 weeks before harvest'
            },
            'Maize': {
                'Early': 'Irrigate at knee-high stage',
                'Mid': 'Critical irrigation at tasseling',
                'Late': 'Reduce irrigation during grain filling'
            }
        }
        
        crop_rec = recommendations.get(crop, {
            'Early': 'Light irrigation as needed',
            'Mid': 'Regular irrigation during growth',
            'Late': 'Reduce irrigation before harvest'
        })
        
        recommendation = crop_rec.get(growth_stage, 'Monitor soil moisture regularly')
        
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"**Recommendation:** {recommendation}")
            st.info(f"**Soil Type:** {soil_type} soil requires specific irrigation scheduling")
        
        with col2:
            st.info(f"**Best Time:** Early morning or late evening")
            st.info(f"**Method:** Drip irrigation recommended for water conservation")
    
    def show_moisture_trend(self, current_moisture):
        """Show soil moisture trend"""
        # Generate sample trend data
        days = list(range(1, 8))
        moisture_trend = [current_moisture - i*2 + np.random.randint(-5, 5) for i in range(7)]
        moisture_trend = [max(0, min(100, m)) for m in moisture_trend]  # Clamp between 0-100
        
        fig = px.line(
            x=days,
            y=moisture_trend,
            title="7-Day Soil Moisture Trend",
            labels={'x': 'Days Ago', 'y': 'Soil Moisture (%)'}
        )
        fig.add_hline(y=30, line_dash="dash", line_color="red", annotation_text="Critical Level")
        fig.add_hline(y=50, line_dash="dash", line_color="orange", annotation_text="Moderate Level")
        st.plotly_chart(fig, use_container_width=True)
    
    def show_irrigation_statistics(self):
        """Show irrigation statistics and charts"""
        col1, col2 = st.columns(2)
        
        with col1:
            # Irrigation vs yield correlation
            irrigation_levels = ['Low', 'Medium', 'High', 'Optimal']
            yields = [2.5, 3.8, 4.2, 5.1]
            
            fig = px.bar(
                x=irrigation_levels,
                y=yields,
                title="Irrigation Level vs Crop Yield",
                labels={'x': 'Irrigation Level', 'y': 'Yield (tons/ha)'},
                color=yields,
                color_continuous_scale='Blues'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Water usage efficiency
            crops = ['Rice', 'Wheat', 'Maize', 'Cotton']
            water_efficiency = [2.5, 8.5, 6.2, 4.1]  # kg yield per cubic meter water
            
            fig = px.funnel(
                y=crops,
                x=water_efficiency,
                title="Water Use Efficiency by Crop",
                labels={'y': 'Crop', 'x': 'Yield (kg) per m³ water'}
            )
            st.plotly_chart(fig, use_container_width=True)
    
    def show_yield_prediction(self):
        """Enhanced yield prediction module"""
        current_lang = get_current_language()
        
        st.markdown("""
        <style>
        .module-header {
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            padding: 2rem;
            border-radius: 15px;
            margin-bottom: 2rem;
            text-align: center;
            color: white;
        }
        .input-section {
            background: white;
            padding: 2rem;
            border-radius: 10px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            margin-bottom: 2rem;
        }
        .result-section {
            background: linear-gradient(135deg, #56ab2f 0%, #a8e063 100%);
            color: white;
            padding: 2rem;
            border-radius: 10px;
            margin-bottom: 2rem;
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="module-header">
            <h1>{get_text('Yield Prediction System', current_lang)}</h1>
            <p>{get_text('AI-powered crop yield prediction based on multiple factors', current_lang)}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Input Section
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown('<div class="input-section">', unsafe_allow_html=True)
            st.markdown(f"### {get_text('Farm Details', current_lang)}")
            
            area = st.number_input(f"{get_text('Area (hectares)', current_lang)}", 0.1, 100.0, 5.0, 0.1, help="Total cultivation area")
            state = st.selectbox(f"{get_text('State', current_lang)}", 
                ["Andhra Pradesh", "Bihar", "Gujarat", "Haryana", "Karnataka", "Maharashtra", 
                 "Punjab", "Tamil Nadu", "Uttar Pradesh", "West Bengal"],
                help="Select your state"
            )
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="input-section">', unsafe_allow_html=True)
            st.markdown(f"### {get_text('Crop Details', current_lang)}")
            
            crop_type = st.selectbox(f"{get_text('Crop Type', current_lang)}", 
                ["Rice", "Wheat", "Maize", "Cotton", "Pulses", "Sugarcane"],
                help="Type of crop being cultivated"
            )
            season = st.selectbox(f"{get_text('Season', current_lang)}", 
                ["Kharif", "Rabi", "Summer", "Whole Year"],
                help="Cultivation season"
            )
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="input-section">', unsafe_allow_html=True)
            st.markdown(f"### {get_text('Environmental Factors', current_lang)}")
            
            rainfall = st.number_input(f"{get_text('Rainfall', current_lang)} (mm)", 0, 1000, 500, 10, help="Expected rainfall during season")
            fertilizer = st.number_input(f"Fertilizer (kg/ha)", 0, 500, 100, 5, help="Fertilizer usage per hectare")
            crop_year = st.number_input(f"{get_text('Crop Year', current_lang)}", 2020, 2030, 2024, help="Cultivation year")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Prediction Button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button(f"🚀 {get_text('Predict Yield', current_lang)}", width='stretch', type="primary"):
                if self.yield_model and self.yield_preprocessor:
                    try:
                        # Prepare input data
                        input_df = pd.DataFrame([{
                            "index": 0,
                            "State": state,
                            "Crop": crop_type,
                            "Crop_Year": crop_year,
                            "Season": season,
                            "Area": area,
                            "Yield": 0  # Placeholder
                        }])
                        
                        # Preprocess and predict
                        input_processed = self.yield_preprocessor.transform(input_df.drop('Yield', axis=1))
                        predicted_yield = self.yield_model.predict(input_processed)[0]
                        
                        # Save prediction
                        user = st.session_state.get('user')
                        if user:
                            self.db.save_prediction(
                                user['id'],
                                'yield',
                                {
                                    'area': area,
                                    'state': state,
                                    'crop': crop_type,
                                    'season': season,
                                    'rainfall': rainfall,
                                    'fertilizer': fertilizer,
                                    'year': crop_year
                                },
                                f"{predicted_yield:.2f} tons/ha"
                            )
                        
                        # Display result with improved formatting
                        total_yield = predicted_yield * area
                        
                        st.markdown(f"""
                        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                    padding: 2rem; border-radius: 15px; margin: 1rem 0; 
                                    box-shadow: 0 8px 25px rgba(0,0,0,0.15); color: white;">
                            <h2 style="text-align: center; margin-bottom: 2rem; font-size: 1.8rem;">
                                🎯 {get_text('Predicted Yield Analysis', current_lang)}
                            </h2>
                            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
                                        gap: 1.5rem; text-align: center;">
                                <div style="background: rgba(255,255,255,0.1); padding: 1.5rem; border-radius: 10px; 
                                           backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.2);">
                                    <h3 style="font-size: 2rem; margin: 0; font-weight: bold;">{predicted_yield:.2f}</h3>
                                    <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">{get_text('Yield per hectare (tons)', current_lang)}</p>
                                </div>
                                <div style="background: rgba(255,255,255,0.1); padding: 1.5rem; border-radius: 10px; 
                                           backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.2);">
                                    <h3 style="font-size: 2rem; margin: 0; font-weight: bold;">{total_yield:.2f}</h3>
                                    <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">{get_text('Total production (tons)', current_lang)}</p>
                                </div>
                                <div style="background: rgba(255,255,255,0.1); padding: 1.5rem; border-radius: 10px; 
                                           backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.2);">
                                    <h3 style="font-size: 2rem; margin: 0; font-weight: bold;">{area:.1f}</h3>
                                    <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">{get_text('Cultivation area (ha)', current_lang)}</p>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Show yield insights
                        self.show_yield_insights(predicted_yield, crop_type, area, rainfall, fertilizer, current_lang)
                        
                        # Show yield comparison
                        self.show_yield_comparison(crop_type, predicted_yield, current_lang)
                        
                    except Exception as e:
                        st.error(f"Prediction error: {str(e)}")
                else:
                    st.error("Model not available")
        
        # Statistics Section
        st.markdown(f"### {get_text('Yield Statistics & Trends', current_lang)}")
        self.show_yield_statistics()
    
    def show_yield_insights(self, predicted_yield, crop_type, area, rainfall, fertilizer, current_lang):
        """Show detailed yield insights with improved formatting"""
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); 
                    padding: 2rem; border-radius: 15px; margin: 1rem 0; 
                    box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
            <h3 style="color: #2c3e50; margin-bottom: 1.5rem; text-align: center; font-size: 1.5rem;">
                {get_text('Yield Insights', current_lang)}
            </h3>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); 
                        gap: 1.5rem;">
        """, unsafe_allow_html=True)
        
        # Calculate efficiency metrics
        water_efficiency = predicted_yield / max(rainfall, 1) * 1000  # kg per mm rainfall
        fertilizer_efficiency = predicted_yield / max(fertilizer, 1)  # kg yield per kg fertilizer
        
        # Calculate profit estimate (sample rates)
        crop_rates = {
            'Rice': 2000, 'Wheat': 2200, 'Maize': 1800, 
            'Cotton': 6000, 'Pulses': 4000, 'Sugarcane': 3000
        }
        rate = crop_rates.get(crop_type, 2000)
        estimated_revenue = predicted_yield * area * rate
        
        # Metric cards
        metrics = [
            ("Yield/ha", f"{predicted_yield:.2f} tons", "#28a745"),
            ("Water Efficiency", f"{water_efficiency:.2f} kg/mm", "#17a2b8"),
            ("Fertilizer Efficiency", f"{fertilizer_efficiency:.2f} kg/kg", "#fd7e14"),
            ("Est. Revenue", f"₹{estimated_revenue:,.0f}", "#20c997")
        ]
        
        for icon, value, color in metrics:
            st.markdown(f"""
            <div style="background: white; padding: 1.5rem; border-radius: 10px; 
                       border-left: 5px solid {color}; box-shadow: 0 2px 8px rgba(0,0,0,0.05);
                       text-align: center; transition: transform 0.3s ease;"
                   onmouseover="this.style.transform='translateY(-5px)'"
                   onmouseout="this.style.transform='translateY(0)'">
                <h4 style="color: {color}; margin-bottom: 0.5rem; font-size: 1.1rem;">
                    {icon}
                </h4>
                <p style="color: #495057; font-size: 1.2rem; margin: 0; font-weight: bold;">
                    {value}
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div></div>", unsafe_allow_html=True)
        
        # Recommendations
        st.markdown(f"#### {get_text('Recommendations', current_lang)}")
        
        recommendations = []
        
        if predicted_yield < 2:
            recommendations.append("Yield is below average. Consider improving soil fertility and irrigation.")
        elif predicted_yield < 4:
            recommendations.append("Yield is moderate. Optimize fertilizer and water management.")
        else:
            recommendations.append("Good yield potential. Maintain current practices.")
        
        if rainfall < 300:
            recommendations.append("Low rainfall expected. Ensure proper irrigation facilities.")
        
        if fertilizer < 50:
            recommendations.append("Low fertilizer usage. Consider soil testing and balanced fertilization.")
        
        for rec in recommendations:
            st.info(rec)
    
    def show_yield_comparison(self, crop_type, predicted_yield, current_lang):
        """Show yield comparison with averages"""
        # Average yields (sample data)
        avg_yields = {
            'Rice': 3.5, 'Wheat': 3.0, 'Maize': 2.8,
            'Cotton': 1.5, 'Pulses': 1.2, 'Sugarcane': 70.0
        }
        
        avg_yield = avg_yields.get(crop_type, 3.0)
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name=f"{get_text('Your Predicted Yield', current_lang)}",
            x=[crop_type],
            y=[predicted_yield],
            marker_color='lightblue'
        ))
        
        fig.add_trace(go.Bar(
            name=f"{get_text('National Average', current_lang)}",
            x=[crop_type],
            y=[avg_yield],
            marker_color='darkblue'
        ))
        
        fig.update_layout(
            title=f"{get_text('Yield Comparison', current_lang)}",
            yaxis_title=f"{get_text('Yield (tons/ha)', current_lang)}",
            barmode='group'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def show_yield_statistics(self):
        """Show yield statistics and trends"""
        current_lang = get_current_language()
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Yield trends over years
            years = ['2018', '2019', '2020', '2021', '2022', '2023']
            yield_trend = [2.8, 3.0, 3.2, 3.4, 3.5, 3.7]
            
            fig = px.line(
                x=years,
                y=yield_trend,
                title=f"{get_text('National Yield Trend (Last 6 Years)', current_lang)}",
                labels={'x': f"{get_text('Year', current_lang)}", 'y': f"{get_text('Average Yield (tons/ha)', current_lang)}"},
                markers=True
            )
            fig.update_traces(line_color='green', line_width=3)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # State-wise yield comparison
            states = ['Punjab', 'Haryana', 'Uttar Pradesh', 'Maharashtra', 'Gujarat']
            state_yields = [4.2, 3.8, 3.2, 2.8, 2.5]
            
            fig = px.bar(
                x=states,
                y=state_yields,
                title="State-wise Average Yield",
                labels={'x': 'State', 'y': 'Yield (tons/ha)'},
                color=state_yields,
                color_continuous_scale='Viridis'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Factor impact analysis
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Rainfall impact
            rainfall_ranges = ['<300mm', '300-500mm', '500-700mm', '>700mm']
            yield_by_rainfall = [2.1, 3.2, 3.8, 3.5]
            
            fig = px.bar(
                x=rainfall_ranges,
                y=yield_by_rainfall,
                title="Rainfall Impact on Yield",
                labels={'x': 'Rainfall Range', 'y': 'Yield (tons/ha)'}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Area impact
            area_ranges = ['<2ha', '2-5ha', '5-10ha', '>10ha']
            yield_by_area = [2.8, 3.2, 3.5, 3.8]
            
            fig = px.bar(
                x=area_ranges,
                y=yield_by_area,
                title="Farm Size Impact on Yield",
                labels={'x': 'Farm Size', 'y': 'Yield (tons/ha)'}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col3:
            # Season impact
            seasons = ['Kharif', 'Rabi', 'Summer']
            yield_by_season = [3.5, 3.2, 2.8]
            
            fig = px.pie(
                values=yield_by_season,
                names=seasons,
                title="Average Yield by Season"
            )
            st.plotly_chart(fig, use_container_width=True)
