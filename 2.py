import tkinter as tk
from tkinter import ttk, messagebox
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import smtplib
import random
import string
from email.message import EmailMessage
from email_validator import validate_email, EmailNotValidError

# Google Sheets Authentication
SHEET_URL = "https://docs.google.com/spreadsheets/d/1iF4PpVfxC6k5Zmls_PI5K_qWrIq-BBbV9uyDfWtTn0A/edit?usp=sharing"  # Replace with your Google Sheet URL
CREDENTIALS_FILE = "credentials.json"  # Ensure this file is in the same directory

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
client = gspread.authorize(creds)
sheet = client.open_by_url(SHEET_URL).sheet1  # Open the first sheet

# Email Configuration
EMAIL_SENDER = "sonalimitra5224@gmail.com"  # Replace with your email
EMAIL_PASSWORD = "vzso fgmk hlva vvcz"  # Use an App Password if needed

otp_storage = {}  # Dictionary to store OTPs

# Function to send OTP
def send_otp():
    email = email_entry.get().strip()

    try:
        validate_email(email)  # Validate email format
    except EmailNotValidError:
        messagebox.showerror("Error", "Invalid email address!")
        return

    otp = ''.join(random.choices(string.digits, k=6))  # Generate a 6-digit OTP
    otp_storage[email] = otp

    msg = EmailMessage()
    msg.set_content(f"Your OTP for subscription verification is: {otp}")
    msg["Subject"] = "Subscription OTP Verification"
    msg["From"] = EMAIL_SENDER
    msg["To"] = email

    try:
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        messagebox.showinfo("OTP Sent", "An OTP has been sent to your email!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to send OTP: {e}")

# Function to verify OTP and save subscriber details
def subscribe():
    name = name_entry.get().strip()
    dob = dob_entry.get().strip()
    email = email_entry.get().strip()
    phone = phone_entry.get().strip()
    gender = gender_var.get()
    entered_otp = otp_entry.get().strip()

    if not name or not dob or not email or not phone or gender == "Select Gender":
        messagebox.showerror("Error", "All fields are required!")
        return

    if email not in otp_storage or otp_storage[email] != entered_otp:
        messagebox.showerror("Error", "Invalid OTP!")
        return

    # Fetch the next serial number
    existing_data = sheet.get_all_values()
    serial_no = len(existing_data)  # Auto-increment S. No.

    # Save details to Google Sheet
    sheet.append_row([serial_no, name, dob, email, phone, gender])

    messagebox.showinfo("Success", "Subscription successful!")
    name_entry.delete(0, tk.END)
    dob_entry.delete(0, tk.END)
    email_entry.delete(0, tk.END)
    phone_entry.delete(0, tk.END)
    otp_entry.delete(0, tk.END)
    gender_var.set("Select Gender")
    del otp_storage[email]  # Remove OTP after successful subscription

# Function to view subscribers
def view_subscribers():
    subscribers = sheet.get_all_values()
    
    if len(subscribers) <= 1:  # Check if only headers exist
        messagebox.showinfo("Info", "No subscribers yet!")
        return
    
    view_window = tk.Toplevel(root)
    view_window.title("Subscribers List")
    view_window.state('zoomed')  # Make window full-screen

    # Create a Treeview
    tree = ttk.Treeview(view_window, columns=("S. No.", "Name", "DOB", "E-mail", "Phone Number", "Gender"), show="headings")
    
    # Define Column Headings
    tree.heading("S. No.", text="S. No.")
    tree.heading("Name", text="Name")
    tree.heading("DOB", text="DOB")
    tree.heading("E-mail", text="E-mail")
    tree.heading("Phone Number", text="Phone Number")
    tree.heading("Gender", text="Gender")

    # Define Column Widths
    tree.column("S. No.", width=50)
    tree.column("Name", width=150)
    tree.column("DOB", width=100)
    tree.column("E-mail", width=200)
    tree.column("Phone Number", width=150)
    tree.column("Gender", width=100)

    # Insert Data into Table
    for row in subscribers[1:]:  # Skip headers
        tree.insert("", tk.END, values=row)

    tree.pack(expand=True, fill="both")

# Create Main Window
root = tk.Tk()
root.title("Subscription Form")
root.state('zoomed')  # Make full-screen

# Labels and Entry Fields
tk.Label(root, text="Name:").pack(pady=5)
name_entry = tk.Entry(root, width=30)
name_entry.pack()

tk.Label(root, text="Date of Birth (DD/MM/YYYY):").pack(pady=5)
dob_entry = tk.Entry(root, width=30)
dob_entry.pack()

tk.Label(root, text="Email:").pack(pady=5)
email_entry = tk.Entry(root, width=30)
email_entry.pack()

tk.Label(root, text="Phone Number:").pack(pady=5)
phone_entry = tk.Entry(root, width=30)
phone_entry.pack()

tk.Label(root, text="Gender:").pack(pady=5)
gender_var = tk.StringVar(value="Select Gender")
gender_dropdown = ttk.Combobox(root, textvariable=gender_var, values=["Male", "Female", "Other"], state="readonly")
gender_dropdown.pack()

tk.Label(root, text="Enter OTP:").pack(pady=5)
otp_entry = tk.Entry(root, width=30)
otp_entry.pack()

# Buttons
tk.Button(root, text="Send OTP", command=send_otp, bg="orange", fg="black").pack(pady=5)
tk.Button(root, text="Subscribe", command=subscribe, bg="green", fg="white").pack(pady=5)
tk.Button(root, text="View Subscribers", command=view_subscribers, bg="blue", fg="white").pack(pady=5)

root.mainloop()
