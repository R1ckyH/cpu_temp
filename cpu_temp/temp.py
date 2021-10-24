# -*- coding: utf-8 -*-
import psutil

from apscheduler.schedulers.background import BackgroundScheduler

from cpu_temp.utils import *


class TempChecker:
    def __init__(self, server: ServerInterface):
        self.task = BackgroundScheduler()
        self.cmd_server = server
        self.warn_start = False
        self.task_start = False
        self.count = 0
        self.show_msg = False
        self.now_time = 0

    def warning_temp(self):
        self.warn_start = True
        self.task.remove_job("loop")
        self.add_task(1)

    def add_task(self, num):
        if num == 0:
            use_trigger = norm_trigger
            loop_id = "loop"
        else:
            use_trigger = warn_trigger
            loop_id = "warn_loop"
        self.task.add_job(
            self.cal_temp,
            trigger=use_trigger,
            id=loop_id,
            replace_existing=True
        )

    def run_warn(self):
        self.cal_temp(3)

    def warning_temp_stop(self):
        self.task.remove_job("warn_loop")
        self.warn_start = False
        self.add_task(0)

    def open_schedule(self):
        self.count = 0
        self.task = BackgroundScheduler()
        self.add_task(0)
        self.start_on()

    def start_on(self):
        self.task_start = True
        self.task.start()

    def avg_temp(self, num, temp, src: CommandSource = None):
        packet = 0
        cnt = 0
        avg = 0
        if int(datetime.now().strftime("%Y%m%d%H%M%S")) - self.now_time > 60:
            self.show_msg = True
            self.now_time = int(datetime.now().strftime("%Y%m%d%H%M%S"))
        else:
            self.show_msg = False
        if "k10temp" in temp:
            for i in range(0, len(temp["k10temp"])):
                if num == 1:
                    if self.show_msg:
                        print_msg(temp["k10temp"][i][0] + " : " + temp_color(temp["k10temp"][i][1]), num, src=src)
                    else:
                        src.reply(temp["k10temp"][i][0] + " : " + temp_color(temp["k10temp"][i][1]))
                avg = avg + temp["k10temp"][i][1]
                cnt = cnt + 1
            return avg / cnt

        for i in range(0, len(temp["coretemp"])):
            if temp["coretemp"][i][0].startswith("Package id"):
                if packet == 0:
                    packet = 1
                else:
                    break
            if num == 1:
                if show_msg:
                    print_msg(temp["coretemp"][i][0] + " : " + temp_color(temp["coretemp"][i][1]), num, src=src)
                else:
                    src.reply(temp["coretemp"][i][0] + " : " + temp_color(temp["coretemp"][i][1]))
            avg = avg + temp["coretemp"][i][1]
            cnt = cnt + 1
        return avg / cnt

    def cal_temp(self, num=0, src: CommandSource = None):
        temp = psutil.sensors_temperatures()
        try:
            avg_temp = self.avg_temp(num, temp, src)
        except KeyError:
            if src is not None:
                src.reply(error + tr("error_temperature"))
            return
        temp_msg = tr("average_temp") + temp_color(round(avg_temp, 2))
        if "k10temp" in temp:
            tempe = temp["k10temp"][0][1]
        else:
            tempe = temp["coretemp"][0][1]
        high_temp_msg = tr("highest_temp") + temp_color(tempe)
        if num == 0:
            if self.count >= show_freq:
                out_log(temp_msg)
                out_log(high_temp_msg)
                self.count = 0
            else:
                self.count += 1
        elif num != 3:
            if show_msg:
                print_msg(temp_msg, 1, src=src)
                print_msg(high_temp_msg, 1, src=src)
            else:
                src.reply(temp_msg)
                src.reply(high_temp_msg)
        if num == 0 or num == 3:
            if "k10temp" in temp:
                tempe = temp["k10temp"][0][1]
            else:
                tempe = temp["coretemp"][0][1]
            if tempe > warning_degree:
                if not self.warn_start:
                    self.warning_temp()
                print_msg(
                    temp_msg + "\n" +
                    high_temp_msg +
                    rtext_cmd(" §e[❗]§r", f"{tr('click_msg')} {tr('info')}", "!!temp show") +
                    rtext_cmd(f"§c [{tr('restart_raw')}]§r", f"{tr('click_msg')} {tr('restart')}", "!!temp restart") +
                    rtext_cmd(f"§6===={tr('click_msg')} {tr('restart')}====§r", f"{tr('click_msg')} {tr('restart')}",
                              "!!temp restart") +
                    rtext_cmd(f"§e===={tr('click_msg')} {tr('info')}====§r", f"{tr('click_msg')} {tr('information')}",
                              "!!temp show"),
                    0, src=src, server=self.cmd_server
                )
            else:
                if self.warn_start:
                    print_msg(temp_msg, 0, src=src, server=self.cmd_server)
                    print_msg(high_temp_msg, 0, src=src, server=self.cmd_server)
                    self.warning_temp_stop()

    def stop(self):
        self.task_start = False
        self.task.remove_all_jobs()
        self.task.shutdown()
        out_log(SYSTEM_RETURN + tr("cycle_stop"))
