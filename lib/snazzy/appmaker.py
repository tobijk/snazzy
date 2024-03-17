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
import tempfile

from snazzy.task import Task

LOGGER = logging.getLogger(__name__)

class AppMaker(Task):

    def execute(self):
        for entry in self._objects:
            LOGGER.info("building SPA at {}".format(os.path.dirname(entry)))
            self._generate_app(entry)
    #end function

    def _generate_app(self, entry):
        srcfile = os.path.normpath(
            os.sep.join([self._basedir, entry])
        )

        destdir = os.path.normpath(
            os.sep.join([self._sitedir, os.path.dirname(entry)])
        )

        os.makedirs(destdir, exist_ok=True)

        dstfile = os.path.normpath(
            os.sep.join([self._sitedir, entry])
        )

        self._process_html(srcfile, dstfile)

        appdir = os.path.join(os.path.dirname(srcfile), "+app")
        appjs  = os.path.join(os.path.dirname(srcfile), "+app.js")

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpjs  = os.path.join(tmpdir, "app.js")
            tmpcss = os.path.join(tmpdir, "app.css")

            for dirpath, dirnames, filenames in os.walk(appdir):
                for entry in filenames:
                    if not entry.endswith(".xml"):
                        continue

                    template, script, stylesheet = \
                        self._process_component_xml(
                            os.path.join(dirpath, entry)
                        )

                    with open(tmpjs, "a+", encoding="utf-8") as f:
                        f.write(template)
                        f.write(script)

                    with open(tmpcss, "a+", encoding="utf-8") as f:
                        f.write(stylesheet)
                #end for
            #end for

            with open(appjs, "r", encoding="utf-8") as f:
                script = self._convert_js_in_memory(f.read())

            with open(tmpjs, "a+", encoding="utf-8") as f:
                f.write(script)

            appjs  = os.path.join(os.path.dirname(dstfile), "app.js")
            appcss = os.path.join(os.path.dirname(dstfile), "app.css")

            os.rename(tmpjs,  appjs)
            os.rename(tmpcss, appcss)
        #end with
    #end function

#end class
