# -*- encoding: utf-8 -*-
#
# The MIT License (MIT)
#
# Copyright (c) 2024 Tobias Koch <tobias.koch@gmail.com>
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

import logging
import os
import shutil

from snazzy.task import Task

LOGGER = logging.getLogger(__name__)

class CopyFiles(Task):

    def execute(self) -> None:
        for entry in self._objects:
            LOGGER.info("processing {}".format(entry))
            self._process_entry(entry)

    def _process_entry(self, entry: str) -> None:
        srcfile = os.path.normpath(
            os.sep.join([self._basedir, entry])
        )

        destdir = os.path.normpath(
            os.sep.join([self._sitedir, os.path.dirname(entry)])
        )

        os.makedirs(destdir, exist_ok=True)

        if entry.endswith(".scss"):
            dstfile = os.path.normpath(
                os.sep.join([self._sitedir, entry[:-4] + "css"])
            )
            self._convert_scss(srcfile, dstfile)

        elif entry.endswith(".js"):
            dstfile = os.path.normpath(
                os.sep.join([self._sitedir, entry])
            )
            self._convert_js(srcfile, dstfile)

        else:
            shutil.copy2(srcfile, destdir)
    #end function

#end class
