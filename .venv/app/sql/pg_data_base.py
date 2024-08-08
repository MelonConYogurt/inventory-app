import os
import datetime
from dotenv import load_dotenv, find_dotenv
from typing import Optional
from faker import Faker

#import de scaner module
from app.scanner.scan_barcode import *
from app.scanner.code_generator import *


from app.sql.config import load_config

#pg database
import psycopg2

# Faker instance
faker = Faker()

class data_base:
    def __init__(self):
        self.connect = None
        self.cursor = None
        self.config = load_config()
        try:
            # self.connect = psycopg2.connect(**config)
            self.connect = psycopg2.connect(**self.config)
            self.cursor = self.connect.cursor()
            print("Connected to the database")
        except psycopg2.DatabaseError as err:
            print("An exception has occurred: ", err)
            print("Exception TYPE:", type(err))
    
    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.connect:
            self.connect.close()
        print("Database connection closed")

    def search_products(self, code: int):
        try:
            query = "SELECT * FROM main.products WHERE product_code = %s"
            values = (code,)
            self.cursor.execute(query, values)
            product = self.cursor.fetchone()
            if product:
                print(f"Product found:\n {product}")
                return True, product
            else:
                print("Product not found")
                return False, None
        except psycopg2.Error as err:
            print(f"Error in search_products: {err}")
            print("Exception TYPE:", type(err))

    def insert_products(self, name: str, price: float, code: int, quantity: int, category: Optional[str], description: Optional[str]):
        try:
            verify_product = self.search_products(code)
            if verify_product[0]:
                print("Product already exists")
                return
            else:
                query = ("INSERT INTO main.products (product_name, product_price, product_code, product_quantity, product_category, product_description) "
                         "VALUES (%s, %s, %s, %s, %s, %s)")
                values = (name, price, code, quantity, category, description)
                self.cursor.execute(query, values)
                self.connect.commit()
                print(f"Product {name} inserted successfully")
        except psycopg2.Error as err:
            print(f"Error in insert_products: {err}")
            print("Exception TYPE:", type(err))

    def delete_products(self, code: int, quantity: int):
        try:
            # Verify if product exists
            verify_product = self.search_products(code)
            if not verify_product[0]:
                print("Product not found")
                return
            else:
                # Verify if product quantity is sufficient
                query_verificate_quantity = "SELECT product_quantity FROM products WHERE product_code = %s"
                values = (code,)
                self.cursor.execute(query_verificate_quantity, values)
                current_quantity = self.cursor.fetchone()

                if current_quantity and quantity > current_quantity[0]:
                    print(f"Insufficient quantity in stock\nThe stock for the product is: {current_quantity[0]}")
                    return False
                else:
                    # Update the product stock
                    query = "UPDATE products SET product_quantity = product_quantity - %s WHERE product_code = %s"
                    values = (quantity, code)
                    self.cursor.execute(query, values)
                    self.connect.commit()
                    return True
        except psycopg2.Error as err:
            print(f"Error in delete_products: {err}")
            print("Exception TYPE:", type(err))
            
    def drop_product(self, code: int):
        try:
            # Verify if product exists
            verify_product = self.search_products(code)
            if not verify_product[0]:
                print("Product not found")
                return
            else:
                query = "DELETE FROM products WHERE product_code = %s"
                values = (code,)
                self.cursor.execute(query, values)
                self.connect.commit()
                print(f"Product eliminated:\n {verify_product[1]}")
        except psycopg2.Error as err:
            print(f"Error in drop_product: {err}")
            print("Exception TYPE:", type(err))
    
    def sale(self):
        try:
            date = datetime.datetime.now().strftime('%Y%m%d')
            number = faker.Faker().random_number(digits=5)
            generate_code = f"{date}{number}"
            # generate_qr(data = generate_code)  # Define esta función según tus necesidades
            
            sale_data = {
                "sale_code": generate_code,
                "sale_date": datetime.datetime.now().strftime("%Y-%m-%d"),  
                "sale_total": 0
            }
            
            query = "INSERT INTO sales (sale_code, sale_date, sale_total) VALUES (%s, %s, %s)"
            values = (sale_data["sale_code"], sale_data["sale_date"], sale_data["sale_total"])  
           
            self.cursor.execute(query, values)
            new_sale_id = self.cursor.fetchone()[0]  # Obtén el nuevo ID de venta
            self.connect.commit()
            return new_sale_id
        except psycopg2.Error as err:
            print(f"Error in sale: {err}")
            print("Exception TYPE:", type(err))
            
                         
    def sale_products(self):
        try:
            scanner_instance = Scanner()  # Define esta clase según tus necesidades
            sale_id = self.sale()
            product_list = scanner_instance.recorder()  # Define este método según tus necesidades
            for product in product_list:
                verify_product = self.search_products(product)
                if verify_product[0]:
                    product_data = {
                        "product_id": verify_product[1][0],
                        "product_name": verify_product[1][1],
                        "product_price": verify_product[1][2],
                        "product_code": verify_product[1][3]
                    }
                    # Default value
                    quantity = 1
                        
                    query = "INSERT INTO sale_items (sale_id, product_id, quantity, product_price_at_sale) VALUES (%s, %s, %s, %s)"
                    values = (sale_id, product_data["product_id"], quantity, product_data["product_price"])
                    self.cursor.execute(query, values)
                    self.connect.commit()
                    self.delete_products(code=product_data["product_code"], quantity=quantity)
        except psycopg2.Error as err:
            print(f"Error in sale_products: {err}")
            print("Exception TYPE:", type(err))
            
    def fake_product_insert(self, fake_cycles: int):
        try:
            for _ in range(fake_cycles):
                self.insert_products(
                    name=faker.word(),
                    price=faker.random_number(digits=2),
                    code=faker.ean13(),
                    quantity=faker.random_number(digits=2),
                    category=faker.word(),
                    description=faker.sentence(nb_words=3, variable_nb_words=False)
                )
        except psycopg2.Error as err:
            print(f"Error in fake_product_insert: {err}")
            print("Exception TYPE:", type(err))
            
if __name__ == "__main__":
    db = data_base()
    try:
        db.fake_product_insert(10)
        # db.drop_product(
        #     code = 42023
        # )
        # db.insert_products(
        #     name = "Mango con limon",
        #     price= 134234,
        #     code= 2807033817463,
        #     quantity= 100,
        #     category= "hola",
        #     description= "adnfasd",
        # )
        # valor_bool = db.search_products(
        #     code = 27947
        # )
        # print(valor_bool[0])
        # db.sale_products()
        pass
    finally:
        db.close()
