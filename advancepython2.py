
# This is part 1.2

import re
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import cv2
from datetime import datetime
import csv
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from fuzzywuzzy import fuzz
from tkinter import Button, simpledialog
import logging
from tkinter import Toplevel
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
from PIL import Image, ImageTk  
from tkinter import Button,Toplevel
import threading
import random
from datetime import datetime, timedelta


class AsusROG_WarehouseApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.configure(bg="black")
        self.title("ASUS ROG Warehouse Pro")


class ProductManagement(AsusROG_WarehouseApp):
    def __init__(self):
        super().__init__()
        self.product_log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "product_log.csv")
        self.product_log = []
        self.product_id_counter = 1
        self.products = {}
        self.loadProductLogFile()

    def updateProductsDictionary(self):
        self.products = {item.get('id', ''): item for item in self.product_log}

    def locateProducts(self, product_name, specifications_list):
        for product_id, details in self.products.items():
            existing_specifications_list = details['specifications'][1:].split('\n')
            if details['name'] == product_name and self.compareSpecifications(specifications_list, existing_specifications_list):
                return details
        return None

    def compareSpecifications(self, spec_list1, spec_list2):
        formatted_spec_str1 = "\n".join(spec_list1).strip()
        formatted_spec_str2 = "\n".join(spec_list2).strip()
        return fuzz.token_set_ratio(formatted_spec_str1, formatted_spec_str2) == 100

    def addProduct(self, product_name, quantity, specifications):
        if not self.validProductName(product_name):
            self.show_message("Invalid Product Name", "Please add a product with the 'Asus ROG' prefix.")
            return

        if not self.validProductQuantity(quantity):
            self.show_message("Invalid Quantity", "Please enter a quantity between 1 and 5.")
            return

        product_id = self.generateProductID()
        specifications_list = specifications.split('\n')
        formatted_specifications = "\n".join([spec.strip() for spec in specifications_list])

        # Feature: Generate the last ordered timestamp with a random time
        last_ordered = self.generateRandomTimestamp()

        existing_product = self.locateProducts(product_name, specifications_list)
        if existing_product:
            self.manageExistingProducts(existing_product, quantity, formatted_specifications, last_ordered)
        else:
            self.createNewProduct(product_id, product_name, quantity, formatted_specifications, last_ordered)

    def generateRandomTimestamp(self):
        current_time = datetime.now()
        random_days = random.randint(1, 30)
        random_hours = random.randint(0, 23)
        random_minutes = random.randint(0, 59)
        random_seconds = random.randint(0, 59)

        random_time = current_time - timedelta(days=random_days, hours=random_hours, minutes=random_minutes, seconds=random_seconds)

        formatted_timestamp = random_time.strftime("%Y-%m-%d %H:%M:%S")

        return formatted_timestamp

    def validProductName(self, product_name):
        return product_name.lower().startswith("asus rog")

    def validProductQuantity(self, quantity):
        return quantity.isdigit() and 1 <= int(quantity) <= 5

    def generateProductID(self):
        product_id = f"ROG-{str(self.product_id_counter).zfill(3)}"
        return product_id

    def manageExistingProducts(self, existing_product, quantity, formatted_specifications, last_ordered):
        user_response = self.show_confirmation("Merge Products", f"A product with the name '{existing_product['name']}' already exists. Do you want to merge quantities?")
        if user_response:
            self.mergeProductDetails(existing_product, quantity, last_ordered)
        else:
            # User chose not to merge, treat it as a new product
            pass

    def mergeProductDetails(self, existing_product, quantity, last_ordered):
        new_quantity = int(quantity) + existing_product['quantity']
        if new_quantity > 5:
            self.manageMergingLimit(existing_product)
        else:
            existing_product['quantity'] = new_quantity
            existing_product['last_ordered'] = last_ordered
            self.saveProductLogFile()
            self.show_message("Merge Successful", "Product merged successfully!")

    def manageMergingLimit(self, existing_product):
        merge_response = self.show_confirmation("Merge Not Allowed", "Merging exceeds the maximum quantity limit (5). Do you want to create a new product ID?")
        if merge_response:
            product_id = self.generateProductID()
            product_name = existing_product.get('name', '')  # Replace '' with a default value if 'name' is not present
            quantity = existing_product.get('quantity', 0)    # Replace 0 with a default value if 'quantity' is not present
            formatted_specifications = existing_product.get('specifications', '')
            last_ordered = existing_product.get('last_ordered', '')
    
            product_data = self.createProductData(product_id, product_name, quantity, formatted_specifications, last_ordered)
            self.product_log.append(product_data)
            self.saveProductLogFile()
            self.show_message("Success", "New product added successfully!")

    def createNewProduct(self, product_id, product_name, quantity, formatted_specifications, last_ordered):
        product_data = self.createProductData(product_id, product_name, quantity, formatted_specifications, last_ordered)
        self.product_log.append(product_data)
        self.product_id_counter += 1
        self.saveProductLogFile()
        self.show_message("Success", "Product added successfully!")

    def createProductData(self, product_id, product_name, quantity, formatted_specifications, last_ordered):
        return {
            'id': product_id,
            'name': product_name,
            'quantity': int(quantity),
            'specifications': f"\n{formatted_specifications}",
            'last_ordered': last_ordered
        }

    def deleteProduct(self, product_identifier, delete_quantity):
        product = self.findProduct(product_identifier)
        if product:
            self.updateQuantity(product, delete_quantity)
            self.saveProductLogFile()
            self.show_message("Deletion", f"Product {product['name']} successfully updated.")

    def findProduct(self, product_identifier):
        for item in self.product_log:
            if product_identifier.lower() in [item['id'].lower(), item['name'].lower()]:
                return item
        return None

    def updateQuantity(self, product, delete_quantity):
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

    def loadProductLogFile(self):
        try:
            with open(self.product_log_file, 'r') as file:
                lines = file.readlines()
                self.product_log = [line.strip().split(';') for line in lines]
        except FileNotFoundError:
            # If the file doesn't exist yet, initialize an empty product log
            self.product_log = []

    def saveProductLogFile(self):
        # Save the product log to a text file with a custom format
        with open(self.product_log_file, 'w') as file:
            for product in self.product_log:
                file.write(';'.join(map(str, product)) + '\n')

        # Update the products dictionary
        self.updateProductDictionary()

        self.updateProductsDictionary()

    def show_message(self, title, message):
        messagebox.showinfo(title, message)

    def show_confirmation(self, title, message):
        return messagebox.askyesno(title, message)



 

class SearchProductManagement(ProductManagement):
    def __init__(self):
        super().__init__()

    def searchProduct(self, product_identifier):
        product = self.findProduct(product_identifier)
        if product:
            return self.productDetailsLayout(product)
        return None

    def searchProductConcurrently(self, product_identifier):
        # Example of introducing parallelism using concurrent.futures.ThreadPoolExecutor
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(self.findProduct, product_identifier)
            product = future.result()

        if product:
            return self.productDetailsLayout(product)
        return None

    def productDetailsLayout(self, product):
        specifications = "\n".join(spec.strip() for spec in product['specifications'].split('\n') if spec.strip())
        return {
            'id': product['id'],
            'name': product['name'],
            'quantity': product['quantity'],
            'last_ordered': product['last_ordered'],
            'specifications': specifications
        }

    def findProduct(self, product_identifier):
        for item in self.product_log:
            if product_identifier.lower() in [item['id'].lower(), item['name'].lower()]:
                return item
        return None
    
class GenerateReportPDF:
    def __init__(self, products):
        self.products = products

    def createShoppingList(self, filename="shopping_list.pdf"):
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

    def createProductReport(self, filename="product_report.pdf"):
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

class WarehouseMangerGUI(SearchProductManagement):
    def __init__(self):
        super().__init__()
        self.orders = []
        self.orders_displayed = []
        self.removed_orders = []
        self.product_text = None  # Initialize product_text attribute
        self.protocol("WM_DELETE_WINDOW", self.onClose)
        self.power_search_active = False  # Initialize the power_search_active variable
        # self.removed_orders = []  # Initialize removed_orders as an empty list

        # Initialize all frames
        self.launchGIF_Frame()
        self.startAddProductFrame()
        self.startDeleteProductFrame()
        self.startSearchProductFrame()
        self.startShoppingListFrame()
        self.startProductInformationFrame()
        self.startManageOrdersFrame()
        self.startGenerateReportFrame()
        self.startCheckSimilarityFrame()
        self.startUpdateLogFrame()

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




    def startAddProductFrame(self):

        self.addProduct_frame = tk.LabelFrame(self, text="Add Product", bg='black', fg="cyan")
        self.addProduct_frame.grid(row=1, column=0, padx=10, pady=10)
        
        self.product_name_label = tk.Label(self.addProduct_frame, text="Product Name:", bg='black', fg="silver")
        self.product_name_label.grid(row=0, column=0, padx=5, pady=5)
        
        self.product_name_entry = tk.Entry(self.addProduct_frame)
        self.product_name_entry.grid(row=0, column=1, padx=5, pady=5)
        
        self.quantity_label = tk.Label(self.addProduct_frame, text="Product Quantity:", bg="black", fg='silver')
        self.quantity_label.grid(row=1, column=0, padx=5, pady=5)
        
        self.quantity_entry = tk.Entry(self.addProduct_frame)
        self.quantity_entry.grid(row=1, column=1, padx=5, pady=5)
        
        self.product_specs_label = tk.Label(self.addProduct_frame, text="Product Specifications:", bg='black', fg='silver')
        self.product_specs_label.grid(row=2, column=0, padx=5, pady=5)
        
        self.product_specs_entry = tk.Text(self.addProduct_frame, height=1, width=15)
        self.product_specs_entry.grid(row=2, column=1, padx=5, pady=5)
        
        self.addProduct_button = tk.Button(self.addProduct_frame, text="Add Product", bg="silver", fg="black",
                                            command=self. addProductManager)
        self.addProduct_button.grid(row=3, column=0, columnspan=2, padx=5, pady=5)
        

        
    def addProductManager(self):
        product_name = self.product_name_entry.get()
        quantity = self.quantity_entry.get()
        specifications = self.product_specs_entry.get("1.0", "end-1c")
    
        # Check if a similar product exists
        existing_product = self.locateProducts(product_name, specifications.split('\n')[1:])
    
        if existing_product:
            # Ask the user if they want to merge
            merge_decision = messagebox.askyesno("Merge Products", "A similar product already exists. Do you want to merge quantities?")
    
            if merge_decision:
                # Merge products
                new_quantity = int(quantity) + existing_product['quantity']
                if new_quantity <= 5:
                    existing_product['quantity'] = new_quantity
                    existing_product['last_ordered'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    self.saveProductLogFile()
                    messagebox.showinfo("Merge Successful", "Product merged successfully!")
                else:
                    messagebox.showwarning("Merge Not Allowed", "Merging exceeds the maximum quantity limit (5).")
                    return
            else:
                # User chose not to merge, treat it as a new product
                super().addProduct(product_name, quantity, specifications)
        else:
            # No existing product found, create a new entry
            super().addProduct(product_name, quantity, specifications)
    
        # Clear the input fields in the "Add Product" frame
        self.product_name_entry.delete(0, tk.END)
        self.quantity_entry.delete(0, tk.END)
        self.product_specs_entry.delete("1.0", tk.END)
        
            
    

    def startDeleteProductFrame(self):
        self.deleteProduct_frame = tk.LabelFrame(self, text="Delete Product", bg='black', fg='red')
        self.deleteProduct_frame.grid(row=2, column=0 , padx=10, pady=10)

        self.deleteProduct_label = tk.Label(self.deleteProduct_frame, text="Product Name or ID:", bg='black',
                                             fg='silver')
        self.deleteProduct_label.grid(row=0, column=0, padx=5, pady=5)

        self.deleteProduct_entry = tk.Entry(self.deleteProduct_frame)
        self.deleteProduct_entry.grid(row=0, column=1, padx=5, pady=5)

        self.delete_quantity_label = tk.Label(self.deleteProduct_frame, text="Delete Quantity:", bg='black',
                                              fg='silver')
        self.delete_quantity_label.grid(row=1, column=0, padx=5, pady=5)

        self.delete_quantity_entry = tk.Entry(self.deleteProduct_frame)
        self.delete_quantity_entry.grid(row=1, column=1, padx=5, pady=5)

        self.delete_button = tk.Button(self.deleteProduct_frame, text="Delete Product", bg="silver", fg="black", command=self.deleteProductManager) #, command=self.deleteProduct
        self.delete_button.grid(row=3, column=0, columnspan=2, padx=5, pady=5)



    def deleteProductManager(self):
        product_identifier = self.deleteProduct_entry.get()
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
    
        # Call deleteProduct with the appropriate arguments
        self.deleteProduct(product_identifier, delete_quantity_str)
    
        # Clear the input fields after deletion
        self.deleteProduct_entry.delete(0, tk.END)
        self.delete_quantity_entry.delete(0, tk.END)


    def startSearchProductFrame(self):
        self.searchProduct_frame = tk.LabelFrame(self, text="Search Product by Name or ID", bg="black", fg='cyan', padx=10, pady=5)
        self.searchProduct_frame.grid(row=1, column=1)

        self.search_entry = tk.Entry(self.searchProduct_frame, width=50)
        self.search_entry.grid(row=0, column=0, padx=(5, 3), pady=(15, 5), sticky="ew")

        self.search_button = tk.Button(self.searchProduct_frame, text="Search", fg="black", bg='silver', command=self.searchProductManager)
        self.search_button.grid(row=0, column=1, padx=(3, 5), pady=(15, 5), sticky="ew")

        self.power_search_button = tk.Button(self.searchProduct_frame, text="Power Search", bg="cyan", fg="black", command=self.launchPowerSearch)
        self.power_search_button.grid(row=4, column=0, columnspan=2, padx=5, pady=5)


    def launchPowerSearch(self):
        # Call the power_search method and display the results
        products = self.powerSearch(power_search=True)
        self.powerSearchResults(products)

    def powerSearch(self, power_search=False):
        # Retrieve all products in the product log
        if power_search:
            return self.product_log
        else:
            return []

    def powerSearchResults(self, products):
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
            self.showWindow("Power Search Results", result_text)

    def showWindow(self, title, content):
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

    def clearPowerSearchResults(self):
        # Replace 'product_info_text' with the actual name or reference to your Text widget
        # Example: if you have a Text widget named 'my_product_info_text', use self.my_product_info_text
        self.product_info_text.config(state='normal')  # Set the state to normal before updating
        self.product_info_text.delete(1.0, "end")  # Clear the existing text (remove the '-1c')
        self.product_info_text.config(state='disabled')  # Set the state back to disabled (read-only)



    def startProductInformationFrame(self):
        self.product_info_frame = tk.LabelFrame(self, text="Display Product Information", bg='black', fg='cyan')
        self.product_info_frame.grid(row=2, column=1)

        self.product_info_text = tk.Text(self.product_info_frame, height=8, width=50 , bg="black", fg='cyan')
        self.product_info_text.pack(padx=10, pady=10)

    def searchProductManager(self):
        product_identifier = self.search_entry.get()
        product = self.searchProduct(product_identifier)

        if product:
            product_info = self.productDetailsLayout(product)
            self.product_info_text.delete(1.0, tk.END)
            self.product_info_text.insert(tk.END, product_info)
        else:
            self.product_info_text.delete(1.0, tk.END)
            self.product_info_text.insert(tk.END, "Product not found.")




    def startShoppingListFrame(self):
        self.shopping_list_frame = tk.LabelFrame(self, text="Shopping List", bg='black', fg='cyan', padx=10, pady=10)
        self.shopping_list_frame.grid(row=2, column=2)
        
        self.shopping_list_text = tk.Text(self.shopping_list_frame, height=5, width=35)
        self.shopping_list_text.pack(padx=10, pady=10)
        
        self.buttons_frame = tk.Frame(self.shopping_list_frame, bg='black')
        self.buttons_frame.pack()
        
        self.showShoppingList_button = tk.Button(self.buttons_frame, text="View Shopping List", fg='black', bg='silver', command=self.showShoppingList)
        self.showShoppingList_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.download_shopping_list_button = tk.Button(self.buttons_frame, text="Generate Shopping List", fg='black', bg='silver', command=self.downloadShoppingListPDF)
        self.download_shopping_list_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.buttons_frame.pack_configure(expand=True)
        self.buttons_frame.pack_configure(anchor='center')

    def showShoppingList(self):
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
    
    def downloadShoppingListPDF(self):
        # Create a GenerateReportPDF instance with the current products data
        report_generator = GenerateReportPDF(self.product_log)
    
        # Generate the shopping list report
        report_generator.createShoppingList()
    
        # Show a success message
        messagebox.showinfo("Success", "Shopping list generated successfully!")

    def obtainShoppingList(self):
        # Get the shopping list as a formatted string
        shopping_list = ""
        for product in self.product_log:
            if product['quantity'] > 0:
                shopping_list += f"{product['id']} | {product['name']} | Quantity: {product['quantity']}\n"
        return shopping_list

# repair 
    
    def startManageOrdersFrame(self):
        self.manage_orders_frame = tk.LabelFrame(self, text="Manage Orders", bg='black', fg='cyan', padx=10, pady=10)
        self.manage_orders_frame.grid(row=3, column=1)

        self.startTextWidgets()
        self.launchButtons()

    def startTextWidgets(self):
        self.text_widget = tk.Text(self.manage_orders_frame, state='disabled', bg='black', fg='cyan', height=3, width=45)
        self.text_widget.pack(padx=10, pady=10)

    def launchButtons(self):
        button_frame1 = tk.Frame(self.manage_orders_frame, bg='black')
        button_frame1.pack()
    
        buttons_data = [
            ("Add Order", self.addOrder),
            ("Remove Order", self.removeOrder),
            ("Change Order Status", self.changeOrderStatus)
        ]
    
        for button_text, command_func in buttons_data:
            button = tk.Button(button_frame1, text=button_text, bg='silver', fg='black', command=command_func)
            button.pack(side=tk.LEFT, padx=5, pady=5)

    def addOrder(self):
        num_products = simpledialog.askinteger("Add Order", "How many products do you want to add?", parent=self)
    
        if not self.validProductQuantity(num_products):
            return
    
        for _ in range(num_products):
            order_id, order_item, order_quantity = self.getOrderDetails()
    
            if order_id is None or order_item is None or order_quantity is None:
                return
    
            product = self.getProduct(order_item)
    
            if product is None or not self.maximumOrderStock(product, order_quantity):
                return
    
            new_order = self.createOrder(order_id, product, order_quantity)
            self.updateOrderStock(product, order_quantity)
    
            self.orders.append(new_order)
    
            # Schedule the registration after a 1-second delay
            self.after(1000, lambda: self.registerOrder(order_id))

    def validProductQuantity(self, quantity):
        try:
            quantity = int(quantity)  # Try converting to an integer
            return quantity is not None and quantity > 0
        except ValueError:
            return False  # Return False if conversion to integer fails

    def getOrderDetails(self):
        order_id = self.createOrderID()
        order_item = simpledialog.askstring("Add Order", "Enter product ID or name:", parent=self)

        if not order_item:
            messagebox.showinfo("Error", "Please enter a product ID or name for the order.")
            return None, None, None

        order_quantity = simpledialog.askinteger("Add Order", f"Enter quantity for product {order_item}:", parent=self)

        if not self.validProductQuantity(order_quantity):
            return None, None, None

        return order_id, order_item, order_quantity

    def getProduct(self, order_item):
        return next(
            (product for product in self.product_log if product['id'] == order_item or product['name'] == order_item), None)

    def maximumOrderStock(self, product, order_quantity):
        if product['quantity'] < order_quantity:
            messagebox.showinfo("Error", f"Not enough stock for product '{product['name']}'. Cannot add the order.")
            return False
        return True

    def createOrder(self, order_id, product, order_quantity):
        return {
            'id': order_id,
            'item': product,
            'quantity': order_quantity,
            'status': 'registered'
        }

    def updateOrderStock(self, product, order_quantity):
        product['quantity'] -= order_quantity

    def createOrderID(self):
        return f"ORD-{str(len(self.orders) + 1).zfill(3)}"

    def displayAddedMessage(self, order_id, new_order):
        messagebox.showinfo("Order Added", f"Order {order_id} added successfully!\n{new_order['item']['name']}")

    def removeOrder(self):
        order_id_to_remove = simpledialog.askstring("Remove Order", "Enter the order ID to remove:", parent=self)

        if not order_id_to_remove:
            messagebox.showinfo("Error", "Please enter an order ID to remove.")
            return

        order_to_remove = next((order for order in self.orders if order['id'] == order_id_to_remove), None)

        if order_to_remove is None:
            messagebox.showinfo("Error", f"Order with ID '{order_id_to_remove}' not found.")
            return

        self.manageOrderRemoval(order_to_remove)

    def manageOrderRemoval(self, order_to_remove):
        product = order_to_remove.get('item')

        if product is not None:
            product['quantity'] += order_to_remove['quantity']

        self.orders.remove(order_to_remove)

        self.displayOrderRemovedMessage(order_to_remove)
        self.showAllOrders()

    def removeOrderWithID(self, order_id):
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
            self.showAllOrders()
    
            # Force focus back to the main Tkinter window
            self.focus_force()
            # Update the Tkinter event queue to ensure the next message box is displayed correctly
            self.update_idletasks()
        else:
            messagebox.showinfo("Error", f"Order with ID '{order_id}' not found.")

    def displayOrderRemovedMessage(self, removed_order):
        order_id = removed_order.get("id")
        messagebox.showinfo("Order Removed", f"Order with ID '{order_id}' removed successfully!")


    def registerOrder(self, order_id):
        order = next((o for o in self.orders if o.get("id") == order_id), None)
    
        if order:
            order["time_accepted"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            order["status"] = "registered"
    
            # Display a message indicating the successful registration
            self.displayStatusChange(order_id, order["status"])
    
            # Log the order status change
            self.logOrderStatusChange(order_id)
    
            # Automatically display the updated list of orders
            self.showAllOrders()
        
    
    
    def changeOrderStatus(self):
        order_id = self.displayInputBox("Enter Order ID", "Please enter the Order ID:")
    
        if not order_id:
            return
    
        order = next((o for o in self.orders if o.get("id") == order_id), None)
    
        if order:
            # Update the order status to "in the collection queue" and log the changes
            if order.get("status") == "registered":
                # If the status is "registered," simulate a 3-second delay before changing to "in the collection queue"
                self.after(3000, lambda: self.updateOrderAndShow(order_id, "in the collection queue"))
            elif order.get("status") == "in the collection queue":
                # If the status is "in the collection queue," simulate a 3-second delay before changing to "collected"
                time_collected = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.after(3000, lambda: self.updateOrderAndShow(order_id, "collected", time_collected))
            else:
                # If the status is "collected," show the final status changed message and remove the order
                self.displayOrderAndRemove(order_id, time_collected)
        
    def updateOrderAndShow(self, order_id, new_status, time_collected=None):
        # Update the order status
        order = next((o for o in self.orders if o.get("id") == order_id), None)
        if order:
            order["status"] = new_status
    
        # If the new status is "collected," log the time_collected
        if new_status == "collected":
            self.logOrderStatusChange(order_id, time_collected)
    
        # Display the status changed message
        self.displayStatusChange(order_id, new_status)
    
        # If the new status is "collected," remove the order immediately
        if new_status == "collected":
            self.displayOrderAndRemove(order_id, time_collected)
    
        # Automatically update the displayed orders on the screen
        self.showAllOrders()
    
    def displayOrderAndRemove(self, order_id, time_collected=None):
        # Display the final removal message after the order has been removed
        self.removeCollectedOrder(order_id)
    
        # Log the order status change with the time_collected parameter
        self.logOrderStatusChange(order_id, time_collected)

    def orderStatusByIDupdate(self, order_id, new_status):
        order = next((o for o in self.orders if o.get("id") == order_id), None)
        if order:
            # Update the order status
            order["status"] = new_status
    
    def removeOrderCollectedWithID(self, order_id):
        order = next((o for o in self.orders if o.get("id") == order_id), None)
        if order and order.get("status") == "collected":
            # If the order is collected, remove it from the list
            self.removed_orders.append(order)
            self.orders.remove(order)
            # Automatically display the updated list of orders
            self.showAllOrders()
            # Display a message indicating the successful removal of the order
            messagebox.showinfo("Order Removed", f"Order with ID '{order_id}' removed successfully!")
        
    def updateOrderStatus(self, order):
        if order.get("status") == "registered":
            order["time_accepted"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            order["status"] = "in the collection queue"
        elif order.get("status") == "in the collection queue":
            order["time_collected"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            order["status"] = "collected"
    
        self.logOrderStatusChange(order['id'], time_collected=order['time_collected'])
    
        # Automatically update the displayed orders on the screen
        self.showAllOrders()

    def displayStatusChange(self, order_id, new_status):
        messagebox.showinfo("Status Changed", f"Order {order_id} status changed to '{new_status}' successfully!")
    
    def logOrderStatusChange(self, order_id, time_collected=None):
        order = next((o for o in self.orders if o.get("id") == order_id), None)
    
        if order:
            time_accepted = self.timeFormatMethod(order.get('time_accepted'))
            time_collected = self.timeFormatMethod(time_collected) if time_collected else ""
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
    
            self.logFile("update_log.txt", log_message)
    
            # Automatically update the displayed orders on the screen
            self.showAllOrders()
        
    def timeFormatMethod(self, time_str):
        if time_str:
            return datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")
        return ""

    def removeCollectedOrder(self, order_id, time_collected=None):
        order = next((o for o in self.orders if o.get("id") == order_id), None)
        if order and order.get("status") == "collected":
            # If the order is collected, remove it from the list
            self.removed_orders.append(order)
            self.orders.remove(order)
            # Automatically display the updated list of orders
            self.showAllOrders()
            # Display a message indicating the successful removal of the order
            messagebox.showinfo("Order Removed", f"Order with ID '{order_id}' removed successfully!")
    
            if time_collected:
                # Log the time collected in the update log file
                self.logOrderStatusChange(order_id, time_collected)

    def showAllOrders(self):
        orders_text = "\n\n".join([
            f"Order ID: {order['id']}\n"
            f"Item: \n  Name: {order['item']['name']}\n  ID: {order['item']['id']}\n  Last Ordered: {order['item']['last_ordered']}\n  Specifications: {order['item']['specifications'].strip()}\n Quantity: {order['quantity']}\n Status: {order['status']}"
            for order in self.orders])

        self.updateTexts(orders_text)

    def updateTexts(self, orders_text):
        self.text_widget.config(state='normal')
        self.text_widget.delete(1.0, "end-1c")
        self.text_widget.insert("insert", orders_text)
        self.text_widget.config(state='disabled')

    def logFile(self, filename, log_message):
        with open(filename, "a") as log_file:
            log_file.write(log_message)

    def displayInputBox(self, title, prompt):
        user_input = simpledialog.askstring(title, prompt, parent=self)
    
        if user_input is not None:
            return user_input.strip()  # Strip any leading/trailing whitespaces
        return user_input   


# repair


    def startGenerateReportFrame(self):

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

        self.generate_report_button = tk.Button(self.black_frame, text="Generate Report", bg="silver", command=self.generateReportManager)
        self.generate_report_button.pack(pady=10)


    def generateReportManager(self):
        # Create a GenerateReportPDF instance with the current products data
        report_generator = GenerateReportPDF(self.product_log)
    
        # Generate the product report (you can specify a filename if needed)
        report_generator.createProductReport()
    
        # Show a success message
        messagebox.showinfo("Success", "Product report generated successfully!")
        

    def startCheckSimilarityFrame(self):
        self.checkSimilarity_frame = tk.LabelFrame(self, text="Check Similarity", bg='black', fg='cyan', padx=10, pady=10)
        self.checkSimilarity_frame.grid(row=1, column=2)
    
        self.checkSimilarity_text = tk.Text(self.checkSimilarity_frame, height=3, width=35)
        self.checkSimilarity_text.pack(padx=10, pady=10)
    
        self.checkSimilarity_button = tk.Button(self.checkSimilarity_frame, text="Check Similarity", fg="black", bg='silver', command=self.checkSimilarity)
        self.checkSimilarity_button.pack(padx=1, pady=1)

    def checkSimilarity(self):
        selected_specifications = self.checkSimilarity_text.get("1.0", tk.END).strip()

        if not selected_specifications:
            messagebox.showinfo("Error", "Please enter specifications for similarity check.")
            return

        products = self.product_log.copy()

        exact_matches, non_exact_matches = self.similarityProcess(products, selected_specifications)

        result_text = self.resultsFormat(exact_matches, non_exact_matches)

        self.product_info_text.delete(1.0, tk.END)
        self.product_info_text.insert(tk.END, result_text)

    def similarityProcess(self, products, selected_specifications):
        exact_matches = []
        non_exact_matches = []

        for product in products:
            similarity_score = fuzz.token_set_ratio(selected_specifications, product['specifications'])

            if similarity_score == 100:
                exact_matches.append(product)
            elif similarity_score >= 80:
                non_exact_matches.append(product)

        non_exact_matches.sort(key=lambda product: fuzz.token_set_ratio(selected_specifications, product['specifications']), reverse=True)

        return exact_matches, non_exact_matches

    def resultsFormat(self, exact_matches, non_exact_matches):
        result_text = ""

        for product in exact_matches:
            result_text += f"\n Product ID: {product['id']} \n Product Name: {product['name']} \n Similarity Score: 100% \n"
            result_text += "-------------------------"

        for product in non_exact_matches:
            similarity_score = fuzz.token_set_ratio( product['specifications'])
            result_text += f"Product ID: {product['id']} | Product Name: {product['name']} | Similarity Score: {similarity_score}%\n"
            result_text += (
                f"Quantity: {product['quantity']}\n"
                f"Last Time Ordered: {product['last_ordered']}\n"
                f"Specifications: {product['specifications'][1:]}\n\n"
            )

        return result_text



    def startUpdateLogFrame(self):
        self.update_log_frame = tk.LabelFrame(self, text="Update Log File", bg='black', fg='cyan', padx=10, pady=10)
        self.update_log_frame.grid(row=3, column=2)

        img_label = self.displayImage()
        update_log_button = self.createUpdateLogButton()

        self.widgetsSet(img_label, update_log_button)

    def displayImage(self):
        img = Image.open("images/update.png").resize((40, 40))
        img = ImageTk.PhotoImage(img)
        img_label = tk.Label(self.update_log_frame, bg='black', image=img)
        img_label.image = img  # Keep a reference to the image to prevent garbage collection
        img_label.pack()
        return img_label

    def createUpdateLogButton(self):
        return Button(self.update_log_frame, text="Update Log File", bg='silver', fg='black', command=self.showUpdateLog)

    def widgetsSet(self, *widgets):
        for widget in widgets:
            widget.pack(pady=10)

    def showUpdateLog(self):
        # Create a new thread to perform the file read operation
        threading.Thread(target=self.readAndShowLogDetails).start()

    def readAndShowLogDetails(self):
        log_content = self.readLogFile("update_log.txt")

        # Execute the Tkinter GUI update on the main thread
        self.after(0, lambda: self.showLogContents(log_content))

    def showLogContents(self, log_content):
        log_window = Toplevel(self)
        log_window.title("Update Log")
        log_window.geometry("660x400")
    
        center_x, center_y = self.centeringWindow(log_window)
        log_window.geometry(f"+{center_x}+{center_y}")
    
        log_text, log_scrollbar = self.createTextLogWithScrollbar(log_window)
        self.logTextConfiguration(log_text, log_scrollbar)
        self.insertContentsForLog(log_text, log_content)
    
        # Make the Text widget read-only
        log_text.config(state="disabled")
        log_text.focus_set()
    
        # Run the Tkinter event loop
        log_window.mainloop()

    def centeringWindow(self, log_window):
        root_x, root_y = self.winfo_x(), self.winfo_y()
        return root_x + (self.winfo_width() - 700) // 2, root_y + (self.winfo_height() - 400) // 2

    def createTextLogWithScrollbar(self, log_window):
        log_text = tk.Text(log_window, wrap="none", height=20, width=80)
        log_scrollbar = tk.Scrollbar(log_window, command=log_text.yview)
        return log_text, log_scrollbar

    def logTextConfiguration(self, log_text, log_scrollbar):
        log_text.config(yscrollcommand=log_scrollbar.set)
        log_text.pack(side="left", fill="y")
        log_scrollbar.pack(side="right", fill="y")
        log_text['yscrollcommand'] = log_scrollbar.set

    def insertContentsForLog(self, log_text, content):
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
                    entry = entry.replace(time_collected, self.timeFormatMethod(time_collected))
    
                log_text.insert("insert", entry)
                log_text.insert("insert", "\n\n")  # Add a line gap after each log entr

    def readLogFile(self, filename):
        log_content = ""
        try:
            log_path = os.path.join(os.getcwd(), filename)
            with open(log_path, "r") as file:
                log_content = file.read()
        except FileNotFoundError:
            log_content = f"{filename} not found."
        return log_content

    def onClose(self):
        # Clear the update log content
        self.clearUpdateLogFile()

        # Close the application
        self.destroy()

    def clearUpdateLogFile(self):
        log_filename = "update_log.txt"
        try:
            log_path = os.path.join(os.getcwd(), log_filename)
            with open(log_path, "w"):
                pass
        except FileNotFoundError:
            pass        


        
    def launchGIF_Frame(self):
        # Existing code for initializing the gif frame
        self.play_gif_frame = tk.Frame(self, bg='black')
        self.play_gif_frame.grid(row=0, column=1, padx=(60, 10), pady=0)

        self.asus_label = tk.Label(self.play_gif_frame, bg='black')
        self.asus_label.pack()

        # Create an instance of the start_GIFplayer class, passing the parent frame
        gif_player = start_GIFplayer(self.play_gif_frame, 'images/motion.gif', 370, 220)
        gif_player.pack() 


class start_GIFplayer(tk.Label):
    def __init__(self, parent, gif_path, width, height):
        super().__init__(parent, bg='black')
        self.width = width
        self.height = height
        self.loadGIF(gif_path)

    def loadGIF(self, gif_path):
        cap = cv2.VideoCapture(gif_path)

        def showFrame():
            ret, frame = cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = Image.fromarray(frame)
                photo_image = ImageTk.PhotoImage(frame.resize((self.width, self.height)))
                self.configure(image=photo_image)
                self.image = photo_image  # Keep a reference to the image
                self.after(10, showFrame)
            else:
                # Reset the video capture to play the gif in a loop
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                showFrame()

        showFrame()




def main():

    warehouse_app = WarehouseMangerGUI()
    warehouse_app.mainloop()

if __name__ == "__main__":
    main()

