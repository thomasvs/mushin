# To-do list manager.
# Copyright (C) 2006-2008 MiKael NAVARRO
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

import re
import datetime

# Regexps for parsing a task line
CONTEXT_CHAR   = "@"
PROJECT_CHAR   = "p:"
STATUS_CHAR    = "!"
REFERENCE_CHAR = "ref:"
URGENCY_CHAR    = "U:"
IMPORTANCE_CHAR = "I:"
COMPLETE_CHAR   = "C:"
TIME_CHAR       = "T:"
RECURRENCE_CHAR = "R:"
START_CHAR      = "S:"
DUE_CHAR        = "D:"
END_CHAR        = "E:"

WORD_MATCH      = r"([_\w-]+)"
DIGIT_MATCH     = r"([1-5])"
NUMBER_MATCH    = r"(\d+)"
TIMEDELTA_MATCH = r"(\d+)([WDHM])"
DATE_MATCH      = r"(\d\d\d\d-\d\d-\d\d)"

CONTEXT_REGEXP   = re.compile(CONTEXT_CHAR + WORD_MATCH, re.IGNORECASE)
PROJECT_REGEXP   = re.compile(PROJECT_CHAR + WORD_MATCH, re.IGNORECASE)
STATUS_REGEXP    = re.compile(STATUS_CHAR + WORD_MATCH, re.IGNORECASE)
REFERENCE_REGEXP = re.compile(REFERENCE_CHAR + WORD_MATCH, re.IGNORECASE)
URGENCY_REGEXP   = re.compile(URGENCY_CHAR + DIGIT_MATCH, re.IGNORECASE)
IMPORTANCE_REGEXP = re.compile(IMPORTANCE_CHAR + DIGIT_MATCH, re.IGNORECASE)
COMPLETE_REGEXP   = re.compile(COMPLETE_CHAR + NUMBER_MATCH, re.IGNORECASE)
TIME_REGEXP       = re.compile(TIME_CHAR + TIMEDELTA_MATCH, re.IGNORECASE)
RECURRENCE_REGEXP = re.compile(RECURRENCE_CHAR + TIMEDELTA_MATCH, re.IGNORECASE)
START_REGEXP      = re.compile(START_CHAR + DATE_MATCH, re.IGNORECASE)
DUE_REGEXP        = re.compile(DUE_CHAR + DATE_MATCH, re.IGNORECASE)
END_REGEXP        = re.compile(END_CHAR + DATE_MATCH, re.IGNORECASE)


def pluralize(word):
    """
    Pluralize the given word.  Used to set the proper attribute on the dict.
    """
    if word[-1] == 's':
        return word + 'es'

    return word + 's'

def parse(line):
    """Return a dictionary (task mapping) from 'line' parsing."""

    t = {}  # Task mapping
    title = line  # the 'title' extracted from line

    # Parse for GTD attributes
    for attr in ['context', 'project', 'status', 'reference']:
        title = eval(attr.upper() + '_REGEXP').sub('', title)

        matches = eval(attr.upper() + '_REGEXP').findall(line)
        if matches:
            t[pluralize(attr)] = matches

    # Parse additional properties
    for attr in ['urgency', 'importance', 'complete']:
        title = eval(attr.upper() + '_REGEXP').sub('', title)

        matches = eval(attr.upper() + '_REGEXP').findall(line)
        if matches:
            t[attr] = int(matches[-1])  # keep only last!

    # Parse timedelta
    for attr in ['time', 'recurrence']:
        title = eval(attr.upper() + '_REGEXP').sub('', title)

        matches = eval(attr.upper() + '_REGEXP').findall(line)
        if matches:
            match = matches[-1]  # keep only last!
            hours = minutes = 0  # compute hours

            if attr == 'time':  # compute time requiered (in working hours)
                if match[1].upper() == 'W':  # weeks
                    hours = int(match[0]) * gtd.WEEK_IN_HOURS
                elif match[1].upper() == 'D':  # days
                    hours = int(match[0]) * gtd.DAY_IN_HOURS
                elif match[1].upper() == 'H':  # hours
                    hours = int(match[0])
                elif match[1].upper() == 'M':  # minutes
                    minutes = int(match[0])
                else:
                    pass  # invalid time range indicator
                
            elif attr == 'recurrence':  # compute full hours
                if match[1].upper() == 'W':  # weeks
                    hours = int(match[0]) * 7 * 24
                elif match[1].upper() == 'D':  # days
                    hours = int(match[0]) * 24
                elif match[1].upper() == 'H':  # hours
                    hours = int(match[0])
                elif match[1].upper() == 'M':  # minutes
                    minutes = int(match[0])
                else:
                    pass  # invalid time range indicator

            t[attr] = hours * 60 * 60 + minutes * 60
            # before: datetime.timedelta(hours=hours, minutes=minutes)
    
    # Parse dates
    for attr in ['start', 'due', 'end']:
        title = eval(attr.upper() + '_REGEXP').sub('', title)

        matches = eval(attr.upper() + '_REGEXP').findall(line)
        if matches:
            year, month, day = matches[-1].split('-')  # keep only last!
            t[attr] = datetime.datetime(int(year), int(month), int(day))

    # Post-processing
    if t.has_key('end') or t.has_key('reference'):  # ignore completed and archived tasks
        t['complete'] = 100
        
    # Set the title
    t['title'] = " ".join(title.split())  # remove useless blank chars too
    
    return t
