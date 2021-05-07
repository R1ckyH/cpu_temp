# -*- coding: utf-8 -*-
import psutil
import time
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from mcdreforged.api.types import *
from mcdreforged.api.command import *
from mcdreforged.api.rtext import *
from mcdreforged.api.decorator import new_thread


PLUGIN_METADATA = {
    'id': 'cpu_temp',
    'version': '2.5.2',
    'name': 'cpu_temp',
    'description': 'A plugin to check cpu temp regularly.',
    'author': 'ricky',
    'link': 'https://github.com/rickyhoho/cpu_temp',
    'dependencies': {
        'mcdreforged': '>=1.3.0'
    }
}


permission = {
    "help" : 1,
    "show" : 1,
    "start" : 2,
    "stop" : 2,
    "restart" : 2,
    "stoprestart" : 1,
}


def rtext_cmd(txt, msg, cmd):
    return RText(txt).h(msg).c(RAction.run_command, cmd)


#loop or not
temp_loop = True
#interval time
t_hours = 0
t_minutes = 2
t_seconds = 0
show_freq = 15#0 is show without hide
#warning interval time
warn_hours = 0
warn_minutes = 1
warn_seconds = 0
#warn_degrees
warning_degree = 90
high_degree = 70
medium_degree = 50
#restart countdown
restart_countdown = 10
#don't touch
restarting = False
task_start = False
warn_start = False
show_msg = True
count = 0
norm_trigger  = IntervalTrigger(
                hours = t_hours,
                minutes = t_minutes,
                seconds = t_seconds
)
warn_trigger = IntervalTrigger(
                hours = warn_hours,
                minutes = warn_minutes,
                seconds = warn_seconds,
)

plugin = 'cpu_temp'
prefix = '!!temperature'
prefix1 = '!!temp'

timenow = 0
systemreturn = '''§b[§rcpu_temp§b] §r'''
warning = systemreturn + '''§cWarning: '''
error = systemreturn + '''§cError: '''
error_used = error + 'The cycle are already stating!'
error_permission = error + 'You have no Permission to use this command'
error_unknown_command = error + '''Unknown command§r
Type ''' +  rtext_cmd('§7!!temp help§r', 'help page', '!!temp help') + ''' for more information'''
help = '''§b-----------§fcpu_temp§b-----------§r
''' + rtext_cmd('!!temperature / !!temp §ashow help message§r', 'show help message', prefix1) + '''
''' + rtext_cmd('!!temperature show §ashow detail of cpu temperature§r', 'show temperature detail', '!!temp show') + '''
''' + rtext_cmd('!!temperature start §astart loop cpu temperature checking§r', 'start loop cpu temperature', '!!temp start') + '''
''' + rtext_cmd('!!temperature stop §astop loop cpu temperature checking§r', 'stop loop cpu temperature', '!!temp stop') + '''
''' + rtext_cmd('!!temperature restart §arestart server§r', 'restart server', '!!temp restart') +  '''
''' + rtext_cmd('!!temperature stoprestart §astop restarting server§r', 'stop restart server', '!!temp stoprestart') +  '''
§b-----------------------------------§r'''  


def out_log(msg : str):
    msg = msg.replace('§r', '').replace('§d', '').replace('§c', '').replace('§6', '').replace('§e', '').replace('§a', '')
    with open('logs/cpu_temp.log', 'a+') as log:
        log.write(datetime.now().strftime("[%Y-%m-%d %H:%M:%S]") + msg + '\n')
    print("[server] " + datetime.now().strftime("[%H:%M:%S]") + ' [cpu_temp] ' + msg)


def print_msg(msg, num, info: Info = None, src : CommandSource = None, server : ServerInterface = None):
    if src != None:
        server = src.get_server()
        info = src.get_info()
    if num == 0:
        server.say(msg)
        out_log(msg)
    elif num == 1:
        server.reply(info, msg)
        out_log(msg)


class regular_task:
    def __init__(self, server : ServerInterface):
        self.cmd_server = server
    

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
            trigger = use_trigger,
            id = loop_id,
            replace_existing = True
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
        self.task = BackgroundScheduler()
        self.add_task(0)
        self.start_on()


    def start_on(self):
        global task_start
        task_start = True
        self.task.start()


    def avg_temp(self, num, temp, src : CommandSource = None):
        global timenow, show_msg
        packet = 0
        cnt = 0
        avg = 0
        if int(datetime.now().strftime("%Y%m%d%H%M%S")) - timenow > 60:
            show_msg = True
            timenow = int(datetime.now().strftime("%Y%m%d%H%M%S"))
        else:
            show_msg = False
        for i in range(0, len(temp['coretemp'])):
            if temp['coretemp'][i][0].startswith('Package id'):
                if packet == 0:
                    packet = 1
                else:
                    break
            if num == 1:
                if show_msg:
                    print_msg(temp['coretemp'][i][0] + ' : ' + temp_color(temp['coretemp'][i][1]), num, src = src)
                else:
                    src.reply(temp['coretemp'][i][0] + ' : ' + temp_color(temp['coretemp'][i][1]))
            avg = avg + temp['coretemp'][i][1]
            cnt = cnt + 1
        return avg / cnt


    def cal_temp(self, num = 0, src : CommandSource = None):
        global count
        temp = psutil.sensors_temperatures()
        avg_temp = self.avg_temp(num, temp, src)
        temp_msg = 'Average cpu temperature : ' + temp_color(round(avg_temp, 2))
        high_temp_msg = 'The highest core temperature' + ' : ' + temp_color(temp['coretemp'][0][1])
        if num == 0:
            if count >= show_freq:
                out_log(temp_msg)
                out_log(high_temp_msg)
                count = 0
            else:
                count = count + 1
        elif num != 3:
            if show_msg:
                print_msg(temp_msg, 1, src = src)
                print_msg(high_temp_msg, 1, src = src)
            else:
                src.reply(temp_msg)
                src.reply(high_temp_msg)
        if num == 0 or num == 3:
            if temp['coretemp'][0][1] > warning_degree:
                if not warn_start:
                    self.warning_temp()
                print_msg(
                    temp_msg + '\n' +
                    high_temp_msg +
                    rtext_cmd(' §e[▷]§r', 'Click for more information', '!!temp show') + 
                    rtext_cmd(' §c[restart]§r', 'restart server', '!!temp restart') +
                    rtext_cmd('§6====Click to restart server====§r', 'Click to restart server for save', '!!temp restart') +
                    rtext_cmd('§e====Click for more information====§r', 'Click to show temperature details', '!!temp show'),
                    0, src = src, server = self.cmd_server
                )
            else:
                if warn_start:
                    print_msg(temp_msg, 0, src = src, server = self.cmd_server)
                    print_msg(high_temp_msg, 0, src = src, server = self.cmd_server)
                    self.warning_temp_stop()


    def stop(self):
        global task_start
        task_start = False
        self.task.remove_all_jobs()
        self.task.shutdown()
        self.cmd_server.logger.info(systemreturn + 'Cycle stoped')


def temp_color(temperatre):
    tmp = str(temperatre) + '§d°C§r'
    if temperatre > warning_degree:
        return '§c' + tmp
    elif temperatre > high_degree:
        return '§6' + tmp
    elif temperatre > medium_degree:
        return '§e' + tmp
    else:
        return '§a' + tmp


@new_thread('restart')
def restart_server(src : CommandSource):
    global restarting
    server = src.get_server()
    if restarting:
        print_msg(error + 'restart is already running', 0, src = src)
        return
    restarting = True
    for i in range(0, restart_countdown):
        server.logger.info(systemreturn + 'The server will restart after ' + str(restart_countdown - i) +  ' second')
        server.say(systemreturn + 'The server will restart after ' + str(restart_countdown - i) +  ' second ' + rtext_cmd('§c[X]', '§cClick to stop restart', '!!temp stoprestart'))
        time.sleep(1)
        if not restarting:
            return
    restarting = False
    server.restart()


@new_thread('task_process')
def stop_restart(src : CommandSource):
    global restarting
    if restarting:
        print_msg(systemreturn + 'The restart have been stop', 0, src = src)
        restarting = False
    else:
        print_msg(error + 'The restart is already stoped', 0, src = src)


def permission_check(src : CommandSource, cmd):
    if src.get_permission_level() >= permission[cmd]:
        return True
    else:
        return False


@new_thread('task_process')
def help_msg(src : CommandSource):
    global task
    src.reply(help)
    task.cal_temp(2, src = src)


@new_thread('task_process')
def start_task(src : CommandSource):
    if not task_start:
        task.cal_temp(src = src)
        task.open_sche()
        print_msg(systemreturn + 'The cycle start now', 1, info = src.get_info(), src = src)
    else:
        print_msg(error + 'The cycle is already start', 1, info = src.get_info(), src = src)  


@new_thread('task_process')
def stop_task(src : CommandSource):
    if not task_start:
        src.reply(error + 'The cycle is already stop！')
    else:
        task.stop()
        src.get_server().say(systemreturn + 'The cycle have been stop')


def fox_literal(msg):
    return Literal(msg).requires(lambda src : permission_check(src, msg))


def register_command(server : ServerInterface, prefix_use):
    server.register_command(
        Literal(prefix_use).
        runs(help_msg).
        on_child_error(RequirementNotMet, lambda src : src.reply(error_permission), handled = True).
        on_child_error(UnknownArgument, lambda src : src.reply(error_unknown_command), handled = True).
        then(
            fox_literal('help').
            runs(help_msg)
        ).then(
            fox_literal('show').
            runs(lambda src : task.cal_temp(1, src))
        ).then(
            fox_literal('restart').
            runs(restart_server)
        ).then(
            fox_literal('stoprestart').
            runs(stop_restart)
        ).then(
            fox_literal('start').
            runs(lambda src : start_task(src))
        ).then(
            fox_literal('stop').
            runs(lambda src : stop_task(src))
        )
    )


def on_load(server : ServerInterface, old):
    global task
    if old is not None:
        if old.task_start:
            old.task.stop()
    server.register_help_message('!!temp','Check cpu temperatre.')
    task = regular_task(server)
    if temp_loop:
        task.open_sche()
    register_command(server, prefix)
    register_command(server, prefix1)
    

def on_unload(server : ServerInterface):
    global task_start
    if task_start:
        task.stop()
        task_start = False