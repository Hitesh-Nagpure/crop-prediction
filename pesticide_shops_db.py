"""
Database Schema and Sample Data for Pesticide Shops
Add this to your existing database or create a new table
"""

import sqlite3
import json
from datetime import datetime

# SQL Schema for Pesticide Shops Table
CREATE_SHOPS_TABLE_SQL = """
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
    products_available TEXT,  -- JSON or comma-separated list
    license_number VARCHAR(50),
    verified BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for faster location-based queries
CREATE INDEX IF NOT EXISTS idx_location ON pesticide_shops(latitude, longitude);
CREATE INDEX IF NOT EXISTS idx_city ON pesticide_shops(city);
"""

# Python function to insert shop data
def add_shop_to_database(db_connection, shop_data):
    """
    Add a new pesticide shop to the database
    
    Args:
        db_connection: Database connection object
        shop_data: Dictionary with shop information
    """
    cursor = db_connection.cursor()
    
    sql = """
    INSERT INTO pesticide_shops (
        shop_name, owner_name, address, city, state, pincode,
        latitude, longitude, phone, email, products_available,
        opening_time, closing_time, license_number
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    
    values = (
        shop_data['shop_name'],
        shop_data.get('owner_name'),
        shop_data['address'],
        shop_data['city'],
        shop_data['state'],
        shop_data.get('pincode'),
        shop_data['latitude'],
        shop_data['longitude'],
        shop_data.get('phone'),
        shop_data.get('email'),
        shop_data.get('products_available'),
        shop_data.get('opening_time'),
        shop_data.get('closing_time'),
        shop_data.get('license_number')
    )
    
    cursor.execute(sql, values)
    db_connection.commit()
    return cursor.lastrowid


def get_nearby_shops_from_db(db_connection, user_lat, user_lng, radius_km=5):
    """
    Get nearby shops from database using Haversine formula
    
    Args:
        db_connection: Database connection
        user_lat: User latitude
        user_lng: User longitude
        radius_km: Search radius in kilometers
    
    Returns:
        list: List of nearby shops
    """
    cursor = db_connection.cursor()
    
    # Haversine formula in SQL
    # Note: This is an approximation
    sql = """
    SELECT 
        id, shop_name, address, city, latitude, longitude, 
        phone, email, rating, is_open, products_available,
        opening_time, closing_time,
        (
            6371 * acos(
                cos(radians(?)) * cos(radians(latitude)) *
                cos(radians(longitude) - radians(?)) +
                sin(radians(?)) * sin(radians(latitude))
            )
        ) AS distance
    FROM pesticide_shops
    WHERE verified = 1
    HAVING distance < ?
    ORDER BY distance
    LIMIT 50
    """
    
    cursor.execute(sql, (user_lat, user_lng, user_lat, radius_km))
    
    shops = []
    for row in cursor.fetchall():
        shops.append({
            'id': row[0],
            'name': row[1],
            'address': row[2],
            'city': row[3],
            'lat': row[4],
            'lng': row[5],
            'phone': row[6],
            'email': row[7],
            'rating': row[8],
            'open_now': bool(row[9]),
            'products': row[10].split(',') if row[10] else [],
            'opening_time': row[11],
            'closing_time': row[12],
            'distance': round(row[13], 2)
        })
    
    return shops


# Sample data for Pune, Maharashtra
SAMPLE_SHOPS_PUNE = [
    {
        'shop_name': 'Green Farm Pesticides & Seeds',
        'owner_name': 'Ramesh Patil',
        'address': 'Shop No. 15, Market Yard, Gultekdi',
        'city': 'Pune',
        'state': 'Maharashtra',
        'pincode': '411037',
        'latitude': 18.5018,
        'longitude': 73.8636,
        'phone': '+91 9876543210',
        'email': 'greenfarm@example.com',
        'products_available': 'Insecticides,Fungicides,Herbicides,Seeds,Fertilizers',
        'opening_time': '08:00:00',
        'closing_time': '20:00:00',
        'license_number': 'PUN/PEST/2020/001'
    },
    {
        'shop_name': 'Agri Solutions & Supplies',
        'owner_name': 'Suresh Kamble',
        'address': 'Near Bus Stand, Hadapsar',
        'city': 'Pune',
        'state': 'Maharashtra',
        'pincode': '411028',
        'latitude': 18.5089,
        'longitude': 73.9260,
        'phone': '+91 9876543211',
        'email': 'agrisolutions@example.com',
        'products_available': 'Pesticides,Bio-fertilizers,Sprayers,Safety Equipment',
        'opening_time': '07:30:00',
        'closing_time': '21:00:00',
        'license_number': 'PUN/PEST/2019/045'
    },
    {
        'shop_name': 'Kisan Seva Kendra',
        'owner_name': 'Vijay Deshmukh',
        'address': 'Main Road, Pimpri',
        'city': 'Pune',
        'state': 'Maharashtra',
        'pincode': '411018',
        'latitude': 18.6298,
        'longitude': 73.7997,
        'phone': '+91 9876543212',
        'email': 'kisanseva@example.com',
        'products_available': 'All Agricultural Inputs,Tools,Irrigation Equipment',
        'opening_time': '08:00:00',
        'closing_time': '19:00:00',
        'license_number': 'PUN/PEST/2021/089'
    },
    {
        'shop_name': 'Farm Fresh Agro Center',
        'owner_name': 'Prakash Jadhav',
        'address': 'Near Railway Station, Khadki',
        'city': 'Pune',
        'state': 'Maharashtra',
        'pincode': '411003',
        'latitude': 18.5675,
        'longitude': 73.8521,
        'phone': '+91 9876543213',
        'email': 'farmfresh@example.com',
        'products_available': 'Pesticides,Organic Fertilizers,Seeds,Tools',
        'opening_time': '09:00:00',
        'closing_time': '20:00:00',
        'license_number': 'PUN/PEST/2020/123'
    },
    {
        'shop_name': 'Crop Care & Protection',
        'owner_name': 'Santosh More',
        'address': 'Market Area, Wakad',
        'city': 'Pune',
        'state': 'Maharashtra',
        'pincode': '411057',
        'latitude': 18.5975,
        'longitude': 73.7617,
        'phone': '+91 9876543214',
        'email': 'cropcare@example.com',
        'products_available': 'Pesticides,Weedicides,Growth Regulators,Sprayers',
        'opening_time': '08:30:00',
        'closing_time': '20:30:00',
        'license_number': 'PUN/PEST/2022/034'
    },
    {
        'shop_name': 'Bharat Agro Store',
        'owner_name': 'Ganesh Shinde',
        'address': 'Shop Complex, Hinjewadi',
        'city': 'Pune',
        'state': 'Maharashtra',
        'pincode': '411057',
        'latitude': 18.5912,
        'longitude': 73.7389,
        'phone': '+91 9876543215',
        'email': 'bharatagro@example.com',
        'products_available': 'Pesticides,Fertilizers,Seeds,Agricultural Equipment',
        'opening_time': '07:00:00',
        'closing_time': '21:00:00',
        'license_number': 'PUN/PEST/2019/078'
    }
]


def populate_sample_data(db_connection):
    """
    Populate database with sample shop data
    
    Args:
        db_connection: Database connection
    """
    for shop in SAMPLE_SHOPS_PUNE:
        try:
            add_shop_to_database(db_connection, shop)
            print(f"Added: {shop['shop_name']}")
        except Exception as e:
            print(f"Error adding {shop['shop_name']}: {e}")


def integrate_with_existing_db():
    """
    Example code to integrate with your existing database
    """
    # Connect to your existing database
    conn = sqlite3.connect('agrivision_database.db')  # Your database name
    
    # Create table
    conn.executescript(CREATE_SHOPS_TABLE_SQL)
    
    # Populate with sample data
    populate_sample_data(conn)
    
    # Close connection
    conn.close()
    
    print("Database setup complete!")


# Integration with existing Database class
class PesticideShopsDB:
    """Handle pesticide shops database operations"""
    
    def __init__(self, db_connection):
        self.conn = db_connection
        self.setup_database()
    
    def setup_database(self):
        """Create the pesticide_shops table if it doesn't exist"""
        self.conn.executescript(CREATE_SHOPS_TABLE_SQL)
    
    def add_shop(self, shop_data):
        """Add a new shop to the database"""
        return add_shop_to_database(self.conn, shop_data)
    
    def get_nearby_shops(self, lat, lng, radius_km=5):
        """Get shops within specified radius"""
        return get_nearby_shops_from_db(self.conn, lat, lng, radius_km)
    
    def get_all_shops(self):
        """Get all shops from database"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM pesticide_shops WHERE verified = 1 ORDER BY shop_name")
        
        shops = []
        for row in cursor.fetchall():
            shops.append({
                'id': row[0],
                'shop_name': row[1],
                'owner_name': row[2],
                'address': row[3],
                'city': row[4],
                'state': row[5],
                'pincode': row[6],
                'latitude': row[7],
                'longitude': row[8],
                'phone': row[9],
                'email': row[10],
                'rating': row[11],
                'is_open': row[12],
                'opening_time': row[13],
                'closing_time': row[14],
                'products_available': row[15],
                'license_number': row[16],
                'verified': row[17],
                'created_at': row[18],
                'updated_at': row[19]
            })
        
        return shops
    
    def search_shops_by_city(self, city):
        """Search shops by city"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM pesticide_shops WHERE city LIKE ? AND verified = 1", (f"%{city}%",))
        
        shops = []
        for row in cursor.fetchall():
            shops.append({
                'id': row[0],
                'shop_name': row[1],
                'address': row[3],
                'city': row[4],
                'phone': row[9],
                'email': row[10],
                'rating': row[11],
                'latitude': row[7],
                'longitude': row[8]
            })
        
        return shops


if __name__ == "__main__":
    # Run this to set up the database
    integrate_with_existing_db()
