# -*- Mode: Python -*-
# vi:si:et:sw=4:sts=4:ts=4

from mushin.common import log

import datetime

# Colorization
COLOR_CODES = ( { 'none': "",
                  'default': "\033[0m",
                  # primary colors
                  'black': "\033[0;30m",
                  'grey': "\033[0;37m",
                  'red': "\033[0;31m",
                  'green': "\033[0;32m",
                  'blue': "\033[0;34m",
                  'purple': "\033[0;35m",
                  'cyan': "\033[0;36m",
                  'yellow': "\033[0;33m",
                  # bold colors
                  'white': "\033[1;37m",
                  'dark_grey': "\033[1;30m",
                  'dark_red': "\033[1;31m",
                  'dark_green': "\033[1;32m",
                  'dark_blue': "\033[1;34m",
                  'dark_purple': "\033[1;35m",
                  'dark_cyan': "\033[1;36m",
                  'dark_yellow': "\033[1;33m",
                  # other colors                  
                  'normal': "\x1b[0;37;40m",
                  'title': "\x1b[1;32;40m",
                  'heading': "\x1b[1;35;40m",
                  'bold': "\x1b[1;35;40m",
                  'important': "\x1b[1;31;40m",
                  'error': "\x1b[1;31;40m",
                  'reverse': "\x1b[0;7m",
                  'row0': "\x1b[0;35;40m",
                  'row1': "\x1b[0;36;40m" } )

# Default colors
DEFAULT_COLOR    = COLOR_CODES['default']
CONTEXT_COLOR    = COLOR_CODES['dark_yellow']
PROJECT_COLOR    = COLOR_CODES['dark_purple']
STATUS_COLOR     = COLOR_CODES['dark_green']
REFERENCE_COLOR  = COLOR_CODES['dark_blue']
URGENCY_COLOR    = COLOR_CODES['red']
IMPORTANCE_COLOR = COLOR_CODES['red']
COMPLETE_COLOR   = COLOR_CODES['white']
TIME_COLOR       = COLOR_CODES['cyan']
RECURRENCE_COLOR = COLOR_CODES['cyan']
START_COLOR      = COLOR_CODES['red']
DUE_COLOR        = COLOR_CODES['red']
END_COLOR        = COLOR_CODES['green']

# priority colors; from 0 to 5
P_COLORS = [
  COLOR_CODES['dark_green'],
  COLOR_CODES['yellow'],
  COLOR_CODES['dark_yellow'],
  COLOR_CODES['red'],
  COLOR_CODES['dark_red'],
  COLOR_CODES['dark_purple'],
]

def _get_deadline_string(due):
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
            s = "[overdue one day]"
        else:
            s = "[overdue %s days]" % days
    elif due < dayend:
        s = "[due today]"
    else:
        if left.days == 1:
            s = "[one day left]"
        else:
            s = "[%s days left]" % left.days

    return s

class Displayer(object):
    def __init__(self, colored=True):
        self._colored = colored

    def _color(self, text, code):
        if not self._colored:
            return text

        return code + text + DEFAULT_COLOR

    def project(self, text):
        return self._color('p:%s' % text, PROJECT_COLOR)

    def priority(self, text, priority):
        # color according to priority
        if not self._colored:
            return text

        return P_COLORS[int(priority)] + text + DEFAULT_COLOR

    def shortid(self, s):
        return self._color('%s' % s, TIME_COLOR)

    def display(self, thing, shortid=True, due=False):
        """
        Return a string for the given thing.

        @param shortid: if True, also show shortid and priority.
        @param colored: if True, color the return value for output.
        @param due:     whether to show additional due info.
        """
        blocks = []

        if shortid:
            blocks.append(self.shortid(thing.shortid()))
            blocks.append(self.priority(
                '(%.2f)' % thing.priority(), thing.priority()))

        blocks.append(thing.title)

        if thing.contexts:
            blocks.extend([self._color('@%s' % c, CONTEXT_COLOR)
                for c in thing.contexts]) 
        if thing.projects:
            blocks.extend([self.project(p) for p in thing.projects]) 
        if thing.statuses:
            blocks.extend([self._color('!%s' % s, STATUS_COLOR)
                 for s in thing.statuses]) 

        if thing.urgency is not None:
            blocks.append(self._color('U:%d', URGENCY_COLOR) % thing.urgency)
        if thing.importance is not None:
            blocks.append(self._color(
                'I:%d', IMPORTANCE_COLOR) % thing.importance)

        # FIXME: format with H/M/S/...
        def _format_time(seconds):
            minute = 60
            hour = minute * 60
            day = hour * 24
            week = day * 7

            if seconds % week == 0:
                return '%dW' % (seconds / week)
            elif seconds % day == 0:
                return '%dD' % (seconds / day)
            elif seconds % hour == 0:
                return '%dH' % (seconds / hour)
            else:
                return '%dM' % (seconds / minute)

        if thing.time is not None:
            blocks.append(self._color(
                'T:%s' % _format_time(thing.time), TIME_COLOR))
        if thing.recurrence is not None:
            blocks.append(self._color(
                'R:%s' % _format_time(thing.recurrence), RECURRENCE_COLOR))

        if thing.start is not None:
            blocks.append(self._color(
                'S:%s' % thing.start.strftime('%Y-%m-%d'), START_COLOR))
        if thing.due is not None:
            blocks.append(self._color(
                'D:%s' % thing.due.strftime('%Y-%m-%d'), DUE_COLOR))
        if thing.end is not None:
            blocks.append(self._color(
                'E:%s' % thing.end.strftime('%Y-%m-%d'), END_COLOR))

        if thing.complete:
            blocks.append(self._color('C:%s' % thing.complete, COMPLETE_COLOR))

        if due and thing.due:
            blocks.append(_get_deadline_string(thing.due))


        return " ".join(blocks)

    def display_things(self, result, due=False):
        count = 0

        for thing in result:
            print self.display(thing, due=due)
            count += 1

        print '%d open things' % count

# compat method; should be removed
def display(thing, shortid=True, due=False, colored=True):
    displayer = Displayer(colored=colored)
    return displayer.display(thing, shortid, due)
