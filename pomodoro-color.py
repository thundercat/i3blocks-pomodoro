#!/usr/bin/env python3
import subprocess
import re
import datetime
import sys
import yaml
import os
import pomodorocolorchooser
import logging

file_log = False
if file_log:
    handlers = [logging.FileHandler("{0}/{1}.log".format('./', 'pomodoro.log')), logging.StreamHandler()]
else:
    handlers = [logging.StreamHandler()]
logging.basicConfig(level=logging.INFO, handlers=handlers)
logger = logging.getLogger(__name__)
logger.info('Start aplikacji.')


class ConfigurationBase(dict):
    def __init__(self):
        super(ConfigurationBase, self).__init__()
        self.cfg_file = os.path.dirname(os.path.realpath(__file__)) + "/" + os.getenv('INIFILE', "config" + '.yaml')
        self.yaml_data = self.load(self.cfg_file)
        try:
            self.update(self.yaml_data)
        except TypeError:
            self.update(dict())
            raise TypeError

    def load(self, config_filename):
        """
        Metoda wczytuje dane yaml z pliku
        :param config_filename: pełna ścieżka pliku z ustawieniami
        :return:
        """
        try:
            with open(config_filename, 'r') as stream:
                try:
                    return yaml.load(stream)
                except yaml.YAMLError as exc:
                    print(exc)
        except FileNotFoundError:
            self.save_data(self)

    def save_data(self, data):
        self.save(self.cfg_file, data)

    def save(self, config_filename, data):
        """
        Metoda zapisuje dane yaml do pliku
        :param config_filename: pełna ścieżka do pliku z ustawieniami
        :param data: dane yaml do zapisu
        :return:
        """
        with open(config_filename, 'w') as outfile:
            yaml.dump(dict(data), outfile)
            self.yaml_data = self.load(config_filename)


DEFAULT_C_STOP = "#666666"
C_WORKING0 = DEFAULT_C_STOP
DEFAULT_C_PAUSE = "#40e0d0"
COLOR_STOP = "#666666"

# todo: Gui labele z zakresami
# todo: Rezygnacja z i3-gnome-pomodoro
# todo: Gui/CLi zakresy czasu wyliczanie vs edycja w GUI
# todo: Output klasa

# status
STATUS_STOP = 0
STATUS_WORKING = 1
STATUS_PAUSE = 2
STATUS_BREAK = 3
STATUS_LONG_BREAK = 4

# stany przycisków myszy
BUTTON_OFF = 0
BUTTON_LEFT = 1
BUTTON_MID = 2
BUTTON_RIGHT = 3

default_cfg = {'CMD_SKIP': ['i3-gnome-pomodoro', 'skip'],
               'CMD_START': ['i3-gnome-pomodoro', 'start'],
               'CMD_STATUS': ['i3-gnome-pomodoro', 'status'],
               'CMD_STOP': ['i3-gnome-pomodoro', 'stop'],
               'CMD_TGL': ['i3-gnome-pomodoro', 'toggle'],
               'LONG_BREAK': [[12, '#ff0004'], [9, '#ff007f'], [6, '#ff00ff'], [3, '#ff55ff'], [0, '#ffaaff']],
               'NORMAL_BREAK': [[4, '#00aa00'], [3, '#aaff7f'], [2, '#aaffff'], [1, '#ffff7f'], [0, '#ff0000']],
               'WORKING_COLOR': [[20, '#00ff00'], [15, '#CAFF70'], [10, '#FFB90F'], [5, '#FF7F50'], [0, '#ff0000']],
               'PAUSE_COLOR': '#40e0d0',
               'STOP_COLOR': '#666666',
               'TIMEBREAK': 5,
               'TIMELONGBREAK': 15,
               'TIMEPOMODORO': 25,
               }


def load_default_config(config):
       config = default_cfg


try:
    cfg = ConfigurationBase()
    save_flag = False
    for item in default_cfg:
        logger.info("klucz %s", item)
        try:
            a = cfg[item]
        except KeyError:
            logger.info("brak klucza: %s", item)
            cfg[item] = default_cfg[item]
            save_flag = True

except TypeError:
    logger.info("Brak pliku konfiguracyjnego. Utworzenie ")
    cfg = ConfigurationBase()
    load_default_config(cfg)
    save_flag = True

if save_flag:
    logger.info("Zapisanie ustawień")
    cfg.save_data(cfg)


def get_object_color(color_obj, time):
    for item in color_obj:
        if item[0] < time.minute:
            return item[1]

    return color_obj[-1][1]


class Command:
    def __init__(self, cmd_str):
        self.cmd_output = subprocess.run(cmd_str, stdout=subprocess.PIPE).stdout.decode('utf-8')

    def __str__(self):
        return self.cmd_output


def gui(cfg):
    pomodorocolorchooser.make_gui(cfg)


class OutputBase:
    def __init__(self, mode, time):
        self.mode = mode
        self.time = time
        self.output_cfg = dict()

    def __str__(self):
        raise NotImplementedError()


class RecOutput(OutputBase):
    def __init__(self, mode, time):
        super(RecOutput, self).__init__(mode, time)
        self.cli_str = ""

    def __str__(self):
        return


class Apl:
    def __init__(self):
        self.cfg = None
        self.output = None
        self.button_state = None

    def set_button_state(self, button_state):
        self.button_state = button_state

    def on_button(self, button_state):
        try:
            button_state = int(button_state)
        except ValueError:
            return

        if button_state == BUTTON_OFF:
            return

        if button_state == BUTTON_LEFT:
            Command(cfg['CMD_TGL'])
            return

        if button_state == BUTTON_RIGHT:
            Command(cfg['CMD_STOP'])
            Command(cfg['CMD_START'])
            return

        if button_state == BUTTON_MID:
            Command(cfg['CMD_SKIP'])
            return

    def run(self):
        self.on_button(self.button_state)


class Mode:
    def __init__(self, cmd_str):

        self.mode = STATUS_WORKING

        if cmd_str.find("00:00") != -1:
            self.mode = STATUS_STOP

        if cmd_str.find("Long") != -1:
            self.mode = STATUS_LONG_BREAK

        if cmd_str.find("Break") != -1:
            self.mode = STATUS_BREAK

        if cmd_str.find("PAUSED") != -1:
            self.mode = STATUS_PAUSE

    def __int__(self):
        return self.mode


class PomodoroTime:
    def __init__(self, string):
        time = re.compile(r"\d\d:\d\d")

        try:
            time = time.findall(string.strip())[0]
        except IndexError:
            time = "00:00"

        if time[-2] == '6':
            time = time.replace("60", "59")

        self.time = datetime.datetime.strptime(time, "%M:%S")

        self.minute = self.time.minute
        self.second = self.time.second


def get_color(time, mode):
    mode = int(mode)
    if mode == STATUS_STOP:
        return cfg["STOP_COLOR"]

    if mode == STATUS_PAUSE:
        return cfg["PAUSE_COLOR"]

    if mode == STATUS_BREAK:
        return get_object_color(cfg["NORMAL_BREAK"], time)

    if mode == STATUS_LONG_BREAK:
        return get_object_color(cfg["LONG_BREAK"], time)

    if mode == STATUS_WORKING:
        return get_object_color(cfg["WORKING_COLOR"], time)

    return C_WORKING0


def get_rec(time, mode):
    off = "□"
    on = "■"

    buf = ""

    div = 5
    if mode == STATUS_BREAK:
        div = 1
    if mode == STATUS_LONG_BREAK:
        div = 3

    c_on = int(time.minute / div)
    c_off = 4 - c_on

    for i in range(c_off):
        buf = buf + off

    for i in range(c_on):
        buf = buf + on

    return buf


def get_bat(time):
    if time.minute > 20:
        return ""
    if time.minute > 15:
        return ""
    if time.minute > 10:
        return ""
    if time.minute > 5:
        return ""

    return ""


def print_state(cmd_str):

    time = PomodoroTime(str(cmd_str))
    logger.info("time: %s", time.minute)

    mode = Mode(str(cmd_str))
    logger.info("mode: %" + str(int(mode)))

    color = get_color(time, mode)

    print(get_rec(time, mode).strip() + " " + str(cmd_str).strip())

    # wersja z baterią
    # print(get_bat(time).strip() + " " + cmd_str.strip())
    print("")
    print(color.strip())



def update_status():
    cmd_status_output = Command(cfg['CMD_STATUS'])
    print_state(cmd_status_output)


if __name__ == "__main__":
    logger.info("Sys argv: %s", sys.argv)
    try:
        BUTTON_STATE = sys.argv[1]
    except IndexError:
        BUTTON_STATE = 0

    logger.info("Stan przycisku: %s", BUTTON_STATE)
    apl = Apl()
    apl.set_button_state(BUTTON_STATE)
    apl.run()

    update_status()

    try:
        if sys.argv[1] == "gui":
            logger.info("Uruchomienie GUI")
            gui(cfg)
    except IndexError:
        pass

    sys.exit(0)
