from mysql.connector import errorcode
from dotenv import load_dotenv
from pathlib import Path
from faker import Faker
import mysql.connector 
import os
from typing import Optional

# OpenTelemetry imports
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from mysql.connector.opentelemetry.instrumentation import MySQLInstrumentor as OracleMySQLInstrumentor

# Load environment variables
dotenv_path = Path('app/.env')
load_dotenv(dotenv_path=dotenv_path)

# OpenTelemetry configuration
provider = TracerProvider()
processor = BatchSpanProcessor(ConsoleSpanExporter())
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)
tracer = trace.get_tracer(__name__)

OracleMySQLInstrumentor().instrument()

# Faker instance
faker = Faker()

config = {
    "host": os.getenv("HOST"), 
    "port": os.getenv("PORT"),
    "user": os.getenv("USER"),
    "password": os.getenv("PASSWORD"),
    "use_pure": True,
    "database": os.getenv("DATABASE"),
}

class data_base():
    def __init__(self):
        self.connect = None
        self.cursor = None
        try:
            with tracer.start_as_current_span("database_connection"):
                self.connect = mysql.connector.connect(**config)
                if self.connect.is_connected():
                    self.cursor = self.connect.cursor()
                    print("Connected to the database")
                else:
                    print("Failed to connect to the database")
                    raise Exception("Database connection failed")
        except Exception as e:
            print(f"Error connecting to the database: {e}")
            raise

    def close(self):
        if self.connect.is_connected():
            self.cursor.close()
            self.connect.close()
            print("Database connection closed")

    def search_products(self, code: int):
        try:
            query = ("SELECT * FROM products WHERE product_code = %s")
            values = (code,)
            self.cursor.execute(query, values)
            if self.cursor.fetchall():
                print("Product found")
                return True
            else:
                print("Product not found")
                return False
        except mysql.connector.Error as err:
            with tracer.start_as_current_span("search_product_error"):
                if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                    print("Something is wrong with your user name or password")
                elif err.errno == errorcode.ER_BAD_DB_ERROR:
                    print("Database does not exist")
                else:
                    print(err)

    def insert_products(self, name: str, price: float, code: int, quantity: int, category: Optional[str], description: Optional[str]):
        try:
            with tracer.start_as_current_span("insert_product"):
                if self.search_products(code):
                    print("Product already exists")
                    return
                else:
                    query = ("INSERT INTO products (product_name, product_price, product_code, product_quantity, product_category, product_description) "
                             "VALUES (%s, %s, %s, %s, %s, %s)")
                    values = (name, price, code, quantity, category, description)
                    self.cursor.execute(query, values)
                    self.connect.commit()
                    print(f"Product {name} inserted successfully")
        except mysql.connector.Error as err:
            with tracer.start_as_current_span("insert_product_error"):
                if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                    print("Something is wrong with your user name or password")
                elif err.errno == errorcode.ER_BAD_DB_ERROR:
                    print("Database does not exist")
                else:
                    print(err)
                    
    def delete_products(self, code: int, quantity:int):
        try:
            with tracer.start_as_current_span("delete_product"):
                #Veriyfy the if product exist
                if self.search_products(code) == False:
                    print("Product not found")
                    return
                else:
                    #veruify if product quantity is suficent
                    query_verificate_quantity =("SELECT * FROM products WHERE product_code = %s")
                    values= (code,)
                    self.cursor.execute(query_verificate_quantity, values)
                    current_quantity = self.cursor.fetchone()
                    
                    if quantity > current_quantity[4]:
                        print(f"Insufficient quantity in stock\nThe stok for the product is: {current_quantity[4]}")
                        return False
                    else:
                        #Update the product stock
                        query =( "UPDATE products SET product_quantity = product_quantity - %s WHERE product_code = %s")
                        values = (quantity, code)
                        self.cursor.execute(query, values)
                        self.connect.commit()
        except mysql.connector.Error as err:
            with tracer.start_as_current_span("insert_product_error"):
                if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                    print("Something is wrong with your user name or password")
                elif err.errno == errorcode.ER_BAD_DB_ERROR:
                    print("Database does not exist")
                else:
                    print(err)
                    
                    
    def drop_product(self, code: int):
        try:
            with tracer.start_as_current_span("delete_product"):
                #Veriyfy the if product exist
                if self.search_products(code) == False:
                    print("Product not found")
                    return
                else:
                    query=("DELETE FROM products WHERE product_code = %s")
                    values= (code,)
                    self.cursor.execute(query, values)
                    current_drop = self.cursor.fetchone()
                    self.connect.commit()
                    print(f"Procut eliminated:\n {current_drop}")
        except mysql.connector.Error as err:
            with tracer.start_as_current_span("insert_product_error"):
                if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                    print("Something is wrong with your user name or password")
                elif err.errno == errorcode.ER_BAD_DB_ERROR:
                    print("Database does not exist")
                else:
                    print(err)
        
    def fake_product_insert(self, fake_cycles: int):
        try:
            for _ in range(fake_cycles):
                self.insert_products(
                    name=faker.word(),
                    price=faker.random_number(digits=2),
                    code=faker.random_number(digits=5),
                    quantity=faker.random_number(digits=2),
                    category=faker.word(),
                    description=faker.sentence(
                        nb_words=3, variable_nb_words= False
                    )
                )
        except mysql.connector.Error as err:
            with tracer.start_as_current_span("insert_product_error"):
                if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                    print("Something is wrong with your user name or password")
                elif err.errno == errorcode.ER_BAD_DB_ERROR:
                    print("Database does not exist")
                else:
                    print(err)
    
if __name__ == "__main__":
    db = data_base()
    try:
        # db.fake_product_insert(10)
        db.drop_product(
            code = 84109
        )
    finally:
        db.close()
