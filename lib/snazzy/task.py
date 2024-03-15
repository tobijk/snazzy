# -*- encoding: utf-8 -*-
#
# Proprietary
#
# Copyright (c) 2024 Tobias Koch <tobias.koch@gmail.com>
#

class Task:

    def __init__(self, basedir: str, sitedir: str, debug: bool = False):
        self._basedir = basedir
        self._sitedir = sitedir
        self._debug   = debug
        self._objects = []
    #end function

    def add_object(self, entry):
        self._objects.append(entry)

    def execute(self):
        raise NotImplementedError(
            "{} has no execute method".format(self.__class__.__name__)
        )

#end class
