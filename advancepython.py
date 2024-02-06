
# This is part 1.1 

import tkinter as tk
import random
from tkinter import messagebox
from PIL import Image, ImageTk
import cv2
from datetime import datetime
import os
from fuzzywuzzy import fuzz
from tkinter import Button,simpledialog
import logging
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime, timedelta


class AsusROG_WarehouseApp(tk.Tk):
    
    def __init__(self):
        super().__init__()
        self.configure(bg="black")
        self.title("ASUS ROG Warehouse Pro")


class ProductManagement(AsusROG_WarehouseApp):

    def __init__(self):
        super().__init__()
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.product_log_file = os.path.join(script_dir, "product_log.txt")
        self.product_log = []
        self.product_id_counter = 1
        self.products = {}
        self.loadProductLogFile()



    


    def addProduct(self, product_name, quantity, specifications):
         # Feature 1: Check if the product name has the required prefix
         if not product_name.lower().startswith("asus rog"):
             messagebox.showinfo("Invalid Product Name", "Please add a product with the 'Asus ROG' prefix.")
             return

         # Feature 2: Check if the quantity is within the allowed limit (maximum 5)
         if not (quantity.isdigit() and 1 <= int(quantity) <= 5):
             messagebox.showinfo("Invalid Quantity", "Please enter a quantity between 1 and 5.")
             return

         # Feature 3: Generate a unique product ID with the format "ROG-001"
         product_id = self.generateProductID()

         # Feature 4: Handle multiple specifications
         specifications_list = specifications.split('\n')  # Split specifications using newline
         formatted_specifications = "\n".join([spec.strip() for spec in specifications_list])

         last_ordered = self.generateRandomTimestamp()
         # Feature 5: Generate the last ordered timestamp with a random time

         # Feature 6: Check if a similar product exists and prompt for merging
         existing_product = self.locateProducts(product_name, specifications_list)

         if existing_product:
             # Existing product found, prompt for merging
             user_response = messagebox.askyesno("Merge Products", f"A product with the name '{product_name}' already exists. Do you want to merge quantities?")
             if user_response:
                 # Merge products
                 new_quantity = int(quantity) + existing_product['quantity']
                 if new_quantity > 5:
                     merge_response = messagebox.askyesno("Merge Not Allowed", "Merging exceeds the maximum quantity limit (5). Do you want to create a new product ID?")
                     if merge_response:
                         # Create a new product ID and add as a new product
                         product_id = self.generateProductID()
                         product_data = {
                             'id': product_id,
                             'name': product_name,
                             'quantity': int(quantity),
                             'specifications': f"\n{formatted_specifications}",
                             'last_ordered': last_ordered
                         }
                         self.product_log.append(product_data)
                         self.saveProductLogFile()
                         messagebox.showinfo("Success", "New product added successfully!")
                     return
                 else:
                     # Merge products
                     existing_product['quantity'] = new_quantity
                     existing_product['last_ordered'] = last_ordered
                     self.saveProductLogFile()
                     messagebox.showinfo("Merge Successful", "Product merged successfully!")
                     return
             else:
                 # User chose not to merge, treat it as a new product
                 pass

         # No existing product found or user chose not to merge, create a new entry
         product_data = {
             'id': product_id,
             'name': product_name,
             'quantity': int(quantity),
             'specifications': f"\n{formatted_specifications}",
             'last_ordered': last_ordered
         }
         self.product_log.append(product_data)

         # Update the product ID counter for the next product
         self.product_id_counter += 1

         # Save the product log to a file (you may want to use a better serialization method)
         self.saveProductLogFile()

         # Show a success message
         messagebox.showinfo("Success", "Product added successfully!")

    def generateRandomTimestamp(self):
        # Generate a random time within the last 30 days
        current_time = datetime.now()
        random_days = random.randint(1, 30)
        random_hours = random.randint(0, 23)
        random_minutes = random.randint(0, 59)
        random_seconds = random.randint(0, 59)

        random_time = current_time - timedelta(days=random_days, hours=random_hours, minutes=random_minutes, seconds=random_seconds)

        # Format the timestamp
        formatted_timestamp = random_time.strftime("%Y-%m-%d %H:%M:%S")

        return formatted_timestamp

    def generateProductID(self):
        # Generate a product ID with the format "ROG-001"
        product_id = f"ROG-{str(self.product_id_counter).zfill(3)}"
        return product_id
    
    def deleteProduct(self, product_identifier, delete_quantity):
        # Find the product in the log based on ID or name
        product = None
        for item in self.product_log:
            if product_identifier.lower() in [item['id'].lower(), item['name'].lower()]:
                product = item
                break
    
        if product:
            # Update quantity or remove the entire product entry
            if delete_quantity is None:
                # Set quantity to zero instead of removing the product entry
                product['quantity'] = 0
            elif isinstance(delete_quantity, str) and delete_quantity.lower() == 'delete':
                # Remove the entire product entry
                self.product_log.remove(product)
            elif isinstance(delete_quantity, str) and delete_quantity.isdigit():
                # Convert delete_quantity to an integer
                delete_quantity = int(delete_quantity)
                product['quantity'] -= delete_quantity
                if product['quantity'] <= 0:
                    # Set quantity to zero instead of removing the product entry
                    product['quantity'] = 0
            else:
                messagebox.showinfo("Error", "Invalid quantity or 'delete' specified.")
                return
    
            # Save the updated product log
            self.saveProductLogFile()
    
            # Show success message
            messagebox.showinfo("Deletion", f"Product {product['name']} successfully updated.")


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

    def updateProductDictionary(self):
        for index, product in enumerate(self.product_log):
            # ... (your existing code)
    
            product_quantity = product.get('quantity', '')
            print(f"Product Quantity: {product_quantity}")
    
            # Convert the quantity to an integer
            try:
                product_quantity = int(product_quantity)
            except ValueError as e:
                print(f"Error converting quantity to integer: {e}")
                continue  # Skip this product and move to the next one
    
    
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


 

class SearchProductManagement(ProductManagement):


    

    def searchProduct(self, product_identifier):
        for item in self.product_log:
            if product_identifier.lower() in [item['id'].lower(), item['name'].lower()]:
                return self.productDetailsLayout(item)
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
        self.product_text = None  # Initialize product_text attribute
            # Add the following line to set the close button handler
        self.protocol("WM_DELETE_WINDOW", self.onClose)



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
                                            command=self.addProductManager)
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

            # Display product information with the last time ordered
            product_info = (

                f"Product ID: {product['id']}\n"
                f"Product Name: {product['name']}\n"
                f"Quantity: {product['quantity']}\n"
                f"Last Time Ordered: {product['last_ordered']}\n"
                f"Specifications: {product['specifications']}\n"
            ) 

            self.product_info_text.delete(1.0, tk.END)  # Clear previous content
            self.product_info_text.insert(tk.END, product_info)

        else:

            # Product not found
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


    def startManageOrdersFrame(self):

        self.manage_orders_frame = tk.LabelFrame(self, text="Manage Orders", bg='black', fg='cyan', padx=10, pady=10)
        self.manage_orders_frame.grid(row=3, column=1)

        # Create a text widget
        self.text_widget = tk.Text(self.manage_orders_frame, state='disabled', bg='black', fg='cyan', height=3, width=45)
        self.text_widget.pack(padx=10, pady=10)
        
        # First row: Three buttons centered
        button_frame1 = tk.Frame(self.manage_orders_frame, bg='black')  # Create a frame for the first row
        button_frame1.pack()
        
        self.addOrder_button = tk.Button(button_frame1, text="Add Order",bg='silver', fg='black', command=self.addOrder)
        self.addOrder_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.removeOrder_button = tk.Button(button_frame1, text="Remove Order", bg='silver', fg='black', command=self.removeOrder)
        self.removeOrder_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.change_status_button = tk.Button(button_frame1, text="Change Order Status",bg='silver', fg='black', command=self.changeOrderStatus) #
        self.change_status_button.pack(side=tk.LEFT, padx=5, pady=5)

                # Add a button to display orders
        self.displayOrders_button = tk.Button(button_frame1, text="Display Orders",bg='silver', fg='black', command=self.displayOrders)
        self.displayOrders_button.pack(side=tk.LEFT, padx=5, pady=5)
        
    def addOrder(self):

        # Prompt the user for the number of products to add
        num_products = simpledialog.askinteger("Add Order", "How many products do you want to add?", parent=self)
    
        if num_products is None or num_products <= 0:

            messagebox.showinfo("Error", "Please enter a valid number of products to add.")
            return
    
        # Iterate for the specified number of products
        for _ in range(num_products):

            # Generate a unique order ID
            order_id = self.createOrderID()
    
            # Get the product ID or name from the user
            order_item = simpledialog.askstring("Add Order", "Enter product ID or name:", parent=self)
    
            if not order_item:

                messagebox.showinfo("Error", "Please enter a product ID or name for the order.")
                return
    
            # Get the quantity of the product
            order_quantity = simpledialog.askinteger("Add Order", f"Enter quantity for product {order_item}:", parent=self)
    
            if order_quantity is None or order_quantity <= 0:

                messagebox.showinfo("Error", "Please enter a valid quantity.")
                return
    
            # Check if the product exists in the product_log
            product = next(
                (product for product in self.product_log if product['id'] == order_item or product['name'] == order_item), None)
    
            if product is None:

                messagebox.showinfo("Error", f"Product '{order_item}' does not exist. Cannot add the order.")
                return
    
            # Check if there are enough quantities in stock
            if product['quantity'] < order_quantity:

                messagebox.showinfo("Error", f"Not enough stock for product '{order_item}'. Cannot add the order.")
                return
    
            # Create a new order with the generated ID, product dictionary, quantity, and "registered" status
            new_order = {

                'id': order_id,
                'item': product,
                'quantity': order_quantity,
                'status': 'registered'
            }
    
            # Deduct the quantity from the product in the product_log
            product['quantity'] -= order_quantity
    
            # Add the new order to the list of orders
            self.orders.append(new_order)
    
            # Print the order ID on the GUI with the main window as the parent
            messagebox.showinfo("Order Added", f"Order {order_id} added successfully!\n{new_order['item']['name']}", parent=self)
    
            # Automatically display the updated list of orders
            self.displayOrders()
    
            # Force focus back to the main Tkinter window
            self.focus_force()
            # Update the Tkinter event queue to ensure the next message box is displayed correctly
            self.update_idletasks()

    def createOrderID(self):
        # Generate a unique order ID with the format "ORD-001"
        order_id = f"ORD-{str(len(self.orders) + 1).zfill(3)}"
        return order_id

    def displayOrders(self):

        # This method displays the list of orders on the GUI
        orders_text = "\n\n".join([
            f"Order ID: {order['id']}\nItem: \n  Name: {order['item']['name']}\n  ID: {order['item']['id']}\n  Last Ordered: {order['item']['last_ordered']}\n  Specifications: {order['item']['specifications'].strip()}\n Quantity: {order['quantity']}\n Status: {order['status']}"
            for order in self.orders])
    
        # Replace 'text_widget' with the actual name or reference to your text widget
        # Example: if you have a Text widget named 'my_text_widget', use self.my_text_widget
        self.text_widget.config(state='normal')  # Set the state to normal before updating
        self.text_widget.delete(1.0, "end-1c")  # Clear the existing text
        self.text_widget.insert("insert", orders_text)  # Insert the updated text
        self.text_widget.config(state='disabled')  # Set the state back to disabled (read-only)

    def changeOrderStatus(self):

        order_id = self.showOrderInput("Enter Order ID", "Please enter the Order ID:")

        if not order_id:
            return

        order = next((o for o in self.orders if o.get("id") == order_id), None)

        if order:

            if order.get("status") == "registered":
                order["status"] = "in the collection queue"

                messagebox.showinfo("Status Changed", f"Order {order_id} status changed to 'In the Collection Queue'.")

            elif order.get("status") == "in the collection queue":
                order["status"] = "collected"
                messagebox.showinfo("Status Changed", f"Order {order_id} status changed to 'Collected'.")
                # Automatically remove collected order
                self.RemoveOrderWithID(order_id)
                # Update GUI or any other necessary actions

            else:
                messagebox.showinfo("Invalid Action", f"Order {order_id} is already 'Collected'.")

            # Log order status change for each product in the order
            for product_id, quantity in order.get("products", {}).items():

                self.quantityUpdateForProductLog(product_id, quantity)

            # Log the overall order status change
            self.changingLogOrderStatus(order_id)

    def changingLogOrderStatus(self, order_id):

        order = next((o for o in self.orders if o.get("id") == order_id), None)
    
        if order:
            # Get the time the order got accepted
            time_accepted = order.get('time_accepted')

            if time_accepted:
                time_accepted = datetime.strptime(time_accepted, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")
    
            # Get the time the order got collected
            time_collected = order.get('time_collected')

            if time_collected:
                time_collected = datetime.strptime(time_collected, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")

            else:

                # If not collected yet, update the time_collected with the current time
                time_collected = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                order['time_collected'] = time_collected
    
            # Get the order item information
            order_item_info = "\n".join([
                f"Item: {order['item']}",
                
            ])
    
            log_message = (

                f"Order ID: {order['id']}\n"
                f"Time Accepted: {time_accepted}\n"
                f"Time Collected: {time_collected}\n"
                f"Quantity: {order['quantity']}\n"
                f"{order_item_info}\n"
                f"Update Date and Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                f"------------------------------------------"

            )
    
            self.logFile("update_log.txt", log_message)

    def recieveProductName(self, product_id):

        product_log_path = "product_log.txt"  # Update the path accordingly

        try:
            with open(product_log_path, "r") as product_log_file:
                for line in product_log_file:
                    line = line.strip().split(':')
                    if len(line) == 2:
                        stored_product_id, stored_product_name = line
                        if product_id == stored_product_id:
                            return stored_product_name
        except FileNotFoundError:
            print(f"Product log file '{product_log_path}' not found.")

        return 'None'
    
    def showOrderInput(self, title, prompt):

        # Function to create a message box for user input
        user_input = simpledialog.askstring(title, prompt,parent=self)
        return user_input
    
    def changeOrderStatus(self):

        order_id = self.showOrderInput("Enter Order ID", "Please enter the Order ID:")
    
        if not order_id:
            return
    
        order = next((o for o in self.orders if o.get("id") == order_id), None)
    
        if order:

            # Change order status
            if order.get("status") == "registered":
                # Set the time_accepted to the current time
                order["time_accepted"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                order["status"] = "in the collection queue"
                messagebox.showinfo("Status Changed", f"Order {order_id} status changed to 'In the Collection Queue'.")
            elif order.get("status") == "in the collection queue":
                # Set the time_collected to the current time
                order["time_collected"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                order["status"] = "collected"
                messagebox.showinfo("Status Changed", f"Order {order_id} status changed to 'Collected'.")
                # Automatically remove collected order
                self.RemoveOrderWithID(order_id)
                # Update GUI or any other necessary actions
            else:
                messagebox.showinfo("Invalid Action", f"Order {order_id} is already 'Collected'.")
    
            # Log order status change for each product in the order
            for product_id, quantity in order.get("products", {}).items():

                self.quantityUpdateForProductLog(product_id, quantity)
    
            # Log the overall order status change
            self.changingLogOrderStatus(order_id)

    def RemoveOrderWithID(self, order_id):

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
            self.displayOrders()
    
            # Force focus back to the main Tkinter window
            self.focus_force()
            # Update the Tkinter event queue to ensure the next message box is displayed correctly
            self.update_idletasks()

        else:

            messagebox.showinfo("Error", f"Order with ID '{order_id}' not found.")
            
    def removeOrder(self):
        # Prompt the user for the order ID to remove
        order_id_to_remove = simpledialog.askstring("Remove Order", "Enter the order ID to remove:", parent=self)
    
        if not order_id_to_remove:
            messagebox.showinfo("Error", "Please enter an order ID to remove.")
            return
    
        # Find the order in the list of orders based on the order ID
        order_to_remove = next((order for order in self.orders if order['id'] == order_id_to_remove), None)
    
        if order_to_remove is None:
            messagebox.showinfo("Error", f"Order with ID '{order_id_to_remove}' not found.")
            return
    
        # Add the order quantity back to the product in the product_log
        product = next((product for product in self.product_log if product['id'] == order_to_remove['item']['id']), None)
    
        if product is not None:
            product['quantity'] += order_to_remove['quantity']
    
        # Remove the order from the list of orders
        self.orders.remove(order_to_remove)
    
        # Display a message indicating the successful removal of the order
        messagebox.showinfo("Order Removed", f"Order with ID '{order_id_to_remove}' removed successfully!")
    
        # Automatically display the updated list of orders
        self.displayOrders()
    
        # Force focus back to the main Tkinter window
        self.focus_force()
        # Update the Tkinter event queue to ensure the next message box is displayed correctly
        self.update_idletasks()
    
    def startGenerateReport(self):
        # Create a GenerateReportPDF instance with the current products data
        report_generator = GenerateReportPDF(self.product_log)
    
        # Generate the product report (you can specify a filename if needed)
        report_generator.createProductReport()
    
        # Show a success message
        messagebox.showinfo("Success", "Product report generated successfully!") 

    def showProductInformation(self, product):
        # Assume you have a Text widget named 'product_text' for displaying product information
        product_id = product.get("id")
        
        # Correct the reference to the 'product_text' attribute
        start_index = self.product_text.search(f"Product ID: {product_id}", "1.0", tk.END)
        end_index = self.product_text.search("\n\n", start_index, tk.END)
        
        self.product_text.config(state='normal')  # Set the state to normal before updating
        self.product_text.delete(start_index, end_index)  # Remove the product text
        self.product_text.insert(start_index, f"Product ID: {product['id']}\nProduct Name: {product['name']}\nQuantity: {product['quantity']}\nLast Time Ordered: {product['last_time_ordered']}\nSpecifications: {', '.join(product['specifications'])}\n\n")
        self.product_text.config(state='disabled')  # Set the state back to disabled (read-only)

    def updateProductsQuantity(self, removed_order):
        # Update product quantities based on the removed order
        if removed_order:
            for product_id, quantity in removed_order.get("products", {}).items():
                product = next((p for p in self.product_log if p['id'] == product_id), None)
                if product:
                    product['quantity'] += quantity
    
            # Log the quantity update for the last product outside the loop
            if product:
                self.quantityUpdateForProductLog(product_id, product['quantity'])
                # Update the displayed product information
                self.showProductInformation(product)

    def quantityUpdateForProductLog(self, product_id, new_quantity):
        # Log product quantity update in the log file
        product = next((p for p in self.product_log if p['id'] == product_id), None)

        if product:
            log_message = f"Product ID: {product['id']}, Product Name: {product['name']}, Quantity: {new_quantity}, Update Date and Time: {datetime.now()}"
            logging.info(log_message)


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

        self.generate_report_button = tk.Button(self.black_frame, text="Generate Report", bg="silver", command=self.startGenerateReport)
        self.generate_report_button.pack(pady=10)
        

    def startCheckSimilarityFrame(self):
        self.check_similarity_frame = tk.LabelFrame(self, text="Check Similarity", bg='black', fg='cyan', padx=10, pady=10)
        self.check_similarity_frame.grid(row=1, column=2)
    
        self.check_similarity_text = tk.Text(self.check_similarity_frame, height=3, width=35)
        self.check_similarity_text.pack(padx=10, pady=10)
    
        self.check_similarity_button = tk.Button(self.check_similarity_frame, text="Check Similarity", fg="black", bg='silver', command=self.check_similarity)
        self.check_similarity_button.pack(padx=1, pady=1)
    
    # Add this new method to the WarehouseMangerGUI class
    def check_similarity(self):
        # Get the specifications from the Check Similarity frame
        selected_specifications = self.check_similarity_text.get("1.0", tk.END).strip()

        # Validate that there is input for comparison
        if not selected_specifications:
            messagebox.showinfo("Error", "Please enter specifications for similarity check.")
            return

        # Get the list of products from the product log
        products = self.product_log.copy()

        # Initialize selected_product_id
        selected_product_ids = []

        # Separate exact matches and non-exact matches
        exact_matches = []
        non_exact_matches = []

        for product in products:
            similarity_score = fuzz.token_set_ratio(selected_specifications, product['specifications'])

            # Skip the exact match of the searched product
            if similarity_score == 100:
                exact_matches.append(product)
                selected_product_ids.append(product['id'])
            else:
                # Skip products with similarity score less than a threshold (e.g., 80%)
                if similarity_score >= 80:
                    non_exact_matches.append(product)

        # Sort non-exact matches by similarity score
        non_exact_matches.sort(key=lambda product: fuzz.token_set_ratio(selected_specifications, product['specifications']), reverse=True)

        # Display the results in the product_info_text widget
        result_text = ""

        # Insert the exact matches at the beginning if found
        for product in exact_matches:
            result_text += f"\n Product ID: {product['id']} \n Product Name: {product['name']} \n Similarity Score: 100% \n"
            result_text += "-------------------------"

        # Insert the non-exact matches
        for product in non_exact_matches:
            similarity_score = fuzz.token_set_ratio(selected_specifications, product['specifications'])
            result_text += f"Product ID: {product['id']} | Product Name: {product['name']} | Similarity Score: {similarity_score}%\n"
            result_text += (
                f"Quantity: {product['quantity']}\n"
                f"Last Time Ordered: {product['last_ordered']}\n"
                f"Specifications: {product['specifications'][1:]}\n\n"
            )

        # Clear the existing content and insert the new results
        self.product_info_text.delete(1.0, tk.END)
        self.product_info_text.insert(tk.END, result_text)


        
    def startUpdateLogFrame(self):
        self.update_log_frame = tk.LabelFrame(self, text="Update Log File", bg='black', fg='cyan', padx=10, pady=10)
        self.update_log_frame.grid(row=3, column=2)
    
        # Load and resize the image
        img = Image.open("images/update.png")
        img = img.resize((40, 40))
    
        # Convert the image to Tkinter format
        img = ImageTk.PhotoImage(img)
    
        # Display the image
        img_label = tk.Label(self.update_log_frame, image=img, bg='black')
        img_label.image = img  # Keep a reference to the image to prevent garbage collection
        img_label.pack()
    
        # Button to trigger update log file
        update_log_button = Button(self.update_log_frame, text="Update Log File", bg='silver', fg='black' ,command=self.DisplayUpdateLogWindow)
        update_log_button.pack(pady=10)
    
    # Create a new window to display the logs
    def DisplayUpdateLogWindow(self):
        # Create a new window to display the logs
        log_window = tk.Toplevel(self)
        log_window.title("Update Log")
    
        # Set the size of the window
        log_window.geometry("660x400")
    
        # Get the coordinates of the main window
        root_x = self.winfo_x()
        root_y = self.winfo_y()
    
        # Calculate the center position for the log window
        center_x = root_x + (self.winfo_width() - 700) // 2
        center_y = root_y + (self.winfo_height() - 400) // 2
    
        # Set the position of the window
        log_window.geometry(f"+{center_x}+{center_y}")
    
        # Create a Text widget and Scrollbar
        log_text = tk.Text(log_window, wrap="none", height=20, width=80)
        log_scrollbar = tk.Scrollbar(log_window, command=log_text.yview)
        log_text.config(yscrollcommand=log_scrollbar.set)
    
        # Pack the Text widget and Scrollbar
        log_text.pack(side="left", fill="y")
        log_scrollbar.pack(side="right", fill="y")

        # Set the yscrollcommand attribute for the Text widget
        log_text['yscrollcommand'] = log_scrollbar.set
    
        # Display the log content in the Text widget
        log_text.insert("insert", "\n\nUpdate Log:\n")
        log_text.insert("insert", self.readLogFile("update_log.txt"))
    
        # Make the Text widget read-only
        log_text.config(state="disabled")
    
        # Set the focus to the Text widget
        log_text.focus_set()
    
        # Run the Tkinter event loop
        log_window.mainloop()

    def readLogFile(self, filename):
        log_content = ""
        try:
            log_path = os.path.join(os.getcwd(), filename)  # Get the full path to the log file
            with open(log_path, "r") as file:
                log_content = file.read()
        except FileNotFoundError:
            log_content = f"{filename} not found."
    
        return log_content
    
    def logFile(self, log_filename, log_message):
        log_path = os.path.join(os.getcwd(), log_filename)  # Get the full path to the log file
    
        mode = 'a' if 'update' in log_filename else 'w'
    
        with open(log_path, mode) as log_file:
            log_file.write(log_message + "\n")
    
    def onClose(self):
        # Clear the update log content
        self.clearUpdateLogFile()
    
        # Close the application
        self.destroy()
    
    def clearUpdateLogFile(self):
        log_filename = "update_log.txt"
    
        try:
            log_path = os.path.join(os.getcwd(), log_filename)
    
            # Open the file in write mode to clear its content
            with open(log_path, "w"):
                pass  # This will clear the content of the file
    
        except FileNotFoundError:
            # If the file is not found, you can ignore it
            pass

        
    def launchGIF_Frame(self):
        # Existing code for initializing the gif frame
        self.play_gif_frame = tk.Frame(self, bg='black')
        self.play_gif_frame.grid(row=0, column=1, padx=(60, 10), pady=0)

        self.asus_label = tk.Label(self.play_gif_frame, bg='black')
        self.asus_label.pack()

        # Create an instance of the startGIFplayer class, passing the parent frame
        gif_player = startGIFplayer(self.play_gif_frame, 'images/motion.gif', 370, 220)
        gif_player.pack() 


class startGIFplayer(tk.Label):
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

