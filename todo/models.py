from proto import Status, Todo
from pynamodb import attributes
from pynamodb import models
from pynamodb.indexes import GlobalSecondaryIndex, AllProjection
from utils import get_timestamp, get_todo_id


class AssigneeStatusIndex(GlobalSecondaryIndex):
    class Meta:
        index_name = "assignee_status_index"
        read_capacity_units = 2
        write_capacity_units = 2
        projection = AllProjection()

    assignee = attributes.NumberAttribute(hash_key=True)
    status = attributes.NumberAttribute(range_key=True)


class TodoDAO(models.Model):
    class Meta:
        table_name = "dev-todo-k8s-todos"
        host = "http://localstack:4569"

    assignee = attributes.NumberAttribute(hash_key=True)
    id = attributes.NumberAttribute(range_key=True)
    status = attributes.NumberAttribute()
    title = attributes.UnicodeAttribute()
    description = attributes.UnicodeAttribute(null=True)
    created_on = attributes.NumberAttribute()
    due_on = attributes.NumberAttribute()
    completed_on = attributes.NumberAttribute(null=True)

    last_updated = attributes.NumberAttribute()
    assingee_status_index = AssigneeStatusIndex()

    @classmethod
    def from_proto(cls, todo_proto):
        """
        Get a ``TodoDAO`` object from a proto message.

        Args:
            todo_proto (todo_pb2.Todo): The proto message.

        Returns:
            TodoDAO
        """
        todo = TodoDAO(
            hash_key=todo_proto.assignee,
            range_key=todo_proto.id,
            status=todo_proto.status,
            title=todo_proto.title,
            description=todo_proto.description,
            created_on=todo_proto.createdOn,
            due_on=todo_proto.dueOn,
            completed_on=todo_proto.completedOn
        )
        return todo

    def save(self, conditional_operator=None, **expected_values):
        if self.status is None:
            self.status = Status.TODO

        timestamp = get_timestamp()
        self.last_updated = timestamp
        if not self.created_on:
            self.created_on = timestamp
        if not self.id:
            self.id = get_todo_id(self)

        return super(TodoDAO, self).save(conditional_operator, **expected_values)

    def to_proto(self):
        return Todo(
            id=self.id,
            assignee=self.assignee,
            status=self.status,
            title=self.title,
            description=self.description,
            createdOn=self.created_on,
            dueOn=self.due_on,
            completedOn=self.completed_on
        )
