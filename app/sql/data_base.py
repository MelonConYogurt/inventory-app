from mysql.connector import errorcode
from dotenv import load_dotenv
from pathlib import Path
import mysql.connector 
import datetime
import os

dotenv_path = Path('app\.env')

# Load environment variables
load_dotenv(dotenv_path = dotenv_path)


class DataBase:
    def __init__(self):
        try:
            self.connect = mysql.connector.connect(
                host = os.getenv("HOST"), 
                port = os.getenv("PORT"),
                user = os.getenv("USER"),
                password = os.getenv("PASSWORD"),
                database = os.getenv("DATABASE"),
            )
            if self.connect.is_connected():
                self.cursor = self.connect.cursor()
                print("Connected to the database")
            else:
                print("Failed to connect to the database")            
        except Exception as e:
            return e
        
    def insert_products(self, name: str, price: float, code: int, quantity: int, category: str | None, description: str | None):
        try:
            with self.cursor as cursor:
                query =(f"INSERT INTO products (product_name, product_price, product_code, product_quantity, product_category, product_description) VALUES (%s, %s, %s, %s, %s, %s)")
                values = (name, price, code, quantity, category, description)
                cursor.execute(query, values)
                self.connect.commit()
                print(f"Product {name} inserted successfully")    
            
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print(err)
        else:
            self.connect.close()