import streamlit as st
import pandas as pd
import plotly.express as px
from database import Database
import hashlib
from datetime import datetime

class AdminPanel:
    def __init__(self):
        self.db = Database()
        
        # Admin credentials (in production, use proper authentication)
        self.admin_username = "admin"
        self.admin_password_hash = hashlib.sha256("admin123".encode()).hexdigest()
    
    def show_admin_login(self):
        """Display admin login page"""
        st.markdown("""
        <style>
        .admin-login {
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
            st.markdown('<div class="admin-login">', unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.markdown('<h1 style="text-align: center; color: white;">Admin Panel</h1>', unsafe_allow_html=True)
                
                with st.form("admin_login"):
                    username = st.text_input("Username", placeholder="Enter admin username")
                    password = st.text_input("Password", type="password", placeholder="Enter admin password")
                    
                    if st.form_submit_button("Login", use_container_width=True):
                        if username == self.admin_username and hashlib.sha256(password.encode()).hexdigest() == self.admin_password_hash:
                            st.session_state.admin_authenticated = True
                            st.success("Login successful!")
                            st.rerun()
                        else:
                            st.error("Invalid credentials")
                
                st.markdown('<p style="text-align: center; color: white; font-size: 0.8rem;">Default: admin / admin123</p>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    def show_admin_dashboard(self):
        """Display admin dashboard"""
        if not st.session_state.get('admin_authenticated'):
            self.show_admin_login()
            return
        
        st.markdown("""
        <style>
        .admin-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem;
            border-radius: 15px;
            margin-bottom: 2rem;
            text-align: center;
            color: white;
        }
        .admin-card {
            background: white;
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            margin-bottom: 1rem;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Header
        col1, col2, col3 = st.columns([1, 3, 1])
        with col2:
            st.markdown("""
            <div class="admin-header">
                <h1>Admin Dashboard</h1>
                <p>AGRIVISION System Management</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Logout button
        if st.button("Logout", key="admin_logout"):
            st.session_state.admin_authenticated = False
            st.rerun()
        
        # Navigation
        menu = st.sidebar.selectbox(
            "Admin Menu",
            ["Dashboard", "Farmers Management", "Model Management", "Schemes Management", 
             "Pesticide Management", "Shop Management", "Analytics", "Settings"]
        )
        
        if menu == "Dashboard":
            self.show_admin_overview()
        elif menu == "Farmers Management":
            self.show_farmers_management()
        elif menu == "Model Management":
            self.show_model_management()
        elif menu == "Schemes Management":
            self.show_schemes_management()
        elif menu == "Pesticide Management":
            self.show_pesticide_management()
        elif menu == "Shop Management":
            self.show_shop_management()
        elif menu == "Analytics":
            self.show_analytics()
        elif menu == "Settings":
            self.show_settings()
    
    def show_admin_overview(self):
        """Show admin dashboard overview"""
        st.markdown("### System Overview")
        
        # Key Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Farmers", "1,247", "+12%")
        with col2:
            st.metric("Predictions Today", "89", "+5%")
        with col3:
            st.metric("Active Schemes", "18", "+2")
        with col4:
            st.metric("Pesticides Listed", "126", "+8")
        
        # Recent Activity
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Recent Predictions")
            # Sample data - in real app, fetch from database
            recent_predictions = [
                {"User": "Farmer1", "Type": "Crop", "Result": "Rice", "Time": "2 mins ago"},
                {"User": "Farmer2", "Type": "Irrigation", "Result": "Required", "Time": "5 mins ago"},
                {"User": "Farmer3", "Type": "Yield", "Result": "3.2 tons/ha", "Time": "10 mins ago"},
            ]
            
            df_predictions = pd.DataFrame(recent_predictions)
            st.dataframe(df_predictions, use_container_width=True)
        
        with col2:
            st.markdown("#### 🆕 New Registrations")
            new_farmers = [
                {"Name": "Ramesh Kumar", "Email": "ramesh@email.com", "Joined": "Today"},
                {"Name": "Sunita Devi", "Email": "sunita@email.com", "Joined": "Yesterday"},
                {"Name": "Mohammed Ali", "Email": "mohammed@email.com", "Joined": "2 days ago"},
            ]
            
            df_farmers = pd.DataFrame(new_farmers)
            st.dataframe(df_farmers, use_container_width=True)
        
        # System Health
        st.markdown("#### System Health")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.success("All Models Operational")
            st.info("Database: Connected")
        
        with col2:
            st.success("API Response: <200ms")
            st.info("Storage: 67% used")
        
        with col3:
            st.warning("High Traffic Alert")
            st.info("Last Backup: 2 hours ago")
    
    def show_farmers_management(self):
        """Show farmers management interface"""
        st.markdown("### Farmers Management")
        
        # Search and Filter
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            search_farmers = st.text_input("Search farmers", placeholder="Search by name, email, or mobile...")
        
        with col2:
            filter_status = st.selectbox("Status", ["All", "Active", "Inactive"])
        
        with col3:
            if st.button("Refresh"):
                st.rerun()
        
        # Farmers list (sample data)
        farmers_data = [
            {"ID": 1, "Name": "Ramesh Kumar", "Email": "ramesh@email.com", "Mobile": "9876543210", "Joined": "2024-01-15", "Predictions": 45, "Status": "Active"},
            {"ID": 2, "Name": "Sunita Devi", "Email": "sunita@email.com", "Mobile": "9876543211", "Joined": "2024-01-14", "Predictions": 23, "Status": "Active"},
            {"ID": 3, "Name": "Mohammed Ali", "Email": "mohammed@email.com", "Mobile": "9876543212", "Joined": "2024-01-13", "Predictions": 67, "Status": "Active"},
        ]
        
        df_farmers = pd.DataFrame(farmers_data)
        
        # Display with actions
        for index, farmer in df_farmers.iterrows():
            with st.expander(f"{farmer['Name']} - {farmer['Email']}"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown(f"**Mobile:** {farmer['Mobile']}")
                    st.markdown(f"**Joined:** {farmer['Joined']}")
                
                with col2:
                    st.markdown(f"**Predictions:** {farmer['Predictions']}")
                    st.markdown(f"**Status:** {farmer['Status']}")
                
                with col3:
                    if st.button(f"View Details", key=f"view_{farmer['ID']}"):
                        st.info("Detailed analytics would be shown")
                    if st.button(f"Deactivate", key=f"deactivate_{farmer['ID']}"):
                        st.warning("Farmer deactivated")
        
        # Export functionality
        if st.button("Export Farmers Data"):
            st.success("Farmers data exported successfully!")
    
    def show_model_management(self):
        """Show ML model management interface"""
        st.markdown("### Model Management")
        
        # Model Status
        models = [
            {"Name": "Crop Recommendation", "Version": "2.1.0", "Accuracy": "92%", "Status": "Active", "Last Updated": "2024-01-10"},
            {"Name": "Irrigation Recommendation", "Version": "1.8.0", "Accuracy": "88%", "Status": "Active", "Last Updated": "2024-01-08"},
            {"Name": "Yield Prediction", "Version": "3.2.0", "Accuracy": "85%", "Status": "Active", "Last Updated": "2024-01-12"},
        ]
        
        for model in models:
            with st.expander(f"{model['Name']}"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Version", model['Version'])
                    st.metric("Accuracy", model['Accuracy'])
                
                with col2:
                    st.metric("Last Updated", model['Last Updated'])
                    st.metric("Status", model['Status'])
                
                with col3:
                    if st.button(f"Retrain", key=f"retrain_{model['Name']}"):
                        st.info("Model retraining initiated...")
                    if st.button(f"Analytics", key=f"analytics_{model['Name']}"):
                        st.info("Model analytics would be displayed")
        
        # Model Performance Charts
        st.markdown("#### Model Performance Trends")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Accuracy trend
            dates = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
            accuracy = [85, 87, 88, 90, 91, 92]
            
            fig = px.line(
                x=dates,
                y=accuracy,
                title="Model Accuracy Trend",
                labels={'x': 'Month', 'y': 'Accuracy (%)'}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Prediction volume
            prediction_types = ['Crop', 'Irrigation', 'Yield']
            volumes = [450, 320, 280]
            
            fig = px.pie(
                values=volumes,
                names=prediction_types,
                title="Prediction Volume Distribution"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    def show_schemes_management(self):
        """Show government schemes management"""
        st.markdown("### Government Schemes Management")
        
        # Add new scheme
        with st.expander("Add New Scheme"):
            with st.form("add_scheme"):
                title = st.text_input("Scheme Title")
                description = st.text_area("Description")
                eligibility = st.text_area("Eligibility Criteria")
                benefits = st.text_area("Benefits")
                application_process = st.text_area("Application Process")
                deadline = st.text_input("Deadline")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("Add Scheme"):
                        st.success("Scheme added successfully!")
                with col2:
                    if st.form_submit_button("Clear"):
                        st.rerun()
        
        # Existing schemes
        schemes = self.db.get_schemes(50)
        
        if schemes:
            st.markdown("#### Existing Schemes")
            
            for scheme in schemes:
                with st.expander(f"{scheme[0]}"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.markdown(f"**Description:** {scheme[1][:100]}...")
                        st.markdown(f"**Eligibility:** {scheme[2][:100]}...")
                    
                    with col2:
                        st.markdown(f"**Benefits:** {scheme[3][:100]}...")
                        st.markdown(f"**Deadline:** {scheme[5]}")
                    
                    with col3:
                        if st.button(f"Edit", key=f"edit_scheme_{scheme[0]}"):
                            st.info("Edit mode activated")
                        if st.button(f"Deactivate", key=f"deactivate_scheme_{scheme[0]}"):
                            st.warning("Scheme deactivated")
        else:
            st.info("No schemes found in database")
    
    def show_pesticide_management(self):
        """Show pesticide management interface"""
        st.markdown("### Pesticide Management")
        
        # Add new pesticide
        with st.expander("Add New Pesticide"):
            with st.form("add_pesticide"):
                name = st.text_input("Pesticide Name")
                company = st.text_input("Company")
                usage_info = st.text_area("Usage Information")
                crop_applicable = st.text_area("Crops Applicable")
                safety_instructions = st.text_area("Safety Instructions")
                dosage = st.text_input("Dosage")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("Add Pesticide"):
                        if name and company and usage_info:
                            try:
                                # Add pesticide to database
                                pesticide_data = {
                                    'name': name,
                                    'type': pesticide_type,
                                    'company': company,
                                    'usage_info': usage_info,
                                    'crop_applicable': crop_applicable,
                                    'safety_instructions': safety_instructions,
                                    'dosage': dosage,
                                    'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                }
                                
                                # Save to database
                                self.db.add_pesticide(pesticide_data)
                                st.success("Pesticide added successfully!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error adding pesticide: {str(e)}")
                        else:
                            st.error("Please fill in all required fields (Name, Company, Usage Information)")
                with col2:
                    if st.form_submit_button("Clear"):
                        st.rerun()
        
        # Existing pesticides
        search_pesticide = st.text_input("Search pesticides", placeholder="Search by name or company...")
        
        if search_pesticide:
            pesticides = self.db.search_pesticides(search_pesticide)
        else:
            pesticides = self.db.search_pesticides("")  # Get all
        
        if pesticides:
            st.markdown("#### Existing Pesticides")
            
            for pesticide in pesticides:
                with st.expander(f"{pesticide[0]}"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.markdown(f"**Company:** {pesticide[1]}")
                        st.markdown(f"**Usage:** {pesticide[2][:100]}...")
                    
                    with col2:
                        st.markdown(f"**Crops:** {pesticide[3]}")
                        st.markdown(f"**Dosage:** {pesticide[5]}")
                    
                    with col3:
                        if st.button(f"Edit", key=f"edit_pest_{pesticide[0]}"):
                            st.info("Edit mode activated")
                        if st.button(f"Deactivate", key=f"deactivate_pest_{pesticide[0]}"):
                            st.warning("Pesticide deactivated")
        else:
            st.info("No pesticides found")
    
    def show_shop_management(self):
        """Show pesticide shop management interface"""
        st.markdown("### Pesticide Shop Management")
        
        # Add new shop
        with st.expander("Add New Shop"):
            with st.form("add_shop"):
                shop_name = st.text_input("Shop Name")
                owner_name = st.text_input("Owner Name")
                address = st.text_area("Address")
                contact_number = st.text_input("Contact Number")
                email = st.text_input("Email")
                
                # Location coordinates
                col1, col2 = st.columns(2)
                with col1:
                    latitude = st.number_input("Latitude", value=0.0, format="%.6f")
                with col2:
                    longitude = st.number_input("Longitude", value=0.0, format="%.6f")
                
                # Operating hours
                st.markdown("#### Operating Hours")
                col1, col2 = st.columns(2)
                with col1:
                    opening_time = st.time_input("Opening Time")
                with col2:
                    closing_time = st.time_input("Closing Time")
                
                # Additional details
                services_offered = st.text_area("Services Offered", 
                                               help="List the services offered (e.g., Pesticide sales, Farm equipment, Soil testing)")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("Add Shop"):
                        if shop_name and address and contact_number:
                            try:
                                # Add shop to database
                                shop_data = {
                                    'name': shop_name,
                                    'owner_name': owner_name,
                                    'address': address,
                                    'contact': contact_number,
                                    'email': email,
                                    'latitude': latitude,
                                    'longitude': longitude,
                                    'opening_time': str(opening_time),
                                    'closing_time': str(closing_time),
                                    'services_offered': services_offered,
                                    'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                }
                                
                                # Save to database
                                self.db.add_pesticide_shop(shop_data)
                                st.success("Shop added successfully!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error adding shop: {str(e)}")
                        else:
                            st.error("Please fill in all required fields (Shop Name, Address, Contact Number)")
                with col2:
                    if st.form_submit_button("Clear"):
                        st.rerun()
        
        # Existing shops
        search_shop = st.text_input("Search shops", placeholder="Search by name or location...")
        
        if search_shop:
            shops = self.db.search_pesticide_shops(search_shop)
        else:
            shops = self.db.get_pesticide_shops()
        
        if shops:
            st.markdown("#### Existing Shops")
            
            for shop in shops:
                with st.expander(f"{shop[1]}"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.markdown(f"**Owner:** {shop[2] if len(shop) > 2 else 'N/A'}")
                        st.markdown(f"**Address:** {shop[3] if len(shop) > 3 else 'N/A'}")
                        st.markdown(f"**Contact:** {shop[4] if len(shop) > 4 else 'N/A'}")
                    
                    with col2:
                        st.markdown(f"**Email:** {shop[5] if len(shop) > 5 else 'N/A'}")
                        if len(shop) > 6 and shop[6]:
                            st.markdown(f"**Location:** {shop[6]:.4f}, {shop[7]:.4f}")
                        st.markdown(f"**Hours:** {shop[8] if len(shop) > 8 else 'N/A'} - {shop[9] if len(shop) > 9 else 'N/A'}")
                    
                    with col3:
                        if st.button(f"View on Map", key=f"map_{shop[0]}"):
                            if len(shop) > 6 and shop[6]:
                                # Show map (simplified - in real app would use map library)
                                st.info(f"Location: {shop[6]:.4f}, {shop[7]:.4f}")
                            else:
                                st.warning("Location coordinates not available")
                        
                        if st.button(f"Edit", key=f"edit_shop_{shop[0]}"):
                            st.info("Edit mode activated")
                        
                        if st.button(f"Deactivate", key=f"deactivate_shop_{shop[0]}"):
                            st.warning("Shop deactivated")
        else:
            st.info("No shops found")
    
    def show_analytics(self):
        """Show system analytics"""
        st.markdown("### System Analytics")
        
        # User Analytics
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### User Analytics")
            
            # User registration trend
            months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
            registrations = [45, 52, 48, 67, 72, 89]
            
            fig = px.line(
                x=months,
                y=registrations,
                title="User Registration Trend",
                labels={'x': 'Month', 'y': 'New Users'}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("#### 🔮 Prediction Analytics")
            
            # Prediction types distribution
            pred_types = ['Crop', 'Irrigation', 'Yield']
            pred_counts = [450, 320, 280]
            
            fig = px.bar(
                x=pred_types,
                y=pred_counts,
                title="Prediction Types Distribution",
                labels={'x': 'Prediction Type', 'y': 'Count'},
                color=pred_counts,
                color_continuous_scale='Viridis'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Geographic Distribution
        st.markdown("#### Geographic Distribution")
        
        states = ['Punjab', 'Haryana', 'Uttar Pradesh', 'Maharashtra', 'Gujarat', 'Others']
        user_counts = [234, 189, 267, 145, 123, 289]
        
        fig = px.pie(
            values=user_counts,
            names=states,
            title="Users by State"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Model Performance
        st.markdown("#### 🤖 Model Performance Metrics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("🎯 Crop Model Accuracy", "92%", "+2%")
        with col2:
            st.metric("💧 Irrigation Model Accuracy", "88%", "+1%")
        with col3:
            st.metric("📈 Yield Model Accuracy", "85%", "+3%")
        with col4:
            st.metric("⚡ Avg Response Time", "1.2s", "-0.3s")
    
    def show_settings(self):
        """Show admin settings"""
        st.markdown("### ⚙️ System Settings")
        
        # General Settings
        st.markdown("#### 🛠️ General Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**🌐 System Configuration**")
            system_name = st.text_input("System Name", value="AGRIVISION")
            admin_email = st.text_input("Admin Email", value="admin@agrivision.com")
            max_users = st.number_input("Max Users", value=10000, min_value=100)
            
            if st.button("💾 Save General Settings"):
                st.success("✅ General settings saved!")
        
        with col2:
            st.markdown("**🔧 Model Settings**")
            auto_retrain = st.checkbox("Auto Retrain Models", value=True)
            backup_frequency = st.selectbox("Backup Frequency", ["Daily", "Weekly", "Monthly"])
            log_level = st.selectbox("Log Level", ["INFO", "DEBUG", "WARNING", "ERROR"])
            
            if st.button("💾 Save Model Settings"):
                st.success("✅ Model settings saved!")
        
        # Notification Settings
        st.markdown("#### 📧 Notification Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            email_notifications = st.checkbox("Email Notifications", value=True)
            sms_notifications = st.checkbox("SMS Notifications", value=False)
            push_notifications = st.checkbox("Push Notifications", value=True)
        
        with col2:
            new_user_alerts = st.checkbox("New User Alerts", value=True)
            system_alerts = st.checkbox("System Alerts", value=True)
            backup_alerts = st.checkbox("Backup Alerts", value=True)
        
        if st.button("💾 Save Notification Settings"):
            st.success("✅ Notification settings saved!")
        
        # Database Settings
        st.markdown("#### 💾 Database Settings")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔄 Backup Database"):
                st.success("✅ Database backup completed!")
        
        with col2:
            if st.button("🧹 Clean Database"):
                st.warning("⚠️ Database cleanup initiated")
        
        with col3:
            if st.button("📊 Database Stats"):
                st.info("📊 Database statistics would be displayed")
        
        # System Maintenance
        st.markdown("#### 🔧 System Maintenance")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("🔄 Restart System"):
                st.warning("⚠️ System restart scheduled")
        
        with col2:
            if st.button("🧹 Clear Cache"):
                st.success("✅ Cache cleared successfully")
        
        with col3:
            if st.button("📊 Check Health"):
                st.success("✅ System health: Good")
        
        with col4:
            if st.button("📥 Export Logs"):
                st.success("✅ Logs exported successfully")
