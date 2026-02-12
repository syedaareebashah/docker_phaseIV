from typing import Dict, Any, Callable
from mcp.shared.exceptions import McpError
import asyncio
from ..services.task_service import TaskService

class MCPServer:
    def __init__(self):
        self.tools = {}
        self.task_service = TaskService()
        self._register_default_tools()

    def _register_default_tools(self):
        """Register default tools for task management."""
        self.register_tool("add_task", self._add_task)
        self.register_tool("list_tasks", self._list_tasks)
        self.register_tool("complete_task", self._complete_task)
        self.register_tool("delete_task", self._delete_task)
        self.register_tool("update_task", self._update_task)

    def register_tool(self, name: str, handler: Callable):
        """Register a new tool with the server."""
        self.tools[name] = handler

    def get_tool(self, name: str):
        """Get a tool by name."""
        return self.tools.get(name)

    def run(self):
        """Run the MCP server."""
        print("MCP Server started...")
        # In a real implementation, this would start the actual MCP server
        # For this demo, we'll just keep it running
        try:
            while True:
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            print("MCP Server shutting down...")

    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool with the given parameters."""
        if tool_name not in self.tools:
            raise McpError(f"Tool '{tool_name}' not found")
        
        handler = self.tools[tool_name]
        try:
            result = handler(**parameters)
            return {
                "success": True,
                "result": result
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def _add_task(self, user_id: str, content: str, priority: str = "medium", due_date: str = None) -> Dict[str, Any]:
        """Add a new task."""
        return self.task_service.add_task(
            user_id=user_id,
            content=content,
            priority=priority,
            due_date=due_date
        )

    def _list_tasks(self, user_id: str, filter_type: str = "all", sort_by: str = "created_at", 
                   sort_order: str = "desc", limit: int = 10) -> Dict[str, Any]:
        """List tasks for a user."""
        return self.task_service.list_tasks(
            user_id=user_id,
            filter_type=filter_type,
            sort_by=sort_by,
            sort_order=sort_order,
            limit=limit
        )

    def _complete_task(self, user_id: str, task_id: int) -> Dict[str, Any]:
        """Complete a task."""
        return self.task_service.complete_task(
            user_id=user_id,
            task_id=task_id
        )

    def _delete_task(self, user_id: str, task_id: int) -> Dict[str, Any]:
        """Delete a task."""
        return self.task_service.delete_task(
            user_id=user_id,
            task_id=task_id
        )

    def _update_task(self, user_id: str, task_id: int, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update a task."""
        return self.task_service.update_task(
            user_id=user_id,
            task_id=task_id,
            updates=updates
        )

# Global instance for use in other modules
mcp_server = MCPServer()