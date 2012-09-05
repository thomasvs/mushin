# -*- Mode: Python -*-
# vi:si:et:sw=4:sts=4:ts=4

# Morituri - for those about to RIP

# Copyright (C) 2009 Thomas Vander Stichele

# This file is part of morituri.
# 
# morituri is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# morituri is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with morituri.  If not, see <http://www.gnu.org/licenses/>.

"""
Logging Command.
"""

from mushin.extern.command import command
from mushin.common import log

class LogCommand(command.Command, log.Loggable):
    def __init__(self, parentCommand=None, **kwargs):
        command.Command.__init__(self, parentCommand, **kwargs)
        self.logCategory = self.name

    def _doLog(self, level, format, *args):
        kwargs = {}
        log.Loggable.doLog(self, level, -4, format, *args, **kwargs)

    # command.Command has a fake debug method, so choose the right one
    def debug(self, format, *args):
        self._doLog(log.DEBUG, format, *args)

    def info(self, format, *args):
        self._doLog(log.INFO, format, *args)

    def warning(self, format, *args):
        self._doLog(log.WARN, format, *args)
