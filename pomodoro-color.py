#!/usr/bin/env python3
import subprocess
import re
import datetime
import sys

C_STOP = "#666666"
C_WORKING0 = C_STOP
C_PAUSE = "#40e0d0"

time_pomodoro = 25
time_break = 5
time_long_break = 15

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

CMD_START = ["i3-gnome-pomodoro", "start"]
CMD_STOP = ["i3-gnome-pomodoro", "stop"]
CMD_TGL = ["i3-gnome-pomodoro", "toggle"]
CMD_SKIP = ["i3-gnome-pomodoro", "skip"]
CMD_STATUS = ["i3-gnome-pomodoro", "status"]
COLOR_STOP = "#666666"

# status
STOPED = 0
WORKING = 1
PAUSE = 2
BREAK = 3
LONGBREAK = 4

BTOFF = 0
BTLEFT = 1
BTRIGHT = 3
BTMID = 2


def get_object_color(color_obj, time):
    for item in color_obj:
        if item[0] < time.minute:
            return item[1]

    return color_obj[-1][1]


def run_command(cmd):
    return subprocess.run(cmd, stdout=subprocess.PIPE).stdout.decode('utf-8')


def get_mode(cmd_str):
    if cmd_str.find("PAUSED") != -1:
        return PAUSE

    if cmd_str.find("Break") != -1:
        return BREAK

    if cmd_str.find("00:00") != -1:
        return STOPED

    if cmd_str.find("Long") != -1:
        return LONGBREAK

    return WORKING


# czas
def get_time(string):
    string = string.strip()

    time = re.compile(r"\d\d:\d\d")

    try:
        time = time.findall(string)[0]
    except ValueError:
        time = "00:00"
    if time[-2] == '6':
        time[-2] = 5
        time[-1] = 9

    time = datetime.datetime.strptime(time, "%M:%S")

    return time


def get_color(time, mode):
    if mode == STOPED:
        return C_STOP

    if mode == PAUSE:
        return C_PAUSE

    if mode == BREAK:
        return get_object_color(break_colors, time)

    if mode == LONGBREAK:
        return get_object_color(long_break_colors, time)

    if mode == WORKING:
        return get_object_color(working_colors, time)

    return C_WORKING0


def get_rec(time, mode):
    on = "□"
    off = "■"

    buf = ""

    div = 5
    if mode == BREAK:
        div = 1
    if mode == LONGBREAK:
        div = 3

    con = int(time.minute / div)
    coff = 4 - con

    for i in range(coff):
        buf = buf + off

    for i in range(con):
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


def print_state(cmd_str, bt):
    time = get_time(cmd_str)
    mode = get_mode(cmd_str)
    color = get_color(time, mode)

    print(get_rec(time, mode).strip() + " " + cmd_str.strip())
    #print(get_bat(time).strip() + " " + cmd_str.strip())
    print("")
    print(color.strip())


def onBT(button_state):
    button_state = int(button_state)
    #
    if button_state == BTOFF:
        return ""
    if button_state == BTLEFT:
        run_command(CMD_TGL)

    if button_state == BTRIGHT:
        pass
        run_command(CMD_STOP)
        run_command(CMD_START)

    if button_state == BTMID:
        run_command(CMD_SKIP)
    pass


def update_status():
    CMDSTATUSOUTPUT = run_command(CMD_STATUS)
    # os.wait(1);
    print_state(CMDSTATUSOUTPUT, 0)


try:
    BUTTONSTATE = sys.argv[1]
except:
    BUTTONSTATE = 0

onBT(BUTTONSTATE)

update_status()
sys.exit(0)
