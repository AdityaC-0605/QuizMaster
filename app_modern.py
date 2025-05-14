import tkinter as tk
from ttkbootstrap import Style, ttk
from tkinter import messagebox
import mysql.connector as mysql
import hashlib
from datetime import datetime
import yagmail
import random
import csv
import os

class ModernQuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("QuizMaster")
        self.root.geometry("800x600")
        
        # Apply a modern theme
        self.style = Style(theme="superhero")
        
        # Create a notebook for different screens
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Welcome screen
        self.welcome_frame = ttk.Frame(self.notebook, padding=20)
        self.notebook.add(self.welcome_frame, text="Welcome")
        self.setup_welcome_screen()
        
        # Login screen
        self.login_frame = ttk.Frame(self.notebook, padding=20)
        self.notebook.add(self.login_frame, text="Login")
        self.setup_login_screen()
        
        # Signup screen
        self.signup_frame = ttk.Frame(self.notebook, padding=20)
        self.notebook.add(self.signup_frame, text="Signup")
        self.setup_signup_screen()
        
        # Quiz screen (will be created when needed)
        self.quiz_frame = None
        
        # Database connection
        self.cursor = None
        self.mycon = None
        self.connect_to_database()
        
        # Quiz variables
        self.questions = []
        self.current_question_index = 0
        self.score = 0
        self.played = 0
        self.current_username = ""
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Welcome to QuizMaster")
        self.status_bar = ttk.Label(root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def connect_to_database(self):
        try:
            self.mycon = mysql.connect(host="localhost", user="root", password="greenskrulls", database="staladb")
            self.cursor = self.mycon.cursor()
            self.status_var.set("Connected to database")
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to connect to database: {e}")
            self.status_var.set("Database connection failed")
    
    def setup_welcome_screen(self):
        # Title
        title_label = ttk.Label(self.welcome_frame, text="Welcome to QuizMaster", font=("Helvetica", 24))
        title_label.pack(pady=20)
        
        # Logo or image placeholder
        logo_frame = ttk.Frame(self.welcome_frame, width=200, height=200)
        logo_frame.pack(pady=20)
        
        # Description
        description = """
        QuizMaster is an interactive quiz application that tests your knowledge
        across various topics. Login or create an account to start taking quizzes,
        track your progress, and challenge yourself!
        """
        desc_label = ttk.Label(self.welcome_frame, text=description, wraplength=500, justify="center")
        desc_label.pack(pady=20)
        
        # Navigation buttons
        button_frame = ttk.Frame(self.welcome_frame)
        button_frame.pack(pady=20)
        
        login_button = ttk.Button(button_frame, text="Login", command=lambda: self.notebook.select(1))
        login_button.pack(side=tk.LEFT, padx=10)
        
        signup_button = ttk.Button(button_frame, text="Sign Up", command=lambda: self.notebook.select(2))
        signup_button.pack(side=tk.LEFT, padx=10)
        
        exit_button = ttk.Button(button_frame, text="Exit", command=self.root.destroy)
        exit_button.pack(side=tk.LEFT, padx=10)
    
    def setup_login_screen(self):
        # Title
        title_label = ttk.Label(self.login_frame, text="Login to Your Account", font=("Helvetica", 18))
        title_label.pack(pady=20)
        
        # Login form
        form_frame = ttk.Frame(self.login_frame, padding=20)
        form_frame.pack()
        
        ttk.Label(form_frame, text="Username:").grid(row=0, column=0, sticky=tk.W, pady=10)
        self.login_username_entry = ttk.Entry(form_frame, width=30)
        self.login_username_entry.grid(row=0, column=1, pady=10, padx=10)
        
        ttk.Label(form_frame, text="Password:").grid(row=1, column=0, sticky=tk.W, pady=10)
        self.login_password_entry = ttk.Entry(form_frame, show="*", width=30)
        self.login_password_entry.grid(row=1, column=1, pady=10, padx=10)
        
        # Buttons
        button_frame = ttk.Frame(self.login_frame)
        button_frame.pack(pady=20)
        
        login_button = ttk.Button(button_frame, text="Login", command=self.login)
        login_button.pack(side=tk.LEFT, padx=10)
        
        back_button = ttk.Button(button_frame, text="Back", command=lambda: self.notebook.select(0))
        back_button.pack(side=tk.LEFT, padx=10)
    
    def setup_signup_screen(self):
        # Title
        title_label = ttk.Label(self.signup_frame, text="Create a New Account", font=("Helvetica", 18))
        title_label.pack(pady=20)
        
        # Signup form
        form_frame = ttk.Frame(self.signup_frame, padding=20)
        form_frame.pack()
        
        ttk.Label(form_frame, text="Username:").grid(row=0, column=0, sticky=tk.W, pady=10)
        self.signup_username_entry = ttk.Entry(form_frame, width=30)
        self.signup_username_entry.grid(row=0, column=1, pady=10, padx=10)
        
        ttk.Label(form_frame, text="Password:").grid(row=1, column=0, sticky=tk.W, pady=10)
        self.signup_password_entry = ttk.Entry(form_frame, show="*", width=30)
        self.signup_password_entry.grid(row=1, column=1, pady=10, padx=10)
        
        ttk.Label(form_frame, text="Email:").grid(row=2, column=0, sticky=tk.W, pady=10)
        self.signup_email_entry = ttk.Entry(form_frame, width=30)
        self.signup_email_entry.grid(row=2, column=1, pady=10, padx=10)
        
        # Buttons
        button_frame = ttk.Frame(self.signup_frame)
        button_frame.pack(pady=20)
        
        signup_button = ttk.Button(button_frame, text="Sign Up", command=self.signup)
        signup_button.pack(side=tk.LEFT, padx=10)
        
        back_button = ttk.Button(button_frame, text="Back", command=lambda: self.notebook.select(0))
        back_button.pack(side=tk.LEFT, padx=10)