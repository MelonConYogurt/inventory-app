from mysql.connector import errorcode
from dotenv import load_dotenv
from pathlib import Path
from faker import Faker
import mysql.connector 
import os

# OpenTelemetry imports
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from mysql.connector.opentelemetry.instrumentation import MySQLInstrumentor as OracleMySQLInstrumentor

# Load environment variables
dotenv_path = Path('app/.env')
load_dotenv(dotenv_path=dotenv_path)

# Set up OpenTelemetry
provider = TracerProvider()
processor = BatchSpanProcessor(ConsoleSpanExporter())
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)
tracer = trace.get_tracer(__name__)

# Instrument MySQL Connector
OracleMySQLInstrumentor().instrument()

# Faker instance
faker = Faker()


class data_base():
    def __init__(self):
        self.connect = None
        self.cursor = None
        try:
            with tracer.start_as_current_span("database_connection"):
                self.connect = mysql.connector.connect(
                    host=os.getenv("HOST"), 
                    port=os.getenv("PORT"),
                    user=os.getenv("USER"),
                    password=os.getenv("PASSWORD"),
                    database=os.getenv("DATABASE"),
                )
                if self.connect.is_connected():
                    self.cursor = self.connect.cursor()
                    print("Connected to the database")
                else:
                    print("Failed to connect to the database")
        except Exception as e:
            print(f"Error connecting to the database: {e}")
            
    def search_products(self, code: int):
        try:
            with self.cursor as cursor:
                query = ("SELECT * FROM products WHERE product_code = %s")
                values = (code,)
                cursor.execute(query, values)
                if cursor.fetchall():
                    print("Product found")
                    return True
                else:
                    return False
            
        except mysql.connector.Error as err:
            with tracer.start_as_current_span("insert_product_error"):
                if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                    print("Something is wrong with your user name or password")
                elif err.errno == errorcode.ER_BAD_DB_ERROR:
                    print("Database does not exist")
                else:
                    print(err)
        finally:
            pass
        
    def insert_products(self, name: str, price: float, code: int, quantity: int, category: str | None, description: str | None):
        try:
            with tracer.start_as_current_span("insert_product"):
                search_product = self.search_products(code)
                if search_product == True:
                    print("Product already exists")
                    return
                else:
                    query = ("INSERT INTO products (product_name, product_price, product_code, product_quantity, product_category, product_description) "
                            "VALUES (%s, %s, %s, %s, %s, %s)")
                    values = (name, price, code, quantity, category, description)
                    print(values)
                    with self.cursor as cursor:
                        cursor.execute(query, values)
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
        finally:
            pass

    
    def fake_product_insert(self, fake_cicles:int):
        try:
            for _ in range(fake_cicles):
                new_product = self.insert_products(
                    name=faker.name(),
                    price=faker.random_number(digits=2),
                    code=faker.random_number(digits=5),
                    quantity= faker.random_number(digits=2),
                    category=faker.word(),
                    description=faker.sentence()
                )
                print(new_product)
        except mysql.connector.Error as err:
            with tracer.start_as_current_span("insert_product_error"):
                if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                    print("Something is wrong with your user name or password")
                elif err.errno == errorcode.ER_BAD_DB_ERROR:
                    print("Database does not exist")
                else:
                    print(err)
        finally:
            pass
        

if __name__ == "__main__":
    db = data_base()
    db.fake_product_insert(10)