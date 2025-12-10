# Client connecting to server
import socket
import json
from datetime import datetime

PORT = 5050
SERVER = "10.20.203.0"

VALID_MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]

COURSES = {
    "1": "MSc Cyber Security",
    "2": "MSc Information Systems & Computing",
    "3": "MSc Data Analytics"
}



def validate_name(name):
    return name.strip() != "" and not any(char.isdigit() for char in name)


def validate_year(year):
    return year.isdigit() and len(year) == 4 and int(year) >= datetime.now().year


def validate_month(month):
    return month.capitalize() in VALID_MONTHS


def validate_course(choice):
    return choice in COURSES


def validate_details(data):
    errors = {}

    if not validate_name(data["name"]):
        errors["name"] = "Name cannot be empty and must contain no numbers."

    if not data["address"].strip():
        errors["address"] = "Address cannot be empty."

    if not data["education"].strip():
        errors["education"] = "Education field cannot be empty."

    if not validate_year(data["year"]):
        errors["year"] = "Year must be a 4-digit number >= current year."

    if not validate_month(data["month"]):
        errors["month"] = "Month must be a valid month name (e.g., April)."

    return errors


#SAVE

def edit_details(data):
    print("\nWhich field do you want to edit?")
    print("1. Name")
    print("2. Address")
    print("3. Education Qualifications")
    print("4. Course")
    print("5. Start Year")
    print("6. Start Month")
    print("7. Everything is correct — Save")

    choice = int(input("Enter option: ")).strip()

    if choice == 1:
        data["name"] = input("Enter Name: ")

    elif choice == 2:
        data["address"] = input("Enter Address: ")

    elif choice == 3:
        data["education"] = input("Enter Education Qualifications: ")

    elif choice == 4:
        print("\nSelect Course:")
        for i, j in COURSES.items():
            print(f"{i}. {j}")
        c = input("Enter option (1/2/3): ").strip()
        if validate_course(c):
            data["course"] = COURSES[c]

    elif choice == 5:
        data["year"] = input("Enter Start Year: ")

    elif choice == 6:
        data["month"] = input("Enter Start Month: ")

    elif choice == 7:
        return "SAVE"

    return data

# Editing details

def confirm_and_edit(data):
    while True:
        print("      PLEASE CONFIRM YOUR DETAILS        ")
        for key, value in data.items():
            print(f"{key.capitalize()}: {value}")

        errors = validate_details(data)

        if errors:
            print("\nSome fields have problems:")
            for i, j in errors.items():
                print(f"- {i}: {j}")

        # Run edit menu
        result = edit_details(data)

        if result == "SAVE":
            # Ensure no validation errors before saving
            errors = validate_details(data)
            if not errors:
                return data
            else:
                print("\n Cannot save — fix the errors above.")
                continue
        else:
            data = result

# GET USER INPUT

def get_student_details():
    data = {}

    print(" DBS Student Application Form \n")
    print("-----------------------------  \n")
    data["name"] = input(f"Enter your full name: ")
    data["address"] = input(f"Enter your address: ")
    data["education"] = input(f"Enter your education qualifications: ")

    print("\nSelect Course:")
    for key, value in COURSES.items():
        print(f"{key}. {value}")

    course_choice = input("Enter option (1/2/3): ").strip()
    data["course"] = COURSES.get(course_choice, "MSc Cyber Security")
    data["year"] = input("Enter intended start YEAR (e.g. 2026): ")
    data["month"] = input("Enter intended start MONTH (e.g. April): ")

    return data

#
# Client socket

def start_client():
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((SERVER, PORT))
        print("\nConnected to server.\n")

        #  Input + Validation + Editing
        details = get_student_details()
        final_details = confirm_and_edit(details)
       # Send JSON to server
        client.send(json.dumps(final_details).encode())

        #  Receive response (unique number)
        response = client.recv(1024).decode()
        print(f"Your application reference is ", response)

        client.close()

    except Exception as e:
        print("Error submitting details")


if __name__ == "__main__":
    start_client()
