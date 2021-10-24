from datetime import datetime

from mcdreforged.api.all import *

from cpu_temp.resources import *


def tr(key, *args) -> str:
    return ServerInterface.get_instance().tr(f"{plugin}.{key}", *args)


def help_formatter(mcdr_prefix, command, first_msg, click_msg, use_command=None):
    if use_command is None:
        use_command = command
    msg = f'{mcdr_prefix} {command} §a{first_msg}§r'
    return rtext_cmd(msg, f'{tr("click_msg")} {click_msg}', f'{mcdr_prefix} {use_command}')


def rtext_cmd(txt, msg, cmd):
    return RText(txt).h(msg).c(RAction.run_command, cmd)


def fox_literal(msg):
    return Literal(msg).requires(lambda src: permission_check(src, msg))


def print_msg(msg, num, info: Info = None, src: InfoCommandSource = None, server: ServerInterface = None):
    if src is not None:
        server = src.get_server()
        info = src.get_info()
    if num == 0:
        server.say(msg)
        out_log(msg)
    elif num == 1:
        server.reply(info, msg)
        out_log(msg)


def permission_check(src: CommandSource, cmd):
    if src.get_permission_level() >= permission[cmd]:
        return True
    else:
        return False


def out_log(msg: str):
    for i in range(6):
        msg = msg.replace('§' + str(i), '').replace('§' + chr(97 + i), '')
    msg = msg.replace('§6', '').replace('§7', '').replace('§8', '').replace('§9', '').replace('§r', '')
    with open("logs/cpu_temp.log", "a+") as log:
        log.write(datetime.now().strftime("[%Y-%m-%d %H:%M:%S]") + msg + "\n")
    print("[server] " + datetime.now().strftime("[%H:%M:%S]") + " [cpu_temp] " + msg)


def temp_color(temperature):
    tmp = str(temperature) + "§d°C§r"
    if temperature > warning_degree:
        return "§c" + tmp
    elif temperature > high_degree:
        return "§6" + tmp
    elif temperature > medium_degree:
        return "§e" + tmp
    else:
        return "§a" + tmp
