# -*- Mode: Python -*-
# vi:si:et:sw=4:sts=4:ts=4

import datetime

def deadline(due):
    now = datetime.datetime.now()
    daystart = datetime.datetime(year=now.year, month=now.month,
        day=now.day)
    dayend = daystart + datetime.timedelta(days=1)

    s = ""
    if not due:
        return s

    left = due - daystart
    if due < daystart:
        days = -left.days
        if days == 1:
            s = "overdue one day"
        else:
            s = "overdue %s days" % days
    elif due < dayend:
        s = "due today"
    else:
        if left.days == 1:
            s = "due tomorrow"
        else:
            s = "%s days left" % left.days

    return s

def ago(when):
    now = datetime.datetime.now()
    daystart = datetime.datetime(year=now.year, month=now.month,
        day=now.day)
    dayend = daystart + datetime.timedelta(days=1)

    past = when - daystart
    if when < daystart:
        days = -past.days
        if days == 1:
            s = "yesterday"
        else:
            s = "%s days ago" % days
    elif when < dayend:
        s = "today"
    else:
        if past.days == 1:
            s = "tomorrow"
        else:
            s = "in %s days" % past.days

    return s

