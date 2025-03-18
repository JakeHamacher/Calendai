import calendar
import datetime
import json
import os
import tkinter as tk
from tkinter import messagebox, simpledialog
from tkinter import ttk
from typing import Dict, List, TypedDict

class TodoItem(TypedDict):
    task: str
    completed: bool

class CalendarAppState(TypedDict):
    todos: Dict[str, List[TodoItem]]

class CalendarApp:
    def __init__(self, root: tk.Tk):
        self.root: tk.Tk = root
        self.root.title("Calendar App")
        self.root.geometry("800x600")

        # Dark Mode Colors
        self.bg_color = "#2E2E2E"
        self.fg_color = "#FFFFFF"
        self.button_color = "#4E4E4E"
        self.button_fg_color = "#FFFFFF"
        self.highlight_color = "#6E6E6E"
        self.task_highlight_color = "#A9A9A9"  # New color for days with tasks

        self.root.configure(bg=self.bg_color)

        self.style = ttk.Style()
        self.style.theme_use('clam')  # Use a theme that supports background colors

        self.style.configure("TFrame", background=self.bg_color)
        self.style.configure("TLabel", background=self.bg_color, foreground=self.fg_color)
        self.style.configure("TButton", background=self.button_color, foreground=self.button_fg_color,
                             highlightbackground=self.highlight_color, highlightcolor=self.highlight_color)
        self.style.configure("TEntry", fieldbackground=self.bg_color, foreground=self.fg_color,
                             insertcolor=self.fg_color)  # For Entry widgets

        self.state_file: str = 'calendar_state.json'
        self.todos: Dict[str, List[TodoItem]] = {}
        self.load_state()
        self.create_widgets()

    def save_state(self) -> None:
        try:
            with open(self.state_file, 'w') as f:
                json.dump(self.todos, f)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save state: {e}")

    def load_state(self) -> None:
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, 'r') as f:
                    self.todos = json.load(f)
            else:
                self.todos = {}
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load state: {e}")
            self.todos = {}

    def add_todo_dialog(self) -> None:
        AddTodoDialog(self)

    def add_todo(self, date: str, todo: str) -> None:
        if date not in self.todos:
            self.todos[date] = []
        self.todos[date].append({"task": todo, "completed": False})
        self.save_state()
        self.update_calendar()
        self.update_todo_list()

    def complete_todo_dialog(self) -> None:
        selected_index = self.todo_listbox.curselection()
        if selected_index:
            todo_text = self.todo_listbox.get(selected_index[0])
            date_str = todo_text.split(" - ")[0]
            index = int(todo_text.split(" - ")[1].split('.')[0]) - 1
            self.complete_todo(date_str, index)
        else:
            CompleteTodoDialog(self)

    def complete_todo(self, date: str, index: int) -> None:
        if date in self.todos and 0 <= index < len(self.todos[date]):
            self.todos[date][index]["completed"] = True
            self.todos[date] = [todo for todo in self.todos[date] if not todo["completed"]]
            if not self.todos[date]:
                del self.todos[date]
            self.save_state()
            self.update_calendar()
            self.update_todo_list()
        else:
            messagebox.showerror("Error", "Invalid date or index.")

    def create_widgets(self) -> None:
        self.main_frame: ttk.Frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.calendar_frame: ttk.Frame = ttk.Frame(self.main_frame, padding="10")
        self.calendar_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.todo_frame: ttk.Frame = ttk.Frame(self.main_frame, padding="10")
        self.todo_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.controls_frame: ttk.Frame = ttk.Frame(self.todo_frame, padding="10")
        self.controls_frame.pack(fill=tk.X)

        ttk.Button(self.controls_frame, text="Add Todo", command=self.add_todo_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.controls_frame, text="Complete Todo", command=self.complete_todo_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.controls_frame, text="Exit", command=self.root.quit).pack(side=tk.RIGHT, padx=5)

        self.todo_listbox: tk.Listbox = tk.Listbox(self.todo_frame, bg=self.bg_color, fg=self.fg_color)
        self.todo_listbox.pack(fill=tk.BOTH, expand=True, pady=10)

        self.current_date: datetime.date = datetime.date.today()

        # Navigation Frame
        self.navigation_frame = ttk.Frame(self.calendar_frame)
        self.navigation_frame.grid(row=0, column=0, columnspan=7, sticky="ew")

        ttk.Button(self.navigation_frame, text="<", command=self.prev_month).pack(side=tk.LEFT)
        self.month_label = ttk.Label(self.navigation_frame, text="", font=("Arial", 16))
        self.month_label.pack(side=tk.LEFT, expand=True)
        ttk.Button(self.navigation_frame, text=">", command=self.next_month).pack(side=tk.LEFT)

        self.update_calendar()
        self.update_todo_list()

    def prev_month(self) -> None:
        self.current_date = datetime.date(self.current_date.year, self.current_date.month, 1) - datetime.timedelta(days=1)
        self.update_calendar()

    def next_month(self) -> None:
        if self.current_date.month == 12:
            self.current_date = datetime.date(self.current_date.year + 1, 1, 1)
        else:
            self.current_date = datetime.date(self.current_date.year, self.current_date.month + 1, 1)
        self.update_calendar()

    def update_calendar(self) -> None:
        for widget in self.calendar_frame.winfo_children():
            if widget != self.navigation_frame:
                widget.destroy()

        year: int = self.current_date.year
        month: int = self.current_date.month

        cal: list[list[int]] = calendar.monthcalendar(year, month)
        header: str = calendar.month_name[month] + " " + str(year)
        self.month_label.config(text=header)

        days: List[str] = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for idx, day in enumerate(days):
            ttk.Label(self.calendar_frame, text=day).grid(row=1, column=idx)

        for row_idx, week in enumerate(cal, start=2):
            for col_idx, day in enumerate(week):
                if day != 0:
                    date_str: str = f"{year}-{month:02d}-{day:02d}"
                    btn_text: str = str(day)
                    btn: ttk.Button = ttk.Button(
                        self.calendar_frame,
                        text=btn_text,
                        command=lambda d=date_str: self.view_daily(d)
                    )
                    if date_str in self.todos:
                        btn.configure(style="TaskDay.TButton")  # Apply special style
                    btn.grid(row=row_idx, column=col_idx)

        # Define a style for days with tasks
        self.style.configure("TaskDay.TButton", background=self.task_highlight_color, foreground=self.button_fg_color)

    def update_todo_list(self) -> None:
        self.todo_listbox.delete(0, tk.END)
        for date, todos in self.todos.items():
            for idx, todo in enumerate(todos):
                status: str = "Done" if todo["completed"] else "Pending"
                self.todo_listbox.insert(tk.END, f"{date} - {idx + 1}. {todo['task']} [{status}]")

    def view_daily(self, date: str) -> None:
        result: str = f"{date}:\n"
        if date in self.todos:
            for idx, todo in enumerate(self.todos[date]):
                status: str = "Done" if todo["completed"] else "Pending"
                result += f"  {idx + 1}. {todo['task']} [{status}]\n"
        else:
            result += "  No tasks for today."
        messagebox.showinfo("Daily View", result)

class AddTodoDialog(simpledialog.Dialog):
    def __init__(self, parent):
        self.calendar_app = parent
        self.date = datetime.date.today()
        super().__init__(parent.root, title="Add Todo")

    def body(self, master):
        self.selected_date_label = tk.Label(master, text=f"Selected Date: {self.date.strftime('%Y-%m-%d')}")
        self.selected_date_label.pack()

        self.cal = calendar.Calendar()
        self.year = self.date.year
        self.month = self.date.month

        self.month_label = tk.Label(master, text=calendar.month_name[self.month] + " " + str(self.year))
        self.month_label.pack()

        self.calendar_frame = tk.Frame(master)
        self.calendar_frame.pack()

        self.draw_calendar()

        self.task_label = tk.Label(master, text="Task:")
        self.task_label.pack()
        self.task_entry = tk.Entry(master)
        self.task_entry.pack()

        return self.task_entry # initial focus

    def draw_calendar(self):
        # Clear previous calendar
        for widget in self.calendar_frame.winfo_children():
            widget.destroy()

        # Previous and Next month buttons
        prev_button = tk.Button(self.calendar_frame, text="<", command=self.prev_month)
        prev_button.grid(row=0, column=0)
        next_button = tk.Button(self.calendar_frame, text=">", command=self.next_month)
        next_button.grid(row=0, column=6)

        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for col, day in enumerate(days):
            day_label = tk.Label(self.calendar_frame, text=day)
            day_label.grid(row=1, column=col)

        # Calendar days
        weeks = self.cal.monthdayscalendar(self.year, self.month)
        for row, week in enumerate(weeks, start=2):
            for col, day in enumerate(week):
                if day != 0:
                    day_button = tk.Button(self.calendar_frame, text=str(day), width=3, command=lambda d=day: self.set_date(d))
                    day_button.grid(row=row, column=col)

    def prev_month(self):
        self.month -= 1
        if self.month < 1:
            self.month = 12
            self.year -= 1
        self.update_calendar()

    def next_month(self):
        self.month += 1
        if self.month > 12:
            self.month = 1
            self.year += 1
        self.update_calendar()

    def update_calendar(self):
        self.month_label.config(text=calendar.month_name[self.month] + " " + str(self.year))
        self.draw_calendar()

    def set_date(self, day):
        self.date = datetime.date(self.year, self.month, day)
        self.selected_date_label.config(text=f"Selected Date: {self.date.strftime('%Y-%m-%d')}")

    def apply(self):
        task = self.task_entry.get()
        if task:
            date_str = self.date.strftime("%Y-%m-%d")
            self.calendar_app.add_todo(date_str, task)

class CompleteTodoDialog(simpledialog.Dialog):
    def __init__(self, parent):
        self.calendar_app = parent
        self.date = datetime.date.today()
        super().__init__(parent.root, title="Complete Todo")

    def body(self, master):
        self.selected_date_label = tk.Label(master, text=f"Selected Date: {self.date.strftime('%Y-%m-%d')}")
        self.selected_date_label.pack()

        self.cal = calendar.Calendar()
        self.year = self.date.year
        self.month = self.date.month

        self.month_label = tk.Label(master, text=calendar.month_name[self.month] + " " + str(self.year))
        self.month_label.pack()

        self.calendar_frame = tk.Frame(master)
        self.calendar_frame.pack()

        self.draw_calendar()

        self.todo_list_label = tk.Label(master, text="Select a todo to complete:")
        self.todo_list_label.pack()
        self.todo_list = tk.Listbox(master)
        self.todo_list.pack()

        self.update_todo_list()

        return None

    def draw_calendar(self):
        # Clear previous calendar
        for widget in self.calendar_frame.winfo_children():
            widget.destroy()

        # Previous and Next month buttons
        prev_button = tk.Button(self.calendar_frame, text="<", command=self.prev_month)
        prev_button.grid(row=0, column=0)
        next_button = tk.Button(self.calendar_frame, text=">", command=self.next_month)
        next_button.grid(row=0, column=6)

        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for col, day in enumerate(days):
            day_label = tk.Label(self.calendar_frame, text=day)
            day_label.grid(row=1, column=col)

        # Calendar days
        weeks = self.cal.monthdayscalendar(self.year, self.month)
        for row, week in enumerate(weeks, start=2):
            for col, day in enumerate(week):
                if day != 0:
                    day_button = tk.Button(self.calendar_frame, text=str(day), width=3, command=lambda d=day: self.set_date(d))
                    day_button.grid(row=row, column=col)

    def prev_month(self):
        self.month -= 1
        if self.month < 1:
            self.month = 12
            self.year -= 1
        self.update_calendar()

    def next_month(self):
        self.month += 1
        if self.month > 12:
            self.month = 1
            self.year += 1
        self.update_calendar()

    def update_calendar(self):
        self.month_label.config(text=calendar.month_name[self.month] + " " + str(self.year))
        self.draw_calendar()
        self.update_todo_list()

    def set_date(self, day):
        self.date = datetime.date(self.year, self.month, day)
        self.selected_date_label.config(text=f"Selected Date: {self.date.strftime('%Y-%m-%d')}")
        self.update_todo_list()

    def update_todo_list(self):
        self.todo_list.delete(0, tk.END)
        date_str = self.date.strftime("%Y-%m-%d")
        if date_str in self.calendar_app.todos:
            for idx, todo in enumerate(self.calendar_app.todos[date_str]):
                status = "Done" if todo["completed"] else "Pending"
                self.todo_list.insert(tk.END, f"{idx + 1}. {todo['task']} [{status}]")

    def apply(self):
        date_str = self.date.strftime("%Y-%m-%d")
        selected_index = self.todo_list.curselection()
        if selected_index:
            index = selected_index[0]
            self.calendar_app.complete_todo(date_str, index)

if __name__ == "__main__":
    root: tk.Tk = tk.Tk()
    app: CalendarApp = CalendarApp(root)
    root.mainloop()
