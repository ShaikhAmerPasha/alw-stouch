import frappe
from frappe import _

# Define secret key
KEY_validate_key_piapi = "71cd9a112e6b1dc"  # purchase invoice
KEY_validate_key_siapi = "42cd89146e3v1wu"  # sales invoice


# CALL: bench execute alw.alw.apikey.validate_key_piapi --kwargs '{"key":"pointh#rf7s@7475_"}'
@frappe.whitelist(allow_guest=True)
def validate_key_piapi(key):
    # key = frappe.local.session.data.get('api_key')
    if key != KEY_validate_key_piapi:
        # If the key is incorrect, return a 403 Forbidden response
        # return {"valid":"0","status": "failed"}
        frappe.throw(_("Invalid Secret Key"), frappe.PermissionError)
    # If the key is valid, return the response
    return {"valid":"1","status": "success"}

# CALL: bench execute alw.alw.apikey.validate_key_siapi --kwargs '{"key":"pointh#zsER@67#0_"}'
@frappe.whitelist(allow_guest=False)
def validate_key_siapi(key):
    if key != KEY_validate_key_siapi:
        # If the key is incorrect, return a 403 Forbidden response
        frappe.throw(_("Invalid Secret Key"), frappe.PermissionError)
    # If the key is valid, return the response
    return {"valid":"1","status": "success"}
