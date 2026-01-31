import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from database import Database
import joblib
from language_utils import get_text, get_current_language

class Dashboard:
    def __init__(self):
        self.db = Database()
        
        # Load models for preview
        try:
            self.crop_model = joblib.load("models/crop_recommendation_model.pkl")
            self.crop_encoder = joblib.load("models/crop_encoder.pkl")
            self.irrigation_model = joblib.load("models/irrigation_model.pkl")
            self.yield_model = joblib.load("models/yield_prediction_model.pkl")
        except:
            self.crop_model = None
            self.crop_encoder = None
            self.irrigation_model = None
            self.yield_model = None
    
    def show_dashboard(self):
        """Display main dashboard"""
        current_lang = get_current_language()
        
        st.markdown("""
        <style>
        .dashboard-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem;
            border-radius: 15px;
            margin-bottom: 2rem;
            text-align: center;
            color: white;
        }
        .metric-card {
            background: white;
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            margin-bottom: 1rem;
            transition: transform 0.3s ease;
        }
        .metric-card:hover {
            transform: translateY(-5px);
        }
        .preview-card {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            padding: 1.5rem;
            border-radius: 10px;
            margin-bottom: 1rem;
        }
        .scheme-card {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            color: white;
            padding: 1.5rem;
            border-radius: 10px;
            margin-bottom: 1rem;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Header
        st.markdown(f"""
        <div class="dashboard-header">
            <h1>{get_text('AGRIVISION Dashboard', current_lang)}</h1>
            <p>{get_text('Smart Agriculture Decision Support System', current_lang)}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Quick Stats
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h3>{get_text('Crops Analyzed', current_lang)}</h3>
                <h2>22+</h2>
                <p>Different crop varieties</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <h3>{get_text('Water Saved', current_lang)}</h3>
                <h2>30%</h2>
                <p>Through smart irrigation</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <h3>{get_text('Yield Increase', current_lang)}</h3>
                <h2>25%</h2>
                <p>Average improvement</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <h3>{get_text('Farmers Helped', current_lang)}</h3>
                <h2>1000+</h2>
                <p>Across the country</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Model Previews Section
        st.markdown("## AI Model Previews")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            self.show_crop_preview()
        
        with col2:
            self.show_irrigation_preview()
        
        with col3:
            self.show_yield_preview()
        
        # Charts and Analytics
        st.markdown("## Agricultural Analytics")
        self.show_analytics_charts()
    
    def show_crop_preview(self):
        """Show crop recommendation preview"""
        st.markdown("""
        <div class="preview-card">
            <h4>Crop Recommendation</h4>
        </div>
        """, unsafe_allow_html=True)
        
        # Get recent prediction or show demo
        user = st.session_state.get('user')
        if user:
            history = self.db.get_prediction_history(user['id'], 1)
            if history and history[0][0] == 'crop':
                st.success(f"Last Recommended: **{history[0][2]}**")
            else:
                st.info("No recent predictions")
        
        # Quick demo prediction
        with st.expander("Quick Demo"):
            N = st.slider("Nitrogen (N)", 0, 140, 50)
            P = st.slider("Phosphorus (P)", 0, 145, 50)
            K = st.slider("Potassium (K)", 0, 205, 50)
            
            if st.button("🔮 Predict Crop"):
                if self.crop_model and self.crop_encoder:
                    try:
                        data = pd.DataFrame([[N, P, K, 25, 65, 6.5, 100]])
                        crop_encoded = self.crop_model.predict(data)[0]
                        crop_name = self.crop_encoder.inverse_transform([crop_encoded])[0]
                        st.success(f"Recommended: **{crop_name}**")
                    except:
                        st.error("Model not available")
                else:
                    st.info("Model loading...")
    
    def show_irrigation_preview(self):
        """Show irrigation recommendation preview"""
        st.markdown("""
        <div class="preview-card">
            <h4>Irrigation Recommendation</h4>
        </div>
        """, unsafe_allow_html=True)
        
        # Show current irrigation status
        soil_moisture = st.slider("Soil Moisture (%)", 0, 100, 60)
        
        if soil_moisture < 30:
            st.error("Irrigation Required")
            st.warning("Soil moisture is critically low")
        elif soil_moisture < 50:
            st.warning("Consider Irrigation")
            st.info("Soil moisture is moderate")
        else:
            st.success("No Irrigation Needed")
            st.info("Soil moisture is adequate")
        
        # Visual indicator
        fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = soil_moisture,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Soil Moisture"},
            delta = {'reference': 50},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 30], 'color': "lightcoral"},
                    {'range': [30, 50], 'color': "lightyellow"},
                    {'range': [50, 100], 'color': "lightgreen"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 30
                }
            }
        ))
        
        st.plotly_chart(fig, width='stretch')
    
    def show_yield_preview(self):
        """Show yield prediction preview"""
        st.markdown("""
        <div class="preview-card">
            <h4>Yield Prediction</h4>
        </div>
        """, unsafe_allow_html=True)
        
        # Sample yield prediction
        area = st.slider("Area (hectares)", 1, 100, 10)
        rainfall = st.slider("Rainfall (mm)", 0, 500, 200)
        
        # Simple yield calculation (demo)
        base_yield = 2.5
        area_factor = min(area / 10, 2)
        rainfall_factor = min(rainfall / 200, 1.5)
        predicted_yield = base_yield * area_factor * rainfall_factor
        
        st.success(f"Predicted Yield: **{predicted_yield:.2f}** tons/hectare")
        
        # Yield trend chart
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
        yield_trend = [2.1, 2.3, 2.5, 2.8, 3.0, predicted_yield]
        
        fig = px.line(
            x=months, 
            y=yield_trend,
            title="Yield Trend (Last 6 Months)",
            labels={'x': 'Month', 'y': 'Yield (tons/hectare)'}
        )
        fig.update_traces(line_color='green', line_width=3)
        st.plotly_chart(fig, width='stretch')
    
    def show_government_schemes(self):
        """Display government schemes"""
        schemes = self.db.get_schemes(3)
        
        for scheme in schemes:
            with st.expander(f"{scheme[0]}"):
                st.markdown(f"**Description:** {scheme[1]}")
                st.markdown(f"**Eligibility:** {scheme[2]}")
                st.markdown(f"**Benefits:** {scheme[3]}")
                st.markdown(f"**Application Process:** {scheme[4]}")
                st.markdown(f"**Deadline:** {scheme[5]}")
        
        if st.button("View All Schemes"):
            st.session_state.page = "schemes"
            st.rerun()
    
    def show_pesticide_section(self):
        """Display pesticide information"""
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Search Pesticides")
            search_term = st.text_input("Enter pesticide name", placeholder="e.g., Roundup")
            
            if search_term:
                pesticides = self.db.search_pesticides(search_term)
                if pesticides:
                    for pesticide in pesticides:
                        with st.expander(f"{pesticide[0]}"):
                            st.markdown(f"**Company:** {pesticide[1]}")
                            st.markdown(f"**Usage:** {pesticide[2]}")
                            st.markdown(f"**Crops:** {pesticide[3]}")
                            st.markdown(f"**Safety:** {pesticide[4]}")
                            st.markdown(f"**Dosage:** {pesticide[5]}")
                else:
                    st.info("No pesticides found")
        
        with col2:
            st.markdown("### Nearby Pesticide Shops")
            shops = self.db.get_pesticide_shops()
            
            if shops:
                for shop in shops[:3]:  # Show first 3 shops
                    st.markdown(f"**{shop[0]}**")
                    st.markdown(f"{shop[1]}")
                    st.markdown(f"{shop[4]}")
                    st.markdown("---")
            else:
                st.info("No shops available in database")
            
            if st.button("View on Map"):
                st.info("Map integration coming soon!")
    
    def show_analytics_charts(self):
        """Display agricultural analytics charts"""
        col1, col2 = st.columns(2)
        
        with col1:
            # Crop distribution chart
            crops = ['Rice', 'Wheat', 'Maize', 'Cotton', 'Pulses']
            production = [120, 100, 80, 60, 40]
            
            fig = px.pie(
                values=production,
                names=crops,
                title="Crop Production Distribution",
                color_discrete_sequence=px.colors.sequential.Aggrnyl
            )
            st.plotly_chart(fig, width='stretch')
        
        with col2:
            # Seasonal rainfall chart
            seasons = ['Winter', 'Summer', 'Monsoon', 'Autumn']
            rainfall = [50, 150, 400, 100]
            
            fig = px.bar(
                x=seasons,
                y=rainfall,
                title="Seasonal Rainfall Pattern",
                labels={'x': 'Season', 'y': 'Rainfall (mm)'},
                color=rainfall,
                color_continuous_scale='Blues'
            )
            st.plotly_chart(fig, width='stretch')
        
        # Environmental factors chart
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Temperature trend
            temps = [20, 22, 25, 28, 30, 32, 30, 28, 25, 22, 20, 18]
            fig = px.line(
                x=range(1, 13),
                y=temps,
                title="Monthly Temperature Trend",
                labels={'x': 'Month', 'y': 'Temperature (°C)'}
            )
            st.plotly_chart(fig, width='stretch')
        
        with col2:
            # Soil nutrients
            nutrients = ['Nitrogen', 'Phosphorus', 'Potassium']
            values = [65, 45, 80]
            
            fig = go.Figure(data=[
                go.Bar(name='Current Level', x=nutrients, y=values),
                go.Bar(name='Optimal Level', x=nutrients, y=[80, 60, 90])
            ])
            fig.update_layout(title="Soil Nutrient Status", barmode='group')
            st.plotly_chart(fig, width='stretch')
        
        with col3:
            # Crop suitability radar
            categories = ['Soil', 'Climate', 'Water', 'Fertilizer', 'Pest Control']
            values = [85, 70, 60, 75, 80]
            
            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=categories,
                fill='toself',
                name='Current Farm'
            ))
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 100]
                    )),
                showlegend=True,
                title="Farm Suitability Analysis"
            )
            st.plotly_chart(fig, width='stretch')
