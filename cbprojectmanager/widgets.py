import os
import json
import logging
from functools import partial

from avalon.vendor.Qt import QtWidgets, QtCore
from avalon.vendor import qtawesome as qta

from cbprojectmanager.model import TreeModel, Node
from cbprojectmanager import lib, style


class CreateProjectWidget(QtWidgets.QWidget):
    """Widget to create a new collection and project definition"""

    order = -1
    label = "Create"

    data_changed = QtCore.Signal()

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent=parent)

        self.log = logging.getLogger(__name__)

        self.setWindowTitle("Create New Project")
        self.setWindowFlags(QtCore.Qt.Dialog)
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

        cancel_button = QtWidgets.QPushButton("Cancel")
        cancel_button.setStyleSheet(style.flat_button)
        cancel_button.setFixedWidth(500)

        layout.addLayout(create_vlayout)
        layout.addLayout(clone_vlayout)
        layout.addWidget(create_button)
        layout.addWidget(cancel_button)

        self.setLayout(layout)

        self.project_name = project_name

        self.clone_toggle = clone_toggle
        self.clone_project = clone_project

        self.create = create_button
        self.cancel = cancel_button

        # Build connections
        self.connect_signals()

        self.refresh()

    def refresh(self):
        self.toggle_clone_enabled()
        self.populate_clone_project()

    def populate_clone_project(self):

        # Check if widget has a parent
        if self.parent() is None:
            return

        # Get project from the parent, {"projectName": ObjectId(123445)}
        projects = self.parent().projects
        for i, (name, _id) in enumerate(projects.items()):
            self.clone_project.insertItem(i + 1, name, userData=_id)

    def connect_signals(self):
        self.clone_toggle.toggled.connect(self.toggle_clone_enabled)
        self.create.clicked.connect(self.on_create_project)
        self.cancel.clicked.connect(self.close)

    def toggle_clone_enabled(self):

        self.clone_project.blockSignals(True)

        self.clone_project.clear()
        self.populate_clone_project()

        state = self.clone_toggle.isChecked()
        self.clone_project.setEnabled(state)

        self.clone_project.blockSignals(False)

    def on_create_project(self):

        project_name = self.project_name.text()
        assert project_name, "Name cannot be empty!"

        if self.clone_toggle.isChecked():
            clone_from = self.clone_project.currentText()
            template = lib.get_project_template(clone_from)
        else:
            template = lib.get_template()

        self.log.info("Creating project ..")
        self.log.info("Project name: %s" % project_name)

        print("0")
        result = lib.create_project(project_name, template)
        if not result:
            self.log.error("Error occurred in creating project")
            return

        self.close()


class ManageProjectWidget(QtWidgets.QWidget):
    """Widget to manage the current set project

    The user will add, remove, rename and reorder assets with this widget
    """

    order = 1
    label = "Manage"
    data_changed = QtCore.Signal(dict)

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent=parent)

        layout = QtWidgets.QVBoxLayout()

        text = QtWidgets.QLabel("Under development!")
        tab_widget = QtWidgets.QTabWidget()

        button_hlayout = QtWidgets.QHBoxLayout()
        button_hlayout.addStretch()

        update_button = QtWidgets.QPushButton("Update")
        update_button.setMinimumWidth(120)
        update_button.setStyleSheet(style.flat_button)

        button_hlayout.addWidget(update_button)

        layout.addWidget(text)
        layout.addWidget(tab_widget)
        layout.addLayout(button_hlayout)

        self.setLayout(layout)

        self.tab_widget = tab_widget

    def add_widget(self, widget):
        """Add a widget to the tab widget of the Manage widget

        Args:
            widget(QtWidgets.QWidget): instance of a widget

        Returns:
            None

        """

        # Check if widget has the required attributes
        self.validate_widget(widget)

        has_item = self.tab_widget.widget(widget.order)
        if has_item:
            raise RuntimeError("Current index `%i` is occupied" % widget.order)

        self.tab_widget.insertTab(widget.order, widget, widget.label)

    def validate_widget(self, widget):
        """Validate if widget has the required attributes

        Required attributes:
            - order (int)
            - label (str)

        Raises AssertionError if the widget is invalid

        """

        required = {"order": int, "label": str}
        for attr, attr_type in required.items():
            assert hasattr(widget, attr), ("%s is missing attribute `%s`"
                                           % (widget.__class__.__name__, attr))
            value = getattr(widget, attr, None)
            assert value is not None, ("Attribute `%s` cannot be None" %
                                       attr)
            assert isinstance(value, attr_type), (
                    "Attribute `%s` is not of type `%s`" % (attr, attr_type)
            )

    def on_update(self):

        # Trigger the widget's update method
        widget = self.tab_widget.currentWidget()
        widget.update()


class OverviewWidget(QtWidgets.QWidget):

    order = 0
    label = "Overview"

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)

        # Attributes
        self.data_table = {}
        self._tile_width = 150
        self._tile_height = 150

        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(5)

        self.layout = layout

        self.setStyleSheet(style.overview_tile)
        self.setLayout(layout)

    def add_data(self, header, data):
        """Add information which needs to be displayed"""

        if header in self.data_table:
            print("Cannot add similar header, please use `update` in stead")
            return

        data_widget = QtWidgets.QWidget()
        data_widget.setContentsMargins(0, 0, 0, 0)
        data_widget.setFixedHeight(self._tile_height)

        layout = QtWidgets.QVBoxLayout()

        title = QtWidgets.QLabel(header.upper())
        title.setStyleSheet(style.overview_tile_title)

        formlayout = QtWidgets.QFormLayout()
        for label, value in data.items():
            value_label = QtWidgets.QLabel(value)
            formlayout.addRow("%s :" % label, value_label)

        layout.addWidget(title)
        layout.addLayout(formlayout)
        layout.addStretch()

        data_widget.setLayout(layout)

        self.data_table[header] = {"widget": data_widget, "data": data}

        position = self.layout.count() + 1

        self.layout.insertWidget(position, data_widget)

    def update_data(self, header, data):

        self.layout.blockSignals(True)

        if header not in self.data_table:
            return

        widget = self.data_table[header]["widget"]
        self.layout.removeWidget(widget)
        self.data_table.pop(header, None)

        self.add_data(header, data)

        self.layout.blockSignals(False)

    def refresh(self):
        pass

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

        self.connect_signals()

        self.refresh()

    def refresh(self):

        self._install_fontlib()
        self._populate_icons()

    def _install_fontlib(self):

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

        # self.setWindowFlag()
        self.setStyleSheet(style.flat_button)

        layout = QtWidgets.QVBoxLayout()

        dynamic_layout = QtWidgets.QVBoxLayout()
        static_layout = QtWidgets.QVBoxLayout()
        static_layout.addStretch()

        layout.addLayout(dynamic_layout)
        layout.addStretch()
        layout.addLayout(static_layout)

        self.dynamic_layout = dynamic_layout
        self.static_layout = static_layout

        self.setLayout(layout)
        self.layout = layout

    def add_button(self, label, order, widget=None):
        """Add a button to the navigation panel with the given label and order

        Args:
            label(str): Name displayed on the button
            order(int): Number which dictates its order in the panel
            widget(QtWidgets.QWidget): Instance of a widget

        Returns:
            None
        """

        if order < 0:
            layout = self.static_layout
        else:
            layout = self.dynamic_layout

        # Check new position
        widget_at_item = layout.itemAt(abs(order))
        if widget_at_item:
            self.log.warning("Found multiple items for the same order: `%i`"
                             % order)
            return

        button = QtWidgets.QPushButton(label)
        if widget:
            button.clicked.connect(partial(widget.show))

        layout.insertWidget(order, button)

        return button
