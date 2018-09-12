#!/usr/bin/env python3
import subprocess
import re
import datetime

CSTOPED     = "#666666"
CWORKING0   = "#FF3030"
CWORKING5   = "#FF7F50"
CWORKING10  = "#FFB90F"
CWORKING15  = "#CAFF70"
CWORKING20  = "#7FFF00"

CPAUSE  = "#40e0d0"

CMDRESTART = ["i3-gnome-pomodoro stop && i3-gnome-pomodoro start"]
CMDTGL = "i3-gnome-pomodoro toggle"
CMDSKIP = "i3-gnome-pomodoro skip"
CMDSTATUS = ["i3-gnome-pomodoro", "status"]
COLORSTOP = "#666666"

#status
STOPED  = 0
WORKING = 1
PAUSE   = 2
BREAK   = 3

def run_command(cmd):
    return subprocess.run(cmd, stdout=subprocess.PIPE).stdout.decode('utf-8')


def get_mode(cmd_str):
    if(cmd_str.find("PAUSED") != -1):
        return PAUSE

    if (cmd_str.find("Break") != -1):
        return BREAK

    if(cmd_str.find("00:00") != -1):
        return STOPED

    return WORKING

# czas
def get_time(str):
    str = str.strip()
    time = re.compile(r"\d\d:\d\d")
    time = time.findall(str)[0]

    time = datetime.datetime.strptime(time, "%M:%S")

    return time


def get_status():
    pass


def get_color(time, mode):
    if mode == STOPED:
        return CSTOPED

    if mode == PAUSE:
        return CPAUSE

    if mode == BREAK:
        return CPAUSE

    if mode == WORKING:
        if time.minute > 20:
            return CWORKING20

        if time.minute > 15:
            return CWORKING15

        if time.minute > 10:
            return CWORKING10

        if time.minute > 5:
            return CWORKING5

    return CWORKING0


def get_rec(time):
    on = "□"
    off = "■"

    buf = ""

    con = int(time.minute/5)
    coff = 5-con

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


def print_state(cmd_str):
    time = get_time(cmd_str)
    mode = get_mode(cmd_str)
    color = get_color(time, mode)

    print(get_rec(time).strip() + " " + cmd_str.strip())
    #print(get_bat(time).strip() + " " + cmd_str.strip())
    print("")
    print(color.strip())


# todo obsluga klikniecia
# Pokazanie statusu
CMDSTATUSOUTPUT = run_command(CMDSTATUS)

print_state(CMDSTATUSOUTPUT)
