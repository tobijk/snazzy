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

import multiprocessing
import os
import subprocess

from multiprocessing import Pool

from lxml import etree

from snazzy.task import Task

class ComponentMaker(Task):

    def execute(self, worker_pool: Pool) -> None:
        return worker_pool.map(self._process_component_xml, self._objects)

    def _process_component_xml(self, srcfile: str) -> tuple[str, str, str]:
        template   = ""
        script     = ""
        stylesheet = ""

        tree = etree.parse(srcfile)
        root = tree.getroot()

        self._apply_static_asset_prefix(root)

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
