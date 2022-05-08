# -*- coding: utf-8 -*-
import psutil
import re
import time
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime
from typing import TYPE_CHECKING
from cbr.plugin.rtext import *

if TYPE_CHECKING:
    from cbr.plugin.cbrinterface import CBRInterface
    from cbr.plugin.info import MessageInfo

METADATA = {
    'id': 'cpu_temp',
    'version': '4.0.0',
    'name': 'cpu_temp',
    'description': 'A plugin to check cpu temp regularly.',
    'author': 'ricky',
    'link': 'https://github.com/R1ckyH/cpu_temp',
}


def rtext_cmd(txt, msg, cmd):
    return RText(txt).h(msg).c(RAction.run_command, cmd)


# loop or not
temp_loop = True
# interval time
t_hours = 0
t_minutes = 2
t_seconds = 0
show_freq = 15  # 0 is show without hide
# warning interval time
warn_hours = 0
warn_minutes = 1
warn_seconds = 0
# warn_degrees
warning_degree = 90
high_degree = 70
medium_degree = 50
# restart countdown
restart_countdown = 10
# don't touch
restarting = False
task_start = False
warn_start = False
show_msg = True
count = 0
task: 'TemperatureChecker'
norm_trigger = IntervalTrigger(
    hours=t_hours,
    minutes=t_minutes,
    seconds=t_seconds
)
warn_trigger = IntervalTrigger(
    hours=warn_hours,
    minutes=warn_minutes,
    seconds=warn_seconds,
)

plugin = 'cpu_temp'
prefix = '##temperature'
prefix1 = '##temp'

system_return = f'''§b[§r{plugin}§b] §r'''
time_now = 0
warning = system_return + '''§cWarning: '''
error = system_return + '''§cError: '''
error_used = error + 'The cycle are already stating!'
error_permission = error + 'You have no Permission to use this command'
error_unknown_command = error + '''Unknown command§r
Type ''' + rtext_cmd('§7##temp help§r', 'help page', '##temp help') + ''' for more information'''
help_msg = '''§b-----------§fcpu_temp§b-----------§r
''' + rtext_cmd('##temperature / ##temp§a show help message§r', 'show help message', prefix1) + '''
''' + rtext_cmd('##temperature show§a show detail of cpu temperature§r', 'show temperature detail', prefix1 + ' show') + '''
''' + rtext_cmd('##temperature start§a start loop cpu temperature checking§r', 'start loop cpu temperature',
                prefix1 + ' start') + '''
''' + rtext_cmd('##temperature stop§a stop loop cpu temperature checking§r', 'stop loop cpu temperature',
                prefix1 + ' stop') + '''
§b-----------------------------------§r'''


def out_log(msg: str):
    msg = re.sub("§.", "", str(msg))
    with open('logs/cpu_temp.log', 'a+') as log:
        log.write(datetime.now().strftime("[%Y-%m-%d %H:%M:%S]") + msg + '\n')
    print("[CBR] " + datetime.now().strftime("[%H:%M:%S]") + ' [cpu_temp] ' + msg)


def print_msg(msg, num, server: 'CBRInterface', info: 'MessageInfo' = None):
    if num == 0:
        for i in server.get_online_clients():
            server.send_message(i, msg)
        out_log(msg)
    elif num == 1:
        server.reply(info, msg)
        out_log(msg)


class TemperatureChecker:
    def __init__(self, server: 'CBRInterface'):
        self.cmd_server = server
        self.logger = self.cmd_server.logger
        self.task = BackgroundScheduler()

    def warning_temp(self):
        global warn_start
        warn_start = True
        self.task.remove_job('loop')
        self.add_task(1)

    def add_task(self, num):
        if num == 0:
            use_trigger = norm_trigger
            loop_id = 'loop'
        else:
            use_trigger = warn_trigger
            loop_id = 'warn_loop'
        self.task.add_job(
            self.cal_temp,
            trigger=use_trigger,
            id=loop_id,
            replace_existing=True
        )

    def run_warn(self):
        self.cal_temp(3)

    def warning_temp_stop(self):
        global warn_start
        self.task.remove_job('warn_loop')
        warn_start = False
        self.add_task(0)

    def open_sche(self):
        global count
        count = 0
        self.add_task(0)
        self.start_on()

    def start_on(self):
        global task_start
        task_start = True
        self.task.start()

    def cal_avg(self, temp, show_all=False):
        global time_now, show_msg
        packet = 0
        cnt = 0
        avg = 0
        reply_msg = ""
        if int(datetime.now().strftime("%Y%m%d%H%M%S")) - time_now > 120:
            show_msg = True
            time_now = int(datetime.now().strftime("%Y%m%d%H%M%S"))
        else:
            show_msg = False
        for i in range(0, len(temp)):
            if temp[i][0].startswith('Package id'):
                if packet == 0:
                    packet = 1
                else:
                    break
            if show_all:
                reply_msg += temp[i][0] + ' : ' + temp_color(temp[i][1]) + "\n"
            avg = avg + temp[i][1]
            cnt = cnt + 1
        if show_all and show_msg:
            out_log(reply_msg)
        return avg / cnt, reply_msg

    def cal_temp(self, num=0, server: 'CBRInterface' = None, info: 'MessageInfo' = None, reply_msg=""):
        global count
        temp = psutil.sensors_temperatures()
        if 'k10temp' in temp:
            temp_cache = temp['k10temp']
        else:
            temp_cache = temp['coretemp']
        avg_temp, msg = self.cal_avg(temp_cache, num == 1)
        reply_msg += msg
        temp_msg = 'Average cpu temperature : ' + temp_color(round(avg_temp, 2)) + "\n"
        highest_temp_msg = 'The highest core temperature : ' + temp_color(temp_cache[0][1])
        reply_msg += temp_msg
        reply_msg += highest_temp_msg
        if num == 0 or num == 3:
            if num == 0:
                if count >= show_freq:
                    out_log(reply_msg)
                    count = 0
                else:
                    count = count + 1
            tempe = temp_cache[0][1]
            if tempe > warning_degree:
                if not warn_start:
                    self.warning_temp()
                print_msg(
                    temp_msg + '\n' +
                    warning + highest_temp_msg +
                    rtext_cmd(' §e[▷]§r', 'Click for more information', prefix1 + ' show') +
                    '\n' + rtext_cmd('§e====Click for more information====§r', 'Click to show temperature details',
                                     prefix1 + ' show'),
                    0, server=self.cmd_server
                )
            else:
                if warn_start:
                    print_msg(reply_msg, 0, self.cmd_server)
                    self.warning_temp_stop()
        else:
            if num == 1 and show_msg:
                print_msg(reply_msg, 1, server, info)
            else:
                server.reply(info, reply_msg)

    def stop(self):
        global task_start
        task_start = False
        self.task.remove_all_jobs()
        self.task.shutdown()
        self.cmd_server.logger.info(system_return + 'Cycle stopped')


def temp_color(temperature):
    tmp = str(temperature) + '§d°C§r'
    if temperature > warning_degree:
        return '§c' + tmp
    elif temperature > high_degree:
        return '§6' + tmp
    elif temperature > medium_degree:
        return '§e' + tmp
    else:
        return '§a' + tmp


def permission_check(info):
    if info.source_client == "CBR":
        return True
    else:
        return False


def reply_help_msg(server: 'CBRInterface', info: 'MessageInfo'):
    task.cal_temp(2, server, info, reply_msg=help_msg + "\n")


def start_task(server: 'CBRInterface', info: 'MessageInfo'):
    if not task_start:
        task.cal_temp(server=server)
        task.open_sche()
        print_msg(system_return + 'The cycle start now', 1, server, info)
    else:
        print_msg(error + 'The cycle is already start', 1, server, info)


def stop_task(server: 'CBRInterface', info: 'MessageInfo'):
    if not task_start:
        server.reply(info, error + 'The cycle is already stop！')
    else:
        task.stop()
        server.reply(info, system_return + 'The cycle have been stop')


def on_message(server: 'CBRInterface', info: 'MessageInfo'):
    if info.content.startswith(prefix) or info.content.startswith(prefix1):
        info.cancel_send_message()
        args = info.content.split(" ")
        if len(args) == 1:
            reply_help_msg(server, info)
        elif len(args) != 2:
            server.reply(info, error_unknown_command)
        elif args[1] == "help":
            reply_help_msg(server, info)
        elif args[1] == "show":
            task.cal_temp(1, server, info)
        elif args[1] == "start":
            if permission_check(info):
                start_task(server, info)
            else:
                server.reply(info, error_permission)
        elif args[1] == "stop":
            if permission_check(info):
                stop_task(server, info)
            else:
                server.reply(info, error_permission)
        else:
            server.reply(info, error_unknown_command)


def on_command(server: 'CBRInterface', info: 'MessageInfo'):
    on_message(server, info)


def on_load(server: 'CBRInterface'):
    global task
    server.register_help_message('##temp', 'Check cpu temperature.')
    task = TemperatureChecker(server)
    if temp_loop:
        task.open_sche()


def on_unload(server: 'CBRInterface'):
    global task_start
    if task_start:
        task.stop()
        task_start = False
