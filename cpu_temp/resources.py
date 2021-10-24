from apscheduler.triggers.interval import IntervalTrigger


permission = {
    "help": 1,
    "show": 1,
    "start": 2,
    "stop": 2,
    "restart": 2,
    "stoprestart": 1,
}

# loop or not
temp_loop = True
# interval time
t_hours = 0
t_minutes = 2
t_seconds = 0
show_freq = 30  # 0 is show without hide
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
show_msg = True
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

plugin = "cpu_temp"
PREFIX = "!!temperature"
PREFIX1 = "!!temp"
SYSTEM_RETURN = f"""§b[§r{plugin}§b] §r"""
warning = SYSTEM_RETURN + """§cWarning: """
error = SYSTEM_RETURN + """§cError: """
