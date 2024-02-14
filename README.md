-> Installation packages

I have installed these python libraries

pip install pillow
pip install opencv-python-headless
pip install reportlab
pip install fuzzywuzzy
pip install pyinstaller
pip install python-Levenshtein { installed to improve performance }

Additional features
there are two additional features in the entire application
-> The user can click on power search button and it automatically displays all the products in the warehouse on the screen.
-> In the delete product frame , If the user gives the product name or ID and in the product quantity input if the user gives 'delete' command, 
Then the entire product itself will be removed.


The whole Assessment consists of 3 different parts

![Screenshot 2024-02-14 104615](https://github.com/jyotheshkar/Asus-ROG-warehouse-Pro/assets/96298283/18a742b7-82dc-4fc8-82df-3d42ffebb41a)


-> Part 1.1

part one consits of the complete warehouse workflow
Type of Inheritence : Multi-level Inheritence

There are a total of 9 frames displayed on the GUI 

1. Add product frame : In this frame the user can add a product name, quantities and specifications. Once the Product gets added it will automatically Assign an order ID.
example : ROG-001. It will automatically display the last time it was ordered. User can add multiple specifications and also can merge products if the quantity limit does not exceed 5.

2. Delete product frame : In this frame the user can delete a product name with quantities. Once its done the quantities of the product will be removed from the warehouse.
If the user wants to delete the product itself. Then the user can type in delete command in the quantity input box and the entire product will be removed from the warehouse.

3. Search product frame : In the search product frame the user can search for a product with product name or product ID. An additional feature named Power search exists in the frame.
where the user will be able to see all the products that are stored in the warehouse.

4. Product information frame : In this frame. Most of the detials are being displayed. Everything the user searches for will be displayed on the product information frame.
After the similarity check the results will be displayed on the product information frame.

5. Generate report frame : In this frame, There is button option where the user can click on it to generate a report. The report consists of all the products names and its quantities.

6. Check similarity frame : In this frame, The user can check the similarity of a specification between multiple products and then display the products which has the highest amount of similarity.

7. Shopping list frame : In this frame,The user can learn about the products in the warehouse with zero quantities. The user will have two options. 
One is to view the shopping list and another is to generate a PDF for the shopping list.

8. Manage orders frame : In this frame the user can add an order, remove an order, change the order status from registered to in the collection queue to collected.
once the detials are given, manage orders frame automatically generates an order ID. The user can add multiple products for the same order. but if the order does not exist in the warehouse the user cant add the order. 
Once the order is placed the quantities in the product will be deducted. and if at all the user decides to delete the order instead of sending it to the collection queue.
then after deleting the order the quantities and the product detials will be sent back to the warehouse as they were removed from orders.
The user can click on the change order status and then input the order ID to change the status of an order. Display Orders is a button which refershing the display of the mange orders frame.
Every time the user changes the status of an order it is must that the user has to click on the display orders button and the then only the updated status will be displayed.

9. Update Log frame : In this frame there will be records of all the changes an user has done with the order. The use has to click on the update log file button in order to view the records.


Part 1.2

This part consits of the complete warehouse workflow.
The code has been enhanced with concurrency, parallelism and other advanced data structures.
Type of Inheritence : Multi-level Inheritence

GUI difference:
In this GUI there will be a small difference with the workflow. 
In the Manage orders frame, there wont be any display orders button which was used for refresh in the part 1.1
In part 1.2 once the orders status will be changed, It will be automatically updated and displayed.


Part 1.3

This part consits of the complete warehouse workflow.
The code has been enhanced with concurrency, parallelism and other advanced data structures.
Type of Inheritence : Multi-level Inheritence.
There will be an additonal file imported and it is a JSON file.
It contains 30 products in which each product has a random products

GUI difference:

In the manage orders frame, there will be a two new buttons. each button has a purpose. One is Orders JSON and another is Simulation
Orders JSON: in this button the user can click on the button and choose a json file and upload it, Then the json file will be uploaded to the application.
Simulation : In this button the user can start the simulation by clicking on the button. once the simulation starts each and every product in the json file will
enter the simulation and go the process from registered -> in the collection queue -> collected. and all the products are once collected the user can check for them 
in the update log file.
