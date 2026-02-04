"""
CLI-based Todo Application

A simple command-line interface todo application that allows users to:
- Add new todos
- View all todos
- Mark todos as completed
- Delete todos
- Exit application safely

Data is persisted using a JSON file.
"""

import json
import os
from datetime import datetime

# Constants
TODO_FILE = "todos.json"

class TodoApp:
    """Main class for the Todo Application"""

    def __init__(self):
        """Initialize the TodoApp and load existing todos"""
        self.todos = self.load_todos()

    def load_todos(self):
        """
        Load todos from the JSON file.
        If the file doesn't exist, create an empty list.
        """
        if os.path.exists(TODO_FILE):
            try:
                with open(TODO_FILE, 'r') as file:
                    return json.load(file)
            except (json.JSONDecodeError, FileNotFoundError):
                print("Error reading todo file. Starting with empty list.")
                return []
        else:
            return []

    def save_todos(self):
        """Save todos to the JSON file"""
        with open(TODO_FILE, 'w') as file:
            json.dump(self.todos, file, indent=2)

    def add_todo(self, title):
        """Add a new todo with a unique ID and timestamp"""
        if not title.strip():
            print("Error: Todo title cannot be empty.")
            return

        # Find the next available ID
        next_id = 1
        if self.todos:
            next_id = max(todo['id'] for todo in self.todos) + 1

        new_todo = {
            'id': next_id,
            'title': title.strip(),
            'completed': False,
            'timestamp': datetime.now().isoformat()
        }

        self.todos.append(new_todo)
        self.save_todos()
        print(f"Added todo: {title}")

    def view_todos(self):
        """Display all todos with their completion status"""
        if not self.todos:
            print("No todos found.")
            return

        print("\nYour Todos:")
        print("-" * 50)
        for todo in self.todos:
            status = "X" if todo['completed'] else " "
            print(f"{todo['id']}. [{status}] {todo['title']}")
            if 'timestamp' in todo:
                # Format the timestamp for readability
                timestamp = datetime.fromisoformat(todo['timestamp'])
                formatted_time = timestamp.strftime("%Y-%m-%d %H:%M")
                print(f"    Added: {formatted_time}")
        print("-" * 50)

    def mark_completed(self, todo_id):
        """Mark a todo as completed"""
        for todo in self.todos:
            if todo['id'] == todo_id:
                if todo['completed']:
                    print(f"Todo {todo_id} is already marked as completed.")
                else:
                    todo['completed'] = True
                    self.save_todos()
                    print(f"Marked todo {todo_id} as completed: {todo['title']}")
                return
        print(f"Error: Todo with ID {todo_id} not found.")

    def delete_todo(self, todo_id):
        """Delete a todo by ID"""
        for i, todo in enumerate(self.todos):
            if todo['id'] == todo_id:
                title = todo['title']
                confirm = input(f"Are you sure you want to delete '{title}'? (y/N): ")
                if confirm.lower() in ['y', 'yes']:
                    del self.todos[i]
                    self.save_todos()
                    print(f"Deleted todo {todo_id}: {title}")
                else:
                    print("Deletion cancelled.")
                return
        print(f"Error: Todo with ID {todo_id} not found.")

    def run(self):
        """Main application loop"""
        print("Welcome to the CLI-based Todo Application!")
        print("Type 'help' for available commands.")

        while True:
            print("\nOptions:")
            print("1. Add a new todo (add)")
            print("2. View all todos (view)")
            print("3. Mark todo as completed (complete)")
            print("4. Delete a todo (delete)")
            print("5. Exit (exit)")

            choice = input("\nEnter your choice: ").strip().lower()

            if choice in ['1', 'add']:
                title = input("Enter todo title: ")
                self.add_todo(title)

            elif choice in ['2', 'view']:
                self.view_todos()

            elif choice in ['3', 'complete']:
                try:
                    todo_id = int(input("Enter todo ID to mark as completed: "))
                    self.mark_completed(todo_id)
                except ValueError:
                    print("Error: Please enter a valid todo ID (number).")

            elif choice in ['4', 'delete']:
                try:
                    todo_id = int(input("Enter todo ID to delete: "))
                    self.delete_todo(todo_id)
                except ValueError:
                    print("Error: Please enter a valid todo ID (number).")

            elif choice in ['5', 'exit', 'quit']:
                print("Saving and exiting. Goodbye!")
                break

            elif choice in ['help', 'h']:
                print("\nAvailable commands:")
                print("- add: Add a new todo")
                print("- view: View all todos")
                print("- complete: Mark a todo as completed")
                print("- delete: Delete a todo")
                print("- exit: Exit the application")

            else:
                print("Invalid choice. Please enter a valid option.")


def main():
    """Main function to run the application"""
    app = TodoApp()
    app.run()


if __name__ == "__main__":
    main()