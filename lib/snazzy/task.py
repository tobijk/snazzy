# -*- encoding: utf-8 -*-
#
# Proprietary
#
# Copyright (c) 2024 Tobias Koch <tobias.koch@gmail.com>
#

class Task:

    def run(self):
        raise NotImplementedError(
            "{} has no run method".format(self.__class__.__name__)
        )

#end class
