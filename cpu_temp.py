# -*- coding: utf-8 -*-
import psutil
import copy
import daytime
import time
from apscheduler.schedulers.background import BackgroundScheduler
from utils.rtext import *


def rtext_cmd(txt, msg, cmd):
    return RText(txt).h(msg).c(RAction.run_command, cmd)

#interval time
t_hours = 0
t_minutes = 2
t_seconds = 0
warn_hours = 0
warn_minutes = 0
warn_seconds = 30
show_freq = 15
#degrees
warning_degree = 90
high_degree = 70
medium_degree = 50
#others
restart_countdown = 10
stop_restart = 0
task_start = 0
warn_start = 0
count = 0

plugin = 'cpu_temp'
prefix = '!!temperature'
prefix1 = '!!temp'

systemreturn = '''§b[§rcpu_temp§b] §r'''
warning = systemreturn + '''§cWarning: '''
error = systemreturn + '''§cError: '''
error_used = error + 'The cycle are already stating!'
error_permission = error + 'You have no Permission to use this command'
error_unknown_command = error + '''Unknown command§r
Type ''' +  rtext_cmd('§7!!temp help§r', 'help page', '!!temp help') + ''' for more information'''
help = '''§b-----------§fcpu_temp§b-----------§r
''' + rtext_cmd('!!temperature / !!temp', 'show help message', '!!temp') + ''' §ashow help message§r
''' + rtext_cmd('!!temperature show', 'show temperature detail', '!!temp show') + ''' §ashow detail of cpu temperature§r
''' + rtext_cmd('!!temperature start', 'start loop cpu temperature', '!!temp start') + ''' §astart loop cpu temperature checking§r
''' + rtext_cmd('!!temperature stop', 'stop loop cpu temperature', '!!temp stop') + ''' §astop loop cpu temperature checking§r
''' + rtext_cmd('!!temperature restart', 'restart server', '!!temp restart') +  ''' §arestart server§r
''' + rtext_cmd('!!temperature stoprestart', 'stop restart server', '!!temp stoprestart') +  ''' §astop restarting server§r
§b-----------------------------------§r'''  


class regular_task:
    def __init__(self, server):
        self.cmd_server = server
    

    def warning_temp(self):
        global warn_start
        warn_start = 1
        self.task.remove_job('loop')
        self.task.add_job(
            self.run_warn,
            'interval',
            hours = warn_hours,
            minutes = warn_minutes, 
            seconds = warn_seconds,
            id = 'warn_loop',
            replace_existing = True
        )


    def run_warn(self):
        self.cal_temp(3)


    def warning_temp_stop(self):
        global warn_start
        self.task.remove_job('warn_loop')
        warn_start = 0
        self.task.add_job(
            self.cal_temp,
            'interval',
            hours = t_hours,
            minutes = t_minutes,
            seconds = t_seconds,
            id = 'loop',
            replace_existing = True
           )


    def open_sche(self):
        global count, task_start
        task_start = 1
        count = 0
        self.task = BackgroundScheduler()
        self.task.add_job(
            self.cal_temp,
            'interval',
            hours = t_hours,
            minutes = t_minutes,
            seconds = t_seconds,
            id = 'loop',
            replace_existing = True
           )
        self.start_on()


    def start_on(self):
        self.task.start()


    def print_msg(self, msg, num, info = None):
        if num == 0:
            self.cmd_server.say(msg)
            self.cmd_server.logger.info(msg)
        elif num == 1:
            self.cmd_server.reply(info, msg)
            self.cmd_server.logger.info(msg)


    def cal_temp(self, num = 0, info = None):
        temp = psutil.sensors_temperatures()
        packet = 0
        cnt = 0
        avg = 0
        for i in range(0, len(temp['coretemp'])):
            if temp['coretemp'][i][0].startswith('Package id'):
                if packet == 0:
                    packet = 1
                else:
                    break
            if num == 1:
                self.print_msg(temp['coretemp'][i][0] + ' : ' + temp_color(temp['coretemp'][i][1]), num, info)
            avg = avg + temp['coretemp'][i][1]
            cnt = cnt + 1
        if num == 0 or num == 3:
            global count
            #t = time.localtime()
            #current_time = time.strftime("%H:%M:%S", t)
            #print(current_time)
            #print('count' + str(count) + ' ' + temp_color(round(avg / cnt, 2)) + ' ' + str(temp['coretemp'][0][1]))
            if temp['coretemp'][0][1] > warning_degree:
                if warn_start == 0:
                    self.warning_temp()
                self.print_msg('Average cpu temperature : ' + temp_color(round(avg / cnt, 2)), 0)
                self.print_msg(warning + '§rThe highest core temperature' + ' : ' + temp_color(temp['coretemp'][0][1]) + 
                ' ' + rtext_cmd('§e[▷]§r', 'Click for more information', '!!temp show') + 
                ' ' + rtext_cmd('§c[restart]§r', 'restart server', '!!temp restart'), 0)
                self.cmd_server.say(rtext_cmd('§6====Click to restart server====§r', 'Click to restart server for save', '!!temp restart'))
                self.cmd_server.say(rtext_cmd('§e====Click for more information====§r', 'Click to show temperature details', '!!temp show'))
                if num == 0:
                    if count >= show_freq:
                        count = 0
                    else:
                        count = count + 1
            else:
                if num == 0:
                    if count >= show_freq:
                        self.cmd_server.logger.info('Average cpu temperature : ' + temp_color(round(avg / cnt, 2)))
                        self.cmd_server.logger.info('The highest core temperature' + ' : ' + temp_color(temp['coretemp'][0][1]))
                        count = 0
                    else:
                        count = count + 1
                elif warn_start == 1:
                    self.cmd_server.say('Average cpu temperature : ' + temp_color(round(avg / cnt, 2)))
                    self.cmd_server.say('The highest core temperature' + ' : ' + temp_color(temp['coretemp'][0][1]))
                    self.warning_temp_stop()
        elif num == 1:
            self.print_msg('Average cpu temperature : ' + temp_color(round(avg / cnt, 2)), num, info)
        elif num == 2:
            self.print_msg('Average cpu temperature : ' + temp_color(round(avg / cnt, 2)), 1, info)
            self.print_msg('The highest core temperature' + ' : ' + temp_color(temp['coretemp'][0][1]), 1, info)


    def stop(self):
        global task_start
        task_start = 0
        #self.task.print_jobs()
        self.task.remove_all_jobs()
        self.task.shutdown()
        self.cmd_server.logger.info(systemreturn + 'Cycle stoped')


def permission_check(server, info):
    if info.isPlayer:
        return server.get_permission_level(info.player)
    else:
        return 999


def temp_color(temperatre):
    if temperatre > warning_degree:
        return '§c' + str(temperatre) + '§d°C§r'
    elif temperatre > high_degree:
        return '§6' + str(temperatre) + '§d°C§r'
    elif temperatre > medium_degree:
        return '§e' + str(temperatre) + '§d°C§r'
    else:
        return '§a' + str(temperatre) + '§d°C§r'


def error_msg(server, info, num):
    if num == 0:
        server.tell(info.player, error_used)
    elif num == 1:
        server.tell(info.player, error_permission)
    elif num == 2:
        server.tell(info.player, error_unknown_command)


def restart_server(server):
    global stop_restart
    stop_restart = 0
    for i in range(0, restart_countdown):
        server.logger.info(systemreturn + 'The server will restart after ' + str(restart_countdown - i) +  ' second')
        server.say(systemreturn + 'The server will restart after ' + str(restart_countdown - i) +  ' second ' + rtext_cmd('§c[X]', '§cClick to stop restart', '!!temp stoprestart'))
        time.sleep(1)
        if stop_restart == 1:
            return
    server.restart()


def onServerInfo(server, info):
    global task_start
    if info.content.startswith('!!temp') or info.content.startswith('!!temperature'):
        args = info.content.split(' ')
        if len(args) == 1 or args[1] == 'help':
            server.reply(info, help)
            task.cal_temp(2, info)
        elif len(args) == 2:
            if args[1] == 'show':
                task.cal_temp(1, info)
            elif args[1] == 'restart':
                if permission_check(server, info) > 2:
                    restart_server(server)
                else:
                    error_msg(server, info, 1)
            elif args[1] == 'stoprestart':
                global stop_restart
                stop_restart = 1
                task.print_msg(systemreturn + 'The restart have been stop', 0)
            elif args[1] == 'stop':
                if task_start == 0:
                    server.reply(info, error + 'The cycle have been already stoped')
                else:
                    task.stop()
                    server.say(systemreturn + 'The cycle have been stoped')
            elif args[1] == 'start':
                if task_start == 0:
                    task.cal_temp()
                    task.open_sche()
                    task.print_msg(systemreturn + 'The cycle start now', 1, info)
                else:
                    error_msg(server, info, 0)
            else:
                error_msg(server, info, 2)
        else:
            error_msg(server, info, 2)


def on_load(server, old):
    server.add_help_message('!!temp','Check cpu temperatre.')
    global task, task_start
    task = regular_task(server)
    task.open_sche()
    

def on_unload(server):
    global task_start
    if task_start == 1:
        task.stop()
        task_start = 0


def on_info(server, info):
    info2 = copy.deepcopy(info)
    info2.isPlayer = info2.is_player
    onServerInfo(server, info2) 