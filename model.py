import logging

from avalon.tools.projectmanager.model import TreeModel, Node

log = logging.getLogger(__name__)


class TaskModel(TreeModel):

    COLUMNS = ["name", "icon"]

    def __init__(self):
        super(TaskModel, self).__init__()

        self._icons = {
            "__default__": qta.icon("fa.folder-o", color=colors.default)
        }

        self._get_task_icons()

    def _get_task_icons(self):
        # Get the project configured icons from database
        project = io.find_one({"type": "project"})
        tasks = project['config'].get('tasks', [])
        for task in tasks:
            icon_name = task.get("icon", None)
            if icon_name:
                icon = qta.icon("fa.{}".format(icon_name),
                                    color=colors.default)
                self._icons[task["name"]] = icon

    def data(self, index, role):

        if not index.isValid():
            return

        # Add icon to the first column
        if role == QtCore.Qt.DecorationRole:
            if index.column() == 0:
                return index.internalPointer()['icon']

        return super(TaskModel, self).data(index, role)