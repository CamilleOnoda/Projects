from tkinter import *
from tkinter import messagebox
from cryptography.fernet import Fernet
import random
import pyperclip
import string
import os
import json


# -----------------------User interface-----------------------------------------
window = Tk()
window.title("Cryptic Pass")
window.config(padx=30, pady=30)
img = PhotoImage(file="logo.png")
window.iconphoto(False, img)
canvas = Canvas(width=300,height=200)
canvas.create_image(150, 100, image=img)
canvas.grid(column=1, row=0)


# -----------------------Encryption key handling--------------------------------
def generate_key():
    key = Fernet.generate_key()
    with open("secret.key", "wb") as key_file:
        key_file.write(key)


def load_key():
    key_file_path = "secret.key"
    if not os.path.isfile(key_file_path):
        generate_key()
    with open(key_file_path, "rb") as key_file:
        return key_file.read()

encryption_key = load_key()


# -----------------------Data processing----------------------------------------
def main():
    website = website_entry.get().lower().strip()
    email = email_username_entry.get()
    password = password_entry.get()

    if not website or not email or not password:
        messagebox.showinfo(title=None, message="Please fill in all required information")
    else:
        encrypted_password = encrypt_data(password, encryption_key)
        data = read_data()
        create_or_update(data, website, email, encrypted_password)
        clear_entries()
                

def clear_entries():
    website_entry.delete(0, END)
    email_username_entry.delete(0, END)
    password_entry.delete(0, END)


def read_data():
    """Read the json file. If it doesn't exist, it creates a new JSON file."""
    try:
        with open("data.json", "r") as file:
            data = json.load(file)
        return data
    except (FileNotFoundError, json.JSONDecodeError):
        data = []
        return data


def save_data(data):
    with open("data.json", "w") as file:
        json.dump(data, file, indent=4, default=lambda x: x.decode() if 
                  isinstance(x, bytes) else x)


def create_or_update(data, website, email, encrypted_password):
    website = website_entry.get().lower()
    email = email_username_entry.get().lower()

    entry_found = False

    for entry in data:
        if entry["website"] == website and entry["email"] == email:
            update_password = messagebox.askyesno(title=website, message=
                                                  f"The website <{website}>"
                                        " already exists with this email."
                                        " Do you want to update the password?")
            if update_password:
                entry["password"] = encrypted_password
                save_data(data)
                messagebox.showinfo(title=None, message="Password updated!")
            entry_found = True
            break

        elif entry["website"] == website and entry["email"] != email:
            update_info = messagebox.askyesno(title=website, message=f"The website <{website}>"
                                        " already exists in the data file."
                                            " Do you want to add another entry?")
            if update_info:
                data.append({"website": website, "email": email, "password": encrypted_password})
                save_data(data)
                messagebox.showinfo(title=None, message="Password updated!")
            entry_found = True
            break

    if not entry_found:
        append_entry = messagebox.askyesno(title=website, message=f"Do you want to add a new entry?")
        if append_entry:
            data.append({"website": website, "email": email, "password": encrypted_password})
            save_data(data)
            clear_entries()
            messagebox.showinfo(title=None, message="New entry added!")

    return data

 
def search_password():
    """The user enters the name of a website and retrieves the decrypted password."""
    website = website_entry.get().lower()
    email = email_username_entry.get().lower()
    
    if not email or not website:
        messagebox.showinfo(title=None, message="Please fill in all required information.")
    else:
        data = read_data()
        decrypted_password = get_decrypted_password(website, email, data)
    
        if decrypted_password:
            pyperclip.copy(decrypted_password)
            messagebox.showinfo(title=None, message="Password copied to clipboard "
                                f"for website:<{website}>\nEmail:<{email}>")
        else:
            messagebox.showerror(title=None, message="Information not found.")


def get_decrypted_password(website, email, data):
    """Decrypt the password using the encryption key"""
    for entry in data:
        if entry["website"] == website and entry["email"] == email:
            encrypted_password = entry["password"]
            decrypted_password = decrypt_data(encrypted_password, encryption_key)
            return decrypted_password   
    return None


def delete_website():
    """The user can delete all data associated with a website and an email."""
    website = website_entry.get().lower()
    email = email_username_entry.get().lower()

    if not email:
        messagebox.showinfo(title=None, message="Please enter an email address")
    else:
        data = read_data()
        entry_found = False
        for entry in data:
            if entry["website"] == website and entry["email"] == email:
                entry_found = True
                delete = messagebox.askokcancel(title=website, message=f"Do you want to delete "
                                        f"information for:\nWebsite:<{website}>\nEmail:<{email}>?")
                if delete:
                    if entry["email"] == email and entry["website"] == website:
                        data.remove(entry)
                        save_data(data)     
                        messagebox.showinfo(title=None, message=f"Information deleted for:"
                                            f"\nWebsite:<{website}>\nEmail:<{email}>\nd")
        if not entry_found:
            messagebox.showerror(title=None, message=f"Information not found.")


# -----------------------Generate random password-------------------------------
# -----------------------Get the length of the password-------------------------
password_len = IntVar()
length = Spinbox(from_= 6, to_= 12, textvariable=password_len, width=22)
length.grid(column=0, row=5, ipady=2, columnspan=2)

generated_password = StringVar()
combination = [string.punctuation, string.ascii_uppercase, string.digits, string.ascii_lowercase]
def randPassGen():
    password = ""
    for char in range(password_len.get()):
        char = random.choice(combination)
        password = password + random.choice(char)
    generated_password.set(password)


# -----------------------Copy to clipboard--------------------------------------
def copy_password():
    pyperclip.copy(generated_password.get())
    messagebox.showinfo(title=None, message="Password copied to clipboard.")


# -----------------------Data encryption and decryption-------------------------
def encrypt_data(data, key):
    fernet = Fernet(key)
    encrypted_data = fernet.encrypt(data.encode())
    return encrypted_data


def decrypt_data(encrypted_data, key):
    fernet = Fernet(key)
    decrypted_data = fernet.decrypt(encrypted_data).decode()
    return decrypted_data


# -----------------------Labels-------------------------------------------------
website_label = Label(text="Website", font=('Times',12))
website_label.grid(column=0, row=1,sticky=W)
email_username_label = Label(text="Email/Username", font=('Times',12))
email_username_label.grid(column=0, row=3,sticky=W)
password_label = Label(text="Random Password", font=('Times',12))
password_label.grid(column=0, row=4,sticky=W)
password_length_label = Label(text="Password length (6 - 12)", font=('Times',12))
password_length_label.grid(column=0, row=5,sticky=W)


# -----------------------Entries------------------------------------------------
website_entry = Entry(width=50)
website_entry.grid(column=1,row=1)
website_entry.focus()
email_username_entry = Entry(width=50)
email_username_entry.grid(column=1, row=3)
email_username_entry.insert(0, "")
password_entry = Entry(textvariable=generated_password, width=50)
password_entry.grid(column=1, row=4)


# -----------------------Buttons------------------------------------------------
generate_password_button = Button(text="Generate a password", font=('Times',12), command=randPassGen)
generate_password_button.grid(column=1, row=6, sticky=W, padx=(24,0))
save_button = Button(text="Save", font=('Times',12), command=main)
save_button.grid(column=1, row=8, sticky=W, padx=(24,0))
clipboard = Button(text="Copy to clipboard", font=('Times',12), command=copy_password)
clipboard.grid(column=1, row=7, sticky=W, padx=(24,0))
search_button = Button(text="Search Password", width=12, font=('Times',12), command=search_password)
search_button.grid(column=2, row=2)
delete_button = Button(text="Delete Website", width=12, font=('Times',12), command=delete_website)
delete_button.grid(column=2, row=1)


window.mainloop()
