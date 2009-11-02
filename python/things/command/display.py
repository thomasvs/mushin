# -*- Mode: Python -*-
# vi:si:et:sw=4:sts=4:ts=4

from things.common import log

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


def display(thing, shortid=True, colored=True, due=False):
    """
    Return a string for the given thing.

    @param shortid: if True, also show shortid and priority.
    @param colored: if True, color the return value for output.
    @param due:     whether to show additional due info.
    """
    def color(text, code):
        if not colored:
            return text

        return code + text + DEFAULT_COLOR

    def pcolor(text, priority):
        # color according to priority
        if not colored:
            return text

        return P_COLORS[int(priority)] + text + DEFAULT_COLOR

    blocks = []

    if shortid:
        blocks.append(color('%s' % thing.shortid(), TIME_COLOR))
        blocks.append(pcolor('(%.2f)' % thing.priority(), thing.priority()))

    blocks.append(thing.title)

    if thing.contexts:
        blocks.extend([color('@%s' % c, CONTEXT_COLOR)
            for c in thing.contexts]) 
    if thing.projects:
        blocks.extend([color('p:%s' % p, PROJECT_COLOR)
            for p in thing.projects]) 
    if thing.statuses:
        blocks.extend([color('!%s' % s, STATUS_COLOR)
             for s in thing.statuses]) 

    if thing.urgency is not None:
        blocks.append(color('U:%d', URGENCY_COLOR) % thing.urgency)
    if thing.importance is not None:
        blocks.append(color('I:%d', IMPORTANCE_COLOR) % thing.importance)

    # FIXME: format with H/M/S/...
    def _format_time(seconds):
        week = 60 * 60 * 24 * 7
        weeks = seconds / week
        seconds %= week

        day = 60 * 60 * 24
        days = seconds / day
        seconds %= day

        hour = 60 * 60
        hours = seconds / hour
        seconds %= hour

        minute = 60
        minutes = seconds / minute
        seconds %= minute

        blocks = []
        if weeks:
            blocks.append('%dW' % weeks)
        if days:
            blocks.append('%dD' % days)
        if hours:
            blocks.append('%dH' % hours)
        if minutes:
            blocks.append('%dM' % minutes)

        return "".join(blocks)

    if thing.time is not None:
        blocks.append(color(
            'T:%s' % _format_time(thing.time), TIME_COLOR))
    if thing.recurrence is not None:
        blocks.append(color(
            'R:%s' % _format_time(thing.recurrence), RECURRENCE_COLOR))

    if thing.start is not None:
        blocks.append(color(
            'S:%s' % thing.start.strftime('%Y-%m-%d'), START_COLOR))
    if thing.due is not None:
        blocks.append(color(
            'D:%s' % thing.due.strftime('%Y-%m-%d'), DUE_COLOR))
    if thing.end is not None:
        blocks.append(color(
            'E:%s' % thing.due.strftime('%Y-%m-%d'), END_COLOR))

    if thing.complete:
        blocks.append(color('C:%s' % thing.complete, COMPLETE_COLOR))

    if due and thing.due:
        blocks.append(_get_deadline_string(thing.due))


    return " ".join(blocks)

def display_things(result, due=False):
    count = 0

    for thing in result:
        print display(thing, due=due)
        count += 1

    print '%d open things' % count

def lookup(server, shortid):
        # convert argument, which is shortened _id, to start/end range
        startkey = shortid
        endkey = hex(int(startkey, 16) + 1)[2:]
        # leading 0's are now dropped, so readd them
        endkey = '0' * (len(startkey) - len(endkey)) + endkey

        log.debug('lookup', 'Looking up from %s to %s' % (startkey, endkey))

        # FIXME: make the view calculate and sort by priority
        things = list(server.view('things-by-id',
            startkey=startkey, endkey=endkey))
        if len(things) == 0:
            print "No thing found."
        elif len(things) > 1:
            for t in things:
                print display.display(t)
            print "%d things found, please be more specific." % len(things)
        else:
            return things[0]


