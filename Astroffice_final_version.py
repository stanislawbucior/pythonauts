import datetime
import os
import smtplib
from email.mime.text import MIMEText
import getpass
 
class Employee:
 
    def __init__(self, name, ID, department):
        self.name = name
        self.ID = ID
        self.department = department
        self.employee_dict = {}

# load the dictionary of employees in order to edit it by adding a new employee 
    def load_employee_dict_from_file(self, file_name):
        with open(file_name, "r") as f:
            for line in f:
            # Each line has the follwing format: ID: {empl_id}, Name: {name}, Department: {department}
                parts = line.split(',')
                empl_id = parts[0].split(':')[1].strip()
                name = parts[1].split(':')[1].strip()
                department = parts[2].split(':')[1].strip()
                self.employee_dict[empl_id] = (name, department)
 
# save the updated dictionary of employees
    def save_employee_dict_in_file(self, file_name):
        self.load_employee_dict_from_file(file_name)  # Load existing data
   
    # Now, overwrite with the merged data
        with open(file_name, "w") as f:
            for empl_id, empl_info in self.employee_dict.items():
                name, department = empl_info
                f.write(f"ID: {empl_id}, Name: {name}, Department: {department}\n")
 
class Office:
 
    def __init__(self, location, capacity, sdate, edate):
        self.location = location
        self.capacity = capacity
        self.database = {}

        #creates a list of dates from the sdate to the edate
        dates = []
        current_date = sdate 
        while current_date < edate:
            dates.append(current_date)
            current_date += datetime.timedelta(days=1)
           
        for date in dates:
            self.database[date] = []
   
    #returns capacity of an office
    def get_capacity(self):
        return self.capacity

    # creates a file in which the seat bookings in an office will be saved  
    def save_dict_in_file(self, file_name):
        k=[]
        with open(file_name, "w") as f:
            for key in self.database.keys():
               f.write(str(key)+"\n")

# SUPPORTING FUNCTION

# ask user for a date and return it
def get_date_from_user():
    year=input("Year: ")
    month=input("Month: ")
    day=input("Day: ")
    sdate=datetime.date(int(year), int(month), int(day))
    return sdate

# CREATE OBJECT FUNCTIONS

# create a new Employee object
def create_employee():
    try:
        open("Employees.txt", "x")
    except:
        None
    print("What is the name of the new employee?")
    empl_name = input()
    print("What is his/her employee ID?")
    empl_ID = input()
    print("In which department is the new employee working?")
    empl_dep = input()
    new_employee = Employee(empl_name, empl_ID, empl_dep)
    new_employee.employee_dict[empl_ID] = (new_employee.name, new_employee.department)
    new_employee.save_employee_dict_in_file("Employees.txt")
    return new_employee

# create new Office object
def create_office():
    print("Where would you like to open a new office?")
    new_location = input()
    print("What is the maximum capacity of desk within the new office?")
    max_capacity = input()
    print("Enter date from which employees can book seats in the new office")
    sdate = get_date_from_user()
    print("Enter date until which employees can book seats in the new office: ")
    edate=get_date_from_user()
    
    # Update the capacity file with the new office's information
    update_office_capacity(new_location, max_capacity)
    
    new_office = Office(new_location, max_capacity, sdate, edate)
    new_office.save_dict_in_file(f"{new_office.location}.txt")
    return new_office

# MANAGE AND VIEW BOOKING FUNCTIONS

# view the capacity at a certain date in a certain place
def view_capacity():
    office_name = input("Which office do you want to select? ")
    file_name = f"{office_name}.txt"

    # check if the file for the office exists
    if not os.path.exists(file_name):
        print(f"No data available for the office: {office_name}.")
        return
    
    print("On which date do you want to work in this office?")
    date_str = str(get_date_from_user())
    # retrieve office capacity
    capacity = get_office_capacity(office_name)

    with open(file_name, "r") as f:
        for line in f:
            line_date_str, *booked_seats = line.strip().split(', ')
            if line_date_str == date_str:
                seats_left = capacity - len(booked_seats)
                print(f'{len(booked_seats)} seats are occupied and {seats_left} seats are left.')

    return "No data available for the selected date."
 
# Helper function to update the "office_capacity.txt" file 
def update_office_capacity(office_name, capacity):
    with open("office_capacity.txt", "a") as f:
        f.write(f"{office_name}: {capacity}\n")

# Fallback mechanism if "office_capacity.txt" doesn't exist
def get_office_capacity(office_name):
    try:
        with open("office_capacity.txt", "r") as f:
            for line in f:
                office, capacity = line.strip().split(":")
                if office == office_name:
                    return int(capacity)
        return None  # Returns None if office_name is not found
    except FileNotFoundError:
        print("Error: office_capacity.txt file not found.")
        return None

# allows employee to book a seat
def book_seat():
    employee_ID = input("What is your employee ID? ")
    office_name = input("In which office do you want to work? ")
    file_name = str(office_name + ".txt")

    print("Date for which you want to book a seat: ")
    date_str = str(get_date_from_user())
    booked = False

    # Retrieve office capacity
    capacity = get_office_capacity(office_name)
    if capacity is None:
        print(f"No capacity information found for office: {office_name}")
        return

    with open(file_name, "r") as f:
        lines = f.readlines()

    for i in range(len(lines)):
        if lines[i].startswith(date_str):
            seats = [x.strip() for x in lines[i][len(date_str):].split(",") if x.strip()]
            if len(seats) < capacity:
                seats.append(employee_ID)
                lines[i] = date_str + ", " + ", ".join(seats) + "\n"
                booked = True
            else:
                print("Unable to book a seat. Capacity was reached.")
            break

    with open(file_name, "w") as f:
        f.writelines(lines)

    if booked:
        print("Seat booked successfully!")
        if len(seats) < capacity:
            ask_invite = input("Would you like to invite a co-worker? Yes/No: ")
            if ask_invite == "Yes":
                send_email(date_str, office_name)
            else:
                None

# allows employee to cancel a seat booking
def cancel_seat():
    employee_ID = input("What is your employee ID? ")
    office_name = input("In which office do you want to cancel a seat? ")
    file_name = str(office_name + ".txt")

    print("Date for which you want to cancel a seat: ")
    date_str = str(get_date_from_user())
    canceled = False

    # Retrieve office capacity
    capacity = get_office_capacity(office_name)
    if capacity is None:
        print(f"No information found for office: {office_name}")
        return

    with open(file_name, "r") as f:
        lines = f.readlines()

    for i in range(len(lines)):
        if lines[i].startswith(date_str):
            seats = [x.strip() for x in lines[i][len(date_str):].split(",") if x.strip()]
            if employee_ID in seats:
                seats.remove(employee_ID)
                if seats==[]:
                    lines[i]=str(date_str+"\n")
                else:    
                    lines[i] = date_str + ","+",".join(seats) + "\n"
                canceled = True
            else:
                print("Your reservation was not found for the given date.")
            break

    if canceled:
        with open(file_name, "w") as f:
            f.writelines(lines)
        print("Seat canceled successfully!")       

# INVITE A COWORKER TO THE OFFICE FUNCTION

# allows employee to invite a teammate to work in the office on the same day
def send_email(date_str, office_name):
    co_worker = input("Which co-worker would you like to invite? ")
    email_address = input("Please tell me his email address: ")
    subject = "Join me at the office!"
    body = f"Hi {co_worker},\n \nI'll be at our office in {office_name} on {date_str}. Would be wonderful to share the space and catch up. Hope to see you there!\n \nCheers"
    sender = "python3shsg@gmail.com"
    recipients = [f"{email_address}"]
    password = "gobjjlqwgddadkkj"
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
       smtp_server.login(sender, password)
       smtp_server.sendmail(sender, recipients, msg.as_string())
    print("Message sent!")
 
# MOTIVATIONAL MESSAGE FUNCTIONS

# returns a list of all offices created by admin
def get_list_of_offices():
    list_of_offices=[]
    with open("office_capacity.txt", "r") as f:
        for line in f:
            office=line.split(":")[0]
            list_of_offices.append(office)
    return list_of_offices

# returns tomorrrow date
def get_tomorrow_date():
    today=datetime.date.today()
    tomorrow= today+datetime.timedelta(days=1)
    return str(tomorrow)

# returns number of people working in all offices tomorrow
def get_nop_in_office_tomorrow(list_of_offices):
    total=0
    tomorrow=get_tomorrow_date()
    for office in list_of_offices:
        with open(office+".txt", "r") as f:
            for line in f:
                if line[0:10]==tomorrow:   
                    n_booked_seats=len(line.split(","))-1
                    total=total+n_booked_seats
    return total

# prints motivational message for the employee
def motivational_message():
    list_of_offices=get_list_of_offices()
    n_of_people=get_nop_in_office_tomorrow(list_of_offices)
    if n_of_people>0:
        print("The number of employees in the offices tomorrow is "+str(n_of_people)+". Join them!!!")

# MAIN functions

# Start - General function level 1
def MAIN_function():
    password = "Admin123"
    user_input = input("If you're an ADMIN choose 1 - \nIf you're an EMPLOYEE choose 2 \nEnter here: ")
    if user_input == "1":
        password_input = getpass.getpass("Password: ")
        if password_input == password:
            admin_function()
        else:
            print("Password is incorrect.")
    elif user_input == "2":
        employee_function()
 
# Start - General function level 2
def admin_function():
    user_input = input("If you like to create a NEW OFFICE choose 1 -\nIf you like to create a NEW EMPLOYEE choose 2 \nEnter here: ")
    if user_input == "1":
        create_office()
    elif user_input == "2":
        create_employee()
 
# Start - General function level 3
def employee_function():
    motivational_message()
    user_input = input("If you want to BOOK A SEAT choose 1 -\nIf you want to CANCEL A SEAT choose 2 -\nIf you want to VIEW CAPACITY choose 3 \nEnter here: ")
    if user_input == "1":
        book_seat()
    elif user_input == "2":
        cancel_seat()
    elif user_input == "3":
        view_capacity()    
    
MAIN_function()