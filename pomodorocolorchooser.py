from PyQt5.QtWidgets import QApplication, QPushButton, QHBoxLayout, QColorDialog
from PyQt5.QtWidgets import QWidget, QLabel, QGridLayout
from PyQt5.QtGui import QColor
from PyQt5.QtCore import pyqtSlot


class ColorQButton(QPushButton):
    def __init__(self, parent, index, dic_key):
        super(ColorQButton, self).__init__(parent)
        self.index = index
        self.dic_key = dic_key

        self.clicked.connect(self.open_color_dialog)
        self.color = ""

    @pyqtSlot()
    def open_color_dialog(self):
        d_color = QColorDialog.getColor()

        if d_color.isValid():
            self.color = d_color.name()
            self.setStyleSheet("background-color:{};".format(self.color))


class PomodoroColorChooser(QWidget):
    def __init__(self, parent=None, cfg=None):
        super().__init__(parent)
        self.cfg = cfg
        self.button_list = list()
        self.interface()

    def init_buttons(self, label_str, dic_key, cfg=None):
        layout_h = QHBoxLayout()
        label = QLabel(label_str)
        layout_h.addWidget(label)

        for index in range(0, len(cfg[dic_key])):
            bt = ColorQButton(self, index, dic_key)
            bt.setStyleSheet("background-color:{};".format(cfg[dic_key][index][1]))
            bt.color = cfg[dic_key][index][1]
            layout_h.addWidget(bt)
            self.button_list.append(bt)

        return layout_h

    @pyqtSlot()
    def save_colors(self):

        for bt in self.button_list:
            self.cfg[bt.dic_key][bt.index][1] = bt.color
        self.cfg.save_data(self.cfg)

    @pyqtSlot()
    def exit_and_save(self):
        self.save_colors()
        self.close()

    def interface(self):
        layout = QGridLayout()

        quit_button = QPushButton("&Quit && Save", self)
        quit_button.resize(quit_button.sizeHint())
        quit_button.clicked.connect(self.exit_and_save)

        save_button = QPushButton("Save", self)
        save_button.resize(save_button.sizeHint())
        save_button.clicked.connect(self.save_colors)

        layout.addLayout(self.init_buttons("Pomodoro", "WORKING_COLOR", self.cfg), 1, 0, 1, 3)
        layout.addLayout(self.init_buttons("Break", "NORMAL_BREAK", self.cfg), 2, 0, 1, 3)
        layout.addLayout(self.init_buttons("Long break", "LONG_BREAK", self.cfg), 3, 0, 1, 3)

        layout.addWidget(save_button, 4, 0, 1, 3)
        layout.addWidget(quit_button, 5, 0, 1, 3)

        self.setLayout(layout)
        self.resize(300, 100)
        self.setWindowTitle("pomodorocolorchooser")
        self.show()


def make_gui(cfg):
    import sys
    app = QApplication(sys.argv)
    win = PomodoroColorChooser(cfg=cfg)
    sys.exit(app.exec_())


if __name__ == '__main__':
    pass
