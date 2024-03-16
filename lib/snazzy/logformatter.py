# -*- encoding: utf-8 -*-
#
# The MIT License (MIT)
#
# Copyright (c) 2019 Tobias Koch <tobias.koch@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

import sys
import logging

from boltlinux.error import BoltValueError

class LogFormatter(logging.Formatter):

    ESC_BLUE   = '\033[34m'
    ESC_YELLOW = '\033[33m'
    ESC_GREEN  = '\033[32m'
    ESC_RED    = '\033[31m'
    ESC_BOLD   = '\033[1m'
    ESC_ENDC   = '\033[0m'

    def __init__(self, app_name):
        self._app_name = app_name
        self._stdout_isatty = sys.stdout.isatty()

    def set_app_name(self, app_name):
        self._app_name = app_name

    def format(self, record):
        if self._stdout_isatty:
            template = "{ebold_}{appname}{eendc_}: "\
                       "{ebold_}{elevl_}{levelname}{eendc_}: {message}"
        else:
            template = "{appname}: {levelname}: {message}"

        level_to_eascii = {
            logging.DEBUG: self.ESC_BLUE,
            logging.INFO: self.ESC_GREEN,
            logging.WARNING: self.ESC_YELLOW,
            logging.ERROR: self.ESC_RED,
            logging.CRITICAL: self.ESC_RED
        }

        message = template.format(
            ebold_=self.ESC_BOLD,
            eendc_=self.ESC_ENDC,
            elevl_=level_to_eascii[record.levelno],
            appname=self._app_name,
            levelname=record.levelname.lower(),
            message=record.getMessage()
        )

        return message
    #end function

    @staticmethod
    def configure(logger, style, app_name):
        if style not in ["cli", "plain"]:
            raise BoltValueError(
                'invalid logging style "{}".'.format(style)
            )

        logger.handlers.clear()
        handler = logging.StreamHandler()

        if style == "cli":
            handler.setFormatter(LogFormatter(app_name))

        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    #end function

#end class
