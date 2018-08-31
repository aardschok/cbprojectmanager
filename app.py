"""Reference links for inspiration

* http://docs.efestolab.uk/tools/project-manager/index.html
* https://wedevs.s3.amazonaws.com/uploads/2016/02/projects.jpg
* https://www.scoro.com/wp-content/uploads/2017/02/FunctionFox.jpg
"""

import sys
import site

site.addsitedir("C:/Users/Guest4/Development/colorbleed/core")

from avalon.vendor.Qt import QtWidgets, QtCore, QtGui
from avalon.vendor import qtawesome as qta
from avalon import api, style

from widgets import CreateProjectWidget, ManageProjectWidget, Navigation

import lib


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
        main_control_layout = QtWidgets.QHBoxLayout()

        database_label = QtWidgets.QLabel()

        projects_label = QtWidgets.QLabel("Project:")
        projects = QtWidgets.QComboBox()
        projects.insertItem(0, "<None>")

        refresh_button = QtWidgets.QPushButton("R")
        refresh_icon = qta.icon("fa.refresh", color=style.colors.light)

        refresh_button.setFixedWidth(24)
        refresh_button.setFixedHeight(24)

        refresh_button.setIcon(refresh_icon)

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
        create_widget = CreateProjectWidget(parent=self)
        manager_widget = ManageProjectWidget(parent=self)

        stacked_widget.insertWidget(create_widget.order, create_widget)
        stacked_widget.insertWidget(manager_widget.order, manager_widget)

        # Navigation panel widget
        navigation_panel = Navigation()

        # Add buttons to navigation panel
        navigation_panel.add_button(create_widget.label, create_widget.order)
        navigation_panel.add_button(manager_widget.label, manager_widget.order)

        # Add stretch to the navigation panel
        navigation_panel.layout.addStretch()

        split_widget.addWidget(navigation_panel)
        split_widget.addWidget(stacked_widget)
        split_widget.setHandleWidth(4)
        split_widget.setSizes([180, 620])

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

