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
import subprocess
import textwrap

from pathspec import PathSpec

from snazzy.appmaker import AppMaker
from snazzy.copyfiles import CopyFiles
from snazzy.preptask import PrepTask
from snazzy.task import Task

LOGGER = logging.getLogger(__name__)

class SiteMaker:

    def prepare(
            self,
            npm_reinstall: bool = False,
            npm_update: bool = False) -> "SiteMaker":

        self \
            ._create_gitignore() \
            ._npm_install_or_update(npm_reinstall, npm_update) \
            ._create_babel_rc()

        return self
    #end function

    def make(self, debug: bool = False) -> "SiteMaker":
        tasks = self._create_tasks(debug=debug)

        for t in tasks:
            t.execute()

        return self
    #end function

    def clean(self) -> "SiteMaker":
        if os.path.exists("_site"):
            LOGGER.info("removing _site folder")
            shutil.rmtree("_site")

        return self
    #end function

    def distclean(self) -> "SiteMaker":
        self.clean()

        things_to_remove = [
            ".babelrc",
            "node_modules",
            "package-lock.json"
        ]

        for item in things_to_remove:
            if not os.path.exists(item):
                continue

            LOGGER.info("removing {}".format(item))
            shutil.rmtree(item) if os.path.isdir(item) \
                else os.unlink(item)
        #end for

        return self
    #end function

    # HELPERS

    def _create_gitignore(self) -> "SiteMaker":
        if os.path.exists(".gitignore"):
            return self

        LOGGER.info("creating initial .gitignore file")

        with open(".gitignore", "w+", encoding="utf-8") as f:
            f.write(
                textwrap.dedent(
                    """\
                    /.babelrc
                    /_site/
                    /node_modules/
                    .*.swp
                    """
                )
            )
        #end with

        return self
    #end function

    def _npm_install_or_update(
            self,
            npm_reinstall: bool = False,
            npm_update: bool = False) -> "SiteMaker":

        modules = [
            "@babel/core",
            "@babel/cli",
            "@babel/preset-env",
            "handlebars",
            "jquery",
            "marked",
            "sass"
        ]

        if npm_reinstall:
            if os.path.exists("package.json"):
                os.unlink("package.json")
            if os.path.exists("node_modules"):
                shutil.rmtree("node_modules")

        if os.path.exists("package.json") and npm_update:
            cmd = ["npm", "update"]
        else:
            cmd = ["npm", "install", "--save-dev", *modules]

        LOGGER.info("running npm {}...".format(cmd[1]))

        subprocess.run(cmd)
        return self
    #end function

    def _create_babel_rc(self) -> "SiteMaker":
        if os.path.exists(".babelrc"):
            return self

        LOGGER.info("creating .babelrc")

        with open(".babelrc", "w+", encoding="utf-8") as f:
            f.write(
                textwrap.dedent(
                    """ \
                    {
                        "presets": ["@babel/preset-env"]
                    }
                    """
                )
            )
        #end with

        return self
    #end function

    def _make_ignore_spec(self) -> PathSpec:
        ignore_patterns = [
            "/environment.sh",
            "/.git/",
            "/.gitignore",
            "/*requirements.txt",
            ".*.swp",
            "/tox.ini",
            "_*",
            "+*"
        ]

        for ignore_file in [".gitignore", ".snazzyignore"]:
            if not os.path.exists(ignore_file):
                continue

            with open(ignore_file, "r", encoding="utf-8") as f:
                ignore_patterns += \
                    [line for line in
                        [line.strip() for line in f.readlines()]
                            if line and not line.startswith("#")]
            #end with
        #end for

        return PathSpec.from_lines("gitignore", ignore_patterns)
    #end function

    def _create_tasks(self, debug: bool = False) -> list[Task]:
        ignore_spec = self._make_ignore_spec()

        basedir = os.path.abspath(".")
        sitedir = os.path.join(basedir, "_site")

        preptask = PrepTask(basedir, sitedir, debug)
        appmaker = AppMaker(basedir, sitedir, debug)
        copyfiles = CopyFiles(basedir, sitedir, debug)

        module_by_extension = {
            "css":  copyfiles,
            "gif":  copyfiles,
            "html": appmaker,
            "ico":  copyfiles,
            "jpg":  copyfiles,
            "js":   copyfiles,
            "png":  copyfiles,
            "scss": copyfiles,
            "svg":  copyfiles,
        }

        LOGGER.info("compiling tasks")

        for dirpath, dirnames, filenames in os.walk(basedir):
            for entry in filenames:
                full_path = os.path.join(dirpath, entry)

                if ignore_spec.match_file(full_path[len(basedir):]):
                    continue

                try:
                    _, ext = entry.rsplit(".", 1)
                    if ext in module_by_extension:
                        module_by_extension[ext] \
                            .add_object(full_path[len(basedir):])
                except ValueError:
                    pass
            #end for
        #end for

        return [preptask, copyfiles, appmaker]
    #end function

#end function
