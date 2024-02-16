from cryptography.fernet import Fernet
import json
from getpass import getpass

DATABASE_FILE = 'database.json'
KEY_FILE = 'secret.key'

def generate_key():
    key = Fernet.generate_key()
    with open(KEY_FILE, 'wb') as key_file:
        key_file.write(key)

def load_key():
    try:
        return open(KEY_FILE, 'rb').read()
    except FileNotFoundError:
        generate_key()
        return load_key()

def load_database():
    try:
        with open(DATABASE_FILE, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {"entries": []}

def save_database(database):
    with open(DATABASE_FILE, 'w') as file:
        json.dump(database, file, indent=4)  # Indent for pretty formatting

def encrypt(value, key):
    cipher_suite = Fernet(key)
    return cipher_suite.encrypt(value.encode('utf-8')).decode('utf-8')

def decrypt(value, key):
    cipher_suite = Fernet(key)
    return cipher_suite.decrypt(value.encode('utf-8')).decode('utf-8')

def verify_password(input_password, hashed_password, key):
    return input_password == decrypt(hashed_password, key)

def add_initial_admin_entry(database, key):
    admin_entry = {
        "s.no": 1,
        "password": encrypt("admin", key),
        "username": encrypt("admin", key),
        "age": encrypt("1", key),
        "address": encrypt("admin", key),
        "contactno": encrypt("1", key),
        "job_description": encrypt("admin", key),
        "attendance": encrypt("1", key)
    }
    database["entries"].append(admin_entry)
    save_database(database)

def new_entry(database, key):
    entry = {
        "s.no": len(database["entries"]) + 1,
        "password": encrypt(getpass("Enter password: "), key),
        "username": encrypt(input("Enter username: "), key),
        "age": encrypt(input("Enter age: "), key),
        "address": encrypt(input("Enter address: "), key),
        "contactno": encrypt(input("Enter contact number: "), key),
        "job_description": encrypt(input("Enter job description: "), key),
        "attendance": encrypt(input("Enter attendance: "), key)
    }
    database["entries"].append(entry)
    save_database(database)
    print("New entry added successfully.")

def change_entry(database, key):
    s_no = int(input("Enter s.no to change entry: "))
    
    for entry in database["entries"]:
        if entry["s.no"] == s_no:
            print("\nChoose a field to change:")
            print("1. Password")
            print("2. Username")
            print("3. Age")
            print("4. Address")
            print("5. Contact Number")
            print("6. Job Description")
            print("7. Attendance")
            
            field_choice = int(input("Choose a field (1-7): "))
            new_value = encrypt(input("Enter new value: "), key)
            
            fields = ["password", "username", "age", "address", "contactno", "job_description", "attendance"]
            field_to_change = fields[field_choice - 1]
            
            entry[field_to_change] = new_value
            save_database(database)
            print(f"{field_to_change.capitalize()} changed successfully.")
            return
    
    print(f"No entry found with s.no {s_no}.")

def attendance_entry(database, key):
    s_no = int(input("Enter s.no for attendance entry: "))
    
    for entry in database["entries"]:
        if entry["s.no"] == s_no:
            operation = input("Choose + to add attendance, - to subtract attendance: ")
            if operation == "+":
                entry["attendance"] = encrypt(str(int(decrypt(entry["attendance"], key)) + 1), key)
            elif operation == "-":
                entry["attendance"] = encrypt(str(int(decrypt(entry["attendance"], key)) - 1), key)
            else:
                print("Invalid operation. Please choose + or -.")
                return
            
            save_database(database)
            print("Attendance updated successfully.")
            return
    
    print(f"No entry found with s.no {s_no}.")

def search_entry(database, key):
    s_no = int(input("Enter s.no to search entry: "))
    
    for entry in database["entries"]:
        if entry["s.no"] == s_no:
            print("\nEntry Details:")
            print(f"S.No: {entry['s.no']}")
            print(f"Username: {decrypt(entry['username'], key)}")
            print(f"Age: {decrypt(entry['age'], key)}")
            print(f"Address: {decrypt(entry['address'], key)}")
            print(f"Contact Number: {decrypt(entry['contactno'], key)}")
            print(f"Job Description: {decrypt(entry['job_description'], key)}")
            print(f"Attendance: {decrypt(entry['attendance'], key)}")
            print(f"Password: {decrypt(entry['password'], key)}")  # Include password in search results
            return
    
    print(f"No entry found with s.no {s_no}.")

def list_entries(database, key):
    print("\nList of Entries:")
    for entry in database["entries"]:
        print(f"S.No: {entry['s.no']}, Username: {decrypt(entry['username'], key)}")

def delete_entry(database, key):
    s_no_to_delete = int(input("Enter S.No to delete entry: "))
    for entry in database["entries"]:
        if entry["s.no"] == s_no_to_delete:
            database["entries"].remove(entry)
            save_database(database)
            print(f"Entry with S.No {s_no_to_delete} deleted successfully.")
            return
    print(f"No entry found with S.No {s_no_to_delete}.")

def admin_menu(database, key):
    password = getpass("Enter admin password: ")

    if not database["entries"]:
        add_initial_admin_entry(database, key)

    if verify_password(password, database["entries"][0]["password"], key):
        while True:
            print("\nAdmin Menu:")
            print("1. New Entry")
            print("2. Change Entry")
            print("3. Attendance")
            print("4. Search Entry")
            print("5. List Entries")
            print("6. Delete Entry")
            print("7. Logout")
            
            choice = input("Choose an option (1-7): ")
            
            if choice == "1":
                new_entry(database, key)
            elif choice == "2":
                change_entry(database, key)
            elif choice == "3":
                attendance_entry(database, key)
            elif choice == "4":
                search_entry(database, key)
            elif choice == "5":
                list_entries(database, key)
            elif choice == "6":
                delete_entry(database, key)
            elif choice == "7":
                break
            else:
                print("Invalid choice. Please try again.")

def normal_menu(database, key):
    s_no = int(input("Enter s.no: "))
    password = getpass("Enter password: ")
    
    for entry in database["entries"]:
        if entry["s.no"] == s_no and verify_password(password, entry["password"], key):
            print("\nUser Details:")
            print(f"S.No: {entry['s.no']}")
            print(f"Username: {decrypt(entry['username'], key)}")
            print(f"Age: {decrypt(entry['age'], key)}")
            print(f"Address: {decrypt(entry['address'], key)}")
            print(f"Contact Number: {decrypt(entry['contactno'], key)}")
            print(f"Job Description: {decrypt(entry['job_description'], key)}")
            print(f"Attendance: {decrypt(entry['attendance'], key)}")
            return
    
    print("Invalid s.no or password.")

def main():
    key = load_key()
    database = load_database()
    
    while True:
        print("\nMain Menu:")
        print("1. Admin")
        print("2. Normal")
        print("3. Exit")
        
        choice = input("Choose an option (1-3): ")
        
        if choice == "1":
            admin_menu(database, key)
        elif choice == "2":
            normal_menu(database, key)
        elif choice == "3":
            print("Exiting the application.")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
