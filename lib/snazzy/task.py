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

from lxml import etree
from tidylib import tidy_document

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

    def _convert_scss_in_memory(self, scss: str) -> str:
        cmd = [
            "node_modules/.bin/sass",
                    "-s", "expanded" if self._debug else "compressed",
                        "--no-source-map", "--stdin"
        ]

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

    def _process_html(self, srcfile: str, dstfile: str) -> None:
        with open(srcfile, "r", encoding="utf-8") as f:
            html_str = f.read()

        tidy_opts = {
            "doctype": "html5",
            "drop-empty-elements": False,
            "hide-comments": True,
            "indent": False,
            "tidy-mark": False,
            "vertical-space": "auto",
            "wrap": 0,
        }

        if self._debug:
            tidy_opts.update({
                "hide-comments": False,
                "indent": True,
                "vertical-space": "no",
                "wrap": 100,
            })
        #end if

        tidy_str, tidy_errors = tidy_document(html_str, tidy_opts)

        if tidy_errors:
            sys.stderr.write(tidy_errors)

        with open(dstfile, "w+", encoding="utf-8") as f:
            f.write(tidy_str)
    #end function

    def _process_component_xml(self, srcfile: str) -> tuple[str, str, str]:
        template   = ""
        script     = ""
        stylesheet = ""

        tree = etree.parse(srcfile)
        root = tree.getroot()

        component_name = root.get("name", os.path.basename(srcfile)[:-4])

        template_node = root.find("template")
        script_node   = root.find("script")
        style_node    = root.find("style")

        if template_node is not None:
            handlebars = "".join(
                etree.tostring(child, encoding="unicode", method="html")
                    for child in template_node
            )

            # TODO: find a better solution for this.
            handlebars = handlebars\
                .replace("%7B%7B", "{{")\
                .replace("%7D%7D", "}}")

            cmd = ["./node_modules/.bin/handlebars", "--name",
                    component_name, "-i", "-"]

            result = subprocess.run(cmd, input=handlebars, check=True,
                stdout=subprocess.PIPE, universal_newlines=True)

            template = self._convert_js_in_memory(result.stdout)
        #end if

        if script_node is not None:
            script = \
                self._convert_js_in_memory(script_node.text)

        if style_node is not None:
            stylesheet = \
                self._convert_scss_in_memory(style_node.text)

        return template, script, stylesheet
    #end function

#end class
