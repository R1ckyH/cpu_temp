import time
from cpu_temp.temp import TempChecker
from cpu_temp.utils import *

restarting = False
task: TempChecker


@new_thread("restart")
def restart_server(src: InfoCommandSource):
    global restarting
    server = src.get_server()
    if restarting:
        print_msg(error + tr("restarting"), 0, src=src)
        return
    restarting = True
    for i in range(0, restart_countdown):
        restart_msg = SYSTEM_RETURN + tr("restart_msg", str(restart_countdown - i))
        out_log(restart_msg)
        server.say(restart_msg + rtext_cmd("§c[X]", f"{tr('click_msg')} {tr('stop_restart')}", "!!temp stoprestart"))
        time.sleep(1)
        if not restarting:
            return
    restarting = False
    server.restart()


@new_thread("task_process")
def stop_restart(src: InfoCommandSource):
    global restarting
    if restarting:
        print_msg(SYSTEM_RETURN + tr("stop_restart"), 0, src=src)
        restarting = False
    else:
        print_msg(error + tr("already_stop_restart"), 0, src=src)


@new_thread("task_process")
def help_msg(src: InfoCommandSource):
    help_info = '''§b-----------§fChatBridgeReforged_Client§b-----------§r
''' + help_formatter(PREFIX, 'help', tr("help"), tr("help")) + '''
''' + help_formatter(PREFIX, 'show', tr("show"), tr("show")) + '''
''' + help_formatter(PREFIX, 'start', tr("start"), tr("start")) + '''
''' + help_formatter(PREFIX, 'stop', tr("stop"), tr("stop")) + '''
''' + help_formatter(PREFIX, 'restart', tr("restart"), tr("restart")) + '''
''' + help_formatter(PREFIX, 'stoprestart', tr("stop_restart"), tr("stop_restart")) + '''
§b-----------------------------------------------§r'''
    src.reply(help_info)
    task.cal_temp(2, src=src)


@new_thread("task_process")
def start_task(src: InfoCommandSource):
    if not task.task_start:
        task.cal_temp(src=src)
        task.open_schedule()
        print_msg(SYSTEM_RETURN + tr("cycle_start"), 1, info=src.get_info(), src=src)
    else:
        print_msg(error + tr("cycle_already_start"), 1, info=src.get_info(), src=src)


@new_thread("task_process")
def stop_task(src: InfoCommandSource):
    if not task.task_start:
        src.reply(error + tr("cycle_already_stop"))
    else:
        task.stop()
        src.get_server().say(SYSTEM_RETURN + tr("cycle_stop"))


def register_command(server: PluginServerInterface, prefix_use):
    server.register_command(
        Literal(prefix_use).runs(help_msg).
            on_child_error(RequirementNotMet, lambda src: src.reply(error + tr("permission")), handled=True).
            on_child_error(UnknownArgument, lambda src: src.reply(tr("error_unknown_command", help_formatter(PREFIX, "help", "", tr('help')))), handled=True).
            then(
            fox_literal("help").
                runs(help_msg)
        ).then(
            fox_literal("show").
                runs(lambda src: task.cal_temp(1, src))
        ).then(
            fox_literal("restart").
                runs(restart_server)
        ).then(
            fox_literal("stoprestart").
                runs(stop_restart)
        ).then(
            fox_literal("start").
                runs(lambda src: start_task(src))
        ).then(
            fox_literal("stop").
                runs(lambda src: stop_task(src))
        )
    )


def on_load(server: PluginServerInterface, old):
    global task
    if old is not None and hasattr(old, 'task'):
        if old.task.task_start:
            old.task.stop()
    server.register_help_message("!!temp", tr('click_msg'))
    task = TempChecker(server)
    if temp_loop:
        task.open_schedule()
    register_command(server, PREFIX)
    register_command(server, PREFIX1)


def on_unload(server: ServerInterface):
    if task.task_start:
        task.stop()
        task.task_start = False
