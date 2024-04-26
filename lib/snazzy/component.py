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

import random

TEMPLATE = """
<component name="{name}">
    <!--///////////////////////////////////////////////////////////////////////
      -
      - TEMPLATE
      -
      -/////////////////////////////////////////////////////////////////////-->
    <template>
        <div class="{name}" data-css-scope-{scope}=""></div>
    </template>

    <!--///////////////////////////////////////////////////////////////////////
      -
      - SCRIPT
      -
      -/////////////////////////////////////////////////////////////////////-->
    <script>
        <![CDATA[

class {class_name} {{

    constructor(context) {{
        this.context = context;
        this.tree = this.render(context);
    }}

    render(context) {{
        var template = Handlebars.templates["{name}"];
        return $(template(context));
    }}

    mount(element) {{
        element.replaceWith(this.tree);
    }}
}}
        ]]>
    </script>

    <!--///////////////////////////////////////////////////////////////////////
      -
      - STYLE
      -
      -/////////////////////////////////////////////////////////////////////-->
    <style>
        <![CDATA[

.{name}[data-css-scope-{scope}] {{
    // Component CSS here
}}

        ]]>
    </style>
</component>
"""

class Component:

    def __init__(self, name):
        self.name = name

    def generate(self):
        class_name = "".join([s.capitalize() for s in self.name.split("-")])

        return TEMPLATE.format(
            name=self.name,
            class_name=class_name,
            scope=self.generate_random_hexstring()
        )
    #end function

    def generate_random_hexstring(self):
        return ''.join(
            random.choices("0123456789abcdef", k=8)
        )
    #end function

#end class
