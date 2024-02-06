

import json
from tkinter import filedialog
import re
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk,ImageSequence
import cv2
from datetime import datetime
import csv
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from fuzzywuzzy import fuzz
from tkinter import Button,simpledialog
import logging
from tkinter import Toplevel
import os
import csv
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from fuzzywuzzy import fuzz
import concurrent.futures
import tkinter as tk
from tkinter import messagebox
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from tkinter import ttk
from functools import partial
import tkinter as tk
from tkinter import Toplevel, Text, Scrollbar, Button, Label
from concurrent.futures import ThreadPoolExecutor
from PIL import Image, ImageTk  # Import Image and ImageTk from PIL (Pillow) module
import os

import tkinter as tk
from tkinter import Button, Label, Text, Toplevel
from PIL import Image, ImageTk
import os
import threading





class AsusROG_WarehouseApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ASUS ROG Warehouse Pro")
        self.configure(bg="black")

class ProductManagement(AsusROG_WarehouseApp):
    def __init__(self):
        super().__init__()
        self.product_log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "product_log.csv")
        self.product_log = []
        self.product_id_counter = 1
        self.products = {}
        self.load_product_log()

    def update_products_dict(self):
        self.products = {item['id']: item for item in self.product_log}

    def find_existing_product(self, product_name, specifications_list):
        for product_id, details in self.products.items():
            existing_specifications_list = details['specifications'][1:].split('\n')
            if details['name'] == product_name and self.compare_specifications(specifications_list, existing_specifications_list):
                return details
        return None

    def compare_specifications(self, spec_list1, spec_list2):
        formatted_spec_str1 = "\n".join(spec_list1).strip()
        formatted_spec_str2 = "\n".join(spec_list2).strip()
        return fuzz.token_set_ratio(formatted_spec_str1, formatted_spec_str2) == 100

    def add_product(self, product_name, quantity, specifications):
        if not self.is_valid_product_name(product_name):
            self.show_message("Invalid Product Name", "Please add a product with the 'Asus ROG' prefix.")
            return

        if not self.is_valid_quantity(quantity):
            self.show_message("Invalid Quantity", "Please enter a quantity between 1 and 5.")
            return

        product_id = self.generate_product_id()
        specifications_list = specifications.split('\n')
        formatted_specifications = "\n".join([spec.strip() for spec in specifications_list])
        last_ordered = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        existing_product = self.find_existing_product(product_name, specifications_list)
        if existing_product:
            self.handle_existing_product(existing_product, quantity, formatted_specifications, last_ordered)
        else:
            self.create_new_product(product_id, product_name, quantity, formatted_specifications, last_ordered)

    def is_valid_product_name(self, product_name):
        return product_name.lower().startswith("asus rog")

    def is_valid_quantity(self, quantity):
        return quantity.isdigit() and 1 <= int(quantity) <= 5

    def generate_product_id(self):
        product_id = f"ROG-{str(self.product_id_counter).zfill(3)}"
        return product_id

    def handle_existing_product(self, existing_product, quantity, formatted_specifications, last_ordered):
        user_response = self.show_confirmation("Merge Products", f"A product with the name '{existing_product['name']}' already exists. Do you want to merge quantities?")
        if user_response:
            self.merge_products(existing_product, quantity, last_ordered)
        else:
            # User chose not to merge, treat it as a new product
            pass

    def merge_products(self, existing_product, quantity, last_ordered):
        new_quantity = int(quantity) + existing_product['quantity']
        if new_quantity > 5:
            self.handle_merge_exceed_limit(existing_product)
        else:
            existing_product['quantity'] = new_quantity
            existing_product['last_ordered'] = last_ordered
            self.save_product_log()
            self.show_message("Merge Successful", "Product merged successfully!")

    def handle_merge_exceed_limit(self, existing_product):
        merge_response = self.show_confirmation("Merge Not Allowed", "Merging exceeds the maximum quantity limit (5). Do you want to create a new product ID?")
        if merge_response:
            product_id = self.generate_product_id()
            product_name = existing_product.get('name', '')  # Replace '' with a default value if 'name' is not present
            quantity = existing_product.get('quantity', 0)    # Replace 0 with a default value if 'quantity' is not present
            formatted_specifications = existing_product.get('specifications', '')
            last_ordered = existing_product.get('last_ordered', '')
    
            product_data = self.create_product_data(product_id, product_name, quantity, formatted_specifications, last_ordered)
            self.product_log.append(product_data)
            self.save_product_log()
            self.show_message("Success", "New product added successfully!")

    def create_new_product(self, product_id, product_name, quantity, formatted_specifications, last_ordered):
        product_data = self.create_product_data(product_id, product_name, quantity, formatted_specifications, last_ordered)
        self.product_log.append(product_data)
        self.product_id_counter += 1
        self.save_product_log()
        self.show_message("Success", "Product added successfully!")

    def create_product_data(self, product_id, product_name, quantity, formatted_specifications, last_ordered):
        return {
            'id': product_id,
            'name': product_name,
            'quantity': int(quantity),
            'specifications': f"\n{formatted_specifications}",
            'last_ordered': last_ordered
        }

    def delete_product(self, product_identifier, delete_quantity):
        product = self.find_product(product_identifier)
        if product:
            self.update_quantity(product, delete_quantity)
            self.save_product_log()
            self.show_message("Deletion", f"Product {product['name']} successfully updated.")

    def find_product(self, product_identifier):
        for item in self.product_log:
            if product_identifier.lower() in [item['id'].lower(), item['name'].lower()]:
                return item
        return None

    def update_quantity(self, product, delete_quantity):
        if delete_quantity is None:
            product['quantity'] = 0
        elif isinstance(delete_quantity, str) and delete_quantity.lower() == 'delete':
            self.product_log.remove(product)
        elif isinstance(delete_quantity, str) and delete_quantity.isdigit():
            delete_quantity = int(delete_quantity)
            product['quantity'] -= delete_quantity
            if product['quantity'] <= 0:
                product['quantity'] = 0
        else:
            self.show_message("Error", "Invalid quantity or 'delete' specified.")

    def load_product_log(self):
        try:
            with open(self.product_log_file, 'r', newline='') as file:
                reader = csv.DictReader(file)
                self.product_log = list(reader)
        except FileNotFoundError:
            self.product_log = []

    def save_product_log(self):
        with open(self.product_log_file, 'w', newline='') as file:
            fieldnames = ['id', 'name', 'quantity', 'specifications', 'last_ordered']
            writer = csv.DictWriter(file, fieldnames=fieldnames, delimiter=';')
            if not os.path.getsize(self.product_log_file):
                writer.writeheader()
            writer.writerows(self.product_log)

        self.update_products_dict()

    def show_message(self, title, message):
        messagebox.showinfo(title, message)

    def show_confirmation(self, title, message):
        return messagebox.askyesno(title, message)



 

class SearchProductManagement(ProductManagement):
    def __init__(self):
        super().__init__()

    def search_product(self, product_identifier):
        product = self.find_product(product_identifier)
        if product:
            return self.format_product_details(product)
        return None

    def search_product_concurrently(self, product_identifier):
        # Example of introducing parallelism using concurrent.futures.ThreadPoolExecutor
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(self.find_product, product_identifier)
            product = future.result()

        if product:
            return self.format_product_details(product)
        return None

    def format_product_details(self, product):
        specifications = "\n".join(spec.strip() for spec in product['specifications'].split('\n') if spec.strip())
        return {
            'id': product['id'],
            'name': product['name'],
            'quantity': product['quantity'],
            'last_ordered': product['last_ordered'],
            'specifications': specifications
        }

    def find_product(self, product_identifier):
        for item in self.product_log:
            if product_identifier.lower() in [item['id'].lower(), item['name'].lower()]:
                return item
        return None
    
class ReportGenerator:
    def __init__(self, products):
        self.products = products

    def generate_shopping_list_pdf(self, filename="shopping_list.pdf"):
        doc = SimpleDocTemplate(filename, pagesize=letter)
        story = []
    
        title = Paragraph("Shopping List", getSampleStyleSheet()['Title'])
        story.append(title)
    
        product_data = [["Product ID", "Product Name", "Quantity"]]
        for product in self.products:
            if product['quantity'] == 0:
                product_data.append([product['id'], product['name'], str(product['quantity'])])
    
        product_table = Table(product_data, colWidths=[100, 300, 100])
        product_table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                                           ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                                           ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                           ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                           ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                                           ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                                           ('GRID', (0, 0), (-1, -1), 1, colors.grey)]))
    
        story.append(product_table)
    
        doc.build(story)
        print(f"Shopping list generated successfully: {filename}")

    def generate_product_report(self, filename="product_report.pdf"):
        doc = SimpleDocTemplate(filename, pagesize=letter)
        styles = getSampleStyleSheet()

        # Content for the PDF
        content = []

        title = Paragraph("Product Report", styles['Title'])
        content.append(title)
        content.append(Spacer(1, 12))

        # Table data
        table_data = [["Product Name", "Quantity"]]
        for product in self.products:
            table_data.append([product['name'], str(product['quantity'])])

        # Create a table and style
        product_table = Table(table_data, colWidths=[300, 100])
        product_table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                                           ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                                           ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                           ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                           ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                                           ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                                           ('GRID', (0, 0), (-1, -1), 1, colors.grey)]))

        content.append(product_table)

        # Save the PDF file
        doc.build(content)
        print(f"Product report generated successfully: {filename}")

class WarehouseGUI(SearchProductManagement):
    def __init__(self):
        super().__init__()
        self.orders = []
        self.orders_displayed = []
        self.removed_orders = []
        self.product_text = None  # Initialize product_text attribute
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.power_search_active = False  # Initialize the power_search_active variable
        # self.removed_orders = []  # Initialize removed_orders as an empty list

        # Initialize all frames
        self.initialize_play_gif_frame()
        self.initialize_add_product_frame()
        self.initialize_delete_product_frame()
        self.initialize_search_product_frame()
        self.initialize_shopping_list_frame()
        self.initialize_product_info_frame()
        self.initialize_manage_orders_frame()
        self.initialize_generate_report_frame()
        self.initialize_check_similarity_frame()
        self.initialize_update_log_frame()

        # Initialize logging
        logging.basicConfig(filename='warehouse_log.txt', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

        # Existing code for initializing the GUI
        self.icon_image = tk.PhotoImage(file='./images/logo.png')
        self.icon_image = self.icon_image.subsample(2)
        self.iconphoto(True, self.icon_image)

        self.product_log_file = "product_log.txt"  # Define the product log file here
        self.product_log = []
        self.product_id_counter = 1

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)




    def initialize_add_product_frame(self):

        self.add_product_frame = tk.LabelFrame(self, text="Add Product", bg='black', fg="cyan")
        self.add_product_frame.grid(row=1, column=0, padx=10, pady=10)
        
        self.product_name_label = tk.Label(self.add_product_frame, text="Product Name:", bg='black', fg="silver")
        self.product_name_label.grid(row=0, column=0, padx=5, pady=5)
        
        self.product_name_entry = tk.Entry(self.add_product_frame)
        self.product_name_entry.grid(row=0, column=1, padx=5, pady=5)
        
        self.quantity_label = tk.Label(self.add_product_frame, text="Product Quantity:", bg="black", fg='silver')
        self.quantity_label.grid(row=1, column=0, padx=5, pady=5)
        
        self.quantity_entry = tk.Entry(self.add_product_frame)
        self.quantity_entry.grid(row=1, column=1, padx=5, pady=5)
        
        self.product_specs_label = tk.Label(self.add_product_frame, text="Product Specifications:", bg='black', fg='silver')
        self.product_specs_label.grid(row=2, column=0, padx=5, pady=5)
        
        self.product_specs_entry = tk.Text(self.add_product_frame, height=1, width=15)
        self.product_specs_entry.grid(row=2, column=1, padx=5, pady=5)
        
        self.add_product_button = tk.Button(self.add_product_frame, text="Add Product", bg="silver", fg="black",
                                            command=self.handle_add_product)
        self.add_product_button.grid(row=3, column=0, columnspan=2, padx=5, pady=5)
        

        
    def handle_add_product(self):
        product_name = self.product_name_entry.get()
        quantity = self.quantity_entry.get()
        specifications = self.product_specs_entry.get("1.0", "end-1c")
    
        # Check if a similar product exists
        existing_product = self.find_existing_product(product_name, specifications.split('\n')[1:])
    
        if existing_product:
            # Ask the user if they want to merge
            merge_decision = messagebox.askyesno("Merge Products", "A similar product already exists. Do you want to merge quantities?")
    
            if merge_decision:
                # Merge products
                new_quantity = int(quantity) + existing_product['quantity']
                if new_quantity <= 5:
                    existing_product['quantity'] = new_quantity
                    existing_product['last_ordered'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    self.save_product_log()
                    messagebox.showinfo("Merge Successful", "Product merged successfully!")
                else:
                    messagebox.showwarning("Merge Not Allowed", "Merging exceeds the maximum quantity limit (5).")
                    return
            else:
                # User chose not to merge, treat it as a new product
                super().add_product(product_name, quantity, specifications)
        else:
            # No existing product found, create a new entry
            super().add_product(product_name, quantity, specifications)
    
        # Clear the input fields in the "Add Product" frame
        self.product_name_entry.delete(0, tk.END)
        self.quantity_entry.delete(0, tk.END)
        self.product_specs_entry.delete("1.0", tk.END)
        
            
    

    def initialize_delete_product_frame(self):
        self.delete_product_frame = tk.LabelFrame(self, text="Delete Product", bg='black', fg='red')
        self.delete_product_frame.grid(row=2, column=0 , padx=10, pady=10)

        self.delete_product_label = tk.Label(self.delete_product_frame, text="Product Name or ID:", bg='black',
                                             fg='silver')
        self.delete_product_label.grid(row=0, column=0, padx=5, pady=5)

        self.delete_product_entry = tk.Entry(self.delete_product_frame)
        self.delete_product_entry.grid(row=0, column=1, padx=5, pady=5)

        self.delete_quantity_label = tk.Label(self.delete_product_frame, text="Delete Quantity:", bg='black',
                                              fg='silver')
        self.delete_quantity_label.grid(row=1, column=0, padx=5, pady=5)

        self.delete_quantity_entry = tk.Entry(self.delete_product_frame)
        self.delete_quantity_entry.grid(row=1, column=1, padx=5, pady=5)

        self.delete_button = tk.Button(self.delete_product_frame, text="Delete Product", bg="silver", fg="black", command=self.handle_delete_product) #, command=self.delete_product
        self.delete_button.grid(row=3, column=0, columnspan=2, padx=5, pady=5)



    def handle_delete_product(self):
        product_identifier = self.delete_product_entry.get()
        delete_input = self.delete_quantity_entry.get()
    
        if not product_identifier:
            messagebox.showinfo("Error", "Please enter a product name or ID.")
            return
    
        if not delete_input:
            messagebox.showinfo("Error", "Please enter a quantity or 'delete'.")
            return
    
        try:
            delete_quantity = int(delete_input)
            delete_quantity_str = str(delete_quantity)  # Convert to string for comparison
        except ValueError:
            if delete_input.lower() == 'delete':
                delete_quantity = None
                delete_quantity_str = 'delete'
            else:
                messagebox.showinfo("Error", "Invalid input. Please enter a valid quantity or 'delete'.")
                return
    
        # Call delete_product with the appropriate arguments
        self.delete_product(product_identifier, delete_quantity_str)
    
        # Clear the input fields after deletion
        self.delete_product_entry.delete(0, tk.END)
        self.delete_quantity_entry.delete(0, tk.END)


    def initialize_search_product_frame(self):
        self.search_product_frame = tk.LabelFrame(self, text="Search Product by Name or ID", bg="black", fg='cyan', padx=10, pady=5)
        self.search_product_frame.grid(row=1, column=1)

        self.search_entry = tk.Entry(self.search_product_frame, width=50)
        self.search_entry.grid(row=0, column=0, padx=(5, 3), pady=(15, 5), sticky="ew")

        self.search_button = tk.Button(self.search_product_frame, text="Search", fg="black", bg='silver', command=self.handle_search_product)
        self.search_button.grid(row=0, column=1, padx=(3, 5), pady=(15, 5), sticky="ew")

        self.power_search_button = tk.Button(self.search_product_frame, text="Power Search", bg="cyan", fg="black", command=self.perform_power_search)
        self.power_search_button.grid(row=4, column=0, columnspan=2, padx=5, pady=5)


    def perform_power_search(self):
        # Call the power_search method and display the results
        products = self.search_power(power_search=True)
        self.display_power_search_results(products)

    def search_power(self, power_search=False):
        # Retrieve all products in the product log
        if power_search:
            return self.product_log
        else:
            return []

    def display_power_search_results(self, products):
        if not products:
            result_text = "No products found."
        else:
            result_text = "\n\n".join([
                f"Product ID: {product['id']}\n"
                f"Product Name: {product['name']}\n"
                f"Quantity: {product['quantity']}\n"
                f"Last Time Ordered: {product['last_ordered']}\n"
                f"Specifications: {product['specifications']}"
                for product in products
            ])

            # Show the products in a simple window centered on the main window
            self.show_scrollable_window("Power Search Results", result_text)

    def show_scrollable_window(self, title, content):
        # Create a new Toplevel window
        scroll_window = tk.Toplevel(self)

        # Set the window title
        scroll_window.title(title)

        # Calculate the center position of the screen if self.master is None
        if self.master:
            main_window_x = self.master.winfo_rootx() + self.master.winfo_width() // 2
            main_window_y = self.master.winfo_rooty() + self.master.winfo_height() // 2
        else:
            main_window_x = scroll_window.winfo_screenwidth() // 2
            main_window_y = scroll_window.winfo_screenheight() // 2

        # Calculate the position to center the new window
        window_width = 600  # Set your desired width
        window_height = 400  # Set your desired height
        window_x = main_window_x - window_width // 2
        window_y = main_window_y - window_height // 2

        # Set the geometry of the new window
        scroll_window.geometry(f"{window_width}x{window_height}+{window_x}+{window_y}")

        # Create a Text widget inside the Toplevel window
        text_widget = tk.Text(scroll_window, wrap=tk.WORD, height=20, width=80)
        text_widget.pack(expand=True, fill="both")

        # Insert the content into the Text widget
        text_widget.insert("insert", content)

    def clear_displayed_results(self):
        # Replace 'product_info_text' with the actual name or reference to your Text widget
        # Example: if you have a Text widget named 'my_product_info_text', use self.my_product_info_text
        self.product_info_text.config(state='normal')  # Set the state to normal before updating
        self.product_info_text.delete(1.0, "end")  # Clear the existing text (remove the '-1c')
        self.product_info_text.config(state='disabled')  # Set the state back to disabled (read-only)



    def initialize_product_info_frame(self):
        self.product_info_frame = tk.LabelFrame(self, text="Display Product Information", bg='black', fg='cyan')
        self.product_info_frame.grid(row=2, column=1)

        self.product_info_text = tk.Text(self.product_info_frame, height=8, width=50 , bg="black", fg='cyan')
        self.product_info_text.pack(padx=10, pady=10)

    def handle_search_product(self):
        product_identifier = self.search_entry.get()
        product = self.search_product(product_identifier)

        if product:
            product_info = self.format_product_details(product)
            self.product_info_text.delete(1.0, tk.END)
            self.product_info_text.insert(tk.END, product_info)
        else:
            self.product_info_text.delete(1.0, tk.END)
            self.product_info_text.insert(tk.END, "Product not found.")




    def initialize_shopping_list_frame(self):
        self.shopping_list_frame = tk.LabelFrame(self, text="Shopping List", bg='black', fg='cyan', padx=10, pady=10)
        self.shopping_list_frame.grid(row=2, column=2)
        
        self.shopping_list_text = tk.Text(self.shopping_list_frame, height=5, width=35)
        self.shopping_list_text.pack(padx=10, pady=10)
        
        self.buttons_frame = tk.Frame(self.shopping_list_frame, bg='black')
        self.buttons_frame.pack()
        
        self.display_shopping_list_button = tk.Button(self.buttons_frame, text="View Shopping List", fg='black', bg='silver', command=self.display_shopping_list)
        self.display_shopping_list_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.download_shopping_list_button = tk.Button(self.buttons_frame, text="Generate Shopping List", fg='black', bg='silver', command=self.download_shopping_list_pdf)
        self.download_shopping_list_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.buttons_frame.pack_configure(expand=True)
        self.buttons_frame.pack_configure(anchor='center')

    def display_shopping_list(self):
        # Clear the shopping list text widget
        self.shopping_list_text.delete(1.0, tk.END)
    
        # Check for products with zero quantities
        zero_quantity_products = [product for product in self.product_log if product['quantity'] == 0]
    
        # Display the products in the shopping list text widget
        if zero_quantity_products:
            for product in zero_quantity_products:
                product_info = (
                    f"Product ID: {product['id']}\n"
                    f"Product Name: {product['name']}\n"
                    f"Quantity: {product['quantity']}\n\n"
                )
                self.shopping_list_text.insert(tk.END, product_info)
        else:
            self.shopping_list_text.insert(tk.END, "No products with zero quantity.")
    
    def download_shopping_list_pdf(self):
        # Create a ReportGenerator instance with the current products data
        report_generator = ReportGenerator(self.product_log)
    
        # Generate the shopping list report
        report_generator.generate_shopping_list_pdf()
    
        # Show a success message
        messagebox.showinfo("Success", "Shopping list generated successfully!")

    def get_shopping_list(self):
        # Get the shopping list as a formatted string
        shopping_list = ""
        for product in self.product_log:
            if product['quantity'] > 0:
                shopping_list += f"{product['id']} | {product['name']} | Quantity: {product['quantity']}\n"
        return shopping_list

# repair 
    
    def initialize_manage_orders_frame(self):
        self.manage_orders_frame = tk.LabelFrame(self, text="Manage Orders", bg='black', fg='cyan', padx=10, pady=10)
        self.manage_orders_frame.grid(row=3, column=1)

        self.initialize_text_widget()
        self.initialize_buttons()

    def initialize_text_widget(self):
        self.text_widget = tk.Text(self.manage_orders_frame, state='disabled', bg='black', fg='cyan', height=3, width=45)
        self.text_widget.pack(padx=10, pady=10)

    def initialize_buttons(self):
        button_frame1 = tk.Frame(self.manage_orders_frame, bg='black')
        button_frame1.pack()

        buttons_data = [
            ("Add Order", self.add_order),
            ("Remove Order", self.remove_order),
            ("Change Order Status", self.change_order_status),
            ("Orders JSON", self.load_orders_from_json),  # Add this button
            ("Simulation", self.simulate_orders)  # Add the Simulation button
        ]

        for button_text, command_func in buttons_data:
            button = tk.Button(button_frame1, text=button_text, bg='silver', fg='black', command=command_func)
            button.pack(side=tk.LEFT, padx=5, pady=5)


    def simulate_orders(self):
        # Ask for confirmation before starting the simulation
        confirmed = messagebox.askyesno("Start Simulation", "Do you want to start the simulation?")
        if not confirmed:
            return
    
        # Iterate through each order in ascending order
        for i in range(len(self.orders)):
            order = self.orders[i]
            order_id = order.get("id")
    
            # Display the order as "in the collection queue" with a delay
            self.after(1000 * (i + 1), lambda oid=order_id: self.display_order_in_collection_queue(oid))
    
            # Update status to "in the collection queue" with a delay
            self.after(2000 * (i + 1), lambda oid=order_id: self.update_order_status_by_id(oid, "in the collection queue"))
    
            # Display the order as "collected" with a delay
            time_collected = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.after(3000 * (i + 1), lambda oid=order_id, tc=time_collected: self.update_and_show(oid, "collected", tc))
    
        # Display a message when all orders are collected
        last_order_index = len(self.orders) - 1
        self.after(4000 * (last_order_index + 1), self.show_all_orders_collected_message)
    
    def display_order_in_collection_queue(self, order_id):
        # Display the order as "in the collection queue" on the GUI
        messagebox.showinfo("Order in Collection Queue", f"Order {order_id} is in the collection queue!")
    
        # Log the order status change with the time_collected parameter
        time_collected = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_order_status_change(order_id, time_collected=time_collected)
    
        # Automatically display the updated list of orders
        self.display_orders()
        
    
    
    def display_order_as_collected(self, order_id):
        # Display the order as "collected" on the GUI
        messagebox.showinfo("Order Collected", f"Order {order_id} has been collected!")
    
        # Automatically display the updated list of orders
        self.display_orders()

    def show_all_orders_collected_message(self):
        # Log the completion of the simulation to the update log file
        self.log_to_file("update_log.txt", "Simulation complete.\n\n------------------------------------------")
        
        # Save data to the product log file
        self.save_to_product_log()
        
        # Automatically display the updated list of orders
        self.display_orders()


    def load_orders_from_json(self):
        # Open a file dialog to select the JSON file
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
    
        if not file_path:
            return  # User canceled the file dialog
    
        try:
            # Read the JSON file
            with open(file_path, "r") as json_file:
                orders_data = json.load(json_file)
    
            # Clear existing orders and load new orders from the JSON file
            self.clear_orders()
            self.load_orders(orders_data)
    
            # Display a message indicating successful loading
            messagebox.showinfo("Orders Loaded", f"Orders loaded successfully from {file_path}")
        except Exception as e:
            # Display an error message if there is any issue with loading the file
            messagebox.showerror("Error", f"Error loading orders from JSON file:\n{str(e)}")
    
    # Add this method to clear existing orders
    def clear_orders(self):
        self.orders = []
        self.removed_orders = []
        self.display_orders()
    
    # Add this method to load orders from JSON data
    def load_orders(self, orders_data):
        for order_info in orders_data:
            order_id = order_info.get("id")
            products_info = order_info.get("products")
    
            if order_id and products_info:
                new_order = {
                    "id": order_id,
                    "status": "registered",
                    "time_accepted": "",
                    "time_collected": "",
                    "quantity": sum(product.get("quantity", 0) for product in products_info),
                    "item": {
                        "name": ", ".join(product.get("name", "") for product in products_info),
                        "id": ", ".join(product.get("id", "") for product in products_info),
                        "last_ordered": "",
                        "specifications": "",
                    },
                }
    
                self.orders.append(new_order)

    # Display the loaded orders on the screen
        self.display_orders()

    def add_order(self):
        num_products = simpledialog.askinteger("Add Order", "How many products do you want to add?", parent=self)
    
        if not self.is_valid_quantity(num_products):
            return
    
        for _ in range(num_products):
            order_id, order_item, order_quantity = self.get_order_details()
    
            if order_id is None or order_item is None or order_quantity is None:
                return
    
            product = self.get_product(order_item)
    
            if product is None or not self.is_enough_stock(product, order_quantity):
                return
    
            new_order = self.create_order(order_id, product, order_quantity)
            self.update_stock(product, order_quantity)
    
            self.orders.append(new_order)
    
            # Schedule the registration after a 1-second delay
            self.after(1000, lambda: self.register_order(order_id))

    def is_valid_quantity(self, quantity):
        try:
            quantity = int(quantity)  # Try converting to an integer
            return quantity is not None and quantity > 0
        except ValueError:
            return False  # Return False if conversion to integer fails

    def get_order_details(self):
        order_id = self.generate_order_id()
        order_item = simpledialog.askstring("Add Order", "Enter product ID or name:", parent=self)

        if not order_item:
            messagebox.showinfo("Error", "Please enter a product ID or name for the order.")
            return None, None, None

        order_quantity = simpledialog.askinteger("Add Order", f"Enter quantity for product {order_item}:", parent=self)

        if not self.is_valid_quantity(order_quantity):
            return None, None, None

        return order_id, order_item, order_quantity

    def get_product(self, order_item):
        return next(
            (product for product in self.product_log if product['id'] == order_item or product['name'] == order_item), None)

    def is_enough_stock(self, product, order_quantity):
        if product['quantity'] < order_quantity:
            messagebox.showinfo("Error", f"Not enough stock for product '{product['name']}'. Cannot add the order.")
            return False
        return True

    def create_order(self, order_id, product, order_quantity):
        return {
            'id': order_id,
            'item': product,
            'quantity': order_quantity,
            'status': 'registered'
        }

    def update_stock(self, product, order_quantity):
        product['quantity'] -= order_quantity

    def generate_order_id(self):
        return f"ORD-{str(len(self.orders) + 1).zfill(3)}"

    def show_order_added_message(self, order_id, new_order):
        messagebox.showinfo("Order Added", f"Order {order_id} added successfully!\n{new_order['item']['name']}")

    def remove_order(self):
        order_id_to_remove = simpledialog.askstring("Remove Order", "Enter the order ID to remove:", parent=self)

        if not order_id_to_remove:
            messagebox.showinfo("Error", "Please enter an order ID to remove.")
            return

        order_to_remove = next((order for order in self.orders if order['id'] == order_id_to_remove), None)

        if order_to_remove is None:
            messagebox.showinfo("Error", f"Order with ID '{order_id_to_remove}' not found.")
            return

        self.handle_order_removal(order_to_remove)

    def handle_order_removal(self, order_to_remove):
        product = order_to_remove.get('item')

        if product is not None:
            product['quantity'] += order_to_remove['quantity']

        self.orders.remove(order_to_remove)

        self.show_order_removed_message(order_to_remove)
        self.display_orders()

    def remove_order_by_id(self, order_id):
        order_to_remove = next((order for order in self.orders if order.get("id") == order_id), None)
        
        if order_to_remove:
            # Add the order quantity back to the product in the product_log
            product = order_to_remove.get('item')
    
            if product is not None:
                product['quantity'] += order_to_remove['quantity']
    
            # Remove the order from the list of orders
            self.orders.remove(order_to_remove)
    
            # Display a message indicating the successful removal of the order
            messagebox.showinfo("Order Removed", f"Order with ID '{order_id}' removed successfully!")
    
            # Automatically display the updated list of orders
            self.display_orders()
    
            # Force focus back to the main Tkinter window
            self.focus_force()
            # Update the Tkinter event queue to ensure the next message box is displayed correctly
            self.update_idletasks()
        else:
            messagebox.showinfo("Error", f"Order with ID '{order_id}' not found.")

    def show_order_removed_message(self, removed_order):
        order_id = removed_order.get("id")
        messagebox.showinfo("Order Removed", f"Order with ID '{order_id}' removed successfully!")


    def register_order(self, order_id):
        order = next((o for o in self.orders if o.get("id") == order_id), None)
    
        if order:
            order["time_accepted"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            order["status"] = "registered"
    
            # Display a message indicating the successful registration
            self.show_status_changed_message(order_id, order["status"])
    
            # Log the order status change
            self.log_order_status_change(order_id)
    
            # Automatically display the updated list of orders
            self.display_orders()
        
    
    
    def change_order_status(self):
        order_id = self.show_input_box("Enter Order ID", "Please enter the Order ID:")
    
        if not order_id:
            return
    
        order = next((o for o in self.orders if o.get("id") == order_id), None)
    
        if order:
            # Update the order status to "in the collection queue" and log the changes
            if order.get("status") == "registered":
                # If the status is "registered," simulate a 3-second delay before changing to "in the collection queue"
                self.after(3000, lambda: self.update_and_show(order_id, "in the collection queue"))
            elif order.get("status") == "in the collection queue":
                # If the status is "in the collection queue," simulate a 3-second delay before changing to "collected"
                time_collected = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.after(3000, lambda: self.update_and_show(order_id, "collected", time_collected))
            else:
                # If the status is "collected," show the final status changed message and remove the order
                self.show_and_remove(order_id, time_collected)
        
    def update_and_show(self, order_id, new_status, time_collected=None):
        # Update the order status
        order = next((o for o in self.orders if o.get("id") == order_id), None)
        if order:
            order["status"] = new_status
    
        # If the new status is "collected," log the time_collected
        if new_status == "collected":
            self.log_order_status_change(order_id, time_collected)
    
        # Display the status changed message
        self.show_status_changed_message(order_id, new_status)
    
        # If the new status is "collected," remove the order immediately
        if new_status == "collected":
            self.show_and_remove(order_id, time_collected)
    
        # Automatically update the displayed orders on the screen
        self.display_orders()
    
    def show_and_remove(self, order_id, time_collected=None):
        # Display the final removal message after the order has been removed
        self.remove_collected_order(order_id)
    
        # Log the order status change with the time_collected parameter
        self.log_order_status_change(order_id, time_collected)

    def update_order_status_by_id(self, order_id, new_status):
        order = next((o for o in self.orders if o.get("id") == order_id), None)
        if order:
            # Update the order status
            order["status"] = new_status
    
    def remove_collected_order_by_id(self, order_id):
        order = next((o for o in self.orders if o.get("id") == order_id), None)
        if order and order.get("status") == "collected":
            # If the order is collected, remove it from the list
            self.removed_orders.append(order)
            self.orders.remove(order)
            # Automatically display the updated list of orders
            self.display_orders()
            # Display a message indicating the successful removal of the order
            messagebox.showinfo("Order Removed", f"Order with ID '{order_id}' removed successfully!")
        
    def update_order_status(self, order,new_status):
        if order.get("status") == "registered":
            order["time_accepted"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            order["status"] = "in the collection queue"
        elif order.get("status") == "in the collection queue":
            order["time_collected"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            order["status"] = "collected"
    
        self.log_order_status_change(order['id'], time_collected=order['time_collected'])
    
        # Automatically update the displayed orders on the screen
        self.display_orders()

    def show_status_changed_message(self, order_id, new_status):
        messagebox.showinfo("Status Changed", f"Order {order_id} status changed to '{new_status}' successfully!")
    
    def log_order_status_change(self, order_id, time_collected=None):
        order = next((o for o in self.orders if o.get("id") == order_id), None)
    
        if order:
            time_accepted = self.format_time(order.get('time_accepted'))
            time_collected = self.format_time(time_collected) if time_collected else ""
            order_item_info = f"Item: {order['item']['name']}"
    
            log_message = (
                f"Order ID: {order_id}\n"
                f"Time Accepted: {time_accepted}\n"
                f"Time Collected: {time_collected}\n"
                f"Quantity: {order['quantity']}\n"
                f"{order_item_info}\n"
                f"Update Date and Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                f"------------------------------------------"
            )
    
            self.log_to_file("update_log.txt", log_message)
    
            # Automatically update the displayed orders on the screen
            self.display_orders()
        
    def format_time(self, time_str):
        if time_str:
            return datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")
        return ""

    def remove_collected_order(self, order_id, time_collected=None):
        order = next((o for o in self.orders if o.get("id") == order_id), None)
        if order and order.get("status") == "collected":
            # If the order is collected, remove it from the list
            self.removed_orders.append(order)
            self.orders.remove(order)
            # Automatically display the updated list of orders
            self.display_orders()
            # Display a message indicating the successful removal of the order
            messagebox.showinfo("Order Removed", f"Order with ID '{order_id}' removed successfully!")
    
            if time_collected:
                # Log the time collected in the update log file
                self.log_order_status_change(order_id, time_collected)

    def display_orders(self):
        orders_text = "\n\n".join([
            f"Order ID: {order['id']}\n"
            f"Item: \n  Name: {order['item']['name']}\n  ID: {order['item']['id']}\n  Last Ordered: {order['item']['last_ordered']}\n  Specifications: {order['item']['specifications'].strip()}\n Quantity: {order['quantity']}\n Status: {order['status']}"
            for order in self.orders])

        self.update_text_widget(orders_text)

    def update_text_widget(self, orders_text):
        self.text_widget.config(state='normal')
        self.text_widget.delete(1.0, "end-1c")
        self.text_widget.insert("insert", orders_text)
        self.text_widget.config(state='disabled')

    def log_to_file(self, filename, log_message):
        with open(filename, "a") as log_file:
            log_file.write(log_message)

    def show_input_box(self, title, prompt):
        user_input = simpledialog.askstring(title, prompt, parent=self)
    
        if user_input is not None:
            return user_input.strip()  # Strip any leading/trailing whitespaces
        return user_input   


# repair


    def initialize_generate_report_frame(self):

        self.generate_report_frame = tk.LabelFrame(self, text="Generate Report", bg='black', fg="cyan")
        self.generate_report_frame.grid(row=3, column=0, padx=10, pady=10)

        self.black_frame = tk.Frame(self.generate_report_frame, bg="black")
        self.black_frame.pack(padx=6, pady=6)

        report_image = Image.open("images/pdf.png")
        report_image = report_image.resize((30, 30))
        report_image = ImageTk.PhotoImage(report_image)

        self.black_frame.pack()

        self.image_label = tk.Label(self.black_frame, image=report_image, bg="black")
        self.image_label.image = report_image
        self.image_label.pack(pady=10)

        self.generate_report_button = tk.Button(self.black_frame, text="Generate Report", bg="silver", command=self.handle_generate_report)
        self.generate_report_button.pack(pady=10)


    def handle_generate_report(self):
        # Create a ReportGenerator instance with the current products data
        report_generator = ReportGenerator(self.product_log)
    
        # Generate the product report (you can specify a filename if needed)
        report_generator.generate_product_report()
    
        # Show a success message
        messagebox.showinfo("Success", "Product report generated successfully!")
        

    def initialize_check_similarity_frame(self):
        self.check_similarity_frame = tk.LabelFrame(self, text="Check Similarity", bg='black', fg='cyan', padx=10, pady=10)
        self.check_similarity_frame.grid(row=1, column=2)
    
        self.check_similarity_text = tk.Text(self.check_similarity_frame, height=3, width=35)
        self.check_similarity_text.pack(padx=10, pady=10)
    
        self.check_similarity_button = tk.Button(self.check_similarity_frame, text="Check Similarity", fg="black", bg='silver', command=self.check_similarity)
        self.check_similarity_button.pack(padx=1, pady=1)

    def check_similarity(self):
        selected_specifications = self.check_similarity_text.get("1.0", tk.END).strip()

        if not selected_specifications:
            messagebox.showinfo("Error", "Please enter specifications for similarity check.")
            return

        products = self.product_log.copy()

        exact_matches, non_exact_matches = self.process_similarity(products, selected_specifications)

        result_text = self.format_results(exact_matches, non_exact_matches)

        self.product_info_text.delete(1.0, tk.END)
        self.product_info_text.insert(tk.END, result_text)

    def process_similarity(self, products, selected_specifications):
        exact_matches = []
        non_exact_matches = []

        for product in products:
            similarity_score = self.calculate_similarity(selected_specifications, product['specifications'])

            if similarity_score == 100:
                exact_matches.append(product)
            elif similarity_score >= 80:
                non_exact_matches.append(product)

        non_exact_matches.sort(key=lambda product: self.calculate_similarity(selected_specifications, product['specifications']), reverse=True)

        return exact_matches, non_exact_matches

    def calculate_similarity(self, spec_a, spec_b):
        words_a = re.findall(r'\b\w+\b', spec_a)
        words_b = re.findall(r'\b\w+\b', spec_b)

        similar_words_count = sum(1 for word_a in words_a if any(fuzz.ratio(word_a, word_b) >= 80 for word_b in words_b))
        total_words_count = len(words_a)

        if total_words_count > 0:
            similarity_score = (similar_words_count / total_words_count) * 100
        else:
            similarity_score = 0

        return similarity_score

    def format_results(self, exact_matches, non_exact_matches):
        result_text = ""

        for product in exact_matches:
            result_text += f"\n Product ID: {product['id']} \n Product Name: {product['name']} \n Similarity Score: 100% \n"
            result_text += "-------------------------"

        for product in non_exact_matches:
            similarity_score = self.calculate_similarity(product['specifications'])
            result_text += f"Product ID: {product['id']} | Product Name: {product['name']} | Similarity Score: {similarity_score:.2f}%\n"
            result_text += (
                f"Quantity: {product['quantity']}\n"
                f"Last Time Ordered: {product['last_ordered']}\n"
                f"Specifications: {product['specifications'][1:]}\n\n"
            )

        return result_text


    def initialize_update_log_frame(self):
        self.update_log_frame = tk.LabelFrame(self, text="Update Log File", bg='black', fg='cyan', padx=10, pady=10)
        self.update_log_frame.grid(row=3, column=2)

        img_label = self.create_image_label()
        update_log_button = self.create_update_log_button()

        self.pack_widgets(img_label, update_log_button)

    def create_image_label(self):
        img = Image.open("images/update.png").resize((40, 40))
        img = ImageTk.PhotoImage(img)
        img_label = tk.Label(self.update_log_frame, bg='black', image=img)
        img_label.image = img  # Keep a reference to the image to prevent garbage collection
        img_label.pack()
        return img_label

    def create_update_log_button(self):
        return Button(self.update_log_frame, text="Update Log File", bg='silver', fg='black', command=self.show_update_log)

    def pack_widgets(self, *widgets):
        for widget in widgets:
            widget.pack(pady=10)

    def show_update_log(self):
        # Create a new thread to perform the file read operation
        threading.Thread(target=self.read_and_display_log).start()

    def read_and_display_log(self):
        log_content = self.read_log_file("update_log.txt")

        # Execute the Tkinter GUI update on the main thread
        self.after(0, lambda: self.display_log_content(log_content))

    def display_log_content(self, log_content):
        log_window = Toplevel(self)
        log_window.title("Update Log")
        log_window.geometry("660x400")
    
        center_x, center_y = self.calculate_center_position(log_window)
        log_window.geometry(f"+{center_x}+{center_y}")
    
        log_text, log_scrollbar = self.create_log_text_and_scrollbar(log_window)
        self.configure_log_text(log_text, log_scrollbar)
        self.insert_log_content(log_text, log_content)
    
        # Make the Text widget read-only
        log_text.config(state="disabled")
        log_text.focus_set()
    
        # Run the Tkinter event loop
        log_window.mainloop()

    def calculate_center_position(self, log_window):
        root_x, root_y = self.winfo_x(), self.winfo_y()
        return root_x + (self.winfo_width() - 700) // 2, root_y + (self.winfo_height() - 400) // 2

    def create_log_text_and_scrollbar(self, log_window):
        log_text = tk.Text(log_window, wrap="none", height=20, width=80)
        log_scrollbar = tk.Scrollbar(log_window, command=log_text.yview)
        return log_text, log_scrollbar

    def configure_log_text(self, log_text, log_scrollbar):
        log_text.config(yscrollcommand=log_scrollbar.set)
        log_text.pack(side="left", fill="y")
        log_scrollbar.pack(side="right", fill="y")
        log_text['yscrollcommand'] = log_scrollbar.set

    def insert_log_content(self, log_text, content):
        log_text.insert("insert", "\n\nUpdate Log:\n")
    
        # Split the log content into individual log entries
        log_entries = content.split("------------------------------------------")
    
        # Iterate through each log entry and insert it into the Text widget
        for entry in log_entries:
            entry = entry.strip()
            if entry:  # Skip empty entries
                # Extract "Time Collected" information
                time_collected_match = re.search(r"Time Collected: (.+?)$", entry, re.MULTILINE)
                if time_collected_match:
                    time_collected = time_collected_match.group(1)
                    entry = entry.replace(time_collected, self.format_time(time_collected))
    
                log_text.insert("insert", entry)
                log_text.insert("insert", "\n\n")  # Add a line gap after each log entr

    def read_log_file(self, filename):
        log_content = ""
        try:
            log_path = os.path.join(os.getcwd(), filename)
            with open(log_path, "r") as file:
                log_content = file.read()
        except FileNotFoundError:
            log_content = f"{filename} not found."
        return log_content

    def on_close(self):
        # Clear the update log content
        self.clear_update_log()

        # Close the application
        self.destroy()

    def clear_update_log(self):
        log_filename = "update_log.txt"
        try:
            log_path = os.path.join(os.getcwd(), log_filename)
            with open(log_path, "w"):
                pass
        except FileNotFoundError:
            pass        


        
    def initialize_play_gif_frame(self):
        # Existing code for initializing the gif frame
        self.play_gif_frame = tk.Frame(self, bg='black')
        self.play_gif_frame.grid(row=0, column=1, padx=(60, 10), pady=0)

        self.asus_label = tk.Label(self.play_gif_frame, bg='black')
        self.asus_label.pack()

        # Create an instance of the GifPlayer class, passing the parent frame
        gif_player = GifPlayer(self.play_gif_frame, 'images/motion.gif', 370, 220)
        gif_player.pack() 


class GifPlayer(tk.Label):
    def __init__(self, parent, gif_path, width, height):
        super().__init__(parent, bg='black')
        self.width = width
        self.height = height
        self.load_gif(gif_path)

    def load_gif(self, gif_path):
        cap = cv2.VideoCapture(gif_path)

        def show_frame():
            ret, frame = cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = Image.fromarray(frame)
                photo_image = ImageTk.PhotoImage(frame.resize((self.width, self.height)))
                self.configure(image=photo_image)
                self.image = photo_image  # Keep a reference to the image
                self.after(10, show_frame)
            else:
                # Reset the video capture to play the gif in a loop
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                show_frame()

        show_frame()




def main():

    warehouse_app = WarehouseGUI()
    warehouse_app.mainloop()

if __name__ == "__main__":
    main()

