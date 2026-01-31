"""
Crop Disease Detection Module for AgriVision
Detects diseases from crop images using camera or upload
"""

import streamlit as st
import cv2
import numpy as np
from PIL import Image
import io
import base64
from pathlib import Path
import tempfile
import os
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors

class CropDiseaseDetector:
    """Handle crop disease detection from images"""
    
    def __init__(self):
        self.supported_crops = [
            'Tomato', 'Potato', 'Corn', 'Rice', 'Wheat', 
            'Apple', 'Grape', 'Pepper', 'Cotton', 'Sugarcane'
        ]
        
        # Disease database (you'll replace this with your ML model)
        self.disease_info = {
            'healthy': {
                'name': 'Healthy Plant',
                'severity': 'None',
                'symptoms': 'No visible symptoms',
                'treatment': 'Continue regular care and monitoring',
                'prevention': 'Maintain good agricultural practices'
            },
            'bacterial_spot': {
                'name': 'Bacterial Spot',
                'severity': 'Medium',
                'symptoms': 'Small, dark brown spots with yellow halos on leaves',
                'treatment': 'Apply copper-based bactericides, remove infected leaves',
                'prevention': 'Use disease-free seeds, practice crop rotation'
            },
            'early_blight': {
                'name': 'Early Blight',
                'severity': 'Medium',
                'symptoms': 'Dark brown concentric rings on older leaves',
                'treatment': 'Apply fungicides (chlorothalonil), remove infected parts',
                'prevention': 'Avoid overhead irrigation, mulch around plants'
            },
            'late_blight': {
                'name': 'Late Blight',
                'severity': 'High',
                'symptoms': 'Water-soaked spots, white mold on leaf undersides',
                'treatment': 'Apply fungicides immediately, destroy infected plants',
                'prevention': 'Use resistant varieties, ensure good air circulation'
            },
            'leaf_mold': {
                'name': 'Leaf Mold',
                'severity': 'Low',
                'symptoms': 'Yellow spots on upper leaf surface, olive-green mold below',
                'treatment': 'Improve ventilation, apply fungicides',
                'prevention': 'Reduce humidity, space plants properly'
            },
            'powdery_mildew': {
                'name': 'Powdery Mildew',
                'severity': 'Medium',
                'symptoms': 'White powdery coating on leaves and stems',
                'treatment': 'Apply sulfur-based fungicides, neem oil',
                'prevention': 'Ensure good air flow, avoid overcrowding'
            },
            'septoria_leaf_spot': {
                'name': 'Septoria Leaf Spot',
                'severity': 'Medium',
                'symptoms': 'Small circular spots with dark borders on leaves',
                'treatment': 'Remove infected leaves, apply copper fungicides',
                'prevention': 'Mulch soil, avoid wetting foliage'
            },
            'yellow_leaf_curl': {
                'name': 'Yellow Leaf Curl Virus',
                'severity': 'High',
                'symptoms': 'Yellowing, curling, and stunted growth',
                'treatment': 'Remove infected plants, control whiteflies',
                'prevention': 'Use virus-free seedlings, control insect vectors'
            },
            'mosaic_virus': {
                'name': 'Mosaic Virus',
                'severity': 'High',
                'symptoms': 'Mottled yellow and green patterns on leaves',
                'treatment': 'No cure - remove and destroy infected plants',
                'prevention': 'Control aphids, use resistant varieties'
            }
        }
    
    def preprocess_image(self, image):
        """
        Preprocess image for disease detection
        
        Args:
            image: PIL Image object
        
        Returns:
            numpy array: Preprocessed image
        """
        # Resize image
        img = image.resize((224, 224))
        
        # Convert to array
        img_array = np.array(img)
        
        # Normalize
        img_array = img_array / 255.0
        
        return img_array
    
    def analyze_image_features(self, image):
        """
        Analyze basic image features (placeholder for ML model)
        This is a simplified version - you should replace with your trained model
        
        Args:
            image: PIL Image object
        
        Returns:
            dict: Analysis results
        """
        # Convert to OpenCV format (use original PIL Image, not normalized array)
        img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Convert to HSV for better color analysis
        hsv = cv2.cvtColor(img_cv, cv2.COLOR_BGR2HSV)
        
        # Calculate color percentages (simplified disease indicators)
        # Brown/Yellow spots might indicate disease
        # Extended brown range for better detection
        lower_brown = np.array([8, 30, 30])
        upper_brown = np.array([25, 255, 200])
        brown_mask = cv2.inRange(hsv, lower_brown, upper_brown)
        brown_percentage = (np.sum(brown_mask > 0) / brown_mask.size) * 100
        
        # Dark spots (black/dark brown)
        lower_dark = np.array([0, 0, 0])
        upper_dark = np.array([180, 255, 30])
        dark_mask = cv2.inRange(hsv, lower_dark, upper_dark)
        dark_percentage = (np.sum(dark_mask > 0) / dark_mask.size) * 100
        
        # Yellowish areas (disease symptoms)
        lower_yellow = np.array([15, 50, 50])
        upper_yellow = np.array([35, 255, 255])
        yellow_mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
        yellow_percentage = (np.sum(yellow_mask > 0) / yellow_mask.size) * 100
        
        # Green (healthy vegetation)
        lower_green = np.array([40, 40, 40])
        upper_green = np.array([80, 255, 255])
        green_mask = cv2.inRange(hsv, lower_green, upper_green)
        green_percentage = (np.sum(green_mask > 0) / green_mask.size) * 100
        
        return {
            'brown_percentage': brown_percentage,
            'dark_percentage': dark_percentage,
            'yellow_percentage': yellow_percentage,
            'green_percentage': green_percentage
        }
    
    def predict_disease(self, image, crop_type='Unknown'):
        """
        Predict disease from image
        THIS IS A PLACEHOLDER - Replace with your actual ML model prediction
        
        Args:
            image: PIL Image object
            crop_type: Type of crop
        
        Returns:
            dict: Prediction results
        """
        # Analyze image features
        features = self.analyze_image_features(image)
        
        # Simple rule-based prediction (REPLACE WITH YOUR ML MODEL)
        confidence = 0.0
        predicted_disease = 'healthy'
        
        # Check for disease symptoms first (priority order)
        if features['brown_percentage'] > 8:
            predicted_disease = 'early_blight'
            confidence = min(features['brown_percentage'] * 6, 85)
        elif features['yellow_percentage'] > 10:
            predicted_disease = 'yellow_leaf_curl'
            confidence = min(features['yellow_percentage'] * 5, 82)
        elif features['dark_percentage'] > 5:
            predicted_disease = 'late_blight'
            confidence = min(features['dark_percentage'] * 7, 80)
        elif features['green_percentage'] > 70:
            predicted_disease = 'healthy'
            confidence = min(features['green_percentage'], 95)
        else:
            predicted_disease = 'healthy'
            confidence = 70
        
        # Get disease information
        disease_data = self.disease_info.get(predicted_disease, self.disease_info['healthy'])
        
        return {
            'disease': predicted_disease,
            'disease_name': disease_data['name'],
            'confidence': round(confidence, 2),
            'severity': disease_data['severity'],
            'symptoms': disease_data['symptoms'],
            'treatment': disease_data['treatment'],
            'prevention': disease_data['prevention'],
            'crop_type': crop_type,
            'features': features
        }
    
    def load_ml_model(self, model_path):
        """
        Load pre-trained ML model
        Add this when you have a trained model
        
        Args:
            model_path: Path to saved model file
        """
        try:
            # Example for TensorFlow/Keras:
            # from tensorflow import keras
            # self.model = keras.models.load_model(model_path)
            
            # Example for PyTorch:
            # import torch
            # self.model = torch.load(model_path)
            # self.model.eval()
            
            pass
        except Exception as e:
            st.error(f"Error loading model: {str(e)}")
    
    def save_detection_result(self, image, result, save_dir='detection_results'):
        """
        Save detection result for future training/analysis
        
        Args:
            image: PIL Image
            result: Detection result dict
            save_dir: Directory to save results
        """
        try:
            os.makedirs(save_dir, exist_ok=True)
            
            # Generate filename with timestamp
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{result['disease']}_{timestamp}.jpg"
            
            # Save image
            image.save(os.path.join(save_dir, filename))
            
            # Save metadata
            import json
            metadata_file = os.path.join(save_dir, f"{result['disease']}_{timestamp}.json")
            with open(metadata_file, 'w') as f:
                json.dump(result, f, indent=2)
            
            return True
        except Exception as e:
            st.error(f"Error saving result: {str(e)}")
            return False


def render_disease_detection_ui():
    """
    Render the complete disease detection UI
    """
    st.markdown("""
    <style>
    .disease-header {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
    }
    .disease-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        border-left: 5px solid #f5576c;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="disease-header">
        <h1>Crop Disease Detection</h1>
        <p>Upload an image or use your camera to detect crop diseases</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize detector
    if 'disease_detector' not in st.session_state:
        st.session_state.disease_detector = CropDiseaseDetector()
    
    detector = st.session_state.disease_detector
    
    # Crop type selection
    st.markdown("""
    <div class="disease-card">
        <h3>Select Crop Type</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    with col1:
        crop_type = st.selectbox(
            "Select Crop Type",
            detector.supported_crops,
            help="Select the type of crop in your image"
        )
    
    with col2:
        save_results = st.checkbox(
            "Save Results",
            value=False,
            help="Save detection results for analysis"
        )
    
    st.markdown("---")
    
    # Input method selection
    st.markdown("""
    <div class="disease-card">
        <h3>Choose Input Method</h3>
    </div>
    """, unsafe_allow_html=True)
    
    input_method = st.radio(
        "Choose input method:",
        ["Upload Image", "Use Camera"],
        horizontal=True
    )
    
    image = None
    
    if input_method == "Upload Image":
        uploaded_file = st.file_uploader(
            "Upload crop image",
            type=['jpg', 'jpeg', 'png'],
            help="Upload a clear image of the crop leaf or plant"
        )
        
        if uploaded_file:
            image = Image.open(uploaded_file)
            
    else:  # Camera input
        st.info("Click 'Capture Photo' to take a picture of your crop")
        
        # Use Streamlit's camera input (simpler alternative)
        camera_image = st.camera_input("Take a picture")
        
        if camera_image:
            image = Image.open(camera_image)
    
    # Display and analyze image
    if image:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📷 Uploaded Image")
            st.image(image, use_container_width=True)
        
        with col2:
            st.subheader("🔍 Analysis")
            
            with st.spinner("Analyzing image..."):
                # Predict disease
                result = detector.predict_disease(image, crop_type)
                
                # Display results
                st.markdown(f"### {result['disease_name']}")
                
                # Confidence meter
                confidence_color = "green" if result['confidence'] > 70 else "orange" if result['confidence'] > 50 else "red"
                st.markdown(f"""
                <div style="background-color: #f0f0f0; padding: 10px; border-radius: 5px;">
                    <strong>Confidence:</strong> 
                    <span style="color: {confidence_color}; font-size: 20px; font-weight: bold;">
                        {result['confidence']}%
                    </span>
                </div>
                """, unsafe_allow_html=True)
                
                # Severity badge
                severity_colors = {
                    'None': 'green',
                    'Low': 'blue',
                    'Medium': 'orange',
                    'High': 'red'
                }
                severity_color = severity_colors.get(result['severity'], 'gray')
                
                st.markdown(f"""
                <div style="background-color: {severity_color}; color: white; 
                            padding: 8px; border-radius: 5px; text-align: center; 
                            margin: 10px 0; font-weight: bold;">
                    Severity: {result['severity']}
                </div>
                """, unsafe_allow_html=True)
        
        # Detailed information
        st.markdown("---")
        st.subheader("Detailed Information")
        
        # Debug: Show what data we have
        if st.checkbox("Show Debug Info"):
            st.json({
                'Disease': result['disease'],
                'Disease Name': result['disease_name'],
                'Symptoms': result['symptoms'],
                'Treatment': result['treatment'],
                'Prevention': result['prevention']
            })
        
        tab1, tab2, tab3 = st.tabs(["Symptoms", "Treatment", "Prevention"])
        
        with tab1:
            st.markdown("### Symptoms")
            symptoms_text = result.get('symptoms', 'No symptoms information available')
            st.markdown(f"**{symptoms_text}**")
            st.info(symptoms_text)  # Add colored container for visibility
            
        with tab2:
            st.markdown("### Recommended Treatment")
            treatment_text = result.get('treatment', 'No treatment information available')
            st.markdown(f"**{treatment_text}**")
            st.success(treatment_text)  # Add colored container for visibility
            
        with tab3:
            st.markdown("### Prevention Measures")
            prevention_text = result.get('prevention', 'No prevention information available')
            st.markdown(f"**{prevention_text}**")
            st.warning(prevention_text)  # Add colored container for visibility
        
        # Save results
        if save_results:
            if st.button("Save Detection Result"):
                if detector.save_detection_result(image, result):
                    st.success("Result saved successfully!")
        
        # Download report
        st.markdown("---")
        if st.button("Generate PDF Report"):
            pdf_data = create_disease_report_pdf(image, result)
            if pdf_data:
                st.success("PDF report generated successfully!")
                st.download_button(
                    label="Download PDF Report",
                    data=pdf_data,
                    file_name=f"disease_report_{result['disease']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf"
                )
            else:
                st.error("Failed to generate PDF report. Please try again.")


def create_disease_report_pdf(image, result):
    """
    Create a comprehensive PDF report for disease detection
    
    Args:
        image: PIL Image object
        result: Detection result dictionary
    
    Returns:
        bytes: PDF data
    """
    try:
        # Create a buffer for the PDF
        buffer = io.BytesIO()
        
        # Create the PDF document
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        
        # Get styles
        styles = getSampleStyleSheet()
        
        # Create custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.darkblue,
            alignment=1  # Center
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            textColor=colors.darkgreen
        )
        
        # Build the story (content)
        story = []
        
        # Title
        story.append(Paragraph("Crop Disease Detection Report", title_style))
        story.append(Spacer(1, 20))
        
        # Report information
        report_data = [
            ['Report Date:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
            ['Crop Type:', result.get('crop_type', 'Unknown')],
            ['Detected Disease:', result['disease_name']],
            ['Confidence Level:', f"{result['confidence']}%"],
            ['Severity Level:', result.get('severity', 'Unknown')]
        ]
        
        # Create table for report info
        table = Table(report_data, colWidths=[2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(table)
        story.append(Spacer(1, 20))
        
        # Add the image
        story.append(Paragraph("Analyzed Image", heading_style))
        
        # Convert PIL Image to format suitable for ReportLab
        img_buffer = io.BytesIO()
        image.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        
        # Add image with proper sizing
        img = RLImage(img_buffer, width=4*inch, height=3*inch)
        story.append(img)
        story.append(Spacer(1, 20))
        
        # Symptoms section
        story.append(Paragraph("Symptoms", heading_style))
        symptoms_text = result.get('symptoms', 'No symptoms information available')
        story.append(Paragraph(symptoms_text, styles['Normal']))
        story.append(Spacer(1, 12))
        
        # Treatment section
        story.append(Paragraph("Recommended Treatment", heading_style))
        treatment_text = result.get('treatment', 'No treatment information available')
        story.append(Paragraph(treatment_text, styles['Normal']))
        story.append(Spacer(1, 12))
        
        # Prevention section
        story.append(Paragraph("Prevention Measures", heading_style))
        prevention_text = result.get('prevention', 'No prevention information available')
        story.append(Paragraph(prevention_text, styles['Normal']))
        story.append(Spacer(1, 12))
        
        # Technical details
        story.append(Paragraph("Technical Analysis Details", heading_style))
        
        if 'features' in result:
            feature_data = [
                ['Analysis Parameter', 'Value'],
                ['Green Coverage', f"{result['features'].get('green_percentage', 0):.2f}%"],
                ['Brown Spots', f"{result['features'].get('brown_percentage', 0):.2f}%"],
                ['Yellow Areas', f"{result['features'].get('yellow_percentage', 0):.2f}%"],
                ['Dark Spots', f"{result['features'].get('dark_percentage', 0):.2f}%"]
            ]
            
            feature_table = Table(feature_data, colWidths=[3*inch, 2*inch])
            feature_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(feature_table)
        
        story.append(Spacer(1, 20))
        
        # Footer
        story.append(Paragraph("Generated by AgriVision Crop Disease Detection System", styles['Normal']))
        story.append(Paragraph("For agricultural purposes only. Consult with agricultural experts for confirmation.", styles['Normal']))
        
        # Build the PDF
        doc.build(story)
        
        # Get the PDF data
        buffer.seek(0)
        return buffer.getvalue()
        
    except Exception as e:
        print(f"Error generating PDF: {str(e)}")
        return None


# For testing standalone
if __name__ == "__main__":
    create_simple_disease_page()
