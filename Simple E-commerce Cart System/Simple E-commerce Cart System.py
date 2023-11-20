from abc import ABC, abstractmethod
import copy
import logging
from getpass import getpass  # For password input

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Base Product class
class Product:
    def __init__(self, name, price, available, count=10, discount=0):
        self.name = name
        self.price = price
        self.available = available
        self.count = count
        self.discount = discount

    def display_info(self):
        print(f"{self.name} - ${self.price} - Available: {self.available} - Count: {self.count} - Discount: {self.discount}%")

# DiscountStrategy interface using the Strategy Pattern
class DiscountStrategy:
    def apply_discount(self, price):
        return price

class PercentageOffDiscountStrategy(DiscountStrategy):
    def __init__(self, percentage):
        self.percentage = percentage

    def apply_discount(self, price):
        return super().apply_discount(price * (1 - self.percentage / 100))

class BuyOneGetOneFreeDiscountStrategy(DiscountStrategy):
    def apply_discount(self, price):
        return super().apply_discount(price * 0.5)  # Buy one, get one free (50% off)

# CartItem class representing an item in the shopping cart
class CartItem:
    def __init__(self, name, price, quantity, discount_strategy):
        self.name = name
        self.price = price
        self.quantity = quantity
        self.discount_strategy = discount_strategy

    def calculate_total(self):
        return self.discount_strategy.apply_discount(self.price) * self.quantity

    def display_info(self):
        print(f"{self.name} - Quantity: {self.quantity} - Total: ${self.calculate_total()}")

# ShoppingCart class representing the user's shopping cart
class ShoppingCart:
    def __init__(self):
        self.cart_items = []

    def add_item(self, product, quantity, discount_strategy):
        item = CartItem(product.name, product.price, quantity, discount_strategy)
        self.cart_items.append(item)
        logger.info(f"Added {quantity} {product.name} to the cart.")

    def update_quantity(self, product_name, new_quantity):
        for item in self.cart_items:
            if item.name == product_name:
                item.quantity = new_quantity
                logger.info(f"Updated quantity for {product_name} to {new_quantity}.")
                return
        logger.warning(f"Product {product_name} not found in the cart.")

    def remove_item(self, product_name, remove_quantity=None):
        if remove_quantity is None:
            self.cart_items = [item for item in self.cart_items if item.name != product_name]
            logger.info(f"Removed {product_name} from the cart.")
        else:
            for item in self.cart_items:
                if item.name == product_name:
                    item.quantity -= remove_quantity
                    if item.quantity <= 0:
                        self.cart_items.remove(item)
                    logger.info(f"Removed {remove_quantity} {product_name} from the cart.")

    def calculate_total_bill(self):
        total_bill = sum(item.calculate_total() for item in self.cart_items)
        return total_bill

    def display_cart(self):
        cart_info = ", ".join(f"{item.quantity} {item.name}" for item in self.cart_items)
        logger.info(f"Cart Items: You have {cart_info} in your cart.")
        logger.info(f"Total Bill: Your total bill is ${self.calculate_total_bill()}.")

    def checkout(self, product_prototype):
        try:
            self.display_cart()

            # Update product counts and availability
            for item in self.cart_items:
                product_name = item.name
                quantity = item.quantity
                product = product_prototype.products.get(product_name)

                if product:
                    if product.count >= quantity:
                        product.count -= quantity
                        if product.count == 0:
                            product.available = False
                        logger.info(f"Checked out {quantity} {product_name}(s). Updated count: {product.count}, Availability: {product.available}.")
                    else:
                        logger.warning(f"Not enough stock available for {product_name}. Checkout failed.")
                        return

            logger.info("Purchase successful! Thank you for shopping with us.")
        except Exception as e:
            logger.error(f"An error occurred during checkout: {str(e)}")


# Prototype pattern to clone product objects
class ProductPrototype:
    def __init__(self):
        self.products = {}

    def register_product(self, product_class, name, price, available, discount=0):
        product = product_class(name, price, available, discount=discount)
        self.products[name] = product

    def clone(self, name, quantity, discount_strategy):
        product = copy.deepcopy(self.products[name])
        return CartItem(product.name, product.price, quantity, discount_strategy)

# User class for login
class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def authenticate(self, input_password):
        return self.password == input_password

    def login(self):
        print(f"Login to the system - {self.username}:")
        username_input = input("Username: ")
        password_input = getpass("Password: ")

        if self.authenticate(password_input):
            print("Login successful!")
            logger.info(f"{self.username} logged in.")
            return True
        else:
            print("Login failed. Invalid credentials.")
            logger.warning(f"Login failed for {self.username}.")
            return False

class AdminCustomerBridge:
    def __init__(self, prototype):
        self.prototype = prototype
        self.customer_menu_func = None

    def set_customer_menu_func(self, customer_menu_func):
        self.customer_menu_func = customer_menu_func

    def notify_product_added(self, product_name):
        if self.customer_menu_func:
            self.customer_menu_func()

    def notify_product_updated(self, product_name, availability, count, discount):
        if self.customer_menu_func:
            self.customer_menu_func()

# Sample product data
product_data = {
    'Laptop1': {'price': 800, 'available': True, 'count': 20, 'discount': 5},
    'Headphones1': {'price': 50, 'available': False, 'count': 10, 'discount': 0},
}

def load_products(prototype):
    for name, data in product_data.items():
        prototype.register_product(Product, name, data['price'], data['available'], discount=data['discount'])
        prototype.products[name].count = data['count']

def admin_menu(prototype, bridge, customer_menu_func):
    admin_user = User(username="admin", password="admin123")  # Sample admin login

    if not admin_user.login():
        # If login fails, return to the main welcome page
        main_menu()
        return

    while True:
        print("\nAdmin Menu:")
        print("1. Add New Product")
        print("2. Update Product Availability")
        print("3. View Products")
        print("4. Exit")

        admin_choice = input("Enter your choice: ")

        if admin_choice == "1":
            product_name = input("Enter product name: ")
            product_price = float(input("Enter product price: "))
            product_available = input("Is the product available? (True/False): ").capitalize() == "True"
            product_discount = float(input("Enter product discount percentage: "))
            product_count = int(input("Enter initial product count: "))
            prototype.register_product(Product, product_name, product_price, product_available, discount=product_discount)
            prototype.products[product_name].count = product_count
            logger.info(f"Added new product: {product_name}")
            # Notify the customer menu about the new product
            bridge.notify_product_added(product_name)
        elif admin_choice == "2":
            product_name = input("Enter product name to update availability: ")
            product_available = input("Is the product available? (True/False): ").capitalize() == "True"
            product_count = int(input("Enter new product count: "))
            product_discount = float(input("Enter new product discount percentage: "))
            if product_name in prototype.products:
                prototype.products[product_name].available = product_available
                prototype.products[product_name].count = product_count
                prototype.products[product_name].discount = product_discount
                logger.info(f"Updated availability for {product_name} to {product_available}.")
                # Notify the customer menu about the updated availability
                bridge.notify_product_updated(product_name, product_available, product_count, product_discount)
            else:
                logger.warning(f"Product {product_name} not found.")
        elif admin_choice == "3":
            for product in prototype.products.values():
                product.display_info()
        elif admin_choice == "4":
            print("Exiting Admin Menu.")
            break
        else:
            print("Invalid choice. Please try again.")

    # After exiting admin menu, return to the main welcome page
    main_menu()

def customer_menu(prototype, cart, bridge):
    sample_user = User(username="customer", password="pass123")  # Sample customer login

    if not sample_user.login():
        # If login fails, return to the main welcome page
        main_menu()
        return

    bridge.set_customer_menu_func(customer_menu)

    while True:
        print("\nCustomer Menu:")
        print("1. View Products")
        print("2. Add to Cart")
        print("3. Update Quantity")
        print("4. Remove from Cart")
        print("5. Display Cart")
        print("6. Checkout")
        print("7. Exit")

        customer_choice = input("Enter your choice: ")

        if customer_choice == "1":
            for product in prototype.products.values():
                product.display_info()
        elif customer_choice == "2":
            product_name = input("Enter product name to add to cart: ")
            if product_name in prototype.products:
                quantity = int(input("Enter quantity: "))
                discount_strategy = (
                    PercentageOffDiscountStrategy(10) if prototype.products[product_name].discount > 0 else None
                )
                cart.add_item(prototype.clone(product_name, quantity, discount_strategy), quantity, discount_strategy)
            else:
                logger.warning(f"Product {product_name} not found.")
        elif customer_choice == "3":
            product_name = input("Enter product name to update quantity: ")
            new_quantity = int(input("Enter new quantity: "))
            cart.update_quantity(product_name, new_quantity)
        elif customer_choice == "4":
            product_name = input("Enter product name to remove from cart: ")
            remove_quantity = int(input("Enter quantity to remove (Enter 0 to remove all): "))
            cart.remove_item(product_name, remove_quantity)
        elif customer_choice == "5":
            cart.display_cart()
        elif customer_choice == "6":
            cart.checkout(prototype)
            break
        elif customer_choice == "7":
            print("Exiting Customer Menu.")
            break
        else:
            print("Invalid choice. Please try again.")

    # After exiting customer menu, return to the main welcome page
    main_menu()

def main_menu():
    try:
        prototype = ProductPrototype()
        cart = ShoppingCart()

        bridge = AdminCustomerBridge(prototype)

        # Load initial products
        load_products(prototype)

        while True:
            print("Welcome to e-cart!")
            print("Select User Type:")
            print("1. Customer")
            print("2. Admin")
            user_type = input("Enter your choice: ")

            if user_type == "1":
                customer_menu(prototype, cart, bridge)
            elif user_type == "2":
                admin_menu(prototype, bridge, customer_menu)
            else:
                print("Invalid choice. Exiting application.")
                break  # Exit the application

    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    main_menu()
