from functools import wraps
import frappe  # type: ignore
import jwt  # PyJWT for token generation
import datetime
# from datetime import datetime
from frappe.utils.password import check_password  # type: ignore
from frappe.exceptions import AuthenticationError, DoesNotExistError  # type: ignore

SECRET_KEY = "JWTFtkAGnmTVdkroncN-aCbXGBnPdTfnn-j85nESyiQ"  


@frappe.whitelist(allow_guest=True)
def user_login(email, password):
    """Login user and return JWT token along with roles"""
    try:
        user = frappe.get_doc("User", email)
        if not user:
            return {"success": False, "error": "User does not exist"}, 404

        if not check_password(email, password):
            return {"success": False, "error": "Invalid email or password"}, 401

        # Fetch the user's roles
        roles = frappe.get_all("Has Role", filters={"parent": email}, fields=["role"])
        user_roles = [role["role"] for role in roles]

        # Generate JWT token
        payload = {
            "email": email,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=48),  # Token expires in 2 hours
            "iat": datetime.datetime.utcnow()
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

        return {
            "success": True,
            "message": "Login successful",
            "token": token,  
            "user": {
                "full_name": user.full_name,
                "username": user.username,
                "email": user.email,
                "user_type": user.user_type,
                "roles": user_roles  
            },
        }

    except DoesNotExistError:
        return {"success": False, "error": "User does not exist"}, 404
    except AuthenticationError:
        return {"success": False, "error": "Invalid email or password"}, 401
    except Exception as e:
        return {"success": False, "error": str(e)}, 500

    
def validate_jwt_token(func):
    """Decorator to validate JWT token from the Authorization header."""
    @wraps(func)
    def decorated_function(*args, **kwargs):
        auth_header = frappe.get_request_header("Authorization1")
        if not auth_header or not auth_header.startswith("Bearer "):
            frappe.throw("Missing or invalid Authorization token", AuthenticationError)

        token = auth_header.split(" ")[1]  
        print(f"Token received: {token}")  

        try:
           
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            print(f"Decoded token payload: {payload}")  

            frappe.set_user(payload["email"]) 

        except jwt.ExpiredSignatureError:
            frappe.throw("Token has expired. Please log in again.", AuthenticationError)
        except jwt.InvalidTokenError:
            frappe.throw("Invalid token. Authentication failed.", AuthenticationError)

        return func(*args, **kwargs)

    return decorated_function


@frappe.whitelist(allow_guest=True)

def get_all_roles():
    """Fetch all roles available in the system."""
    try:
        roles = frappe.get_all("Role", fields=["name"])
        return roles
    except Exception as e:
        return {"success": False, "error": str(e)}


# Get all books
@frappe.whitelist(allow_guest=True)  
@validate_jwt_token
def get_books():
    return frappe.get_all("Books", fields=["name", "title", "author", "isbn", "published_date", "is_available", "number_of_copy"])

# Get only available books
@frappe.whitelist(allow_guest=True)
@validate_jwt_token
def get_available_books():
    return frappe.get_all(
        "Books",
        filters={"is_available": 1}, 
        fields=["name", "title", "author", "isbn", "published_date", "is_available"]
    )

# Create a new book
@frappe.whitelist(allow_guest=True)
def create_book(title, author, published_date, isbn, number_of_copy, is_available = 1):
    new_book = frappe.get_doc({
        "doctype": "Books",
        "title": title,
        "author": author,
        "published_date": published_date,
        "isbn": isbn,
        "number_of_copy": number_of_copy,
        "is_available": is_available
    })
    new_book.insert()  
    return new_book

# Get a specific book by ID
@frappe.whitelist(allow_guest=True)
@validate_jwt_token
def get_book_by_id(book_id):
    book = frappe.get_doc("Books", book_id)  
    return {
        "name": book.name, 
        "title": book.title,
        "author": book.author,
        "published_date": book.published_date,
        "isbn": book.isbn,
        "number_of_copy": book.number_of_copy
    }

# Update an existing book
@frappe.whitelist(allow_guest=True)
# @validate_jwt_token
def update_book(book_id, title=None, author=None, published_date=None, isbn=None, number_of_copy=None):
    book = frappe.get_doc("Books", book_id)
    
    if title:
        book.title = title
    if author:
        book.author = author
    if published_date:
        book.published_date = published_date
    if isbn:
        book.isbn = isbn
    if number_of_copy:
        book.number_of_copy = number_of_copy
    
    book.save()  # Save the updated book
    return {
        "message": "Book updated successfully",
        "book": {
            "name": book.name, 
            "title": book.title,
            "author": book.author,
            "published_date": book.published_date,
            "isbn": book.isbn
        }
    }

# Delete a book
@frappe.whitelist(allow_guest=True)
@validate_jwt_token
def delete_book(ids):
    """Delete multiple books by their IDs"""
    try:
        ids = frappe.parse_json(ids) if isinstance(ids, str) else ids
        deleted_books = []
        not_found = []

        for book in ids:
            if frappe.db.exists("Books", book):
                frappe.delete_doc("Books", book, ignore_permissions=True)
                deleted_books.append(book)
            else:
                not_found.append(book)

        frappe.db.commit() 

        return {
            "message": "Book deletion completed",
            "deleted_books": deleted_books,
            "not_found": not_found
        }

    except Exception as e:
        return {"error": str(e)}



@frappe.whitelist(allow_guest=True)
def update_book_availability(book, is_available):
    try:
        book_doc = frappe.get_doc("Books", book)
        if not book_doc:
            return {"error": "Book not found"}

        # Convert is_available to boolean
        book_doc.is_available = bool(int(is_available))
        book_doc.save()

        return {"message": f"Book availability updated successfully to {book_doc.is_available}"}

    except Exception as e:
        return {"error": str(e)}


# ==============================
# MEMBER CRUD OPERATIONS
# ==============================

# Get all members
@frappe.whitelist(allow_guest=True)
@validate_jwt_token
def get_members():
    return frappe.get_all("Member", fields=["name", "membership_name", "membership_id", "email", "phone"])

# Create a new member
@frappe.whitelist(allow_guest=True)
def create_member(membership_name, membership_id, email, phone):
    new_member = frappe.get_doc({
        "doctype": "Member",
        "membership_name": membership_name,
        "membership_id": membership_id,
        "email": email,
        "phone": phone
    })
    new_member.insert()
    return new_member

# Get a specific member by ID
@frappe.whitelist(allow_guest=True)
@validate_jwt_token
def get_member_by_id(member_id):
    member = frappe.get_doc("Member", member_id)
    return {
        "name": member.name,
        "membership_name": member.membership_name,
        "membership_id": member.membership_id,
        "email": member.email,
        "phone": member.phone
    }

# Update an existing member
@frappe.whitelist(allow_guest=True)
def update_member(member_id, membership_name=None, membership_id=None, email=None, phone=None):
    member = frappe.get_doc("Member", member_id)

    if membership_name:
        member.membership_name = membership_name
    if membership_id:
        member.membership_id = membership_id
    if email:
        member.email = email
    if phone:
        member.phone = phone

    member.save()
    return {"message": "Member updated successfully", "member": member}

# Delete a member
@frappe.whitelist(allow_guest=True)
def delete_member(ids):
    try:
        import json
        ids = json.loads(ids)

        if not isinstance(ids, list):
            return {"error": "Invalid data format. Expected a list of IDs."}

        deleted_members = []
        not_found = []

        for member_id in ids:
            if frappe.db.exists("Member", member_id):
                frappe.delete_doc("Member", member_id, ignore_permissions=True)
                deleted_members.append(member_id)
            else:
                not_found.append(member_id)

        return {
            "message": "Member deletion completed",
            "deleted_members": deleted_members,
            "not_found": not_found
        }

    except Exception as e:
        return {"error": str(e)}

    
# ==============================
# LOAN CRUD OPERATIONS
# ==============================
@frappe.whitelist(allow_guest=True)
def report_currently_loaned_books():
    """Generate a report of all currently loaned books (books that are not available)."""
    loans = frappe.get_all(
        "Loan",
       
        fields=["name", "member", "book", "loan_date", "return_date"]
    )
    
    if not loans:
        return {"message": "No books are currently loaned."}

    return {"currently_loaned_books": loans}

@frappe.whitelist(allow_guest=True)
# def report_overdue_books():
#     """Generate a report of overdue books (return date has passed, but book is still loaned)."""
#     today = datetime.today().strftime('%Y-%m-%d')

#     overdue_loans = frappe.get_all(
#         "Loan",
#         filters={
#             "return_date": ["<", today],  # Return date has passed
            
#         },
#         fields=["name", "member", "book", "loan_date", "return_date"]
#     )
    
#     if not overdue_loans:
#         return {"message": "No overdue books found."}

#     return {"overdue_books": overdue_loans}

@frappe.whitelist()
@frappe.whitelist()
def get_overdue_books():
    return frappe.db.sql("""
        SELECT 
            l.name AS loan_id,
            m.membership_name AS member_name,
            b.title AS book_title,
            l.loan_date,
            l.return_date
        FROM `tabLoan` l
        JOIN `tabBooks` b ON l.book = b.name
        JOIN `tabMember` m ON l.member = m.name
        WHERE l.return_date < CURDATE() 
    """, as_dict=True)

# Create a new loan (borrow a book)

@frappe.whitelist(allow_guest=True)
def create_loan(member, book, loan_date, return_date):
    try:
        book_doc = frappe.get_doc("Books", book)
        if not book_doc:
            return {"error": "Book not found"}

        if book_doc.number_of_copy <= 0:
            return {"error": "No copies available for loan"}

        member_doc = frappe.get_doc("Member", member)
        if not member_doc:
            return {"error": "Member not found"}

        new_loan = frappe.get_doc({
            "doctype": "Loan",
            "member": member,
            "book": book,
            "loan_date": loan_date,
            "return_date": return_date
        })
        new_loan.insert()

        # Decrease the number_of_copy
        book_doc.number_of_copy -= 1

        # If no copies left, mark the book as unavailable
        if book_doc.number_of_copy == 0:
            book_doc.is_available = False

        book_doc.save()

        return {"message": "Loan created successfully", "loan_id": new_loan.name}
    
    except Exception as e:
        return {"error": str(e)}


# Get all loans
@frappe.whitelist(allow_guest=True)
def get_loans():
    return frappe.get_all("Loan", fields=["name", "member", "book", "loan_date", "return_date"])


# Get a specific loan by ID
@frappe.whitelist(allow_guest=True)
def get_loan_by_id(loan_id):
    try:
        loan = frappe.get_doc("Loan", loan_id)
        return {
            "name": loan.name,
            "loan_id": loan.name,
            "member": loan.member,
            "book": loan.book,
            "loan_date": loan.loan_date,
            "return_date": loan.return_date
        }
    except DoesNotExistError:
        return {"error": "Loan not found"}


# Update loan (return book)
@frappe.whitelist(allow_guest=True)
@frappe.whitelist(allow_guest=True)
def update_loan(loan_id, return_date):
    try:
        loan = frappe.get_doc("Loan", loan_id)
        loan.return_date = return_date
        loan.save()

        # Mark the book as available
        book_doc = frappe.get_doc("Books", loan.book)
        book_doc.is_available = True
        book_doc.save()

        return {"message": "Loan updated successfully", "loan_id": loan.name}

    except Exception as e:
        return {"error": str(e)}
    
@frappe.whitelist(allow_guest=True)
def return_book(loan_id):
    try:
        # Fetch loan details
        loan = frappe.get_doc("Loan", loan_id)
        book_doc = frappe.get_doc("Books", loan.book)

        # Check if loan exists
        if not loan:
            return {"error": "Loan not found"}

        # Increase the number of copies available
        book_doc.number_of_copy += 1
        book_doc.is_available = True  # Mark book as available
        book_doc.save()

        # Delete the loan record
        frappe.delete_doc("Loan", loan_id)

        return {
            "message": "Book returned successfully",
            "book_id": book_doc.name,
            "updated_copies": book_doc.number_of_copy
        }

    except Exception as e:
        return {"error": str(e)}

# Delete a loan (only if book is returned)
@frappe.whitelist(allow_guest=True)
def delete_loan(ids):
    """Delete multiple loans"""
    try:
        deleted_loans = []
        not_found = []
        not_returned = []

        
        ids_list = frappe.parse_json(ids) if isinstance(ids, str) else ids

        for loan_id in ids_list:
            if not frappe.db.exists("Loan", loan_id):
                not_found.append(loan_id)
                continue

            loan = frappe.get_doc("Loan", loan_id)

           
            if not loan.return_date:
                not_returned.append(loan_id)
                continue

            frappe.delete_doc("Loan", loan_id)
            deleted_loans.append(loan_id)

        return {
            "message": "Loan deletion completed",
            "deleted_loans": deleted_loans,
            "not_found": not_found,
            "not_returned": not_returned
        }

    except Exception as e:
        return {"error": str(e)}

    # user
@frappe.whitelist(allow_guest=True)
def create_user(email, first_name, last_name, password, role="User"):
    """Create a new user"""
    try:
        if frappe.db.exists("User", email):
            return {"error": "User already exists"}

        new_user = frappe.get_doc({
            "doctype": "User",
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "enabled": 1,
            "new_password": password,
            "role_profile_name": role  # Assign role
        })
        new_user.insert(ignore_permissions=True)

        return {"message": "User created successfully", "user": new_user.name}

    except Exception as e:
        return {"error": str(e)}
    

@frappe.whitelist(allow_guest=True)
def get_users():
    """Fetch all users with their roles"""
    users = frappe.get_all("User", fields=["name", "first_name","last_name",  "email", "enabled", "user_type"])

    for user in users:
        roles = frappe.get_all("Has Role", filters={"parent": user["name"]}, fields=["role"])
        user["roles"] = [role["role"] for role in roles]
      

    return users


@frappe.whitelist(allow_guest=True)
def user_register(email, first_name, last_name, password,send_welcome_email, role="System User"):
    """Register a new user with a specified role"""
    try:
        # Check if user already exists
        if frappe.db.exists("User", email):
            return {"success": False, "error": "User already exists"}, 400

        # Validate the role
        if not frappe.db.exists("Role", role):
            return {"success": False, "error": f"Role '{role}' does not exist"}, 400

        # Create new user document
        new_user = frappe.get_doc({
            "doctype": "User",
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "enabled": 1,
            "new_password": password,
            "send_welcome_email": send_welcome_email,
            "roles": [{"role": role}]
             
        })
        new_user.insert(ignore_permissions=True)

        return {"success": True, "message": "User registered successfully", "user": new_user.name}

    except Exception as e:
        return {"success": False, "error": str(e)}, 500

# get user by email
@frappe.whitelist(allow_guest=True)
def get_user(email):
    """Fetch a user by email"""
    try:
        user = frappe.get_doc("User", email)
        return {
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "enabled": user.enabled
        }
    except frappe.DoesNotExistError:
        return {"error": "User not found"}
# user get by id 
@frappe.whitelist(allow_guest=True)
def get_user_by_id(user_id):
    """Fetch a user by ID"""
    try:
        user = frappe.get_doc("User", user_id)
        return {
            "user_id": user.name,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "user_type": user.user_type,
            "enabled": user.enabled,
            "roles": [role.role for role in user.roles]  
        }
    except frappe.DoesNotExistError:
        return {"error": "User not found"}

@frappe.whitelist(allow_guest=True)
def update_user(email, first_name=None, last_name=None, password=None, enabled=None, roles=None):
    """Update user details and roles"""
    try:
        user = frappe.get_doc("User", email)

        if first_name:
            user.first_name = first_name
        if last_name:
            user.last_name = last_name
        
        
        if first_name or last_name:
            user.full_name = f"{first_name or user.first_name} {last_name or user.last_name}".strip()

        if password:
            user.new_password = password
        if enabled is not None:
            user.enabled = int(enabled)

        if roles:
            roles_list = frappe.parse_json(roles) if isinstance(roles, str) else roles
            user.set("roles", [])
            for role in roles_list:
                user.append("roles", {"role": role})

        user.save(ignore_permissions=True)
        frappe.db.commit()  # Ensure changes are committed

        return {"message": "User updated successfully", "user": user.name}

    except frappe.DoesNotExistError:
        return {"error": "User not found"}
    except Exception as e:
        return {"error": str(e)}


@frappe.whitelist(allow_guest=True)
def delete_user(ids):
    """Delete multiple users"""
    try:
        email_list = frappe.parse_json(ids) if isinstance(ids, str) else ids

        if not isinstance(email_list, list):
            return {"error": "Invalid input format. Expected a list of emails."}

        not_found = []
        deleted_users = []

        for user_email in email_list:
            user_email = user_email.strip().lower()

            if frappe.db.exists("User", user_email):
                frappe.logger().info(f"Deleting user: {user_email}")  
                frappe.delete_doc("User", user_email, ignore_permissions=True)
                frappe.db.commit()  
                deleted_users.append(user_email)
            else:
                not_found.append(user_email)

        return {
            "message": "User deletion completed",
            "deleted_users": deleted_users,
            "not_found": not_found
        }

    except Exception as e:
        frappe.logger().error(f"Error deleting user: {str(e)}") 
        return {"error": str(e)}


@frappe.whitelist(allow_guest=True)  
# @validate_jwt_token
def get_total_count():
    
   
    
    # Get the total count of books
    total_books = frappe.db.count("Books")
    total_users = frappe.db.count("User")
    total_loans = frappe.db.count("Loan")
    total_members = frappe.db.count("Member")
    
    return {
        "total_books": total_books,
        "total_users": total_users,
        "total_loans": total_loans,
        "total_members": total_members,
        
    }
