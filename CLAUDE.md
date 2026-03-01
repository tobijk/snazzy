# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Snazzy is a minimal web development framework (Python 3) that builds single-page applications from single-file XML components. It uses Handlebars for templating, jQuery for DOM, Babel for JS transpilation, and Sass for CSS preprocessing. The philosophy is minimalism — small, fast apps with few dependencies.

## Development Setup

```bash
. ./environment.sh          # Activates dev environment (adds bin/ and lib/ to PATH/PYTHONPATH)
snazzy prepare              # Installs npm dependencies, creates .babelrc
```

## Common Commands

```bash
snazzy make                 # Build site to _site/
snazzy make --debug         # Build without minification or cache-busting
snazzy make -j 4            # Build with 4 parallel workers
snazzy clean                # Remove _site/
snazzy distclean            # Remove _site/, node_modules/, .babelrc, package-lock.json
snazzy new <name>           # Generate component scaffold to stdout
```

## Linting

```bash
tox -e py3                  # Run flake8 on bin/ and lib/
```

Flake8 config is in `tox.ini` with specific ignored rules (E305, E302, E265, E128, E221, E226, E127, W504, E131, E126, E266, E241, E251, E122, E202).

## Architecture

**Entry point**: `bin/snazzy` → `SnazzyCli.main()` in `lib/snazzy/cli.py`

**Build pipeline** (orchestrated by `SiteMaker`):
1. `PrepTask` — copies JS libraries (handlebars, jquery, marked) to `_site/static/`
2. `CopyFiles` — copies static assets, converts SCSS→CSS, transpiles/minifies JS via Babel
3. `AppMaker` — builds SPAs from HTML files by processing referenced XML components

**Task system**: All build tasks inherit from `Task` (lib/snazzy/task.py), which provides multiprocessing-based parallel file processing. SiteMaker routes files to task handlers by extension.

**Component processing**: `ComponentMaker` parses XML component files, extracts template/script/style sections, compiles Handlebars templates, converts SCSS→CSS, transpiles JS, and resolves inter-component dependencies with cycle detection. Each component gets an auto-generated CSS scope identifier for style isolation.

**Component XML format**:
```xml
<component name="my-component">
  <template><!-- Handlebars HTML --></template>
  <script><![CDATA[/* JavaScript */]]></script>
  <style><![CDATA[/* SCSS */]]></style>
  <dependencies>
    <depends>other-component</depends>
  </dependencies>
</component>
```

## Key Dependencies

- Python: `lxml` (XML parsing), `pytidylib` (HTML validation)
- System: `nodejs`, `npm`, `python3-lxml`, `python3-tidylib`, `python3-pathspec`
- NPM (installed via `snazzy prepare`): `@babel/core`, `@babel/cli`, `@babel/preset-env`, `handlebars`, `jquery`, `marked`, `sass`
