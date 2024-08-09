import datetime
from faker import Faker

#import de scaner module
from app.scanner.scan_barcode import *
from app.scanner.code_generator import *

#Load config for connection
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

    def drop_product(self, code: int):
        try:
            # Verify if product exists
            verify_product = self.search_products(code)
            if not verify_product[0]:
                print("Product not found")
                return
            else:
                query = "DELETE FROM main.products WHERE product_code = %s RETURNING *"
                values = (code,)
                
                #Execute the query
                self.cursor.execute(query, values)
                #Get the info of the delete item
                delete_info = self.cursor.fetchone()
                self.connect.commit()

                print(f"Product eliminated:\n {delete_info}")
        except psycopg2.Error as err:
            print(f"Error in drop_product: {err}")
            print("Exception TYPE:", type(err))        
   
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
            raise

    def insert_products(self, name: str, price: float, code: int, quantity: int, category: str| None = None, description: str| None = None):
        try:
            verify_product = self.search_products(code)
            if verify_product[0]:
                print("Product already exists")
                return
            else:
                query = ("INSERT INTO main.products (product_name, product_price, product_code, product_quantity, product_category, product_description) VALUES (%s, %s, %s, %s, %s, %s) RETURNING * ")
                values = (name, price, code, quantity, category, description)
                self.cursor.execute(query, values)
                data_insert = self.cursor.fetchone()
                self.connect.commit()
                print(f"Product {data_insert} inserted successfully")
        except psycopg2.Error as err:
            print(f"Error in insert_products: {err}")
            print("Exception TYPE:", type(err))
            self.connect.rollback()
            raise

    def delete_products(self, code: int, quantity: int):
        try:
            verify_product = self.search_products(code)
            if not verify_product[0]:
                print("Product not found")
                return
            else:
                query_verificate_quantity = "SELECT product_quantity FROM main.products WHERE product_code = %s"
                values = (code,)
                self.cursor.execute(query_verificate_quantity, values)
                current_quantity = self.cursor.fetchone()
                if current_quantity and quantity > current_quantity[0]:
                    print(f"Insufficient quantity in stock\nThe stock for the product is: {current_quantity[0]}")
                    return False
                else:
                    query = "UPDATE main.products SET product_quantity = product_quantity - %s WHERE product_code = %s"
                    values = (quantity, code)
                    self.cursor.execute(query, values)
                    return True
        except psycopg2.Error as err:
            print(f"Error in delete_products: {err}")
            print("Exception TYPE:", type(err))
            self.connect.rollback()
            raise

    def sale(self):
        try:
            date = datetime.datetime.now().strftime('%Y%m%d')
            number = faker.random_number(digits=5)
            generate_code = f"{date}{number}"
            generate_qr(data=generate_code)  
            
            sale_data = {
                "sale_code": generate_code,
                "sale_date": datetime.datetime.now().strftime("%Y-%m-%d"),  
                "sale_total": 0
            }
            
            query = "INSERT INTO main.sales (sale_code, sale_date, sale_total) VALUES (%s, %s, %s) RETURNING sale_id"
            values = (sale_data["sale_code"], sale_data["sale_date"], sale_data["sale_total"])  
        
            self.cursor.execute(query, values)
            sale_id = self.cursor.fetchone()[0]  # Obtén el nuevo ID de venta
            return sale_id
        except psycopg2.Error as err:
            print(f"Error in sale: {err}")
            print("Exception TYPE:", type(err))
            self.connect.rollback()
            raise

    def sale_products(self):
        self.connect.autocommit = False
        try:
            scanner_instance = Scanner()  
            product_list = scanner_instance.recorder()  
            if not product_list:
                raise ValueError("Empty list")
            
            valid_products = [product for product in product_list if self.search_products(product)[0]]
            if not valid_products:
                raise ValueError("No valid products found")
            
            sale_id = self.sale()  
            if not sale_id:
                raise ValueError("Failed to create sale")
            
            for product in product_list:
                verify_product = self.search_products(product)
                if verify_product[0]:
                    product_data = {
                        "product_id": verify_product[1][0],
                        "product_name": verify_product[1][1],
                        "product_price": verify_product[1][2],
                        "product_code": verify_product[1][3],
                        "product_quantity": 1
                    }
                    # user_input = input(f"Enter quantity for product {product_data['product_name']} (default is 1): ")
                    # try:
                    #     product_quantity = int(user_input) if user_input else 1
                    # except ValueError:
                    #     print("Invalid quantity input. Using default value of 1.")
                    #     product_quantity = 1
                    # product_data["product_quantity"] = product_quantity
                            
                    query = "INSERT INTO main.sale_products (sale_id, product_id, quantity, product_price_at_sale) VALUES (%s, %s, %s, %s) RETURNING *"
                    values = (sale_id, product_data["product_id"], product_data["product_quantity"], product_data["product_price"])
                    self.cursor.execute(query, values)
                    sale_item_data = self.cursor.fetchone()
                    print(f"Sale product: {sale_item_data}")
                    self.delete_products(code=product_data["product_code"], quantity=product_data["product_quantity"])
        
            self.connect.commit()            
        except (psycopg2.Error, Exception) as err:
            print(f"Error in sale_products: {err}")
            print("Exception TYPE:", type(err))
            self.connect.rollback()
            raise
        finally:
            self.connect.autocommit = True
    
    def update_product_data(self,
                        name: str | None = None,
                        price: float | None = None,
                        code: int | None = None,
                        quantity: int | None = None,
                        category: str | None = None,
                        description: str | None = None):
        try:
            product_data_in_db = self.search_products(code=code)
            if not product_data_in_db:
                print("Product not found.")
                return

            update_fields = []
            update_values = []

            if name is not None:
                update_fields.append("product_name = %s")
                update_values.append(name)
            if price is not None:
                update_fields.append("product_price = %s")
                update_values.append(price)
            if quantity is not None:
                update_fields.append("product_quantity = %s")
                update_values.append(quantity)
            if category is not None:
                update_fields.append("product_category = %s")
                update_values.append(category)
            if description is not None:
                update_fields.append("product_description = %s")
                update_values.append(description)
            
            if not update_fields:
                print("No fields to update.")
                return

            update_values.append(code)
            
            query = f"UPDATE main.products SET {', '.join(update_fields)} WHERE product_code = %s RETURNING *"
            self.cursor.execute(query, update_values)
            product_update_data = self.cursor.fetchone()
            self.connection.commit()
            print(f"Product updated successfully: {product_update_data}")
        
        except psycopg2.Error as err:
            print(f"Error in update_product_data: {err}")
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
        # db.fake_product_insert(10)
        # db.drop_product(
        #     code = 42023
        # )
        # db.insert_products(
        #     name = "Miel de abeja",
        #     price= 10000,
        #     code= 2980008614257,
        #     quantity= 100,
        # )
        # valor_bool = db.search_products(
        #     code = 27947
        # )
        # print(valor_bool[0])
        db.sale_products()
        pass
    finally:
        db.close()
