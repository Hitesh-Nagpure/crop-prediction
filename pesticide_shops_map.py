"""
Nearby Pesticide Shops Map Integration for AgriVision
Find and display nearby pesticide shops on an interactive map
"""

import streamlit as st
import folium
from streamlit_folium import st_folium
import requests
import json
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import pandas as pd

class PesticideShopLocator:
    """Handle pesticide shop location and mapping"""
    
    def __init__(self):
        self.geolocator = Nominatim(user_agent="agrivision_pesticide_locator")
        self.default_location = (18.5204, 73.8567)  # Pune, Maharashtra
        
    def get_user_location_from_browser(self):
        """
        Get user's location using browser geolocation API
        Returns JavaScript component for location access
        """
        location_html = """
        <div id="location-container" style="padding: 20px; text-align: center;">
            <button onclick="getLocation()" 
                    style="padding: 12px 24px; font-size: 16px; 
                           background-color: #4CAF50; color: white; 
                           border: none; border-radius: 5px; cursor: pointer;">
                📍 Get My Current Location
            </button>
            <p id="status" style="margin-top: 10px; color: #666;"></p>
            <input type="hidden" id="latitude" />
            <input type="hidden" id="longitude" />
        </div>

        <script>
        function getLocation() {
            const status = document.getElementById('status');
            
            if (!navigator.geolocation) {
                status.textContent = 'Geolocation is not supported by your browser';
                return;
            }
            
            status.textContent = 'Locating...';
            
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    const lat = position.coords.latitude;
                    const lng = position.coords.longitude;
                    
                    document.getElementById('latitude').value = lat;
                    document.getElementById('longitude').value = lng;
                    
                    status.textContent = `✅ Location found: ${lat.toFixed(4)}, ${lng.toFixed(4)}`;
                    
                    // Send to Streamlit
                    window.parent.postMessage({
                        type: 'streamlit:setComponentValue',
                        value: {lat: lat, lng: lng}
                    }, '*');
                },
                (error) => {
                    let errorMsg = '';
                    switch(error.code) {
                        case error.PERMISSION_DENIED:
                            errorMsg = 'Location access denied. Please enable location permissions.';
                            break;
                        case error.POSITION_UNAVAILABLE:
                            errorMsg = 'Location information unavailable.';
                            break;
                        case error.TIMEOUT:
                            errorMsg = 'Location request timed out.';
                            break;
                        default:
                            errorMsg = 'An unknown error occurred.';
                    }
                    status.textContent = '❌ ' + errorMsg;
                }
            );
        }
        </script>
        """
        return location_html
    
    def geocode_address(self, address):
        """
        Convert address to coordinates
        
        Args:
            address: Address string
        
        Returns:
            tuple: (latitude, longitude) or None
        """
        try:
            location = self.geolocator.geocode(address)
            if location:
                return (location.latitude, location.longitude)
            return None
        except Exception as e:
            st.error(f"Geocoding error: {str(e)}")
            return None
    
    def reverse_geocode(self, lat, lng):
        """
        Convert coordinates to address
        
        Args:
            lat: Latitude
            lng: Longitude
        
        Returns:
            str: Address string
        """
        try:
            location = self.geolocator.reverse(f"{lat}, {lng}")
            return location.address if location else "Unknown location"
        except Exception as e:
            return "Unknown location"
    
    def search_nearby_shops_google(self, lat, lng, radius=5000, api_key=None):
        """
        Search for nearby pesticide shops using Google Places API
        
        Args:
            lat: Latitude
            lng: Longitude
            radius: Search radius in meters (default 5km)
            api_key: Google Places API key
        
        Returns:
            list: List of shop dictionaries
        """
        if not api_key:
            st.warning("Google Places API key not configured. Using database data.")
            return self.get_shops_from_database(lat, lng, radius/1000)
        
        try:
            url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
            params = {
                'location': f"{lat},{lng}",
                'radius': radius,
                'keyword': 'pesticide shop agricultural store farm supply',
                'key': api_key
            }
            
            response = requests.get(url, params=params)
            data = response.json()
            
            if data['status'] == 'OK':
                shops = []
                for place in data['results']:
                    shops.append({
                        'name': place['name'],
                        'address': place.get('vicinity', 'N/A'),
                        'lat': place['geometry']['location']['lat'],
                        'lng': place['geometry']['location']['lng'],
                        'rating': place.get('rating', 'N/A'),
                        'open_now': place.get('opening_hours', {}).get('open_now', None),
                        'place_id': place['place_id']
                    })
                return shops
            else:
                st.warning(f"Google Places API: {data['status']}")
                return self.get_shops_from_database(lat, lng, radius/1000)
                
        except Exception as e:
            st.error(f"Error searching shops: {str(e)}")
            return self.get_shops_from_database(lat, lng, radius/1000)
    
    def get_shops_from_database(self, lat, lng, radius_km=5):
        """
        Get shops from the local database
        
        Args:
            lat: Latitude
            lng: Longitude
            radius_km: Search radius in kilometers
        
        Returns:
            list: List of shop dictionaries
        """
        try:
            from database import Database
            db = Database()
            shops = db.get_nearby_shops(lat, lng, radius_km)
            
            # Convert database format to map format
            map_shops = []
            for shop in shops:
                map_shops.append({
                    'name': shop['name'],
                    'address': shop['address'],
                    'lat': shop['lat'],
                    'lng': shop['lng'],
                    'rating': shop.get('rating', 0),
                    'phone': shop.get('phone', ''),
                    'open_now': shop.get('open_now', True),
                    'products': shop.get('products', []),
                    'distance': shop.get('distance', 0)
                })
            
            return map_shops
            
        except Exception as e:
            st.error(f"Error accessing database: {str(e)}")
            return self.get_demo_shops(lat, lng)
    
    def get_demo_shops(self, center_lat, center_lng):
        """
        Get demo pesticide shops data
        Replace with your actual database or API
        
        Args:
            center_lat: Center latitude
            center_lng: Center longitude
        
        Returns:
            list: Demo shop data
        """
        # Demo data - replace with your actual database
        demo_shops = [
            {
                'name': 'Green Farm Pesticides',
                'address': 'Shop No. 5, Market Yard, Pune',
                'lat': center_lat + 0.01,
                'lng': center_lng + 0.01,
                'rating': 4.5,
                'phone': '+91 9876543210',
                'open_now': True,
                'products': ['Insecticides', 'Fungicides', 'Herbicides']
            },
            {
                'name': 'Agri Solutions Store',
                'address': 'Near Bus Stand, Pune',
                'lat': center_lat - 0.015,
                'lng': center_lng + 0.02,
                'rating': 4.2,
                'phone': '+91 9876543211',
                'open_now': True,
                'products': ['Pesticides', 'Fertilizers', 'Seeds']
            },
            {
                'name': 'Kisan Seva Kendra',
                'address': 'Main Road, Pune',
                'lat': center_lat + 0.02,
                'lng': center_lng - 0.01,
                'rating': 4.7,
                'phone': '+91 9876543212',
                'open_now': False,
                'products': ['All Agricultural Inputs']
            },
            {
                'name': 'Farm Fresh Supplies',
                'address': 'Agricultural Market, Pune',
                'lat': center_lat - 0.01,
                'lng': center_lng - 0.015,
                'rating': 4.0,
                'phone': '+91 9876543213',
                'open_now': True,
                'products': ['Pesticides', 'Tools', 'Equipment']
            },
            {
                'name': 'Crop Care Center',
                'address': 'Station Road, Pune',
                'lat': center_lat + 0.005,
                'lng': center_lng + 0.025,
                'rating': 4.4,
                'phone': '+91 9876543214',
                'open_now': True,
                'products': ['Pesticides', 'Bio-fertilizers']
            }
        ]
        
        return demo_shops
    
    def calculate_distance(self, lat1, lng1, lat2, lng2):
        """
        Calculate distance between two points in kilometers
        
        Args:
            lat1, lng1: First point coordinates
            lat2, lng2: Second point coordinates
        
        Returns:
            float: Distance in kilometers
        """
        return geodesic((lat1, lng1), (lat2, lng2)).kilometers
    
    def create_map(self, center_lat, center_lng, shops, zoom_start=13):
        """
        Create interactive folium map with shop markers
        
        Args:
            center_lat: Map center latitude
            center_lng: Map center longitude
            shops: List of shop dictionaries
            zoom_start: Initial zoom level
        
        Returns:
            folium.Map: Interactive map object
        """
        # Create base map
        m = folium.Map(
            location=[center_lat, center_lng],
            zoom_start=zoom_start,
            tiles='OpenStreetMap'
        )
        
        # Add user location marker
        folium.Marker(
            [center_lat, center_lng],
            popup='Your Location',
            tooltip='You are here',
            icon=folium.Icon(color='red', icon='user', prefix='fa')
        ).add_to(m)
        
        # Add circle to show search radius
        folium.Circle(
            radius=5000,  # 5km
            location=[center_lat, center_lng],
            color='blue',
            fill=True,
            fillOpacity=0.1,
            popup='Search Area (5km radius)'
        ).add_to(m)
        
        # Add shop markers
        for i, shop in enumerate(shops):
            # Calculate distance
            distance = self.calculate_distance(
                center_lat, center_lng,
                shop['lat'], shop['lng']
            )
            
            # Create popup content
            popup_html = f"""
            <div style="width: 250px;">
                <h4 style="margin: 0 0 10px 0; color: #2E7D32;">{shop['name']}</h4>
                <p style="margin: 5px 0;"><b>📍 Address:</b><br>{shop['address']}</p>
                <p style="margin: 5px 0;"><b>📏 Distance:</b> {distance:.2f} km</p>
            """
            
            if 'rating' in shop and shop['rating']:
                popup_html += f"<p style='margin: 5px 0;'><b>⭐ Rating:</b> {shop['rating']}/5</p>"
            
            if 'phone' in shop and shop['phone']:
                popup_html += f"<p style='margin: 5px 0;'><b>📞 Phone:</b> {shop['phone']}</p>"
            
            if 'open_now' in shop:
                status = '🟢 Open Now' if shop['open_now'] else '🔴 Closed'
                popup_html += f"<p style='margin: 5px 0;'><b>Status:</b> {status}</p>"
            
            if 'products' in shop and shop['products']:
                popup_html += f"<p style='margin: 5px 0;'><b>🌾 Products:</b><br>{', '.join(shop['products'])}</p>"
            
            popup_html += f"""
                <a href="https://www.google.com/maps/dir/?api=1&destination={shop['lat']},{shop['lng']}" 
                   target="_blank" style="display: inline-block; margin-top: 10px; 
                   padding: 8px 15px; background-color: #4CAF50; color: white; 
                   text-decoration: none; border-radius: 4px;">
                   🗺️ Get Directions
                </a>
            </div>
            """
            
            # Determine marker color based on distance
            if distance < 2:
                color = 'green'
            elif distance < 5:
                color = 'orange'
            else:
                color = 'blue'
            
            # Add marker
            folium.Marker(
                [shop['lat'], shop['lng']],
                popup=folium.Popup(popup_html, max_width=300),
                tooltip=f"{shop['name']} ({distance:.1f} km)",
                icon=folium.Icon(color=color, icon='shopping-cart', prefix='fa')
            ).add_to(m)
        
        return m
    
    def get_shop_details_google(self, place_id, api_key):
        """
        Get detailed information about a shop using Google Places API
        
        Args:
            place_id: Google Place ID
            api_key: Google API key
        
        Returns:
            dict: Detailed shop information
        """
        try:
            url = "https://maps.googleapis.com/maps/api/place/details/json"
            params = {
                'place_id': place_id,
                'fields': 'name,formatted_address,formatted_phone_number,opening_hours,rating,website,reviews',
                'key': api_key
            }
            
            response = requests.get(url, params=params)
            data = response.json()
            
            if data['status'] == 'OK':
                return data['result']
            
        except Exception as e:
            st.error(f"Error getting shop details: {str(e)}")
        
        return None


def render_pesticide_shops_map():
    """
    Render the complete pesticide shops map interface
    """
    st.markdown("""
    <style>
    .shops-header {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
    }
    .shops-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        border-left: 5px solid #00f2fe;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="shops-header">
        <h1>Nearby Pesticide Shops</h1>
        <p>Find pesticide and agricultural supply shops near you</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize locator
    if 'shop_locator' not in st.session_state:
        st.session_state.shop_locator = PesticideShopLocator()
    
    locator = st.session_state.shop_locator
    
    # Location input options
    st.markdown("""
    <div class="shops-card">
        <h3>Select Your Location</h3>
    </div>
    """, unsafe_allow_html=True)
    
    location_method = st.radio(
        "How would you like to set your location?",
        ["Use Current Location", "Search by Address", "Manual Coordinates"],
        horizontal=True
    )
    
    user_lat, user_lng = None, None
    
    if location_method == "Use Current Location":
        st.info("Click the button below to allow location access")
        
        # Simple location input using Streamlit
        col1, col2 = st.columns([3, 1])
        with col1:
            manual_location = st.checkbox("Can't access location? Enter manually instead")
        
        if manual_location:
            col1, col2 = st.columns(2)
            with col1:
                user_lat = st.number_input("Latitude", value=18.5204, format="%.6f")
            with col2:
                user_lng = st.number_input("Longitude", value=73.8567, format="%.6f")
        else:
            st.info("Tip: For best results, enable location access in your browser settings")
            # Use default location for now
            user_lat, user_lng = locator.default_location
            st.success(f"Using default location: Pune, Maharashtra ({user_lat:.4f}, {user_lng:.4f})")
    
    elif location_method == "Search by Address":
        address = st.text_input(
            "Enter your address or city",
            placeholder="e.g., Pune, Maharashtra or Shop Road, Hadapsar, Pune"
        )
        
        if address:
            with st.spinner("Searching for location..."):
                coords = locator.geocode_address(address)
                if coords:
                    user_lat, user_lng = coords
                    st.success(f"Location found: {user_lat:.4f}, {user_lng:.4f}")
                else:
                    st.error("Could not find location. Please try a different address.")
    
    else:  # Manual coordinates
        col1, col2 = st.columns(2)
        with col1:
            user_lat = st.number_input("Latitude", value=18.5204, format="%.6f")
        with col2:
            user_lng = st.number_input("Longitude", value=73.8567, format="%.6f")
    
    # Search radius
    st.markdown("---")
    search_radius = st.slider(
        "Search Radius (km)",
        min_value=1,
        max_value=50,
        value=5,
        help="How far to search for pesticide shops"
    )
    
    # Search button
    if st.button("Find Nearby Shops", type="primary", use_container_width=True):
        if user_lat and user_lng:
            with st.spinner("Searching for nearby pesticide shops..."):
                # Get nearby shops
                # You can add Google API key here if you have one
                shops = locator.search_nearby_shops_google(
                    user_lat, user_lng, 
                    radius=search_radius * 1000  # Convert km to meters
                )
                
                if shops:
                    st.session_state.shops_data = shops
                    st.session_state.user_location = (user_lat, user_lng)
                    st.success(f"Found {len(shops)} shops within {search_radius} km")
                else:
                    st.warning("No shops found in this area. Try increasing the search radius.")
        else:
            st.error("Please set your location first")
    
    # Display map and results
    if 'shops_data' in st.session_state and 'user_location' in st.session_state:
        st.markdown("---")
        
        # Create tabs for map and list view
        tab1, tab2 = st.tabs(["Map View", "List View"])
        
        with tab1:
            # Create and display map
            user_lat, user_lng = st.session_state.user_location
            shops = st.session_state.shops_data
            
            map_obj = locator.create_map(user_lat, user_lng, shops)
            st_folium(map_obj, width=700, height=500)
            
            # Map legend
            st.markdown("""
            **Legend:**
            - Your Location
            - Green markers: < 2 km away
            - Orange markers: 2-5 km away
            - Blue markers: > 5 km away
            """)
        
        with tab2:
            # Sort shops by distance
            shops_with_distance = []
            for shop in shops:
                distance = locator.calculate_distance(
                    user_lat, user_lng,
                    shop['lat'], shop['lng']
                )
                shop['distance'] = distance
                shops_with_distance.append(shop)
            
            shops_with_distance.sort(key=lambda x: x['distance'])
            
            # Display shop cards
            for i, shop in enumerate(shops_with_distance):
                with st.expander(f"#{i+1} - {shop['name']} ({shop['distance']:.2f} km)"):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.markdown(f"**Address:** {shop['address']}")
                        st.markdown(f"**Distance:** {shop['distance']:.2f} km")
                        
                        if 'rating' in shop and shop['rating']:
                            st.markdown(f"**Rating:** {shop['rating']}/5")
                        
                        if 'phone' in shop and shop['phone']:
                            st.markdown(f"**Phone:** {shop['phone']}")
                        
                        if 'open_now' in shop:
                            status = 'Open Now' if shop['open_now'] else 'Closed'
                            st.markdown(f"**Status:** {status}")
                        
                        if 'products' in shop and shop['products']:
                            st.markdown(f"**Products:** {', '.join(shop['products'])}")
                    
                    with col2:
                        # Get directions button
                        directions_url = f"https://www.google.com/maps/dir/?api=1&destination={shop['lat']},{shop['lng']}"
                        st.markdown(f"[Get Directions]({directions_url})")
                        
                        # Call button (if phone available)
                        if 'phone' in shop and shop['phone']:
                                st.markdown(f"[Call Now](tel:{shop['phone']})")
    
    # Add shop button (for shop owners)
    st.markdown("---")
    with st.expander("Are you a shop owner? Add your shop"):
        st.info("Feature coming soon! Shop owners can register their shops here.")
        
        shop_name = st.text_input("Shop Name")
        shop_address = st.text_input("Shop Address")
        shop_phone = st.text_input("Phone Number")
        
        if st.button("Submit Shop Details"):
            st.success("Thank you! Your shop will be added after verification.")


# Standalone page for testing
if __name__ == "__main__":
    render_pesticide_shops_map()
