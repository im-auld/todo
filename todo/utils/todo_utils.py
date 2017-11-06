from datetime import datetime
import hashlib


def get_timestamp(dt=None):
    if dt is None:
        dt = datetime.utcnow()
    return int(dt.timestamp())


def get_todo_id(todo):
    """
    Get the id from a todo, if one isn't present create one.

    Args:
        todo (models.TodoDAO): 

    Returns:
        int
    """
    if todo.id:
        return todo.id
    ha = hashlib.sha1()
    ha.update('assignee:{}'.format(todo.assignee).encode("UTF-8"))
    ha.update('createdOn:{}'.format(todo.created_on).encode("UTF-8"))
    return int(ha.hexdigest(), 16) % (2 ** 32)
