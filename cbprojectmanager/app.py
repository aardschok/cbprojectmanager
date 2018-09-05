"""Reference links for inspiration

* http://docs.efestolab.uk/tools/project-manager/index.html
* https://wedevs.s3.amazonaws.com/uploads/2016/02/projects.jpg
* https://www.scoro.com/wp-content/uploads/2017/02/FunctionFox.jpg
"""

import sys
import site

site.addsitedir("C:/Users/Guest4/Development/colorbleed/core")

from avalon.vendor.Qt import QtWidgets
from avalon.vendor import qtawesome as qta
from avalon import api, style

from cbprojectmanager.widgets import (
    CreateProjectWidget,
    ManageProjectWidget,
    Navigation
)

from cbprojectmanager import lib

module = sys.modules[__name__]
module.window = None


class Window(QtWidgets.QWidget):

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)

        self.setWindowTitle("Project Manager")
        self.resize(1200, 800)

        self.projects = {}

        layout = QtWidgets.QVBoxLayout()

        # Main control
        ctrl_button_w = 30
        ctrl_button_h = 30

        # Calculate icon size
        icon_size = QtCore.QSize(ctrl_button_w - 4, ctrl_button_h - 4)

        main_control_layout = QtWidgets.QHBoxLayout()

        database_label = QtWidgets.QLabel()

        # Main buttons - create
        create_button = QtWidgets.QPushButton()
        create_icon = qta.icon("fa.plus-square", color=style.colors.light)

        create_button.setIconSize(icon_size)

        create_button.setFixedWidth(ctrl_button_w)
        create_button.setFixedHeight(ctrl_button_h)

        create_button.setIcon(create_icon)
        create_button.setStyleSheet(cbstyle.flat_button)

        # Main buttons - refresh
        refresh_button = QtWidgets.QPushButton()
        refresh_icon = qta.icon("fa.refresh", color=style.colors.light)

        refresh_button.setIconSize(icon_size)

        refresh_button.setFixedWidth(ctrl_button_w)
        refresh_button.setFixedHeight(ctrl_button_h)

        refresh_button.setIcon(refresh_icon)
        refresh_button.setStyleSheet(cbstyle.flat_button)

        # Project switch control
        projects_label = QtWidgets.QLabel("Project:")
        projects = QtWidgets.QComboBox()
        projects.insertItem(0, "<None>")

        # Add buttons to the main control layout
        main_control_layout.addWidget(create_button)
        main_control_layout.addStretch()
        main_control_layout.addWidget(database_label)
        main_control_layout.addWidget(projects_label)
        main_control_layout.addWidget(projects)
        main_control_layout.addWidget(refresh_button)

        # Splitter for tabwidget and preview / details widget
        split_widget = QtWidgets.QSplitter()

        # Widgets will be stored in a StackedWidget
        stacked_widget = QtWidgets.QStackedWidget()

        # Control widgets which make the tool
        manager_widget = ManageProjectWidget(parent=self)

        stacked_widget.insertWidget(manager_widget.order, manager_widget)

        # Navigation panel widget
        navigation_panel = Navigation()

        # Add buttons to navigation panel
        navigation_panel.add_button(manager_widget.label, manager_widget.order)

        # By adding widget we create a popup
        navigation_panel.add_button(create_widget.label,
                                    create_widget.order,
                                    widget=create_widget)

        # Add widgets to the SplitWidget
        split_widget.addWidget(navigation_panel)
        split_widget.addWidget(stacked_widget)
        split_widget.setHandleWidth(4)
        split_widget.setSizes([100, 700])

        layout.addLayout(main_control_layout)
        layout.addWidget(split_widget)

        self.setLayout(layout)

        self._navigation_panel = navigation_panel
        self._stacked_widget = stacked_widget

        self._database_label = database_label
        self._projects = projects
        self._refersh_button = refresh_button

        self.connect_signals()

        self.refresh()

    def connect_signals(self):
        """Create connections between widgets"""

        self._navigation_panel.index_changed.connect(
            self._stacked_widget.setCurrentIndex)

        self._refersh_button.clicked.connect(self.refresh)

    def refresh(self):
        """Refresh connection to database and """

        lib.install()
        self.set_database_label(lib.get_database_name())

        projects = list(lib.get_projects())
        self.projects = {p["name"]: p["_id"] for p in projects}

        self.populate_projects(projects)

    def set_database_label(self, name=None):
        label = "Database: {}".format(name or "<None>")
        self._database_label.setText(label)

    def populate_projects(self, projects):
        """Add projects to project dropdown menu"""

        for idx, project in enumerate(projects):
            self._projects.insertItem(idx + 1,
                                      project["name"],
                                      userData=project["_id"])

    def get_project(self, as_id=False):

        current_index = self._projects.currentIndex()
        if current_index == 0:
            return

        item = self._projects.itemAt(current_index)
        if as_id:
            _id = item.userData()
            assert _id, "This is a bug!"
            return _id

        project_name = item.text()
        assert project_name, "This is a bug!"

        return project_name

    def on_project_changed(self, name):

        current_project = self._projects.currentText()
        if name == current_project:
            return

        self.refresh()

        idx = self._projects.findText(name)
        if idx == -1:
            raise RuntimeError("Something went wrong, can't find name `%s`"
                               % name)

        self._projects.setCurrentIndex(idx)

        # Refresh the overview with
        self._overview.refresh(name)

    def on_project_index_changed(self):
        project_name = self._projects.currentText()
        self._overview.refresh(project_name)

    def on_create(self):
        create_widget = CreateProjectWidget(parent=self)
        create_widget.data_changed.connect(self.on_project_changed)

        create_widget.show()


if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)
    print("Updating Session")
    api.Session.update({"AVALON_MONGO": "mongodb://STORAGE1:27017"})
    print("Creating window ..")
    w = Window()
    w.setStyleSheet(style.load_stylesheet())
    print("Displaying ..")
    w.show()

    sys.exit(app.exec_())

