import tkinter as tk
from tkinter import scrolledtext
import json
from datetime import datetime
import os
import sys
from pathlib import Path

# File to store todos
TODO_FILE = Path.home() / "daily_todos.json"

def load_todos():
    """Load todos from file, check if they're from today"""
    if not TODO_FILE.exists():
        return []
    
    try:
        with open(TODO_FILE, 'r') as f:
            data = json.load(f)
            # Check if the date matches today
            if data.get('date') == datetime.now().strftime('%Y-%m-%d'):
                return data.get('todos', [])
            else:
                # Different day, delete old file
                TODO_FILE.unlink()
                return []
    except:
        return []

def save_todos(todos):
    """Save todos with today's date"""
    data = {
        'date': datetime.now().strftime('%Y-%m-%d'),
        'todos': todos
    }
    with open(TODO_FILE, 'w') as f:
        json.dump(data, f)

class TodoPrompt:
    def __init__(self, force_show=False):
        self.force_show = force_show
        self.root = tk.Tk()
        self.root.title("Daily Todo List")
        self.root.geometry("500x450")
        
        # Center the window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.root.winfo_screenheight() // 2) - (450 // 2)
        self.root.geometry(f"500x450+{x}+{y}")
        
        # Make window stay on top initially
        self.root.attributes('-topmost', True)
        
        # Load existing todos
        self.existing_todos = load_todos()
        
        # Determine the title based on mode
        if self.existing_todos and force_show:
            title_text = "📝 Your Todo List for Today"
        elif self.existing_todos:
            title_text = "📝 Edit Your Todo List"
        else:
            title_text = "📝 What's on your plate today?"
        
        # Title label
        title = tk.Label(
            self.root, 
            text=title_text,
            font=("Arial", 16, "bold"),
            pady=10
        )
        title.pack()
        
        # Date label
        date_label = tk.Label(
            self.root,
            text=datetime.now().strftime('%A, %B %d, %Y'),
            font=("Arial", 10),
            fg="gray"
        )
        date_label.pack()
        
        # Instructions
        instructions = tk.Label(
            self.root,
            text="Add your tasks for today (one per line):",
            font=("Arial", 10)
        )
        instructions.pack(pady=5)
        
        # Text area for todos
        self.text_area = scrolledtext.ScrolledText(
            self.root,
            width=55,
            height=15,
            font=("Arial", 11),
            wrap=tk.WORD,
            padx=10,
            pady=10
        )
        self.text_area.pack(pady=10, padx=20)
        
        # Pre-fill with existing todos if any
        if self.existing_todos:
            self.text_area.insert("1.0", "\n".join(self.existing_todos))
        
        self.text_area.focus()
        
        # Button frame
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)
        
        # Save button
        save_btn = tk.Button(
            btn_frame,
            text="Save & Close",
            command=self.save_and_close,
            font=("Arial", 11, "bold"),
            bg="#4CAF50",
            fg="white",
            padx=20,
            pady=5,
            cursor="hand2"
        )
        save_btn.pack(side=tk.LEFT, padx=5)
        
        # Cancel button
        cancel_btn = tk.Button(
            btn_frame,
            text="Cancel",
            command=self.root.destroy,
            font=("Arial", 11),
            padx=20,
            pady=5,
            cursor="hand2"
        )
        cancel_btn.pack(side=tk.LEFT, padx=5)
        
        # Clear button (only show if there are existing todos)
        if self.existing_todos:
            clear_btn = tk.Button(
                btn_frame,
                text="Clear All",
                command=self.clear_all,
                font=("Arial", 11),
                fg="red",
                padx=20,
                pady=5,
                cursor="hand2"
            )
            clear_btn.pack(side=tk.LEFT, padx=5)
        
        # Bind keyboard shortcuts
        self.root.bind('<Control-Return>', lambda e: self.save_and_close())
        self.root.bind('<Escape>', lambda e: self.root.destroy())
        
    def save_and_close(self):
        """Save the todos and close the window"""
        content = self.text_area.get("1.0", tk.END).strip()
        if content:
            # Split by lines and filter out empty lines
            todos = [line.strip() for line in content.split('\n') if line.strip()]
            save_todos(todos)
        else:
            # If empty, delete the file
            if TODO_FILE.exists():
                TODO_FILE.unlink()
        self.root.destroy()
    
    def clear_all(self):
        """Clear all todos"""
        self.text_area.delete("1.0", tk.END)
        if TODO_FILE.exists():
            TODO_FILE.unlink()
        self.root.destroy()
    
    def run(self):
        """Run the GUI"""
        self.root.mainloop()

def main():
    # Check if script is run with --view flag
    force_show = '--view' in sys.argv or '-v' in sys.argv
    
    # Load existing todos
    todos = load_todos()
    
    # Show prompt if:
    # 1. Force view flag is set (user wants to view/edit)
    # 2. OR todo list is empty (startup/wake behavior)
    if force_show or not todos:
        app = TodoPrompt(force_show=force_show)
        app.run()
    # If todos exist and not forced, do nothing (don't show the prompt)

if __name__ == "__main__":
    main()