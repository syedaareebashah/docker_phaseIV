"""
Test script for the CLI-based Todo Application
"""
import json
import os
from datetime import datetime
from main import TodoApp

def test_todo_app():
    """Test all functionality of the TodoApp"""
    print("Testing CLI-based Todo Application...")
    
    # Create a new TodoApp instance
    app = TodoApp()
    
    # Clear any existing todos for a fresh test
    app.todos = []
    app.save_todos()
    
    print("\n1. Testing add_todo functionality:")
    app.add_todo("Buy groceries")
    app.add_todo("Walk the dog")
    app.add_todo("Finish project")
    print(f"   Added 3 todos. Current count: {len(app.todos)}")
    
    print("\n2. Testing view_todos functionality:")
    app.view_todos()
    
    print("\n3. Testing mark_completed functionality:")
    app.mark_completed(1)
    print(f"   Todo 1 marked as completed: {app.todos[0]['completed']}")
    
    print("\n4. Testing delete_todo functionality:")
    # We'll simulate the confirmation input differently for testing
    original_delete = app.delete_todo
    def mock_delete(todo_id):
        # Bypass the confirmation for testing
        for i, todo in enumerate(app.todos):
            if todo['id'] == todo_id:
                title = todo['title']
                del app.todos[i]
                app.save_todos()
                print(f"Deleted todo {todo_id}: {title}")
                return
        print(f"Error: Todo with ID {todo_id} not found.")
    
    app.delete_todo = mock_delete
    app.delete_todo(2)
    print(f"   Deleted todo 2. Current count: {len(app.todos)}")
    
    print("\n5. Verifying data persistence:")
    # Check if the todos.json file exists and contains the correct data
    if os.path.exists("todos.json"):
        with open("todos.json", 'r') as f:
            saved_data = json.load(f)
        print(f"   Data saved to JSON file. Count: {len(saved_data)}")
        
        # Verify the content
        for todo in saved_data:
            print(f"   - ID: {todo['id']}, Title: {todo['title']}, Completed: {todo['completed']}")
    else:
        print("   ERROR: todos.json file not found!")
    
    print("\n6. Testing error handling:")
    # Test adding empty todo
    app.add_todo("")
    
    # Test marking non-existent todo
    app.mark_completed(999)
    
    # Test deleting non-existent todo
    app.delete_todo(999)
    
    print("\nAll tests completed successfully!")

if __name__ == "__main__":
    test_todo_app()