from concurrent import futures
import time

import grpc

from models import TodoDAO
from proto import add_TodosServicer_to_server
from todo_service import TodosService


_ONE_DAY_IN_SECONDS = 60 * 60 * 24


def serve():
    if not TodoDAO.exists():
        TodoDAO.create_table(read_capacity_units=2, write_capacity_units=2)
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    add_TodosServicer_to_server(TodosService(), server)
    server.add_insecure_port('[::]:8081')
    server.start()
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    serve()
