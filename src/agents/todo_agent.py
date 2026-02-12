from typing import Dict, Any, List
from enum import Enum
import json
from ..mcp_server.server import MCPServer
from ..services.task_service import TaskService
from ..database.session import get_session

class Intent(Enum):
    ADD_TASK = "add_task"
    LIST_TASKS = "list_tasks"
    COMPLETE_TASK = "complete_task"
    DELETE_TASK = "delete_task"
    UPDATE_TASK = "update_task"
    UNKNOWN = "unknown"

class TodoAgent:
    def __init__(self):
        self.task_service = TaskService()
        self.mcp_server = MCPServer()

    def classify_intent(self, message: str) -> Intent:
        """Classify the user's intent based on their message."""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["add", "create", "new", "make"]):
            if any(word in message_lower for word in ["task", "todo", "item"]):
                return Intent.ADD_TASK
        
        if any(word in message_lower for word in ["list", "show", "see", "my", "all"]):
            if any(word in message_lower for word in ["task", "todo", "item", "list"]):
                return Intent.LIST_TASKS
        
        if any(word in message_lower for word in ["complete", "done", "finish", "mark"]):
            if any(word in message_lower for word in ["task", "todo", "item"]):
                return Intent.COMPLETE_TASK
        
        if any(word in message_lower for word in ["delete", "remove", "cancel"]):
            if any(word in message_lower for word in ["task", "todo", "item"]):
                return Intent.DELETE_TASK
                
        if any(word in message_lower for word in ["update", "change", "modify", "edit"]):
            if any(word in message_lower for word in ["task", "todo", "item"]):
                return Intent.UPDATE_TASK
        
        return Intent.UNKNOWN

    def process_message(self, user_id: str, message: str, conversation_id: str) -> Dict[str, Any]:
        """Process a user message and return a response with potential tool calls."""
        intent = self.classify_intent(message)
        
        if intent == Intent.ADD_TASK:
            return self._handle_add_task(user_id, message)
        elif intent == Intent.LIST_TASKS:
            return self._handle_list_tasks(user_id)
        elif intent == Intent.COMPLETE_TASK:
            return self._handle_complete_task(user_id, message)
        elif intent == Intent.DELETE_TASK:
            return self._handle_delete_task(user_id, message)
        elif intent == Intent.UPDATE_TASK:
            return self._handle_update_task(user_id, message)
        else:
            return self._handle_unknown(user_id, message)

    def _handle_add_task(self, user_id: str, message: str) -> Dict[str, Any]:
        """Handle adding a new task."""
        # Extract task content from message (simple approach)
        # In a real implementation, this would use more sophisticated NLP
        import re
        
        # Look for phrases like "add task to [content]" or "create task [content]"
        patterns = [
            r"add task to (.+)",
            r"create task (.+)",
            r"add (.+) as a task",
            r"remember to (.+)",
            r"need to (.+)"
        ]
        
        content = None
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                content = match.group(1).strip()
                break
        
        if not content:
            # If we can't extract content, use the whole message minus command words
            content = re.sub(r"(add|create|remember|need to|task to)\s+", "", message, flags=re.IGNORECASE).strip()
        
        if not content:
            content = "New task"
        
        # Create the tool call
        tool_call = {
            "tool_name": "add_task",
            "parameters": {
                "user_id": user_id,
                "content": content,
                "priority": "medium"
            }
        }
        
        # Execute the tool call
        try:
            result = self.task_service.add_task(
                user_id=user_id,
                content=content,
                priority="medium"
            )
            
            return {
                "response": f"I've added the task '{content}' to your list.",
                "tool_calls": [tool_call],
                "result": result
            }
        except Exception as e:
            return {
                "response": f"Sorry, I couldn't add that task: {str(e)}",
                "tool_calls": [tool_call],
                "result": {"error": str(e)}
            }

    def _handle_list_tasks(self, user_id: str) -> Dict[str, Any]:
        """Handle listing tasks."""
        tool_call = {
            "tool_name": "list_tasks",
            "parameters": {
                "user_id": user_id,
                "filter_type": "all",
                "sort_by": "created_at",
                "sort_order": "desc",
                "limit": 10
            }
        }
        
        try:
            tasks = self.task_service.list_tasks(
                user_id=user_id,
                filter_type="all",
                sort_by="created_at",
                sort_order="desc",
                limit=10
            )
            
            if not tasks:
                response = "You don't have any tasks yet."
            else:
                task_list = "\n".join([f"- {task.title}" for task in tasks[:5]])  # Show first 5
                if len(tasks) > 5:
                    task_list += f"\n... and {len(tasks) - 5} more tasks"
                
                response = f"Here are your tasks:\n{task_list}"
            
            return {
                "response": response,
                "tool_calls": [tool_call],
                "result": {"tasks": [task.dict() for task in tasks]}
            }
        except Exception as e:
            return {
                "response": f"Sorry, I couldn't retrieve your tasks: {str(e)}",
                "tool_calls": [tool_call],
                "result": {"error": str(e)}
            }

    def _handle_complete_task(self, user_id: str, message: str) -> Dict[str, Any]:
        """Handle completing a task."""
        # Simple implementation - look for task ID in message
        import re
        
        # Look for numbers in the message which might be task IDs
        numbers = re.findall(r'\d+', message)
        task_id = None
        if numbers:
            task_id = int(numbers[0])  # Take the first number as task ID
        
        if not task_id:
            return {
                "response": "Please specify which task to complete by its number.",
                "tool_calls": [],
                "result": {"error": "No task ID specified"}
            }
        
        tool_call = {
            "tool_name": "complete_task",
            "parameters": {
                "user_id": user_id,
                "task_id": task_id
            }
        }
        
        try:
            result = self.task_service.complete_task(
                user_id=user_id,
                task_id=task_id
            )
            
            return {
                "response": f"I've marked task #{task_id} as completed.",
                "tool_calls": [tool_call],
                "result": result
            }
        except Exception as e:
            return {
                "response": f"Sorry, I couldn't complete that task: {str(e)}",
                "tool_calls": [tool_call],
                "result": {"error": str(e)}
            }

    def _handle_delete_task(self, user_id: str, message: str) -> Dict[str, Any]:
        """Handle deleting a task."""
        import re
        
        # Look for numbers in the message which might be task IDs
        numbers = re.findall(r'\d+', message)
        task_id = None
        if numbers:
            task_id = int(numbers[0])  # Take the first number as task ID
        
        if not task_id:
            return {
                "response": "Please specify which task to delete by its number.",
                "tool_calls": [],
                "result": {"error": "No task ID specified"}
            }
        
        tool_call = {
            "tool_name": "delete_task",
            "parameters": {
                "user_id": user_id,
                "task_id": task_id
            }
        }
        
        try:
            result = self.task_service.delete_task(
                user_id=user_id,
                task_id=task_id
            )
            
            return {
                "response": f"I've deleted task #{task_id}.",
                "tool_calls": [tool_call],
                "result": result
            }
        except Exception as e:
            return {
                "response": f"Sorry, I couldn't delete that task: {str(e)}",
                "tool_calls": [tool_call],
                "result": {"error": str(e)}
            }

    def _handle_update_task(self, user_id: str, message: str) -> Dict[str, Any]:
        """Handle updating a task."""
        # This is a simplified implementation
        return {
            "response": "Task update functionality is not fully implemented in this demo.",
            "tool_calls": [],
            "result": {"error": "Not implemented"}
        }

    def _handle_unknown(self, user_id: str, message: str) -> Dict[str, Any]:
        """Handle unknown intents."""
        return {
            "response": "I'm your AI assistant for managing tasks. You can ask me to add, list, complete, or delete tasks. For example: 'Add a task to buy groceries' or 'Show my tasks'.",
            "tool_calls": [],
            "result": {"error": "Unknown intent"}
        }