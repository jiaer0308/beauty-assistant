import os
import mysql.connector

# Configuration - based on seed_foundations.py
DB_HOST = os.environ.get("DB_HOST", "www.dcs5604.com")
DB_USER = os.environ.get("DB_USER", "baDB")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "Panda24685l$")
DB_NAME = os.environ.get("DB_NAME", "beauty_assisant")

def list_categories():
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM categories")
        rows = cursor.fetchall()
        for row in rows:
            print(f"{row[0]}: {row[1]}")
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_categories()
