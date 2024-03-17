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

import getopt
import sys
import textwrap

from snazzy.error import InvocationError
from snazzy.sitemaker import SiteMaker

class SnazzyCli:

    EXIT_OK  = 0
    EXIT_ERR = 1

    COPYRIGHT = textwrap.dedent(
    """\
    Copyright (c) 2024, Tobias Koch <tobias.koch@gmail.com>

    """)

    @classmethod
    def snazzy(cls) -> None:
        usage = SnazzyCli.COPYRIGHT + textwrap.dedent(
        """\
          This is the snazzy low-npm frontend framework build tool.

        USAGE:

          snazzy <command> [options]

        COMMANDS:

          prepare
          make
          clean
          distclean

        Type 'snazzy <command> --help' for help on individual commands.
        """)

        try:
            opts, args = getopt.getopt(sys.argv[1:], "h", ["help"])
        except getopt.GetoptError as e:
            raise InvocationError(
                "error parsing command line: {}".format(str(e))
            )

        if len(args) < 1:
            sys.stdout.write(usage)
            sys.exit(SnazzyCli.EXIT_OK)

        for o, v in opts:
            if o in ["-h", "--help"]:
                sys.stdout.write(usage)
                sys.exit(SnazzyCli.EXIT_OK)

        command = args[0]

        try:
            getattr(cls, command)(*args[1:])
        except AttributeError as e:
            print(e)
            raise InvocationError(
                "unknown command \"{}\"".format(command)
            )
    #end function

    @classmethod
    def prepare(cls, *args: list[str]) -> None:
        usage = SnazzyCli.COPYRIGHT + textwrap.dedent(
        """\
          This command installs the minimum amount of node modules needed to
          do meaningful frontend development. It also creates an initial
          .gitignore file and a .babelrc.

        USAGE:

          snazzy prepare [options]

        OPTIONS:

          -h, --help        Show this help text.
          --npm-update      Run npm update.
          --npm-reinstall   Force reinstallation of node modules.

        """)

        options = {
            "npm_reinstall":
                False,
            "npm_update":
                False
        }

        try:
            opts, args = getopt.getopt(
                args, "h", ["help", "npm-reinstall", "npm-update"]
            )
        except getopt.GetoptError as e:
            raise InvocationError(
                "error parsing command line: {}".format(str(e))
            )

        for o, v in opts:
            if o in ["-h", "--help"]:
                sys.stdout.write(usage)
                sys.exit(SnazzyCli.EXIT_OK)
            elif o == "--npm-reinstall":
                options["npm_reinstall"] = True
            elif o == "--npm-update":
                options["npm_update"] = True
        #end for

        SiteMaker().prepare(**options)
    #end function

    @classmethod
    def make(cls, *args: list[str]) -> None:
        usage = SnazzyCli.COPYRIGHT + textwrap.dedent(
        """\
          This command generates the _site directory, copies static assets,
          processes Scss and JavaScript files and compiles the SPA(s).

        USAGE:

          snazzy make [options]

        OPTIONS:

          --debug    Don't mangle and optimize CSS and JavaScript in any way.

        """
        )

        try:
            opts, args = getopt.getopt(args, "h", ["help", "debug"])
        except getopt.GetoptError as e:
            raise InvocationError(
                "error parsing command line: {}".format(str(e))
            )

        options = {
            "debug": False
        }

        for o, v in opts:
            if o in ["-h", "--help"]:
                sys.stdout.write(usage)
                sys.exit(SnazzyCli.EXIT_OK)
            elif o == "--debug":
                options["debug"] = True
        #end for

        SiteMaker().make(**options)
    #end function

    @classmethod
    def clean(cls, *args: list[str]) -> None:
        usage = SnazzyCli.COPYRIGHT + textwrap.dedent(
        """\
          This command removes the _site directory.

        USAGE:

          snazzy clean

        """
        )

        try:
            opts, args = getopt.getopt(args, "h", ["help"])
        except getopt.GetoptError as e:
            raise InvocationError(
                "error parsing command line: {}".format(str(e))
            )

        for o, v in opts:
            if o in ["-h", "--help"]:
                sys.stdout.write(usage)
                sys.exit(SnazzyCli.EXIT_OK)

        SiteMaker().clean()
    #end function

    @classmethod
    def distclean(cls, *args: list[str]) -> None:
        usage = SnazzyCli.COPYRIGHT + textwrap.dedent(
        """\
          This command returns the source tree to its pristine state.

        USAGE:

          snazzy distclean

        """
        )

        try:
            opts, args = getopt.getopt(args, "h", ["help"])
        except getopt.GetoptError as e:
            raise InvocationError(
                "error parsing command line: {}".format(str(e))
            )

        for o, v in opts:
            if o in ["-h", "--help"]:
                sys.stdout.write(usage)
                sys.exit(SnazzyCli.EXIT_OK)

        SiteMaker().distclean()
    #end function

#end function
