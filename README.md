# Pomodoro-color
Pomodoro for i3blocks
 
 ![Screenshot](/screenshot.png)

Install:\
 `gnome-pomodoro`

python:\
 `pip install PyQt5 PyYAML`

Add in ~/.i3blocks.conf

```
[pomodorocolor]
command=/home/${USER}/PycharmProjects/i3-pomodoro-color/pomodoro-color.py ${BLOCK_BUTTON}
signal=2
interval=1
color=#C9CCDB
label=
```

Command for color chooser:
```
pomodoro-color.py gui
```

Mouse buttons functions:
- left - Toggle/Start
- mid - Skip
- right - Restart