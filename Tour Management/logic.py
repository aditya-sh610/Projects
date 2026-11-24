# logic.py - Business logic for VAY Travels

import math
import os
from datetime import datetime
from config import EARTH_RADIUS, SPEED_KMH, PRICE_PER_KM_PER_PERSON

def validate_date(date, currdate):
    """Validate date format and constraints."""
    errors = []
    if not date or len(date) != 10 or date[4] != "-" or date[7] != "-":
        errors.append("Please enter a valid date in YYYY-MM-DD format")
        return errors
    try:
        travel_date = datetime.strptime(date, "%Y-%m-%d").date()
        current_date = datetime.strptime(currdate, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        errors.append("Please enter a valid date in YYYY-MM-DD format")
        return errors
    if travel_date <= current_date:
        errors.append("Enter a valid date after today")
    return errors

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance using Haversine formula."""
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.asin(math.sqrt(a))
    return EARTH_RADIUS * c

def calculate_price(distance, num_people, hotel_price):
    """Calculate total price."""
    return round(distance * PRICE_PER_KM_PER_PERSON * num_people) + hotel_price

def calculate_travel_time(distance):
    """Calculate travel time in hours and minutes."""
    hours = distance / SPEED_KMH
    h = int(hours)
    m = int((hours - h) * 60)
    return h, m

def read_reviews(username=None):
    """Read reviews from file."""
    review_path = os.path.join(os.path.dirname(__file__), "review.txt")
    try:
        with open(review_path, "r", encoding="utf-8") as f:
            data = f.readlines()
        if username:
            for i in range(len(data)):
                if data[i].strip() == username:
                    return data[i+1].strip() if i+1 < len(data) else "No reviews yet!"
            return "No reviews yet!"
        return data
    except FileNotFoundError:
        return "No reviews yet!"

def write_review(username, currdate, review):
    """Write review to file."""
    review_path = os.path.join(os.path.dirname(__file__), "review.txt")
    review_entry = f"\n\n----------------\n{username}\n{currdate}: {review}"
    with open(review_path, "a", encoding="utf-8") as f:
        f.write(review_entry)