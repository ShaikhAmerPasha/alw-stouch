# app_name = "alw"
# app_title = "Alw"
# app_publisher = "ERPGulf"
# app_description = "API for ALW"
# app_email = "support@erpgulf.com"
# app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "alw",
# 		"logo": "/assets/alw/logo.png",
# 		"title": "Alw",
# 		"route": "/alw",
# 		"has_permission": "alw.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/alw/css/alw.css"
# app_include_js = "/assets/alw/js/alw.js"

# include js, css files in header of web template
# web_include_css = "/assets/alw/css/alw.css"
# web_include_js = "/assets/alw/js/alw.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "alw/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "alw/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "alw.utils.jinja_methods",
# 	"filters": "alw.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "alw.install.before_install"
# after_install = "alw.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "alw.uninstall.before_uninstall"
# after_uninstall = "alw.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "alw.utils.before_app_install"
# after_app_install = "alw.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "alw.utils.before_app_uninstall"
# after_app_uninstall = "alw.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "alw.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

#### HASEEB=> alw.alw.sales.schedule_sales_import
# scheduler_events = {
# 	"all": [
# 		"alw.tasks.all"
# 	],
# 	"daily": [
# 		"alw.tasks.daily"
# 	],
# 	"hourly": [
# 		"alw.tasks.hourly"
# 	],
# 	"weekly": [
# 		"alw.tasks.weekly"
# 	],
# 	"monthly": [
# 		"alw.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "alw.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "alw.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "alw.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["alw.utils.before_request"]
# after_request = ["alw.utils.after_request"]

# Job Events
# ----------
# before_job = ["alw.utils.before_job"]
# after_job = ["alw.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"alw.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }


# doctype_js = {
#     "Imported Sales Invoice": "public/js/test1.js" ,
#     "Imported Purchase Invoice": "public/js/test2.js" ,
#      "Company" : "public/js/import.js", # Add the script for the Imported Sales Invoice Doctype
# }
# doctype_list_js = {"Imported Sales Invoice" : "public/js/sales_list.js",
#                    "Imported Purchase Invoice" : "public/js/purchase_list.js"
#                    }
# fixtures = [ {"dt": "Custom Field","filters": [["module", "=", "Alw"]] }]
