import os
import json
import logging

from avalon.vendor.Qt import QtWidgets, QtCore, QtGui
from avalon.vendor import qtawesome as qta

from model import TreeModel, Node
import style


class CreateProjectWidget(QtWidgets.QWidget):
    """Widget to create a new collection and project definition"""

    order = 0
    label = "Create"

    data_changed = QtCore.Signal()

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent=parent)

        self.setStyleSheet(style.create_widget)

        layout = QtWidgets.QVBoxLayout()
        layout.setAlignment(QtCore.Qt.AlignCenter)
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(20)

        create_vlayout = QtWidgets.QVBoxLayout()

        project_label = QtWidgets.QLabel("Project Name")

        project_name = QtWidgets.QLineEdit()
        project_name.setPlaceholderText("Example: MARVEL_Spiderman_HomeComing")
        project_name.setStyleSheet("QLineEdit: {font-size: 50px}")

        create_vlayout.addWidget(project_label)
        create_vlayout.addWidget(project_name)

        # Clone from existing
        clone_vlayout = QtWidgets.QVBoxLayout()

        clone_label_hlayout = QtWidgets.QHBoxLayout()

        clone_toggle = QtWidgets.QCheckBox()
        clone_toggle.setFixedWidth(24)
        clone_toggle.setFixedHeight(24)
        clone_label = QtWidgets.QLabel("Clone")

        clone_label_hlayout.addWidget(clone_label)
        clone_label_hlayout.addWidget(clone_toggle)

        clone_project = QtWidgets.QComboBox()

        clone_vlayout.addLayout(clone_label_hlayout)
        clone_vlayout.addWidget(clone_project)

        create_button = QtWidgets.QPushButton("Create")
        create_button.setStyleSheet(style.flat_button)
        create_button.setFixedWidth(500)

        layout.addLayout(create_vlayout)
        layout.addLayout(clone_vlayout)
        layout.addWidget(create_button)

        self.setLayout(layout)

        self.project_name = project_name

        self.clone_toggle = clone_toggle
        self.clone_project = clone_project

        self.create = create_button

        # Build connections
        self.connect_signals()

        self.refresh()

    def refresh(self):
        self.toggle_clone_enabled()
        self.populate_clone_project()

    def populate_clone_project(self):

        self.clone_project.insertItem(0, "<None>")

        if self.parent() is None:
            return

        projects = self.parent().projects
        for i, project in enumerate(projects):
            self.clone_project.insertItem(i + 1,
                                          project["name"],
                                          userData=project["_id"])

    def connect_signals(self):
        self.clone_toggle.toggled.connect(self.toggle_clone_enabled)

    def toggle_clone_enabled(self):
        state = self.clone_toggle.isChecked()
        self.clone_project.setEnabled(state)


class ManageProjectWidget(QtWidgets.QWidget):
    """Widget to manage the current set project

    The user will add, remove, rename and reorder assets with this widget
    """

    order = 1
    label = "Manage"

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent=parent)

        layout = QtWidgets.QVBoxLayout()

        text = QtWidgets.QLabel("Under development!")
        update_button = QtWidgets.QPushButton("Update")

        layout.addWidget(text)
        layout.addWidget(update_button)

        self.setLayout(layout)


class PreviewWidget(QtWidgets.QWidget):

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent=parent)

        self.setStyleSheet(style.preview)

        layout = QtWidgets.QVBoxLayout()

        self.preview_field = QtWidgets.QTextEdit()
        self.preview_field.setReadOnly(True)
        self.preview_field.setTabStopWidth(4)

        layout.addWidget(self.preview_field)

        self.setLayout(layout)

        self.update_data({"project": "",
                          "silos": "",
                          "tasks": "",
                          "applications": ""})

    def update_data(self, data):

        self.preview_field.blockSignals(True)
        self.preview_field.setText(json.dumps(data, indent=4))
        self.preview_field.blockSignals(True)


class TaskWidget(QtWidgets.QWidget):

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent=parent)

        layout = QtWidgets.QVBoxLayout()

        # controls
        top_layout = QtWidgets.QHBoxLayout()
        label = QtWidgets.QLabel("Tasks")

        add_button = QtWidgets.QPushButton("+")
        add_button.setFixedWidth(28)
        remove_button = QtWidgets.QPushButton("-")
        remove_button.setFixedWidth(28)

        top_layout.addWidget(label)
        top_layout.addStretch()
        top_layout.addWidget(add_button)
        top_layout.addWidget(remove_button)

        tree_view = QtWidgets.QTreeView()
        tree_model = TreeModel()
        tree_view.setModel(tree_model)

        layout.addLayout(top_layout)
        layout.addWidget(tree_view)

        self.setLayout(layout)

        self.add_button = add_button
        self.remove_button = remove_button

        self.tree_model = tree_model

        self._add_dialog = AddTaskIconDialog()

        self.connect_signals()

    def connect_signals(self):

        self.add_button.clicked.connect(self.on_add)
        self._add_dialog.addTask.connect(self.update_task_view)

    def on_add(self):
        self._add_dialog.show()

    def update_task_view(self, dict):

        node = Node()
        node.update(dict)

        self.tree_model.add_child(node)


class AddTaskIconDialog(QtWidgets.QWidget):

    addTask = QtCore.Signal(dict)

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent=parent)

        self.setWindowFlag(QtCore.Qt.Dialog)

        if parent:
            self.setStyleSheet(parent.styleSheet())

        layout = QtWidgets.QVBoxLayout()

        task_icon_layout = QtWidgets.QHBoxLayout()
        task_name = QtWidgets.QLineEdit()
        icon_name = QtWidgets.QComboBox()

        icon_preview_button = QtWidgets.QPushButton()
        icon_preview_button.setEnabled(False)
        icon_preview_button.setStyleSheet(style.preview_button)

        task_icon_layout.addWidget(task_name)
        task_icon_layout.addWidget(icon_name)
        task_icon_layout.addWidget(icon_preview_button)

        buttons_layout = QtWidgets.QHBoxLayout()
        accept_button = QtWidgets.QPushButton("Accept")
        cancel_button = QtWidgets.QPushButton("Cancel")

        buttons_layout.addWidget(accept_button)
        buttons_layout.addWidget(cancel_button)

        layout.addLayout(task_icon_layout)
        layout.addLayout(buttons_layout)

        self.setLayout(layout)

        self.task_name = task_name
        self.icon_name = icon_name
        self.icon_preview = icon_preview_button

        self.fontlib = {}

        # self.connect_signals()

        # self.refresh()

    def refresh(self):

        self._install_fontlib()
        self._populate_icons()

    def _install_fontlib(self):
        return
        # TODO: fix qta thingy
        package = os.path.dirname(qta.__file__)
        fonts = os.path.join(package, "fonts",
                             "fontawesome-webfont-charmap.json")

        with open(fonts, "r") as f:
            font_lib = json.load(f)

        self.fontlib = font_lib

    def _populate_icons(self):
        self.icon_name.blockSignals(True)
        icons = [""] + list(self.fontlib.keys())
        self.icon_name.addItems(icons)
        self.icon_name.blockSignals(False)

    def connect_signals(self):
        return

    def on_accept(self):

        # TODO: make preflight check
        self.addTask.emit({"name": self.task_name.currentText(),
                           "icon": self.icon_name.currentText()})

        self.close()

    def _create_preview(self):

        icon_name = "fa.{}".format(self.icon_name.currentText())
        new_icon = qta.icon(icon_name, color=style.colors.dark)
        self.icon_preview.setIcon(new_icon)


class Navigation(QtWidgets.QWidget):
    """Navigation panel widget"""

    index_changed = QtCore.Signal(int)
    log = logging.getLogger("Navigation")

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent=parent)

        self.setStyleSheet(style.flat_button)

        layout = QtWidgets.QVBoxLayout()

        self.setLayout(layout)
        self.layout = layout

    def add_button(self, label, order):
        """Add a button to the navigation panel with the given label and order

        Args:
            label(str): Name displayed on the button
            order(int): Number which dictates its order in the panel

        Returns:
            None
        """

        # Check new position
        widget = self.layout.itemAt(order)
        if widget:
            self.log.warning("Found multiple items for the same order: `%i`"
                             % order)
            return

        button = QtWidgets.QPushButton(label)
        button.clicked.connect(lambda: self.index_changed.emit(order))

        self.layout.insertWidget(order, button)
