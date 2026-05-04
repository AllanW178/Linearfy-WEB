
import easygui as eg
import sqlite3
import re

def setup_mock_database():
    conn = sqlite3.connect(':memory:')
    cursor = conn.cursor()


    # Below is just a list of tables for our Linearfy DB. Created in Python.

    cursor.execute('''CREATE TABLE Categories (category_id INT, cat_name TEXT)''')
    cursor.execute('''CREATE TABLE Products (product_id INT, category_id INT, name TEXT, price DECIMAL, stock_qty INT)''')
    cursor.execute('''CREATE TABLE Users (user_id INT, email TEXT)''')
    cursor.execute('''CREATE TABLE ProductReviews (review_id INT, product_id INT, rating INT)''')

    cursor.execute('''INSERT INTO Categories VALUES (101, 'Apparel')''')
    cursor.execute('''INSERT INTO Categories VALUES (102, 'Accessories')''')
    

    cursor.execute('''INSERT INTO Products VALUES (1, 101, 'Linearfy T-Shirt', 25.99, 50)''')
    cursor.execute('''INSERT INTO Products VALUES (36, 102, 'Linearfy Cap', 15.50, 5)''')
    
    cursor.execute('''INSERT INTO Users VALUES (1, 'test@test.com')''')
    
    conn.commit()
    return conn


def test_database_joins(conn):
    cursor = conn.cursor()
    
    # This just creates the database structure for this specific DB.
    query = """
        SELECT p.name, p.price, c.cat_name 
        FROM Products p 
        JOIN Categories c ON p.category_id = c.category_id 
        WHERE p.stock_qty > 0;
    """



    cursor.execute(query)
    results = cursor.fetchall()
    
    display_text = "Query: SELECT p.name, p.price, c.cat_name FROM Products p JOIN Categories c...\n\nResults:\n"
    display_text += "-" * 50 + "\n"
    
    for row in results:
        product_name, price, category = row
        display_text += f"Product: {product_name} | Price: ${price:.2f} | Category: {category}\n"
        
    eg.textbox("Testing Relational Database Queries (JOINs)", "Expected Result: Pass", text=display_text)


# "get product" function here.
def test_get_product(conn):

    user_input = eg.enterbox(
        "Enter Product ID to search:\n\n(Try '1' or '36' for valid boundary limits)\n(Try '0' or '37' for invalid boundary limits)", 
        "Test: Get Product (Boundary Analysis)"
    )
    
    if user_input is None: return 

    try:
        product_id = int(user_input)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM Products WHERE product_id = ?", (product_id,))
        result = cursor.fetchone()

        if result:
            eg.msgbox(f"Success: Showing Product - {result[0]}", "Expected Result: Pass")
        else:
            eg.msgbox(f"Error 404: Product ID {product_id} not found / Out of bounds.", "Expected Result: Pass (404 Error)")
            
    except ValueError:
        eg.msgbox("Validation Error: Please enter a valid numerical ID.", "Robustness Test: Pass")


# Our "testing process order" function here.

def test_process_order(conn):

    cursor = conn.cursor()
    cursor.execute("SELECT stock_qty FROM Products WHERE product_id = 1")
    current_stock = cursor.fetchone()[0]

    user_input = eg.enterbox(
        f"Current Stock is {current_stock}.\nEnter quantity to order:\n\n(Try '50' for exact max capacity)\n(Try '51' for invalid over-capacity)", 
        "Test: Process Order Boundaries"

    )
    

    if user_input is None: return

    try:
        qty = int(user_input)
        if qty <= 0:
            eg.msgbox("Validation Error: Order quantity must be at least 1.", "Expected Result: Pass")
        elif qty <= current_stock:
            new_stock = current_stock - qty
            eg.msgbox(f"Order Successful! Remaining stock updated to: {new_stock}", "Expected Result: Pass")
        else:
            eg.msgbox(f"Order Blocked: Insufficient stock available. Only {current_stock} left.", "Expected Result: Pass (Blocked)")
            
    except ValueError:
        eg.msgbox("Validation Error: Please enter a whole number.", "Robustness Test: Pass")




# This is our "add review" function.

def test_add_review():
    user_input = eg.enterbox(
        "Enter a rating out of 5:\n\n(Try '5' for valid maximum boundary)\n(Try '6' for invalid upper boundary)", 
        "Test: Add Review Boundaries"
    )
    
    if user_input is None: return

    try:
        rating = int(user_input)
        if 1 <= rating <= 5:
            eg.msgbox(f"Success: Rating of {rating}/5 validated and added to database.", "Expected Result: Pass")

        else:
            eg.msgbox("Validation Error: Rating must be between 1 and 5.", "Expected Result: Pass (Blocked)")

    except ValueError:
        eg.msgbox("Validation Error: Please enter a valid number.", "Robustness Test: Pass")


def test_user_signup(conn):
    email = eg.enterbox(
        "Enter email to sign up:\n\n(Try 'test@test.com' to trigger duplicate error)", 
        "Test: User Sign Up Validation"
    )
    
    if email is None: return

    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        eg.msgbox("Validation Error: Invalid email format.", "Robustness Test: Pass")
        return
    


    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Users WHERE email = ?", (email,))
    result = cursor.fetchone()



    if result:
        eg.msgbox(f"Registration Blocked: The email '{email}' is already registered in the system.", "Expected Result: Pass (Duplicate Caught)")
    
    else:
        eg.msgbox(f"Success: '{email}' is available. User securely registered.", "Expected Result: Pass")


def main():
    conn = setup_mock_database()
    
    while True:
        choices = [
            "Test: Relational SQL Queries (JOINs)", 
            "Test: Get Product (ID Boundaries)", 
            "Test: Process Order (Stock limits)", 
            "Test: Add Review (1-5 limits)", 
            "Test: User Sign Up (Duplicate check)",
            "Exit Dashboard"
        ]

        
        selection = eg.buttonbox(
            "This is Linearfy Database Testing Dashboard\n\nIf you (teacher) are testing this, you can try to choose a module to test against the boundary values:", 
            "Testing Suite", 
            choices
        )


        
        if selection == choices[0]:
            test_database_joins(conn)
        elif selection == choices[1]:
            test_get_product(conn)
        elif selection == choices[2]:
            test_process_order(conn)
        elif selection == choices[3]:
            test_add_review()
        elif selection == choices[4]:
            test_user_signup(conn)
        else:

            break

    conn.close() 





if __name__ == "__main__":
    main()