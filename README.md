# cpu_temp
-----
[中文](https://github.com/rickyhoho/cpu_temp/blob/master/README_cn.md)

**For linux only**

A plugin for [MCDReforged1.x](https://github.com/Fallen-Breath/MCDReforged) to check cpu temp regularly

You have to install python module <strong>`daytime`, `psutil` and `apscheduler`</strong> to use cpu_temp

You can execute `pip install daytime psutil apscheduler` to install it

Type `!!temp` or `!!temperature` to use this plugin

`!!temp restart` need helper or more permission to use

# varible useage
-----

`temp_loop` is loop start when load or not

`t_hours`, `t_minutes`, `t_seconds` is the regulay loop interval time

`warn_hours`, `warn_minutes`, `warn_seconds` is the warning loop interval time

`show_freq` is the frequency that the plugin print log after run regular loop for `show_freq` times(recommand don't change it)

`warning_degree`, `high_degree`, `medium_degree` is the warning degre and degree color setup

`restart_countdown` is the restart countdown
