"""
These small stylesheets are to add an extra bit of flare to the existing
darrk style sheet
"""

from avalon.style import colors


create_widget = """QLineEdit {
font-size: 24px;
}

QLabel {
font-size: 24px;
}

QComboBox {
font-size: 24px;
}

"""

overview_tile = """QWidget {
color: %s;
background-color: %s;
}
""" % (
    colors.default,
    colors.dark
)

overview_tile_title = """QLabel {
height: 16px;
font: bold;
font-size: 14px; 
color: %s;
background-color: %s;
}
""" % (colors.default, colors.dark)

flat_button = """QPushButton {
font-size: 20px;
height: 38px;
background-color: %s; 
border: none;
}

QPushButton:hover {
color: black;
border: 2px solid %s;
background: %s;
}
""" % (
    colors.dark,  # Default background color
    colors.default,
    colors.default)  # Hover background color

preview_button = """QPushButton:disabled {
border: none;
color: %s;
}""" % colors.light

preview = """QTextEdit {
font-size: 14px;
color: %s;
}""" % colors.light
