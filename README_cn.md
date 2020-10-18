# cpu_temp
-----
[English](https://github.com/rickyhoho/cpu_temp/blob/master/README.md)

**仅限linux使用**

一个 [MCDReforged1.x](https://github.com/Fallen-Breath/MCDReforged) 定时检测cpu温度的插件

你需要安装python模块 `daytime`, `psutil` 和 `apscheduler` 去使用cpu_temp

你可以运行指令 `pip install daytime psutil apscheduler` 去安装所需要的python模块

输入 `!!temp` 或 `!!temperature` 去使用此插件

`!!temp restart` 需要helper以上的权限去使用

# 函数用法
-----

`t_hours`, `t_minutes`, `t_seconds` 是定期检测的时间间隔

`warn_hours`, `warn_minutes`, `warn_seconds` 是警报运行间隔

`show_freq` 是服务器间隔检测而输出log的次数(建议不要改)
