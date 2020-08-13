# -*- coding: utf-8 -*-
import psutil
import copy
import daytime
import time
from apscheduler.schedulers.background import BackgroundScheduler
from utils.rtext import *


def rtext_cmd(txt, msg, cmd):
    return RText(txt).h(msg).c(RAction.run_command, cmd)

#循环时间
t_hours = 0
t_minutes = 2
t_seconds = 0
warn_hours = 0
warn_minutes = 0
warn_seconds = 30
show_freq = 15
#预警温度
warning_degree = 90
high_degree = 70
medium_degree = 50
#其他
restart_countdown = 10
#不要动
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
error_used = error + '循环早就开始了!'
error_permission = error + '你没有权限使用此指令'
error_unknown_command = error + '''未知指令§r
Type ''' +  rtext_cmd('§7!!temp help§r', '帮助页面', '!!temp help') + ''' 获取更多资讯'''
help = '''§b-----------§fcpu_temp§b-----------§r
''' + rtext_cmd('!!temperature / !!temp', '显示帮助信息', '!!temp') + ''' §a显示帮助信息§r
''' + rtext_cmd('!!temperature show', '显示温度详情', '!!temp show') + ''' §a显示cpu温度的详情§r
''' + rtext_cmd('!!temperature start', '启动预警循环', '!!temp start') + ''' §a启动温度预警循环§r
''' + rtext_cmd('!!temperature stop', '停止预警循环', '!!temp stop') + ''' §a停止温度预警循环§r
''' + rtext_cmd('!!temperature restart', '重启', '!!temp restart') +  ''' §a重启服务器§r
''' + rtext_cmd('!!temperature stoprestart', '中止重启', '!!temp stoprestart') +  ''' §a中止重启服务器§r
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
                self.print_msg('平均cpu温度 : ' + temp_color(round(avg / cnt, 2)), 0)
                self.print_msg(warning + '§rcpu单核心最高温度' + ' : ' + temp_color(temp['coretemp'][0][1]) + 
                ' ' + rtext_cmd('§e[▷]§r', '点击获得更多资讯', '!!temp show') + 
                ' ' + rtext_cmd('§c[重启]§r', '重启服务器', '!!temp restart'), 0)
                self.cmd_server.say(rtext_cmd('§6====点击重启服务器====§r', '点击重启服务器', '!!temp restart'))
                self.cmd_server.say(rtext_cmd('§e====点击获取更多资讯====§r', '点击获取资讯详情', '!!temp show'))
                if num == 0:
                    if count >= show_freq:
                        count = 0
                    else:
                        count = count + 1
            else:
                if num == 0:
                    if count >= show_freq:
                        self.cmd_server.logger.info('平均cpu温度 : ' + temp_color(round(avg / cnt, 2)))
                        self.cmd_server.logger.info('cpu单核心最高温度' + ' : ' + temp_color(temp['coretemp'][0][1]))
                        count = 0
                    else:
                        count = count + 1
                elif warn_start == 1:
                    self.print_msg('平均cpu温度 : ' + temp_color(round(avg / cnt, 2)), 0)
                    self.print_msg('cpu单核心最高温度' + ' : ' + temp_color(temp['coretemp'][0][1]), 0)
                    self.warning_temp_stop()
        elif num == 1:
            self.print_msg('平均cpu温度 : ' + temp_color(round(avg / cnt, 2)), num, info)
        elif num == 2:
            self.print_msg('平均cpu温度 : ' + temp_color(round(avg / cnt, 2)), 1, info)
            self.print_msg('cpu单核心最高温度' + ' : ' + temp_color(temp['coretemp'][0][1]), 1, info)


    def stop(self):
        global task_start
        task_start = 0
        #self.task.print_jobs()
        self.task.remove_all_jobs()
        self.task.shutdown()
        self.cmd_server.logger.info(systemreturn + '循环停止')


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
        server.logger.info(systemreturn + '服务器会在' + str(restart_countdown - i) +  '秒后重启')
        server.say(systemreturn + '服务器会在' + str(restart_countdown - i) +  '秒后重启 ' + rtext_cmd('§c[X]', '§cClick to stop restart', '!!temp stoprestart'))
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
                task.print_msg(systemreturn + '重启已经被中止', 0)
            elif args[1] == 'stop':
                if task_start == 0:
                    server.reply(info, error + '循环早就停止了！')
                else:
                    task.stop()
                    server.say(systemreturn + '循环已经停止')
            elif args[1] == 'start':
                if task_start == 0:
                    task.cal_temp()
                    task.open_sche()
                    task.print_msg(systemreturn + '循环开始了', 1, info)
                else:
                    error_msg(server, info, 0)
            else:
                error_msg(server, info, 2)
        else:
            error_msg(server, info, 2)


def on_load(server, old):
    server.add_help_message('!!temp','服务器温度警报插件.')
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