import logging
import sys

weekdays = "Mon Tue Wed Thu Fri Sat Sun".split(" ")

def time_num(t):
    if ":" in t:
        h, m = t.split(":")
        return int(h) * 60 + int(m)
    else:
        return int(t) * 60

def games_allowed(schedule, when):
        t = when.timetuple()
        h, m, dow = t[3], t[4], t[6]
        dows = weekdays[dow]
        tm = h * 60 + m
        for row in schedule:
            if dows in row:
                times = row[dows]
                start, end = [time_num(x) for x in times.split("-")]
                if start <= tm < end:
                    return True
        return False

