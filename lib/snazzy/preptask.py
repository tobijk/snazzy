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

from snazzy.error import SnazzyError
from snazzy.task import Task

LOGGER = logging.getLogger(__name__)

class PrepTask(Task):

    def execute(self) -> None:
        self._sanity_check()

        for module in ["handlebars", "jquery", "marked"]:
            self._copy_js_module(module)
    #end function

    def _sanity_check(self) -> None:
        for item in ["package.json", "node_modules"]:
            if not os.path.exists(item):
                raise SnazzyError(
                    "{} not found, did you run snazzy prepare?".format(item)
                )
    #end function

    def _copy_js_module(self, module_name: str) -> None:
        search_paths = [
            os.path.join(
                self._basedir,
                "node_modules",
                module_name,
                "dist",
                "{}.min.js".format(module_name)
            ),
            os.path.join(
                self._basedir,
                "node_modules",
                module_name,
                "{}.min.js".format(module_name)
            )
        ]

        srcfile = None

        for path in search_paths:
            if os.path.exists(path):
                srcfile = path

        if not srcfile:
            raise SnazzyError(
                "cannot find {}, did you run snazzy prepare?"
                .format(module_name)
            )

        destdir = os.path.join(
            self._sitedir, "static", self._prefix, "ext", "js"
        )
        dstfile = os.path.join(
            destdir, "{}.js".format(module_name)
        )

        LOGGER.info(
            "installing {} to /static/ext/js/{}"
            .format(module_name, os.path.basename(dstfile))
        )

        if not os.path.exists(dstfile):
            os.makedirs(destdir, exist_ok=True)
            shutil.copyfile(srcfile, dstfile)
    #end function

#end class
