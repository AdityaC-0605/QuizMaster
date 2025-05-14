import csv
import mysql.connector as mysql
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os

# Add at the beginning of the file, after imports
from configparser import ConfigParser
import hashlib

class QuestionManager:
    def __init__(self, root):
        self.root = root
        self.root.title("QuizMaster - Question Manager")
        
        # Load database configuration from config file
        self.config = self.load_config()
        self.connect_to_database()
        
        self.root.geometry("700x500")
        
        # Database connection
        self.mycon = None
        self.cursor = None
        self.connect_to_database()
        
        # Main frame
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        ttk.Label(self.main_frame, text="QuizMaster Question Manager", font=("Helvetica", 16)).pack(pady=10)
        
        # Tabs
        self.tab_control = ttk.Notebook(self.main_frame)
        
        # Add Question Tab
        self.add_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.add_tab, text="Add Question")
        self.setup_add_question_tab()
        
        # View Questions Tab
        self.view_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.view_tab, text="View Questions")
        self.setup_view_questions_tab()
        
        # Import/Export Tab
        self.import_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.import_tab, text="Import/Export")
        self.setup_import_export_tab()
        
        self.tab_control.pack(expand=1, fill="both")
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.status_bar = ttk.Label(self.main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def load_config(self):
        config = ConfigParser()
        try:
            config.read('config.ini')
            return config['DATABASE']
        except:
            # Create default config if not exists
            config['DATABASE'] = {
                'host': 'localhost',
                'user': 'root',
                'password': 'greenskrulls',
                'database': 'staladb'
            }
            with open('config.ini', 'w') as f:
                config.write(f)
            return config['DATABASE']
    
    def connect_to_database(self):
        try:
            self.mycon = mysql.connect(
                host=self.config.get('host'),
                user=self.config.get('user'),
                password=self.config.get('password'),
                database=self.config.get('database')
            )
            self.cursor = self.mycon.cursor()
            
            # Check if tables exist, create if not
            self.cursor.execute("SHOW TABLES LIKE 'questions'")
            table_exists = self.cursor.fetchone()
            
            if not table_exists:
                self.cursor.execute('''
                    CREATE TABLE questions (
                        question NVARCHAR(255),
                        opt1 NVARCHAR(255),
                        opt2 NVARCHAR(255),
                        opt3 NVARCHAR(255),
                        opt4 NVARCHAR(255),
                        answer NVARCHAR(255)
                    )
                ''')
                self.mycon.commit()
            
            self.cursor.execute("SHOW TABLES LIKE 'player'")
            table_exists = self.cursor.fetchone()
            
            if not table_exists:      
                self.cursor.execute('''
                    CREATE TABLE player (
                      usrname VARCHAR(255),
                      passwd VARCHAR(255),
                      email VARCHAR(255),
                      datee DATE,
                      score INT DEFAULT 0,
                      played INT DEFAULT 0
                    )
                ''')
                self.mycon.commit()
                
            # Add categories table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS categories (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(50) UNIQUE
                )
            """)
            
            # Modify questions table to include category
            self.cursor.execute("""
                ALTER TABLE questions 
                ADD COLUMN IF NOT EXISTS category_id INT,
                ADD FOREIGN KEY (category_id) REFERENCES categories(id)
            """)
            
            # Add default category
            self.cursor.execute("INSERT IGNORE INTO categories (name) VALUES ('General')")
            self.mycon.commit()
            
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to connect to database: {e}")
    
    def setup_add_question_tab(self):
        frame = ttk.Frame(self.add_tab, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Question entry
        ttk.Label(frame, text="Question:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.question_entry = ttk.Entry(frame, width=60)
        self.question_entry.grid(row=0, column=1, columnspan=3, sticky=tk.W+tk.E, pady=5)
        
        # Options
        ttk.Label(frame, text="Option A:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.opt1_entry = ttk.Entry(frame, width=40)
        self.opt1_entry.grid(row=1, column=1, sticky=tk.W+tk.E, pady=5)
        
        ttk.Label(frame, text="Option B:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.opt2_entry = ttk.Entry(frame, width=40)
        self.opt2_entry.grid(row=2, column=1, sticky=tk.W+tk.E, pady=5)
        
        ttk.Label(frame, text="Option C:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.opt3_entry = ttk.Entry(frame, width=40)
        self.opt3_entry.grid(row=3, column=1, sticky=tk.W+tk.E, pady=5)
        
        ttk.Label(frame, text="Option D:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.opt4_entry = ttk.Entry(frame, width=40)
        self.opt4_entry.grid(row=4, column=1, sticky=tk.W+tk.E, pady=5)
        
        # Correct answer
        ttk.Label(frame, text="Correct Answer:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.answer_var = tk.StringVar()
        self.answer_var.set("Option A")
        options = ["Option A", "Option B", "Option C", "Option D"]
        self.answer_dropdown = ttk.Combobox(frame, textvariable=self.answer_var, values=options, state="readonly")
        self.answer_dropdown.grid(row=5, column=1, sticky=tk.W, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=6, column=0, columnspan=4, pady=10)
        
        ttk.Button(button_frame, text="Add Question", command=self.add_question).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear Fields", command=self.clear_fields).pack(side=tk.LEFT, padx=5)
    
    def setup_view_questions_tab(self):
        frame = ttk.Frame(self.view_tab, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Search frame
        search_frame = ttk.Frame(frame)
        search_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=5)
        self.search_entry = ttk.Entry(search_frame, width=40)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="Search", command=self.search_questions).pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="Show All", command=self.load_questions).pack(side=tk.LEFT, padx=5)
        
        # Questions treeview
        self.tree_frame = ttk.Frame(frame)
        self.tree_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.tree_scroll = ttk.Scrollbar(self.tree_frame)
        self.tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.question_tree = ttk.Treeview(self.tree_frame, columns=("question", "opt1", "opt2", "opt3", "opt4", "answer"), 
                                         show="headings", yscrollcommand=self.tree_scroll.set)
        
        self.question_tree.heading("question", text="Question")
        self.question_tree.heading("opt1", text="Option A")
        self.question_tree.heading("opt2", text="Option B")
        self.question_tree.heading("opt3", text="Option C")
        self.question_tree.heading("opt4", text="Option D")
        self.question_tree.heading("answer", text="Answer")
        
        self.question_tree.column("question", width=200)
        self.question_tree.column("opt1", width=100)
        self.question_tree.column("opt2", width=100)
        self.question_tree.column("opt3", width=100)
        self.question_tree.column("opt4", width=100)
        self.question_tree.column("answer", width=100)
        
        self.question_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.tree_scroll.config(self.question_tree.yview)
        
        # Action buttons
        action_frame = ttk.Frame(frame)
        action_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(action_frame, text="Delete Selected", command=self.delete_question).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Edit Selected", command=self.edit_question).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Refresh", command=self.load_questions).pack(side=tk.LEFT, padx=5)
        
        # Load questions initially
        self.load_questions()
    
    def setup_import_export_tab(self):
        frame = ttk.Frame(self.import_tab, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Import section
        import_frame = ttk.LabelFrame(frame, text="Import Questions", padding="10")
        import_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(import_frame, text="Import questions from a CSV file").pack(anchor=tk.W, pady=5)
        ttk.Button(import_frame, text="Import from CSV", command=self.import_from_csv).pack(anchor=tk.W, pady=5)
        
        # Export section
        export_frame = ttk.LabelFrame(frame, text="Export Questions", padding="10")
        export_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(export_frame, text="Export all questions to a CSV file").pack(anchor=tk.W, pady=5)
        ttk.Button(export_frame, text="Export to CSV", command=self.export_to_csv).pack(anchor=tk.W, pady=5)
        
        # Add Statistics section
        stats_frame = ttk.LabelFrame(frame, text="Statistics", padding="10")
        stats_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(stats_frame, text="Generate Report", command=self.generate_report).pack(anchor=tk.W, pady=5)
    
    def generate_report(self):
        try:
            self.cursor.execute("""
                SELECT 
                    COUNT(*) as total_questions,
                    (SELECT COUNT(*) FROM player) as total_players,
                    (SELECT AVG(score) FROM player) as avg_score
                FROM questions
            """)
            stats = self.cursor.fetchone()
            
            report = f"""Quiz Statistics Report
            
Total Questions: {stats[0]}
Total Players: {stats[1]}
Average Score: {stats[2]:.2f}
            """
            
            file_path = filedialog.asksaveasfilename(
                title="Save Report",
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            
            if file_path:
                with open(file_path, 'w') as f:
                    f.write(report)
                messagebox.showinfo("Success", "Report generated successfully")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate report: {e}")
    
    def validate_question(self, question, options):
        # Add after the add_question method
        if len(question) < 10:
            return False, "Question must be at least 10 characters long"
        
        # Check for duplicate options
        if len(set(options)) != len(options):
            return False, "Options must be unique"
        
        # Check if question already exists
        self.cursor.execute("SELECT COUNT(*) FROM questions WHERE question = %s", (question,))
        if self.cursor.fetchone()[0] > 0:
            return False, "This question already exists"
            
        return True, ""
    
    def add_question(self):
        # Modify the existing add_question method
        question = self.question_entry.get().strip()
        options = [
            self.opt1_entry.get().strip(),
            self.opt2_entry.get().strip(),
            self.opt3_entry.get().strip(),
            self.opt4_entry.get().strip()
        ]
        
        # Validate inputs
        valid, message = self.validate_question(question, options)
        if not valid:
            messagebox.showerror("Validation Error", message)
            return
            
        opt1 = self.opt1_entry.get().strip()
        opt2 = self.opt2_entry.get().strip()
        opt3 = self.opt3_entry.get().strip()
        opt4 = self.opt4_entry.get().strip()
        
        # Map dropdown selection to actual answer value
        answer_map = {
            "Option A": opt1,
            "Option B": opt2,
            "Option C": opt3,
            "Option D": opt4
        }
        answer = answer_map[self.answer_var.get()]
        
        # Validate inputs
        if not all([question, opt1, opt2, opt3, opt4]):
            messagebox.showerror("Input Error", "All fields are required")
            return
        
        try:
            self.cursor.execute('INSERT INTO questions VALUES (%s, %s, %s, %s, %s, %s)',
                           (question, opt1, opt2, opt3, opt4, answer))
            self.mycon.commit()
            self.status_var.set(f"Question added successfully")
            self.clear_fields()
            messagebox.showinfo("Success", "Question added successfully")
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to add question: {e}")
    
    def clear_fields(self):
        self.question_entry.delete(0, tk.END)
        self.opt1_entry.delete(0, tk.END)
        self.opt2_entry.delete(0, tk.END)
        self.opt3_entry.delete(0, tk.END)
        self.opt4_entry.delete(0, tk.END)
        self.answer_var.set("Option A")
    
    def load_questions(self):
        # Clear existing items
        for item in self.question_tree.get_children():
            self.question_tree.delete(item)
        
        try:
            self.cursor.execute("SELECT * FROM questions")
            questions = self.cursor.fetchall()
            
            for question in questions:
                self.question_tree.insert("", tk.END, values=question)
            
            self.status_var.set(f"Loaded {len(questions)} questions")
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to load questions: {e}")
    
    def search_questions(self):
        search_term = self.search_entry.get().strip()
        if not search_term:
            self.load_questions()
            return
        
        # Clear existing items
        for item in self.question_tree.get_children():
            self.question_tree.delete(item)
        
        try:
            self.cursor.execute("SELECT * FROM questions WHERE question LIKE %s", (f"%{search_term}%",))
            questions = self.cursor.fetchall()
            
            for question in questions:
                self.question_tree.insert("", tk.END, values=question)
            
            self.status_var.set(f"Found {len(questions)} questions matching '{search_term}'")
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to search questions: {e}")
    
    def delete_question(self):
        selected_item = self.question_tree.selection()
        if not selected_item:
            messagebox.showinfo("Selection Required", "Please select a question to delete")
            return
        
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this question?")
        if not confirm:
            return
        
        try:
            values = self.question_tree.item(selected_item[0], 'values')
            question = values[0]
            
            self.cursor.execute("DELETE FROM questions WHERE question = %s", (question,))
            self.mycon.commit()
            
            self.load_questions()
            self.status_var.set("Question deleted successfully")
            messagebox.showinfo("Success", "Question deleted successfully")
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to delete question: {e}")
    
    def edit_question(self):
        selected_item = self.question_tree.selection()
        if not selected_item:
            messagebox.showinfo("Selection Required", "Please select a question to edit")
            return
        
        values = self.question_tree.item(selected_item[0], 'values')
        
        # Create edit window
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Edit Question")
        edit_window.geometry("600x400")
        
        frame = ttk.Frame(edit_window, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Original question to identify for update
        original_question = values[0]
        
        # Question entry
        ttk.Label(frame, text="Question:").grid(row=0, column=0, sticky=tk.W, pady=5)
        question_entry = ttk.Entry(frame, width=60)
        question_entry.insert(0, values[0])
        question_entry.grid(row=0, column=1, columnspan=3, sticky=tk.W+tk.E, pady=5)
        
        # Options
        ttk.Label(frame, text="Option A:").grid(row=1, column=0, sticky=tk.W, pady=5)
        opt1_entry = ttk.Entry(frame, width=40)
        opt1_entry.insert(0, values[1])
        opt1_entry.grid(row=1, column=1, sticky=tk.W+tk.E, pady=5)
        
        ttk.Label(frame, text="Option B:").grid(row=2, column=0, sticky=tk.W, pady=5)
        opt2_entry = ttk.Entry(frame, width=40)
        opt2_entry.insert(0, values[2])
        opt2_entry.grid(row=2, column=1, sticky=tk.W+tk.E, pady=5)
        
        ttk.Label(frame, text="Option C:").grid(row=3, column=0, sticky=tk.W, pady=5)
        opt3_entry = ttk.Entry(frame, width=40)
        opt3_entry.insert(0, values[3])
        opt3_entry.grid(row=3, column=1, sticky=tk.W+tk.E, pady=5)
        
        ttk.Label(frame, text="Option D:").grid(row=4, column=0, sticky=tk.W, pady=5)
        opt4_entry = ttk.Entry(frame, width=40)
        opt4_entry.insert(0, values[4])
        opt4_entry.grid(row=4, column=1, sticky=tk.W+tk.E, pady=5)
        
        # Correct answer
        ttk.Label(frame, text="Correct Answer:").grid(row=5, column=0, sticky=tk.W, pady=5)
        answer_var = tk.StringVar()
        
        # Determine which option is the correct answer
        correct_answer = values[5]
        if correct_answer == values[1]:
            answer_var.set("Option A")
        elif correct_answer == values[2]:
            answer_var.set("Option B")
        elif correct_answer == values[3]:
            answer_var.set("Option C")
        elif correct_answer == values[4]:
            answer_var.set("Option D")
        
        options = ["Option A", "Option B", "Option C", "Option D"]
        answer_dropdown = ttk.Combobox(frame, textvariable=answer_var, values=options, state="readonly")
        answer_dropdown.grid(row=5, column=1, sticky=tk.W, pady=5)
        
        # Save button
        def save_edit():
            new_question = question_entry.get().strip()
            new_opt1 = opt1_entry.get().strip()
            new_opt2 = opt2_entry.get().strip()
            new_opt3 = opt3_entry.get().strip()
            new_opt4 = opt4_entry.get().strip()
            
            # Map dropdown selection to actual answer value
            answer_map = {
                "Option A": new_opt1,
                "Option B": new_opt2,
                "Option C": new_opt3,
                "Option D": new_opt4
            }
            new_answer = answer_map[answer_var.get()]
            
            # Validate inputs
            if not all([new_question, new_opt1, new_opt2, new_opt3, new_opt4]):
                messagebox.showerror("Input Error", "All fields are required")
                return
            
            try:
                self.cursor.execute('''
                    UPDATE questions 
                    SET question = %s, opt1 = %s, opt2 = %s, opt3 = %s, opt4 = %s, answer = %s 
                    WHERE question = %s
                ''', (new_question, new_opt1, new_opt2, new_opt3, new_opt4, new_answer, original_question))
                self.mycon.commit()
                self.load_questions()
                self.status_var.set("Question updated successfully")
                messagebox.showinfo("Success", "Question updated successfully")
                edit_window.destroy()
            except Exception as e:
                messagebox.showerror("Database Error", f"Failed to update question: {e}")
        
        ttk.Button(frame, text="Save Changes", command=save_edit).grid(row=6, column=0, columnspan=2, pady=10)
    
    def import_from_csv(self):
        file_path = filedialog.askopenfilename(
            title="Select CSV file",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, newline='', encoding='utf-8') as csvfile:
                csvreader = csv.reader(csvfile)
                next(csvreader)  # Skip header
                
                count = 0
                for row in csvreader:
                    if len(row) != 6:
                        continue
                        
                    question, opt1, opt2, opt3, opt4, answer = row
                    self.cursor.execute('INSERT INTO questions VALUES (%s, %s, %s, %s, %s, %s)',
                                   (question, opt1, opt2, opt3, opt4, answer))
                    count += 1
                
                self.mycon.commit()
                self.load_questions()
                self.status_var.set(f"Imported {count} questions from CSV")
                messagebox.showinfo("Import Successful", f"Imported {count} questions from CSV")
        except Exception as e:
            messagebox.showerror("Import Error", f"Failed to import questions: {e}")
    
    def export_to_csv(self):
        file_path = filedialog.asksaveasfilename(
            title="Save CSV file",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            self.cursor.execute("SELECT * FROM questions")
            questions = self.cursor.fetchall()
            
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                csvwriter = csv.writer(csvfile)
                csvwriter.writerow(['question', 'opt1', 'opt2', 'opt3', 'opt4', 'answer'])
                csvwriter.writerows(questions)
            
            self.status_var.set(f"Exported {len(questions)} questions to CSV")
            messagebox.showinfo("Export Successful", f"Exported {len(questions)} questions to CSV")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export questions: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = QuestionManager(root)
    root.mainloop()
