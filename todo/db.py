import logging
import sys

from pynamodb.exceptions import TableError
from proto import ErrorCode, Status, NOT_FOUND, SERVER_ERROR, DONE
from utils import get_timestamp

from models import TodoDAO


ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.INFO)
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO, handlers=[ch])


def add_todo_from_proto(todo_proto):
    """
    Create and save a todo from a proto message.

    Args:
        todo_proto: 

    Returns:
        TodoDAO, ErrorCode
    """
    try:
        todo = TodoDAO.from_proto(todo_proto)
        todo.save()
        error_code = None
    except TableError:
        todo = TodoDAO()
        error_code = SERVER_ERROR
    return todo, error_code


def get_todo_by_keys(assignee, todo_id):
    try:
        todo = TodoDAO.get(assignee, todo_id)
        error_code = None
    except TodoDAO.DoesNotExist:
        todo = TodoDAO()
        error_code = NOT_FOUND
    except Exception:
        todo = TodoDAO()
        error_code = SERVER_ERROR
    return todo, error_code


def complete_todo(assignee, todo_id):
    todo, error_code = get_todo_by_keys(assignee, todo_id)
    if not error_code:
        todo.status = DONE
        todo.completed_on = get_timestamp()
        try:
            todo.save()
        except Exception:
            error_code = SERVER_ERROR
    return todo, error_code


def get_todos_in_status(assignee, status):
    try:
        todos = [td.to_proto() for td in TodoDAO.assingee_status_index.query(assignee, status__eq=status)]
        error_code = None
    except Exception as err:
        logging.error("error fetching todos from DB: %s", err)
        todos = []
        error_code = SERVER_ERROR
    return todos, error_code


def update_todo_status(assignee, todo_id, status):
    todo, error_code = get_todo_by_keys(assignee, todo_id)
    if not error_code:
        todo.status = status
        try:
            todo.save()
        except Exception:
            error_code = SERVER_ERROR
    return todo, error_code
