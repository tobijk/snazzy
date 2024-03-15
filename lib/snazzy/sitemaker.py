# -*- encoding: utf-8 -*-
#
# Proprietary
#
# Copyright (c) 2024 Tobias Koch <tobias.koch@gmail.com>
#

import os
import shlex
import subprocess
import textwrap

from pathspec import PathSpec

from snazzy.appmaker import AppMaker
from snazzy.copyfiles import CopyFiles
from snazzy.cssmaker import CssMaker
from snazzy.preptask import PrepTask

class SiteMaker:

    def prepare(
            self,
            npm_reinstall: bool = False,
            npm_update: bool = False):

        self \
            ._create_gitignore() \
            ._npm_install_or_update(npm_reinstall, npm_update) \
            ._create_babel_rc()

        return self
    #end function

    def make(self, debug: bool = False):
        tasks = self._create_tasks(debug=debug)

        for t in tasks:
            t.execute()

        return self
    #end function

    def clean(self):
        if os.path.exists("_site"):
            shutil.rmtree("_site")

        return self
    #end function

    def distclean(self):
        self.clean()

        things_to_remove = [
            ".babelrc",
            "node_modules",
            "package-lock.json"
        ]

        for item in things_to_remove:
            if not os.path.exits(item):
                continue

            shutil.rmtree(item) if os.path.isdir(item) \
                else os.unlink(item)
        #end for

        return self
    #end function

    # HELPERS

    def _create_gitignore(self):
        if os.path.exists(".gitignore"):
            return

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
            npm_update: bool = False):

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

        subprocess.run(cmd)
        return self
    #end function

    def _create_babel_rc(self):
        if os.path.exists(".babelrc"):
            return

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

    def _make_ignore_spec(self):
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
                    [line for line in [line.strip() for line in f.readlines()] \
                        if line and not line.startswith("#")]
            #end with
        #end for

        return PathSpec.from_lines("gitignore", ignore_patterns)
    #end function

    def _create_tasks(self, debug: bool = False):
        ignore_spec = self._make_ignore_spec()

        basedir = os.path.abspath(".")
        sitedir = os.path.join(basedir, "_site")

        preptask = PrepTask(basedir, sitedir, debug)
        appmaker = AppMaker(basedir, sitedir, debug)
        cssmaker = CssMaker(basedir, sitedir, debug)
        copyfiles = CopyFiles(basedir, sitedir, debug)

        module_by_extension = {
            "css":  copyfiles,
            "gif":  copyfiles,
            "html": appmaker,
            "jpg":  copyfiles,
            "js":   copyfiles,
            "png":  copyfiles,
            "scss": cssmaker,
            "svg":  copyfiles,
        }

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

        return [preptask, copyfiles, cssmaker, appmaker]
    #end function

#end function

if __name__ == "__main__":
    sm = SiteMaker()
    sm._create_tasks()
