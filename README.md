# About

This is a minimal Web development framework. Instead of downloading thousands
of packages from NPM, it builds on a template engine (Handlebars), a DOM
manipulation library (jQuery), and a JavaScript transpiler (Babel).

Single page applications are built from single file components, which are XML
files containing a) a template section, b) a script section and c) a style
section. All programming is done in pure, object-oriented JavaScript.

Since Snazzy apps are hand-crafted, they tend to be small -- meaning they load
swiftly and run efficiently.

# Installation

Before running snazzy, some dependencies have to be installed. On Debian,
install required packages via

```
sudo apt-get install \
    python3-lxml \
    python3-pathspec \
    python3-tidylib \
    nodejs \
    npm
```

The snazzy tool can be run from the source tree without additional installation.
All you have to do is to source `environment.sh`. After that snazzy is in the
path of that session and should run without problems.
