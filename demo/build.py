#!/usr/bin/env python3

# tested on Windows 7 with Python 3
# 'java' required in path for 'minify_js' task
# 'lessc' required in path for 'compile_less_and_minify' task (run 'npm install -g less')
# run this script from its directory

import os, sys
sys.path.append(os.path.normpath(os.path.join(os.path.dirname(__file__), "..")))
import echibuilder

b = echibuilder.EchiBuilder("build", True, True)

b.push("delete_old_output")
b.push("build_tree", ["build.py", "other"])
b.push("compile_wiki", b.output_glob(os.path.join("book", "*.html")))
b.push("minify_js", ["script.js"])
b.push("compile_less_and_minify", ["style.css"])
b.push("minify_css", ["style.css"])
b.push("cat", [
    {
        "input": [os.path.join("lib", "lib.js"), "script.js"],
        "output": "script.js"
    }
])
b.push("delete_useless", ["lib"])

b.run()
