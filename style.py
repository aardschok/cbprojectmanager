from avalon.style import colors


create_widget = """QLineEdit {
font-size: 30px
}

QLabel {
font-size: 30px
}

QComboBox {
font-size: 30px
}

"""

flat_button = """QPushButton {
font-size: 20px;
height: 38px;
background-color: %s; 
border: none;
}

QPushButton:hover {
color: black;
border: 2px solid %s;
background: %s
}
""" % (colors.dark,  # Default background color
       colors.default,
       colors.default)  # Hover background color

preview_button = """QPushButton:disabled {
border: none;
color: %s
}""" % colors.light

preview = """QTextEdit {
font-size: 14px;
color: %s;
}""" % colors.light
