# CLI-based Todo Application

A simple command-line interface todo application that allows users to manage their tasks efficiently.

## Features

- Add new todos
- View all todos
- Mark todos as completed
- Delete todos
- Exit application safely
- Data persistence using JSON file

## Requirements

- Python 3.10 or higher

## How to Run

1. Make sure you have Python 3.10+ installed on your system
2. Download or clone this repository
3. Navigate to the project directory in your terminal
4. Run the application using the following command:

```bash
python main.py
```

## Usage

Once the application starts, you'll see a menu with the following options:

1. Add a new todo (add)
2. View all todos (view)
3. Mark todo as completed (complete)
4. Delete a todo (delete)
5. Exit (exit)

You can either enter the number of your choice or type the command in parentheses.

### Adding a Todo

Select option 1 or type "add", then enter the title for your new todo.

### Viewing Todos

Select option 2 or type "view" to see all your todos with their completion status and timestamp.

### Marking as Completed

Select option 3 or type "complete", then enter the ID of the todo you want to mark as completed.

### Deleting a Todo

Select option 4 or type "delete", then enter the ID of the todo you want to delete. You'll be asked for confirmation before the deletion occurs.

### Exiting

Select option 5 or type "exit" to save your todos and exit the application.

## Data Storage

Todos are stored in a `todos.json` file in the same directory as the application. This file is automatically created when you add your first todo and updated whenever you make changes.

## License

This project is open source and available under the MIT License.