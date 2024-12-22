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

import functools
import logging
import os
import shutil
import sys
import tempfile

from multiprocessing.pool import Pool
from multiprocessing.pool import ThreadPool

from lxml import etree
from tidylib import tidy_document

from snazzy.task import Task
from snazzy.componentmaker import ComponentMaker

LOGGER = logging.getLogger(__name__)

class AppMaker(Task):

    def execute(self, worker_pool: Pool) -> None:
        partial_generate_app = functools.partial(
            self._generate_app, worker_pool=worker_pool
        )

        with ThreadPool(len(self._objects)) as pool:
            pool.map(partial_generate_app, self._objects)
    #end function

    def _generate_app(self, entry, worker_pool) -> None:
        LOGGER.info("building SPA at {}".format(os.path.dirname(entry)))

        srcfile = os.path.normpath(
            os.sep.join([self._basedir, entry])
        )

        dstfile = os.path.normpath(
            os.sep.join([self._sitedir, entry])
        )

        srcdir = os.path.dirname(srcfile)
        dstdir = os.path.dirname(dstfile)

        os.makedirs(dstdir, exist_ok=True)

        appdir = os.path.join(srcdir, "+app")
        appjs  = os.path.join(srcdir, "+app.js")

        component_maker = ComponentMaker(
            self._basedir, self._sitedir, self._debug, self._prefix
        )

        for dirpath, _, filenames in os.walk(appdir):
            for entry in filenames:
                if entry.endswith(".xml"):
                    component_maker.add_object(os.path.join(dirpath, entry))

        all_components = component_maker.execute(worker_pool)

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpjs  = os.path.join(tmpdir, "app.js")
            tmpcss = os.path.join(tmpdir, "app.css")

            for component in all_components:
                template   = component.template
                script     = component.script
                stylesheet = component.style

                with open(tmpjs, "a+", encoding="utf-8") as f:
                    f.write(template)
                    f.write(script)

                with open(tmpcss, "a+", encoding="utf-8") as f:
                    f.write(stylesheet)
            #end for

            with open(appjs, "r", encoding="utf-8") as f:
                script = self._convert_js_in_memory(f.read())
            with open(tmpjs, "a+", encoding="utf-8") as f:
                f.write(script)
            with open(tmpcss, "a+", encoding="utf-8"):
                pass

            appjs = os.path.join(
                dstdir, "app.js" if self._debug else "app-{}.js"
                    .format(self._prefix)
            )

            appcss = os.path.join(
                dstdir, "app.css" if self._debug else "app-{}.css"
                    .format(self._prefix)
            )

            shutil.move(tmpjs,  appjs)
            shutil.move(tmpcss, appcss)
        #end with

        self._process_html(srcfile, dstfile)
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

#end class
