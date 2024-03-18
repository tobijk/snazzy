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
import subprocess
import sys
import tempfile

from lxml import etree
from tidylib import tidy_document

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

            appjs = os.path.join(
                os.path.dirname(dstfile), "app.js" if self._debug
                    else "app-{}.js".format(self._prefix)
            )
            appcss = os.path.join(
                os.path.dirname(dstfile), "app.css" if self._debug
                    else "app-{}.css".format(self._prefix)
            )

            os.rename(tmpjs,  appjs)
            os.rename(tmpcss, appcss)
        #end with
    #end function

    def _process_html(self, srcfile: str, dstfile: str) -> None:
        with open(srcfile, "r", encoding="utf-8") as f:
            tree = etree.parse(f, parser=etree.HTMLParser())

        root = tree.getroot()
        self._apply_static_asset_prefix(root)

        html_str = "<!DOCTYPE html>\n" + \
            etree.tostring(root, encoding="unicode", method="html",
                pretty_print = True if self._debug else False)

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

    def _apply_static_asset_prefix(self, fragment: etree.Element) -> None:
        if not self._prefix:
            return

        for element in fragment.xpath("//*[@src] | //*[@href]"):
            for attr_name in ["src", "href"]:
                attr = element.get(attr_name)
                if not attr:
                    continue

                if attr.startswith("static/"):
                    element.set(
                        attr_name, "static/{}/{}"
                            .format(self._prefix, attr[len("static/"):])
                    )
                elif attr in ["app.js", "app.css"]:
                    element.set(
                        attr_name, "app-{}.{}"
                            .format(self._prefix, attr.split(".")[1])
                    )
            #end for
        #end for
    #end function

#end class
