cors = {
    "allow_origins": ["http://localhost:3000"],  
    "allow_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    "allow_headers": ["Content-Type", "Authorization", "X-Frappe-CSRF-Token"],
}



app_name = "library_management"
app_title = "Library Management"
app_publisher = "Frappe"
app_description = "App for managing Articles, Members, Memberships and Transactions for Libraries"
app_icon = "icon-book"
app_color = "#589494"
app_email = "info@frappe.io"
app_url = "https://frappe.io/apps/library_management"
app_version = "0.0.1"

role_home_page = {
	"Library Member": "article"
}
override_whitelisted_methods = {
     "library_management.api.user_login": "library_management.api.user_login",
     "library_management.api.user_register": "library_management.api.user_register",
      # User APIs
    "library_management.api.get_users": "library_management.api.get_users",
    "library_management.api.get_user_by_id": "library_management.api.get_user_by_id",
    "library_management.api.update_user": "library_management.api.update_user",
    "library_management.api.delete_user": "library_management.api.delete_user",
    #get all roles
    "library_management.api.get_all_roles": "library_management.api.get_all_roles",
    
     # Books API
    "library_management.api.get_books": "library_management.api.get_books",
    "library_management.api.get_available_books": "library_management.api.get_available_books",
    "library_management.api.create_book": "library_management.api.create_book",
    "library_management.api.get_book_by_id": "library_management.api.get_book_by_id",
    "library_management.api.update_book": "library_management.api.update_book",
    "library_management.api.delete_book": "library_management.api.delete_book",
    "library_management.api.update_book_availability": "library_management.api.update_book_availability",
    
	# Members API
    "library_management.api.get_members": "library_management.api.get_members",
    "library_management.api.create_member": "library_management.api.create_member",
    "library_management.api.get_member_by_id": "library_management.api.get_member_by_id",
    "library_management.api.update_member": "library_management.api.update_member",
    "library_management.api.delete_member": "library_management.api.delete_member",


      # Loans API (Newly Added)
    "library_management.api.get_loans": "library_management.api.get_loans",
    "library_management.api.report_currently_loaned_books": "library_management.api.report_currently_loaned_books",
    "library_management.api.get_overdue_books": "library_management.api.get_overdue_books",
   "library_management.api.create_loan": "library_management.api.create_loan",
    "library_management.api.get_loan_by_id": "library_management.api.get_loan_by_id",
    "library_management.api.update_loan": "library_management.api.update_loan",
    "library_management.api.delete_loan": "library_management.api.delete_loan",
    "library_management.api.return_book": "library_management.api.return_book",
    # total count
    "library_management.api.get_total_count": "library_management.api.get_total_count",
}
fixtures = [
    {"dt": "User"}
]



# CORS settings
def get_cors_headers():
    return {
        "Access-Control-Allow-Origin": "*", 
        "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization1",
    }

# Hooking into request-response cycle
def on_request(response):
    if response:
        headers = get_cors_headers()
        for key, value in headers.items():
            response.headers[key] = value
    return response


# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/library_management/css/library_management.css"
# app_include_js = "/assets/library_management/js/library_management.js"

# include js, css files in header of web template
# web_include_css = "/assets/library_management/css/library_management.css"
# web_include_js = "/assets/library_management/js/library_management.js"

# Installation
# ------------

# before_install = "library_management.install.before_install"
# after_install = "library_management.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "library_management.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.core.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.core.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
#	}
# }

# Scheduled Tasks
# ---------------

scheduler_events = {
	"daily": [
		"library_management.tasks.daily"
	],
}

# scheduler_events = {
# 	"all": [
# 		"library_management.tasks.all"
# 	],
# 	"daily": [
# 		"library_management.tasks.daily"
# 	],
# 	"hourly": [
# 		"library_management.tasks.hourly"
# 	],
# 	"weekly": [
# 		"library_management.tasks.weekly"
# 	]
# 	"monthly": [
# 		"library_management.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "library_management.install.before_tests"

