import logging
import sys

from proto import TodoResponse, TodoCollectionResponse, Status, ErrorCode, TodosServicer

import db


ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.INFO)
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO, handlers=[ch])


class TodosService(TodosServicer):
    def addTodo(self, request, context):
        """
        Add a todo

        Args:
            request (proto.todo_pb2.AddTodoRequest): 
            context: 

        Returns:
            
        """
        logging.info("Adding to do")
        todo, error_code = db.add_todo_from_proto(request.todo)
        if error_code:
            logging.error("Transaction failed with error code: %s", ErrorCode.Name(error_code))
        response = TodoResponse(todo=todo.to_proto(), error=error_code)
        return response

    def getTodo(self, request, context):
        todo, error_code = db.get_todo_by_keys(request.assignee, request.id)
        if error_code:
            logging.error("get failed with error code: %s", ErrorCode.Name(error_code))
        response = TodoResponse(todo=todo.to_proto(), error=error_code)
        return response

    def completeTodo(self, request, context):
        """
        
        Args:
            request: 
            context: 

        Returns:

        """
        todo, error_code = db.complete_todo(request.assignee, request.id)
        if error_code:
            logging.error("could not complete todo; error code: %s", ErrorCode.Name(error_code))
        response = TodoResponse(todo=todo.to_proto(), error=error_code)
        return response

    def getTodosByStatus(self, request, context):
        """
        
        Args:
            request: 
            context: 

        Returns:

        """
        logging.info("Getting all todos in status: %s", Status.Name(request.status))
        todos, error_code = db.get_todos_in_status(request.assignee, request.status)
        if error_code:
            logging.error("Transaction failed with error code: %s", ErrorCode.Name(error_code))
        response = TodoCollectionResponse(todos=todos, error=error_code)
        return response

    def updateStatus(self, request, context):
        """
        
        Args:
            request: 
            context: 

        Returns:

        """
        todo, error_code = db.update_todo_status(request.assignee, request.id, request.status)
        if error_code:
            logging.error("could not update status; error code: %s", ErrorCode.Name(error_code))
        response = TodoResponse(todo=todo.to_proto(), error=error_code)
        return response

    def editTodo(self, request, context):
        """
        
        Args:
            request: 
            context: 

        Returns:

        """
        pass

