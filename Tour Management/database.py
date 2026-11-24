# database.py - Database operations for VAY Travels

import mysql.connector as mysql
import os
from config import DB_CONFIG

class DatabaseManager:
    def __init__(self):
        self.connection = None
        self.cursor = None
        try:
            self.connect()
        except mysql.Error as err:
            print(f"Database connection failed: {err}")

    def connect(self):
        try:
            db_config = dict(DB_CONFIG)
            db_config.update({
                key: value for key, value in {
                    "host": os.getenv("VAY_DB_HOST"),
                    "user": os.getenv("VAY_DB_USER"),
                    "password": os.getenv("VAY_DB_PASSWORD"),
                    "database": os.getenv("VAY_DB_NAME"),
                }.items() if value
            })
            self.connection = mysql.connect(**db_config)
            self.cursor = self.connection.cursor()
            print("Database connection successful")
        except mysql.Error as err:
            raise

    def ensure_connection(self):
        if not self.connection or not self.connection.is_connected():
            self.connect()

    def get_current_date(self):
        self.ensure_connection()
        self.cursor.execute("SELECT CURDATE();")
        return str(self.cursor.fetchone()[0])

    def get_user_credentials(self):
        self.ensure_connection()
        self.cursor.execute("SELECT * FROM passcheck")
        data = self.cursor.fetchall()
        userlist = {}
        for i in data:
            userlist[i[0]] = i[1]
        return userlist

    def get_user_role(self, username):
        self.ensure_connection()
        self.cursor.execute('''SELECT role FROM passcheck WHERE username = %s;''', (username,))
        data = self.cursor.fetchall()
        return data[0][0] if data else None

    def insert_user(self, username, password, role):
        self.ensure_connection()
        self.cursor.execute("INSERT INTO passcheck (username, password, role) VALUES (%s, %s, %s)", (username, password, role))
        self.connection.commit()

    def get_all_tour_ids(self):
        self.ensure_connection()
        self.cursor.execute("SELECT tourid FROM travels;")
        return [row[0] for row in self.cursor.fetchall()]

    def get_booking_by_tourid(self, tourid):
        self.ensure_connection()
        self.cursor.execute("SELECT * FROM travels WHERE tourid = %s", (tourid,))
        return self.cursor.fetchall()

    def update_booking(self, tourid, field, value):
        self.ensure_connection()
        allowed_fields = {"departure", "arrival", "traveldate", "durationdays", "persons"}
        if field not in allowed_fields:
            raise ValueError("Invalid booking field")
        query = f"UPDATE travels SET {field} = %s WHERE tourid = %s"
        self.cursor.execute(query, (value, tourid))
        self.connection.commit()

    def delete_booking(self, tourid):
        self.ensure_connection()
        self.cursor.execute("DELETE FROM hotels WHERE tourid = %s", (tourid,))
        self.cursor.execute("DELETE FROM travels WHERE tourid = %s", (tourid,))
        self.connection.commit()

    def get_user_bookings(self, username):
        self.ensure_connection()
        query = '''SELECT departure, arrival, traveldate, durationdays, persons FROM travels WHERE username = %s;'''
        self.cursor.execute(query, (username,))
        return self.cursor.fetchall()

    def insert_booking(self, tourid, departure, arrival, date, days, persons, username):
        self.ensure_connection()
        query = '''INSERT INTO travels VALUES (%s, %s, %s, %s, %s, %s, %s);'''
        self.cursor.execute(query, (tourid, departure, arrival, date, days, persons, username))
        self.connection.commit()

    def get_next_tourid(self):
        self.ensure_connection()
        self.cursor.execute("SELECT COALESCE(MAX(tourid), 0) + 1 FROM travels;")
        return self.cursor.fetchone()[0]

    def insert_hotel_flight(self, hotel, dep_flight, arr_flight, tourid):
        self.ensure_connection()
        query = '''INSERT INTO hotels VALUES (%s, %s, %s, %s);'''
        self.cursor.execute(query, (hotel, dep_flight, arr_flight, tourid))
        self.connection.commit()

    def get_coordinates(self, city):
        self.ensure_connection()
        self.cursor.execute('SELECT latitude, longitude FROM coordinates WHERE city = %s;', (city,))
        coords = self.cursor.fetchone()
        return [float(x) for x in coords] if coords else None

    def get_all_bookings(self):
        self.ensure_connection()
        self.cursor.execute("SELECT * FROM travels;")
        return self.cursor.fetchall()

    def get_all_users(self):
        self.ensure_connection()
        self.cursor.execute("SELECT username FROM passcheck;")
        return [row[0] for row in self.cursor.fetchall()]

    def get_report_data(self, fields):
        self.ensure_connection()
        allowed_fields = {"tourid", "departure", "arrival", "traveldate", "durationdays", "persons", "username"}
        if not fields or any(field not in allowed_fields for field in fields):
            raise ValueError("Invalid report fields")
        query = f"SELECT {', '.join(fields)} FROM travels;"
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

# Global instance
db_manager = DatabaseManager()