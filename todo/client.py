from argparse import ArgumentParser, ArgumentTypeError
from datetime import datetime

import grpc

from utils import get_timestamp
import proto as pb


ARG_DATE_FORMAT = "%Y-%m-%d"


ENVS = {
    "local": "localhost:8081",
    "minikube": "192.168.99.100:30218",
}


def valid_date(s):
    try:
        return datetime.strptime(s, ARG_DATE_FORMAT)
    except ValueError:
        msg = "Not a valid date: '{0}'.".format(s)
        raise ArgumentTypeError(msg)


def add_todo(args, stub):
    todo = pb.Todo()
    todo.title = args.title
    todo.dueOn = get_timestamp(args.dueOn)
    if args.status:
        todo.status = pb.Status.Value(args.status.upper())
    if args.description:
        todo.description = args.description
    todo.assignee = args.assignee
    response = stub.addTodo(pb.AddTodoRequest(todo=todo))
    print("Todo client received: {}".format(response.todo))


def get_todo(args, stub):
    request = pb.GetTodoRequest(id=args.id, assignee=args.assignee)
    response = stub.getTodo(request)
    print(response.todo)


def complete_todo(args, stub):
    request = pb.CompleteTodoRequest(id=args.id, assignee=args.assignee)
    response = stub.completeTodo(request)
    print(response)


def get_by_status(args, stub):
    request = pb.GetByStatusRequest(status=args.status, assignee=args.assignee)
    response = stub.getTodosByStatus(request)
    print(response)


if __name__ == '__main__':
    parser = ArgumentParser(description='Client for the todo-k8s service')
    subparsers = parser.add_subparsers(title="RPC Calls")

    # Add command
    add_parser = subparsers.add_parser("add", help="Add a new todo")
    add_parser.add_argument("assignee", metavar="assignee", type=int, help="The assigned user id")
    add_parser.add_argument("title", metavar="title", type=str, help="The title")
    add_parser.add_argument("dueOn", metavar="dueOn", type=valid_date, help="The due date Ex: 2017-06-17")
    add_parser.add_argument("-d", "--description", metavar="description", type=str, help="A description")
    add_parser.add_argument("-s", "--status", metavar="status", type=str, choices=pb.Status.keys(), help="Set the status")
    add_parser.add_argument("-e", "--env", metavar="environment", type=str, choices=ENVS.keys(), help="Set the status")
    add_parser.set_defaults(func=add_todo)

    # get command
    get_parser = subparsers.add_parser("get", help="Get a todo")
    get_parser.add_argument("id", metavar="id", type=int, help="A todo ID")
    get_parser.add_argument("assignee", metavar="a", type=int, help="The assigned user")
    get_parser.add_argument("-e", "--env", metavar="environment", type=str, choices=ENVS.keys(), help="Set the status")
    get_parser.set_defaults(func=get_todo)

    # mark complete
    complete_parser = subparsers.add_parser("complete", help="Mark a todo as complete")
    complete_parser.add_argument("id", metavar="id", type=int, help="A todo ID")
    complete_parser.add_argument("assignee", metavar="a", type=int, help="The assigned user")
    complete_parser.add_argument("-e", "--env", metavar="environment", type=str, choices=ENVS.keys(), help="Set the status")
    complete_parser.set_defaults(func=complete_todo)

    # get by status command
    get_status_parser = subparsers.add_parser("sget", help="Get all todos in the givens status")
    get_status_parser.add_argument("-e", "--env", metavar="environment", type=str, choices=ENVS.keys(), help="Set the status")
    get_status_parser.add_argument("status", metavar="status", type=str, choices=pb.Status.keys(), help="The status")
    get_status_parser.add_argument("assignee", metavar="a", type=int, help="The assigned user")
    get_status_parser.set_defaults(func=get_by_status)

    args = parser.parse_args()
    channel = grpc.insecure_channel(ENVS.get(args.env, "pre-staging"))
    stub = pb.TodosStub(channel)
    args.func(args, stub)
