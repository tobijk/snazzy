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

import os
import shutil
import subprocess

class Task:

    def __init__(self, basedir: str, sitedir: str, debug: bool = False):
        self._basedir = basedir
        self._sitedir = sitedir
        self._debug   = debug
        self._objects = []
    #end function

    def add_object(self, entry: str) -> None:
        self._objects.append(entry)

    def execute(self) -> None:
        raise NotImplementedError(
            "{} has no execute method".format(self.__class__.__name__)
        )

    def _convert_scss(self, srcfile: str, dstfile: str) -> None:
        cmd = [
            "node_modules/.bin/sass",
                "-I", os.path.dirname(srcfile),
                    "-s", "expanded" if self._debug else "compressed",
                        "--no-source-map",
                            srcfile, dstfile
        ]

        subprocess.run(cmd)
    #end function

    def _convert_js(self, srcfile: str, dstfile: str) -> None:
        if self._debug:
            shutil.copyfile(srcfile, dstfile)
            return

        cmd = [
            "./node_modules/.bin/babel",
                "--minified", "-o", dstfile, srcfile
        ]

        subprocess.run(cmd)
    #end function

    def _convert_js_in_memory(self, srcfile: str) -> str:
        with open(srcfile, "r", encoding="utf-8") as f:
            ibuf = f.read()

        if self._debug:
            return ibuf

        cmd = [
            "./node_modules/.bin/babel",
                "--minified", "--filename", "app.js"
        ]

        result = subprocess.run(
            cmd, input=ibuf, stdout=subprocess.PIPE, universal_newlines=True
        )

        return result.stdout
    #end function

#end class
