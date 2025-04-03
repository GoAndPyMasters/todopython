import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import date
from tkcalendar import DateEntry

DATA_FILE = "tasks.json"

class TaskManager:
    def __init__(self):
        self.tasks = []
        self.load_tasks()

    def load_tasks(self):
        """Load tasks from a JSON file."""
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                self.tasks = json.load(f)
        else:
            self.tasks = []

    def save_tasks(self):
        """Save tasks to a JSON file."""
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(self.tasks, f, indent=4)

    def add_task(self, title, status, date_str):
        """Add a new task to the list."""
        new_task = {
            "id": len(self.tasks) + 1,
            "title": title,
            "status": status,
            "date": date_str
        }
        self.tasks.append(new_task)
        self.save_tasks()

    def update_task_status(self, task_id, new_status):
        """Update the status of a given task."""
        for task in self.tasks:
            if task["id"] == task_id:
                task["status"] = new_status
                break
        self.save_tasks()

    def delete_task(self, task_id):
        """Delete a task from the list."""
        self.tasks = [task for task in self.tasks if task["id"] != task_id]
        self.save_tasks()

    def get_tasks_by_status(self, status):
        """Return a list of tasks filtered by status."""
        return [task for task in self.tasks if task["status"] == status]

class KanbanApp:
    def __init__(self, root, manager):
        self.root = root
        self.manager = manager

        # Updated Dark Theme Colors
        self.bg_color = "#2C3E50"       # Dark background
        self.primary_color = "#E74C3C"  # Vibrant red for headers
        self.accent_color = "#3498DB"   # Blue accent for buttons
        self.card_bg = "#34495E"        # Darker card background
        self.text_color = "#ECF0F1"     # Light text

        self.root.title("Kanban-Style To-Do List with Calendar")
        self.root.geometry("1080x600")
        self.root.resizable(False, False)
        self.root.configure(background=self.bg_color)

        # Configure ttk style for dark theme
        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure("TFrame", background=self.bg_color)
        style.configure("Header.TLabel", font=("Helvetica", 20, "bold"), background=self.bg_color, foreground=self.primary_color)
        style.configure("SubHeader.TLabel", font=("Helvetica", 16, "bold"), background=self.bg_color, foreground=self.text_color)
        style.configure("Card.TFrame", background=self.card_bg, relief="raised", borderwidth=1)
        style.configure("Card.TLabel", background=self.card_bg, foreground=self.text_color)
        style.configure("Accent.TButton", font=("Helvetica", 12, "bold"), foreground="white", background=self.accent_color)
        style.map("Accent.TButton", background=[('active', self.accent_color)])
        style.configure("Delete.TButton", font=("Helvetica", 10, "bold"), foreground="white", background="#c0392b")
        style.map("Delete.TButton", background=[('active', "#e74c3c")])

        # Main frame
        main_frame = ttk.Frame(self.root, padding=10, style="TFrame")
        main_frame.pack(expand=True, fill=tk.BOTH)

        # Header
        header_label = ttk.Label(main_frame, text="Kanban Board - To-Do List", style="Header.TLabel")
        header_label.pack(anchor="center", pady=(0, 20))

        # Button to add new task
        add_task_button = ttk.Button(main_frame, text="Add New Task", command=self.add_task_dialog, style="Accent.TButton")
        add_task_button.pack(anchor="center", pady=(0, 20))

        # Frame for Kanban columns
        columns_frame = ttk.Frame(main_frame, style="TFrame")
        columns_frame.pack(expand=True, fill=tk.BOTH)
        columns_frame.columnconfigure(0, weight=1)
        columns_frame.columnconfigure(1, weight=1)
        columns_frame.columnconfigure(2, weight=1)

        # Create columns: To do, Doing, Done
        self.todo_frame = self.create_status_column(columns_frame, "To do", 0)
        self.doing_frame = self.create_status_column(columns_frame, "Doing", 1)
        self.done_frame = self.create_status_column(columns_frame, "Done", 2)

        # Populate the board with existing tasks
        self.refresh_board()

    def create_status_column(self, parent, status_name, col_index):
        """Create a column for tasks with a given status."""
        frame = ttk.Frame(parent, padding=10, style="TFrame")
        frame.grid(row=0, column=col_index, sticky="nsew")
        status_label = ttk.Label(frame, text=status_name, style="SubHeader.TLabel")
        status_label.pack(anchor="center", pady=5)
        cards_container = ttk.Frame(frame, style="TFrame")
        cards_container.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)
        return cards_container

    def refresh_board(self):
        """Clear and rebuild the task cards in each column."""
        for widget in self.todo_frame.winfo_children():
            widget.destroy()
        for widget in self.doing_frame.winfo_children():
            widget.destroy()
        for widget in self.done_frame.winfo_children():
            widget.destroy()
        self.create_cards_for_status("To do", self.todo_frame)
        self.create_cards_for_status("Doing", self.doing_frame)
        self.create_cards_for_status("Done", self.done_frame)

    def create_cards_for_status(self, status, parent_frame):
        """Create a card for each task in a given status."""
        tasks = self.manager.get_tasks_by_status(status)
        for task in tasks:
            card_frame = ttk.Frame(parent_frame, style="Card.TFrame", padding=10)
            card_frame.pack(fill=tk.X, pady=5)

            title_label = ttk.Label(card_frame, text=task["title"], style="Card.TLabel", font=("Helvetica", 12, "bold"))
            title_label.pack(anchor="w")
            date_label = ttk.Label(card_frame, text=f"Date: {task['date']}", style="Card.TLabel", font=("Helvetica", 10))
            date_label.pack(anchor="w", pady=(0,5))

            # Frame for buttons (move and delete)
            button_frame = ttk.Frame(card_frame, style="TFrame")
            button_frame.pack(anchor="e", pady=(5, 0))

            # Move buttons
            if status != "To do":
                btn_todo = ttk.Button(button_frame, text="To do", command=lambda tid=task["id"]: self.move_task(tid, "To do"))
                btn_todo.pack(side=tk.LEFT, padx=2)
            if status != "Doing":
                btn_doing = ttk.Button(button_frame, text="Doing", command=lambda tid=task["id"]: self.move_task(tid, "Doing"))
                btn_doing.pack(side=tk.LEFT, padx=2)
            if status != "Done":
                btn_done = ttk.Button(button_frame, text="Done", command=lambda tid=task["id"]: self.move_task(tid, "Done"))
                btn_done.pack(side=tk.LEFT, padx=2)

            # Delete button
            btn_delete = ttk.Button(button_frame, text="Delete", command=lambda tid=task["id"]: self.delete_task(tid), style="Delete.TButton")
            btn_delete.pack(side=tk.LEFT, padx=2)

    def add_task_dialog(self):
        """Open a dialog to add a new task with a calendar for date selection."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add New Task")
        dialog.geometry("350x250")
        dialog.resizable(False, False)
        dialog.configure(background=self.bg_color)

        ttk.Label(dialog, text="Title:", background=self.bg_color, font=("Helvetica", 12), foreground=self.text_color).pack(pady=(10, 0))
        title_entry = ttk.Entry(dialog, width=30)
        title_entry.pack(pady=5)

        ttk.Label(dialog, text="Select Date:", background=self.bg_color, font=("Helvetica", 12), foreground=self.text_color).pack(pady=(10, 0))
        # Calendar DateEntry widget
        date_entry = DateEntry(dialog, width=27, background='darkblue', foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        date_entry.pack(pady=5)

        def confirm():
            title = title_entry.get().strip()
            selected_date = date_entry.get_date()
            dt = selected_date.strftime("%Y-%m-%d")
            if not title:
                messagebox.showwarning("Warning", "Title cannot be empty.")
                return
            self.manager.add_task(title, "To do", dt)
            self.refresh_board()
            dialog.destroy()

        ttk.Button(dialog, text="Add Task", command=confirm, style="Accent.TButton").pack(pady=15)

    def move_task(self, task_id, new_status):
        """Move a task to a new status and refresh the board."""
        self.manager.update_task_status(task_id, new_status)
        self.refresh_board()

    def delete_task(self, task_id):
        """Delete a task and refresh the board."""
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this task?"):
            self.manager.delete_task(task_id)
            self.refresh_board()

def main():
    manager = TaskManager()
    root = tk.Tk()
    app = KanbanApp(root, manager)
    root.mainloop()

if __name__ == "__main__":
    main()
