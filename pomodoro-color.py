#!/usr/bin/env python3
import subprocess
import re
import datetime
import sys

# czas poszczególnych trybów
time_pomodoro = 25
time_break = 5
time_long_break = 15

C_STOP = "#666666"
C_WORKING0 = C_STOP
C_PAUSE = "#40e0d0"
COLOR_STOP = "#666666"

# todo: Zmiana kolorów
# todo: Zapis ustawień kolorów do pliku, oraz ich odczyt,
# todo: Zapis czasów
# todo: Proste GUI z wyborem kolorów i znaków
# todo: Rezygnacja z i3-gnome-pomodoro
# todo: Poprawnie działania long break pause itp
long_break_colors = [[12, "#7FFF00"],
                     [9, "#7FFF00"],
                     [6, "#7FFF00"],
                     [3, "#7FFF00"],
                     [0, "#7FFF00"]]

break_colors = [[4, "#7FFF00"],
                [3, "#7FFF00"],
                [2, "#7FFF00"],
                [1, "#7FFF00"],
                [0, "#7FFF00"]]

working_colors = [[20, "#7FFF00"],
                  [15, "#CAFF70"],
                  [10, "#FFB90F"],
                  [5, "#FF7F50"],
                  [0, "#FF3030"]]

# komendy sterujące pomodoro
CMD_START = ["i3-gnome-pomodoro", "start"]
CMD_STOP = ["i3-gnome-pomodoro", "stop"]
CMD_TGL = ["i3-gnome-pomodoro", "toggle"]
CMD_SKIP = ["i3-gnome-pomodoro", "skip"]
CMD_STATUS = ["i3-gnome-pomodoro", "status"]

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


def get_object_color(color_obj, time):
    for item in color_obj:
        if item[0] < time.minute:
            return item[1]

    return color_obj[-1][1]


def run_command(cmd):
    return subprocess.run(cmd, stdout=subprocess.PIPE).stdout.decode('utf-8')


# todo: kolejność wyłapywania
def get_mode(cmd_str):
    if cmd_str.find("00:00") != -1:
        return STATUS_STOP

    if cmd_str.find("Long") != -1:
        return STATUS_LONG_BREAK

    if cmd_str.find("Break") != -1:
        return STATUS_BREAK

    if cmd_str.find("PAUSED") != -1:
        return STATUS_PAUSE

    return STATUS_WORKING


def get_time(string):
    string = string.strip()

    time = re.compile(r"\d\d:\d\d")

    try:
        time = time.findall(string)[0]
    except IndexError:
        time = "00:00"
    if time[-2] == '6':
        time[-2] = 5
        time[-1] = 9

    time = datetime.datetime.strptime(time, "%M:%S")

    return time


def get_color(time, mode):
    if mode == STATUS_STOP:
        return C_STOP

    if mode == STATUS_PAUSE:
        return C_PAUSE

    if mode == STATUS_BREAK:
        return get_object_color(break_colors, time)

    if mode == STATUS_LONG_BREAK:
        return get_object_color(long_break_colors, time)

    if mode == STATUS_WORKING:
        return get_object_color(working_colors, time)

    return C_WORKING0


def get_rec(time, mode):
    on = "□"
    off = "■"

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
    time = get_time(cmd_str)
    mode = get_mode(cmd_str)
    color = get_color(time, mode)

    print(get_rec(time, mode).strip() + " " + cmd_str.strip())
    # wersja z baterią
    # print(get_bat(time).strip() + " " + cmd_str.strip())
    print("")
    print(color.strip())


def on_button(button_state):
    button_state = int(button_state)
    #
    if button_state == BUTTON_OFF:
        return ""
    if button_state == BUTTON_LEFT:
        run_command(CMD_TGL)

    if button_state == BUTTON_RIGHT:
        pass
        run_command(CMD_STOP)
        run_command(CMD_START)

    if button_state == BUTTON_MID:
        run_command(CMD_SKIP)
    pass


def update_status():
    cmd_status_output = run_command(CMD_STATUS)
    print_state(cmd_status_output)


if __name__ == "__main__":
    try:
        BUTTON_STATE = sys.argv[1]
    except IndexError:
        BUTTON_STATE = 0

    on_button(BUTTON_STATE)

    update_status()
    sys.exit(0)
