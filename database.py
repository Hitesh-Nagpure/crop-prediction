import sqlite3
import hashlib
import json
from datetime import datetime
import pandas as pd

class Database:
    def __init__(self, db_name="agrivision.db"):
        self.db_name = db_name
        self.init_database()
    
    def init_database(self):
        """Initialize database with all required tables"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE,
                mobile TEXT UNIQUE,
                password TEXT NOT NULL,
                language TEXT DEFAULT 'english',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        # Government schemes table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS government_schemes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                eligibility TEXT,
                benefits TEXT,
                application_process TEXT,
                deadline TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Pesticide information table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pesticides (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                company TEXT,
                usage_info TEXT,
                crop_applicable TEXT,
                safety_instructions TEXT,
                dosage TEXT,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        # Pesticide shops table (Enhanced version)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pesticide_shops (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                shop_name VARCHAR(200) NOT NULL,
                owner_name VARCHAR(100),
                address TEXT NOT NULL,
                city VARCHAR(100),
                state VARCHAR(100),
                pincode VARCHAR(10),
                latitude DECIMAL(10, 8) NOT NULL,
                longitude DECIMAL(11, 8) NOT NULL,
                phone VARCHAR(15),
                email VARCHAR(100),
                rating DECIMAL(2, 1) DEFAULT 0.0,
                is_open BOOLEAN DEFAULT 1,
                opening_time TIME,
                closing_time TIME,
                products_available TEXT,
                license_number VARCHAR(50),
                verified BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes for better performance
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_shops_location ON pesticide_shops(latitude, longitude)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_shops_city ON pesticide_shops(city)
        ''')
        
        # User predictions history
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS prediction_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                prediction_type TEXT,
                input_data TEXT,
                result TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        self.seed_default_data()
    
    def seed_default_data(self):
        """Seed default data for government schemes and pesticides"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Check if data already exists
        cursor.execute("SELECT COUNT(*) FROM pesticides")
        pesticide_count = cursor.fetchone()[0]
        
        if pesticide_count == 0:
            # Real-world pesticide data
            pesticides_data = [
                # Herbicides
                {
                    'name': 'Glyphosate 48% SL',
                    'company': 'Bharat Agro',
                    'usage_info': 'Broad-spectrum systemic herbicide for weed control in various crops',
                    'crop_applicable': 'Tea, Coffee, Rubber, Non-crop areas',
                    'safety_instructions': 'Wear protective gloves and mask. Avoid contact with skin and eyes.',
                    'dosage': '2.5-3.0 ml per liter of water'
                },
                {
                    'name': '2,4-D 80% WP',
                    'company': 'UPL Limited',
                    'usage_info': 'Selective herbicide for broadleaf weed control in cereal crops',
                    'crop_applicable': 'Wheat, Rice, Maize, Sorghum',
                    'safety_instructions': 'Use protective clothing. Avoid spray drift to susceptible crops.',
                    'dosage': '0.5-1.0 kg per hectare'
                },
                {
                    'name': 'Paraquat Dichloride 24% SL',
                    'company': 'Syngenta India',
                    'usage_info': 'Non-selective contact herbicide for weed control',
                    'crop_applicable': 'Tea, Coffee, Orchards, Non-crop areas',
                    'safety_instructions': 'Highly toxic. Use full protective equipment.',
                    'dosage': '2.0-2.5 ml per liter of water'
                },
                {
                    'name': 'Pendimethalin 30% EC',
                    'company': 'BASF India',
                    'usage_info': 'Pre-emergence herbicide for annual grasses and broadleaf weeds',
                    'crop_applicable': 'Cotton, Soybean, Groundnut, Sunflower',
                    'safety_instructions': 'Avoid inhalation. Use in well-ventilated areas.',
                    'dosage': '2.5-3.0 liters per hectare'
                },
                {
                    'name': 'Atrazine 50% WP',
                    'company': 'Dhanuka Agritech',
                    'usage_info': 'Selective pre-emergence and early post-emergence herbicide',
                    'crop_applicable': 'Maize, Sorghum, Sugarcane',
                    'safety_instructions': 'Avoid contamination of water bodies.',
                    'dosage': '1.0-1.5 kg per hectare'
                },
                
                # Insecticides
                {
                    'name': 'Chlorpyrifos 20% EC',
                    'company': 'PI Industries',
                    'usage_info': 'Broad-spectrum organophosphate insecticide',
                    'crop_applicable': 'Cotton, Rice, Vegetables, Fruits',
                    'safety_instructions': 'Highly toxic. Use full protective equipment.',
                    'dosage': '2.0-3.0 ml per liter of water'
                },
                {
                    'name': 'Imidacloprid 17.8% SL',
                    'company': 'Bayer CropScience',
                    'usage_info': 'Systemic insecticide for sucking pests',
                    'crop_applicable': 'Cotton, Rice, Vegetables, Chilli',
                    'safety_instructions': 'Moderately toxic. Avoid contact with skin.',
                    'dosage': '0.3-0.5 ml per liter of water'
                },
                {
                    'name': 'Spinosad 45% SC',
                    'company': 'Dow AgroSciences',
                    'usage_info': 'Natural insecticide for caterpillar control',
                    'crop_applicable': 'Cotton, Vegetables, Fruits',
                    'safety_instructions': 'Low toxicity. Still use basic protection.',
                    'dosage': '0.5-1.0 ml per liter of water'
                },
                {
                    'name': 'Lambda-cyhalothrin 5% EC',
                    'company': 'Syngenta India',
                    'usage_info': 'Broad-spectrum pyrethroid insecticide',
                    'crop_applicable': 'Cotton, Vegetables, Pulses',
                    'safety_instructions': 'Toxic to aquatic life. Avoid water contamination.',
                    'dosage': '0.5-1.0 ml per liter of water'
                },
                {
                    'name': 'Thiamethoxam 25% WG',
                    'company': 'Syngenta India',
                    'usage_info': 'Systemic insecticide for early season pest control',
                    'crop_applicable': 'Rice, Cotton, Vegetables',
                    'safety_instructions': 'Toxic to bees. Avoid application during flowering.',
                    'dosage': '0.2-0.4 g per liter of water'
                },
                
                # Fungicides
                {
                    'name': 'Mancozeb 75% WP',
                    'company': 'Indofil Industries',
                    'usage_info': 'Broad-spectrum protective fungicide',
                    'crop_applicable': 'Grapes, Tomato, Potato, Vegetables',
                    'safety_instructions': 'Avoid inhalation. Use protective mask.',
                    'dosage': '2.0-3.0 g per liter of water'
                },
                {
                    'name': 'Carbendazim 50% WP',
                    'company': 'BASF India',
                    'usage_info': 'Systemic fungicide for wide range of fungal diseases',
                    'crop_applicable': 'Cereals, Vegetables, Fruits',
                    'safety_instructions': 'Avoid prolonged exposure. Use gloves.',
                    'dosage': '1.0-2.0 g per liter of water'
                },
                {
                    'name': 'Copper Oxychloride 50% WP',
                    'company': 'UPL Limited',
                    'usage_info': 'Protective fungicide for bacterial and fungal diseases',
                    'crop_applicable': 'Tomato, Chilli, Grapes, Mango',
                    'safety_instructions': 'Irritant to skin and eyes. Use protection.',
                    'dosage': '3.0-4.0 g per liter of water'
                },
                {
                    'name': 'Azoxystrobin 23% SC',
                    'company': 'Syngenta India',
                    'usage_info': 'Broad-spectrum systemic fungicide',
                    'crop_applicable': 'Grapes, Paddy, Wheat, Vegetables',
                    'safety_instructions': 'Low toxicity. Standard precautions required.',
                    'dosage': '0.5-1.0 ml per liter of water'
                },
                {
                    'name': 'Tebuconazole 25.9% EC',
                    'company': 'Bayer CropScience',
                    'usage_info': 'Systemic triazole fungicide',
                    'crop_applicable': 'Grapes, Wheat, Barley, Vegetables',
                    'safety_instructions': 'Avoid inhalation. Use protective equipment.',
                    'dosage': '0.5-1.0 ml per liter of water'
                },
                
                # Bactericides
                {
                    'name': 'Streptomycin Sulfate 90% SP',
                    'company': 'Hindustan Antibiotics',
                    'usage_info': 'Antibiotic bactericide for bacterial diseases',
                    'crop_applicable': 'Tomato, Chilli, Brinjal, Citrus',
                    'safety_instructions': 'Avoid inhalation. Use protective mask.',
                    'dosage': '0.5-1.0 g per liter of water'
                },
                {
                    'name': 'Copper Hydroxide 77% WP',
                    'company': 'UPL Limited',
                    'usage_info': 'Protective bactericide and fungicide',
                    'crop_applicable': 'Tomato, Potato, Vegetables',
                    'safety_instructions': 'Irritant to skin and eyes. Use protection.',
                    'dosage': '2.0-3.0 g per liter of water'
                },
                {
                    'name': 'Bacillus subtilis 0.5% WP',
                    'company': 'Biostadt India',
                    'usage_info': 'Biological bactericide for disease control',
                    'crop_applicable': 'Vegetables, Fruits, Spices',
                    'safety_instructions': 'Non-toxic. Standard precautions.',
                    'dosage': '2.0-3.0 g per liter of water'
                },
                {
                    'name': 'Pseudomonas fluorescens 0.5% WP',
                    'company': 'Tata Rallis',
                    'usage_info': 'Biocontrol agent for soil-borne diseases',
                    'crop_applicable': 'All crops, especially vegetables',
                    'safety_instructions': 'Completely safe. No special precautions.',
                    'dosage': '5.0-10.0 g per liter of water'
                },
                {
                    'name': 'Validamycin 3% L',
                    'company': 'PI Industries',
                    'usage_info': 'Antibiotic for sheath blight in rice',
                    'crop_applicable': 'Rice, Wheat',
                    'safety_instructions': 'Low toxicity. Basic protection recommended.',
                    'dosage': '2.0-3.0 ml per liter of water'
                }
            ]
            
            # Insert pesticides
            for pesticide in pesticides_data:
                cursor.execute('''
                    INSERT INTO pesticides (name, company, usage_info, crop_applicable, 
                                          safety_instructions, dosage, is_active)
                    VALUES (?, ?, ?, ?, ?, ?, 1)
                ''', (
                    pesticide['name'],
                    pesticide['company'],
                    pesticide['usage_info'],
                    pesticide['crop_applicable'],
                    pesticide['safety_instructions'],
                    pesticide['dosage']
                ))
        
        # Government schemes data (existing)
        cursor.execute("SELECT COUNT(*) FROM government_schemes")
        schemes_count = cursor.fetchone()[0]
        
        if schemes_count == 0:
            # Add sample government schemes
            schemes = [
                {
                    'title': 'Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)',
                    'description': 'Income support of ₹6,000 per year to small and marginal farmers',
                    'eligibility': 'Small and marginal farmers with cultivable land up to 2 hectares',
                    'benefits': '₹6,000 per year in three equal installments',
                    'application_process': 'Apply through common service centers or online portal',
                    'deadline': 'Ongoing'
                },
                {
                    'title': 'Pradhan Mantri Fasal Bima Yojana (PMFBY)',
                    'description': 'Crop insurance scheme to provide financial support to farmers',
                    'eligibility': 'All farmers growing notified crops in notified areas',
                    'benefits': 'Insurance coverage against crop loss due to natural calamities',
                    'application_process': 'Apply through designated insurance companies',
                    'deadline': 'Before sowing season'
                },
                {
                    'title': 'Soil Health Card Scheme',
                    'description': 'Provides soil health cards to farmers to understand soil nutrient status',
                    'eligibility': 'All farmers',
                    'benefits': 'Free soil testing and nutrient management recommendations',
                    'application_process': 'Apply through agriculture department',
                    'deadline': 'Ongoing'
                }
            ]
            
            for scheme in schemes:
                cursor.execute('''
                    INSERT INTO government_schemes (title, description, eligibility, benefits, application_process, deadline)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (scheme['title'], scheme['description'], scheme['eligibility'], 
                     scheme['benefits'], scheme['application_process'], scheme['deadline']))
        
        # Add sample pesticides
        cursor.execute("SELECT COUNT(*) FROM pesticides")
        if cursor.fetchone()[0] == 0:
            pesticides = [
                {
                    'name': 'Roundup',
                    'company': 'Monsanto',
                    'usage_info': 'Broad-spectrum herbicide for weed control',
                    'crop_applicable': 'All crops',
                    'safety_instructions': 'Use protective equipment, avoid skin contact',
                    'dosage': '2-3 ml per liter of water'
                },
                {
                    'name': 'Confidor',
                    'company': 'Bayer',
                    'usage_info': 'Insecticide for sucking pests',
                    'crop_applicable': 'Cotton, Rice, Vegetables',
                    'safety_instructions': 'Use gloves and mask during application',
                    'dosage': '0.5-1 ml per liter of water'
                },
                {
                    'name': 'Bavistin',
                    'company': 'BASF',
                    'usage_info': 'Fungicide for fungal diseases',
                    'crop_applicable': 'Cereals, Pulses, Oilseeds',
                    'safety_instructions': 'Avoid inhalation, wash hands after use',
                    'dosage': '2 grams per liter of water'
                }
            ]
            
            for pesticide in pesticides:
                cursor.execute('''
                    INSERT INTO pesticides (name, company, usage_info, crop_applicable, safety_instructions, dosage)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (pesticide['name'], pesticide['company'], pesticide['usage_info'],
                     pesticide['crop_applicable'], pesticide['safety_instructions'], pesticide['dosage']))
        
        conn.commit()
        conn.close()
    
    def hash_password(self, password):
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_user(self, name, email, mobile, password):
        """Create new user"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        try:
            hashed_password = self.hash_password(password)
            cursor.execute('''
                INSERT INTO users (name, email, mobile, password)
                VALUES (?, ?, ?, ?)
            ''', (name, email, mobile, hashed_password))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    def authenticate_user(self, email, password):
        """Authenticate user login"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        hashed_password = self.hash_password(password)
        cursor.execute('''
            SELECT id, name, email, language FROM users 
            WHERE (email = ? OR mobile = ?) AND password = ? AND is_active = 1
        ''', (email, email, hashed_password))
        
        user = cursor.fetchone()
        if user:
            # Update last login
            cursor.execute('''
                UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?
            ''', (user[0],))
            conn.commit()
        
        conn.close()
        return user
    
    def get_user(self, user_id):
        """Get user details"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, name, email, mobile, language, created_at 
            FROM users WHERE id = ?
        ''', (user_id,))
        
        user = cursor.fetchone()
        conn.close()
        return user
    
    def update_user_language(self, user_id, language):
        """Update user language preference"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE users SET language = ? WHERE id = ?
        ''', (language, user_id))
        
        conn.commit()
        conn.close()
        return True
    
    def get_schemes(self, limit=10):
        """Get government schemes"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT title, description, eligibility, benefits, application_process, deadline
            FROM government_schemes 
            WHERE is_active = 1
            ORDER BY created_at DESC
            LIMIT ?
        ''', (limit,))
        
        schemes = cursor.fetchall()
        conn.close()
        return schemes
    
    def add_pesticide(self, pesticide_data):
        """Add a new pesticide to the database"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO pesticides (name, company, usage_info, crop_applicable, 
                                      safety_instructions, dosage, is_active)
                VALUES (?, ?, ?, ?, ?, ?, 1)
            ''', (
                pesticide_data['name'],
                pesticide_data.get('company', ''),
                pesticide_data.get('usage_info', ''),
                pesticide_data.get('crop_applicable', ''),
                pesticide_data.get('safety_instructions', ''),
                pesticide_data.get('dosage', '')
            ))
            
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def search_pesticides(self, search_term):
        """Search pesticides by name"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT name, company, usage_info, crop_applicable, safety_instructions, dosage
            FROM pesticides 
            WHERE is_active = 1 AND name LIKE ?
            ORDER BY name
        ''', (f'%{search_term}%',))
        
        pesticides = cursor.fetchall()
        conn.close()
        return pesticides
    
    def add_pesticide_shop(self, shop_data):
        """Add a new pesticide shop to the database (Enhanced version)"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO pesticide_shops (shop_name, owner_name, address, city, state, pincode,
                                             latitude, longitude, phone, email, rating, is_open,
                                             opening_time, closing_time, products_available, license_number, verified)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
            ''', (
                shop_data['shop_name'],
                shop_data.get('owner_name', ''),
                shop_data['address'],
                shop_data.get('city', ''),
                shop_data.get('state', ''),
                shop_data.get('pincode', ''),
                shop_data.get('latitude', 0.0),
                shop_data.get('longitude', 0.0),
                shop_data.get('phone', ''),
                shop_data.get('email', ''),
                shop_data.get('rating', 0.0),
                shop_data.get('is_open', 1),
                shop_data.get('opening_time', ''),
                shop_data.get('closing_time', ''),
                shop_data.get('products_available', ''),
                shop_data.get('license_number', '')
            ))
            
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def search_pesticide_shops(self, search_term):
        """Search pesticide shops by name or address (Enhanced version)"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, shop_name, owner_name, address, city, state, pincode,
                   latitude, longitude, phone, email, rating, is_open,
                   opening_time, closing_time, products_available, license_number
            FROM pesticide_shops 
            WHERE verified = 1 AND (shop_name LIKE ? OR address LIKE ? OR city LIKE ?)
            ORDER BY shop_name
        ''', (f'%{search_term}%', f'%{search_term}%', f'%{search_term}%'))
        
        shops = cursor.fetchall()
        conn.close()
        return shops
    
    def get_nearby_shops(self, user_lat, user_lng, radius_km=5):
        """Get nearby shops using simplified distance calculation"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Get all verified shops first
        cursor.execute('''
            SELECT id, shop_name, address, city, latitude, longitude, 
                   phone, email, rating, is_open, products_available,
                   opening_time, closing_time
            FROM pesticide_shops
            WHERE verified = 1
        ''')
        
        shops = []
        for row in cursor.fetchall():
            # Calculate distance using Python
            shop_lat = row[4]
            shop_lng = row[5]
            
            # Simple distance calculation (Haversine approximation)
            distance = ((shop_lat - user_lat) ** 2 + (shop_lng - user_lng) ** 2) ** 0.5 * 111  # Rough km conversion
            
            if distance <= radius_km:
                shops.append({
                    'id': row[0],
                    'name': row[1],
                    'address': row[2],
                    'city': row[3],
                    'lat': shop_lat,
                    'lng': shop_lng,
                    'phone': row[6],
                    'email': row[7],
                    'rating': row[8],
                    'open_now': bool(row[9]),
                    'products': row[10].split(',') if row[10] else [],
                    'opening_time': row[11],
                    'closing_time': row[12],
                    'distance': round(distance, 2)
                })
        
        # Sort by distance
        shops.sort(key=lambda x: x['distance'])
        
        conn.close()
        return shops[:50]  # Limit to 50 results
    
    def get_pesticide_shops(self):
        """Get all pesticide shops (Enhanced version)"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, shop_name, owner_name, address, city, state, pincode,
                   latitude, longitude, phone, email, rating, is_open,
                   opening_time, closing_time, products_available, license_number
            FROM pesticide_shops 
            WHERE verified = 1
            ORDER BY shop_name
        ''')
        
        shops = cursor.fetchall()
        conn.close()
        return shops
    
    def populate_sample_shops(self):
        """Populate database with sample shop data"""
        from pesticide_shops_db import SAMPLE_SHOPS_PUNE
        
        conn = sqlite3.connect(self.db_name)
        
        for shop in SAMPLE_SHOPS_PUNE:
            try:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO pesticide_shops (shop_name, owner_name, address, city, state, pincode,
                                         latitude, longitude, phone, email, products_available,
                                         opening_time, closing_time, license_number, verified)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
                ''', (
                    shop['shop_name'],
                    shop.get('owner_name', ''),
                    shop['address'],
                    shop['city'],
                    shop['state'],
                    shop.get('pincode', ''),
                    shop['latitude'],
                    shop['longitude'],
                    shop.get('phone', ''),
                    shop.get('email', ''),
                    shop.get('products_available', ''),
                    shop.get('opening_time', ''),
                    shop.get('closing_time', ''),
                    shop.get('license_number', '')
                ))
                conn.commit()
                print(f"Added: {shop['shop_name']}")
            except Exception as e:
                print(f"Error adding {shop['shop_name']}: {e}")
        
        conn.close()
    
    def save_prediction(self, user_id, prediction_type, input_data, result):
        """Save prediction history"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO prediction_history (user_id, prediction_type, input_data, result)
            VALUES (?, ?, ?, ?)
        ''', (user_id, prediction_type, json.dumps(input_data), result))
        
        conn.commit()
        conn.close()
    
    def get_prediction_history(self, user_id, limit=10):
        """Get user prediction history"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT prediction_type, input_data, result, created_at
            FROM prediction_history 
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT ?
        ''', (user_id, limit))
        
        history = cursor.fetchall()
        conn.close()
        return history
