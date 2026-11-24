import os

# Database Configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'yourpassword',
    'database': 'yourdatabase'
}

# Application Constants
APP_TITLE = "VAY Travels"
WINDOW_SIZE = "1200x700"
LOGIN_WINDOW_SIZE = "800x900"
SIGNUP_WINDOW_SIZE = "800x600"

# Cities and Hotels Data
CITIES = ["Delhi", "Mumbai", "Chennai", "Bangalore", "Kolkata", "Ahmedabad", "Lucknow"]

HOTELS_BY_CITY = {
    "Delhi": [
        "The Leela Palace - Rs15000",
        "Taj Mahal Hotel - Rs12000",
        "ITC Maurya - Rs10000",
        "The Imperial - Rs9500",
        "Lemon Tree Premier - Rs5000",
        "Bloomrooms @ New Delhi Railway Station - Rs3000",
        "Hotel Ajanta - Rs3000",
        "Hotel Hari Piorko - Rs1200",
        "Hotel Perfect - Rs1000",
        "Hotel Sunstar Heritage - Rs800"
    ],
    "Mumbai": [
        "The Oberoi Mumbai - Rs16000",
        "Taj Mahal Palace - Rs14000",
        "Trident Nariman Point - Rs9500",
        "JW Marriott Mumbai Sahar - Rs10000",
        "ITC Maratha - Rs8000",
        "Residency Hotel Fort - Rs2500",
        "Hotel Sea Princess - Rs3500",
        "Hotel Tourist - Rs1000",
        "Hotel Kohinoor Elite - Rs900"
    ],
    "Bangalore": [
        "The Ritz-Carlton - Rs14000",
        "The Leela Palace - Rs13000",
        "ITC Gardenia - Rs9000",
        "Shangri-La Hotel - Rs8500",
        "Taj MG Road - Rs7000",
        "Lemon Tree Premier - Rs4500",
        "Hotel Empire International - Rs2800",
        "Treebo Trend Royal Orchid - Rs2000",
        "Hotel Jaya International - Rs1100",
        "Hotel Nandhini Palace - Rs900"
    ],
    "Chennai": [
        "ITC Grand Chola - Rs13500",
        "Taj Coromandel - Rs12000",
        "The Raintree Hotel - Rs8500",
        "The Leela Palace - Rs11000",
        "Radisson Blu - Rs7500",
        "Hotel Pandian - Rs2300",
        "Hotel Aswani - Rs1800",
        "Hotel Raj Regency - Rs900",
        "Hotel Marina Residency - Rs1200",
        "Hotel Horizon - Rs800"
    ],
    "Ahmedabad": [
        "The House of MG - Rs8500",
        "Hyatt Regency Ahmedabad - Rs9500",
        "Fortune Landmark - Rs7000",
        "The Grand Bhagwati - Rs5000",
        "Hotel Ramada - Rs4500",
        "Hotel Express - Rs1800",
        "Hotel Atithi - Rs1500",
        "Hotel Grand Bhagwati - Rs1000",
        "Hotel Silver Oak - Rs900",
        "Hotel Rainbow Inn - Rs700"
    ],
    "Kolkata": [
        "The Oberoi Grand - Rs12500",
        "ITC Sonar - Rs11000",
        "The Park Kolkata - Rs8000",
        "JW Marriott Kolkata - Rs10000",
        "Hyatt Regency Kolkata - Rs7500",
        "Hotel Casa Fortuna - Rs2000",
        "Hotel Comfort - Rs900",
        "Hotel Sonar Bangla - Rs1500",
        "Hotel Green Park - Rs1200",
        "Hotel Metro - Rs800"
    ],
    "Lucknow": [
        "Lebua Lucknow - Rs9000",
        "Clarks Avadh - Rs7500",
        "Hotel Landmark - Rs4000",
        "Hyatt Regency Lucknow - Rs8000",
        "Hotel Taj Mahal - Rs6000",
        "Hotel Krishna - Rs1500",
        "Hotel City Inn - Rs800",
        "Hotel Marina - Rs900",
        "Hotel Royal Palace - Rs1200",
        "Hotel Park Inn - Rs1000"
    ]
}

FLIGHTS = ["Indigo", "Vistara", "Air India", "Akasa Air"]

# Other Constants
EARTH_RADIUS = 6371  # km
SPEED_KMH = 800
PRICE_PER_KM_PER_PERSON = 5
GIF_PATH = os.path.join(os.path.dirname(__file__), "plane.gif")

# Modern UI Color Palette
PRIMARY_COLOR = "#1976D2"      # Blue
SECONDARY_COLOR = "#0D47A1"    # Dark Blue
ACCENT_COLOR = "#FF6F00"       # Orange
SUCCESS_COLOR = "#4CAF50"      # Green
WARNING_COLOR = "#FF9800"      # Orange
ERROR_COLOR = "#F44336"        # Red
BACKGROUND_COLOR = "#F5F5F5"   # Light Gray
CARD_COLOR = "#FFFFFF"         # White
TEXT_COLOR = "#212121"         # Dark Gray
TEXT_LIGHT = "#757575"         # Light Gray

# Modern Fonts
TITLE_FONT = ("Segoe UI", 28, "bold")
HEADER_FONT = ("Segoe UI", 24, "bold")
SUBHEADER_FONT = ("Segoe UI", 18, "bold")
BUTTON_FONT = ("Segoe UI", 12, "bold")
BODY_FONT = ("Segoe UI", 14)
SMALL_FONT = ("Segoe UI", 12)