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

class SiteMaker:

    def prepare(self, npm_reinstall: bool = False):
        self \
            ._create_gitignore() \
            ._create_package_json() \
            ._npm_install(npm_reinstall) \
            ._create_babel_rc()
    #end function

    def make(self, debug: bool = False):
        task_list = self._scan_source_tree(debug=debug)

        # 2. Copy Handlebars, jQuery, Marked into place (make each of these
        #    optional)

        # 2. Add each file to the correct plugin:
        #    - Images (copy files)
        #    - CSS and SCSS files (copy files or scss generator)
        #    - Additional JavaScript files (copy files)
        #    - index.html, main.js and related components (app builder)

        # 3. Run each plugin generated in step 2
    #end function

    def _scan_source_tree(self, debug: bool = False):
        ignore_patterns = [
            "/environment.sh",
            "/.git/",
            "/.gitignore",
            "/*requirements.txt",
            ".*.swp",
            "/tox.ini",
            "_*"
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

        pathspec = PathSpec.from_lines("gitignore", ignore_patterns)
        basedir  = os.path.abspath(".")
        sitedir  = os.path.join(basedir, "_site")

        files_to_process = []

        for dirpath, dirnames, filenames in os.walk(basedir):
            for entry in filenames:
                full_path = os.path.join(dirpath, entry)

                if pathspec.match_file(full_path[len(basedir):]):
                    continue

                files_to_process.append(full_path)
            #end for
        #end for

        #cssmaker  = CssMaker(basedir, sitedir, debug)
        #copyfiles = CopyFiles(basedir, sitedir)

        for entry in files_to_process:
            print(entry)
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

            shutil.rmtree(item) if os.path.isdir(item) else os.unlink(item)
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

    def _create_package_json(self):
        if os.path.exists("package.json"):
            return

        with open("package.json", "w+", encoding="utf-8") as f:
            f.write(
                textwrap.dedent(
                    """\
                    {
                      "devDependencies": {
                        "@babel/cli": "^7.23.9",
                        "@babel/core": "^7.24.0",
                        "@babel/preset-env": "^7.24.0",
                        "handlebars": "^4.7.8",
                        "jquery": "^3.7.1",
                        "marked": "^12.0.0",
                        "sass": "^1.71.1"
                      }
                    }
                    """
                )
            )
        #end with

        return self
    #end function

    def _npm_install(self, npm_reinstall: bool = False):
        if os.path.exists("node_modules"):
            if not npm_reinstall:
                return
            shutil.rmtree("node_modules")
        #end if

        modules = [
            "@babel/core",
            "@babel/cli",
            "@babel/preset-env",
            "handlebars",
            "jquery",
            "marked",
            "sass"
        ]

        cmd = ["npm", "install"]

        if not os.path.exists("package.json"):
            cmd += ["--save-dev", *modules]

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

#end function

if __name__ == "__main__":
    sm = SiteMaker()
    sm._scan_source_tree()
