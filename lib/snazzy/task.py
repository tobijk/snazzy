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
import sys

class Task:

    def __init__(self, basedir: str, sitedir: str,
            debug: bool = False, static_prefix: str = ""):
        self._basedir = basedir
        self._sitedir = sitedir
        self._debug   = debug
        self._prefix  = static_prefix
        self._objects = []
    #end function

    def add_object(self, entry: str) -> None:
        self._objects.append(entry)

    def execute(self) -> None:
        raise NotImplementedError(
            "{} has no execute method".format(self.__class__.__name__)
        )

    def _convert_scss(self, srcfile: str, dstfile: str) -> None:
        with open(srcfile, "r") as f:
            scss = f.read()

        css = self._convert_scss_in_memory(scss, [os.path.dirname(srcfile)])

        with open(dstfile, "w") as f:
            f.write(css)
    #end function

    def _convert_scss_in_memory(
            self, scss: str, include_paths: list[str] = None) -> str:
        if include_paths is None:
            include_paths = []

        scss = scss.replace("##STATIC##",
            os.path.normpath(os.sep.join(["/static", self._prefix])))

        cmd = [
            "node_modules/.bin/sass",
                    "-s", "expanded" if self._debug else "compressed",
                        "--no-source-map", "--stdin"
        ]

        for path in include_paths:
            cmd.append("-I")
            cmd.append(path)

        result = subprocess.run(
            cmd, input=scss, stdout=subprocess.PIPE, universal_newlines=True
        )

        return result.stdout
    #end function

    def _convert_js(self, srcfile: str, dstfile: str) -> None:
        if self._debug:
            shutil.copyfile(srcfile, dstfile)
            return

        cmd = [
            "./node_modules/.bin/babel",
                "--minified",
                    "--no-comments",
                        "-o", dstfile, srcfile
        ]

        subprocess.run(cmd)
    #end function

    def _convert_js_in_memory(self, js: str) -> str:
        if self._debug:
            return js

        cmd = [
            "./node_modules/.bin/babel",
                "--minified",
                    "--no-comments",
                        "--filename", "app.js"
        ]

        result = subprocess.run(
            cmd, input=js, stdout=subprocess.PIPE, universal_newlines=True
        )

        return result.stdout
    #end function

#end class
