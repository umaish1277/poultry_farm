import frappe
import json
import os

# Define the permission matrix
# format: DocType: [ {role, read, write, create, delete, submit, cancel, amend} ]
PERMISSIONS = {
    # Masters
    "Poultry Farm": [
        {"role": "Administrator", "read": 1, "write": 1, "create": 1, "delete": 1},
        {"role": "Poultry Manager", "read": 1, "write": 1, "create": 1, "delete": 1},
        {"role": "Poultry User", "read": 1}
    ],
    "Poultry Shed": [
        {"role": "Administrator", "read": 1, "write": 1, "create": 1, "delete": 1},
        {"role": "Poultry Manager", "read": 1, "write": 1, "create": 1, "delete": 1},
        {"role": "Poultry User", "read": 1}
    ],
    "Poultry Batch": [
        {"role": "Administrator", "read": 1, "write": 1, "create": 1, "delete": 1},
        {"role": "Poultry Manager", "read": 1, "write": 1, "create": 1, "delete": 1},
        {"role": "Poultry User", "read": 1}
    ],
    "Poultry Breed Standard": [
        {"role": "Administrator", "read": 1, "write": 1, "create": 1, "delete": 1},
        {"role": "Poultry Manager", "read": 1, "write": 1, "create": 1, "delete": 1}
    ],
    "Vaccination Template": [
        {"role": "Administrator", "read": 1, "write": 1, "create": 1, "delete": 1},
        {"role": "Poultry Manager", "read": 1, "write": 1, "create": 1, "delete": 1}
    ],
    # Operations
    "Daily Flock Entry": [
        {"role": "Administrator", "read": 1, "write": 1, "create": 1, "delete": 1, "submit": 1, "cancel": 1, "amend": 1},
        {"role": "Poultry Manager", "read": 1, "write": 1, "create": 1, "delete": 1, "submit": 1, "cancel": 1, "amend": 1},
        {"role": "Poultry User", "read": 1, "write": 1, "create": 1}
    ],
    "Live Bird Harvesting": [
        {"role": "Administrator", "read": 1, "write": 1, "create": 1, "delete": 1, "submit": 1, "cancel": 1, "amend": 1},
        {"role": "Poultry Manager", "read": 1, "write": 1, "create": 1, "delete": 1, "submit": 1, "cancel": 1, "amend": 1},
        {"role": "Poultry User", "read": 1}
    ],
    "Poultry Vaccination Schedule": [
        {"role": "Administrator", "read": 1, "write": 1, "create": 1},
        {"role": "Poultry Manager", "read": 1, "write": 1, "create": 1},
        {"role": "Poultry User", "read": 1}
    ],
    # IoT
    "Poultry Sensor": [
        {"role": "Administrator", "read": 1, "write": 1, "create": 1, "delete": 1},
        {"role": "Poultry Manager", "read": 1, "write": 1, "create": 1, "delete": 1},
        {"role": "Poultry User", "read": 1}
    ],
    "Poultry Sensor Reading": [
        {"role": "Administrator", "read": 1, "write": 1, "create": 1, "delete": 1},
        {"role": "Poultry Manager", "read": 1, "write": 1, "create": 1, "delete": 1},
        {"role": "Poultry User", "read": 1, "write": 1, "create": 1}
    ],
    "Environmental Threshold": [
        {"role": "Administrator", "read": 1, "write": 1, "create": 1, "delete": 1},
        {"role": "Poultry Manager", "read": 1, "write": 1, "create": 1, "delete": 1}
    ],
    # Settings
    "Poultry Farm Settings": [
        {"role": "Administrator", "read": 1, "write": 1, "create": 1},
        {"role": "Poultry Manager", "read": 1, "write": 1, "create": 1}
    ]
}

def execute():
    # 1. Ensure Roles Exist
    for role_name in ["Poultry Manager", "Poultry User"]:
        if not frappe.db.exists("Role", role_name):
            frappe.get_doc({"doctype": "Role", "role_name": role_name, "desk_access": 1}).insert(ignore_permissions=True)
            print(f"Created Role: {role_name}")

    # 2. Update JSON Files
    base_path = frappe.get_app_path("poultry_farm", "poultry_farm", "doctype")
    
    for doctype, perms in PERMISSIONS.items():
        module_name = frappe.scrub(doctype)
        json_path = os.path.join(base_path, module_name, f"{module_name}.json")
        
        if not os.path.exists(json_path):
            print(f"Skipping {doctype}: File not found at {json_path}")
            continue
            
        with open(json_path, 'r') as f:
            data = json.load(f)
            
        new_perms = []
        # Keep System Manager if present (or other standard roles if needed)
        # But we will replace Administrator with our specific definition to be sure
        
        if "permissions" in data:
            for p in data["permissions"]:
                if p.get("role") == "System Manager":
                    new_perms.append(p)
                # We skip existing Administrator entries to replace them with the new full-access definition
        
        if not new_perms: # If empty or cleared, add System Manager default
             new_perms.append({"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1, "email": 1, "print": 1, "share": 1, "report": 1, "export": 1})

        # Add new roles (Administrator included in PERMISSIONS dict)
        for p in perms:
            p_obj = p.copy()
            # Defaults for UI
            p_obj["print"] = 1
            p_obj["email"] = 1
            p_obj["report"] = 1
            p_obj["share"] = 1
            p_obj["export"] = 1
            new_perms.append(p_obj)
            
        data["permissions"] = new_perms
        
        with open(json_path, 'w') as f:
            json.dump(data, f, indent=1, separators=(',', ': '))
            f.write('\n') # Add newline at end
            
        print(f"Updated permissions for {doctype}")

    print("RBAC Setup Complete.")

if __name__ == "__main__":
    execute()
