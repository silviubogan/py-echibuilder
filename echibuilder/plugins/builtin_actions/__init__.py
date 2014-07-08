import os, shutil, re, urllib.request, sys
def delete_useless(self, files_to_delete):
    self.log("Deleting useless files")
    for filename in files_to_delete:
        filepath = os.path.join(self.output_folder, filename)
        if os.path.exists(filepath):
            if not os.path.isdir(filepath):
                os.remove(filepath)
            else:
                shutil.rmtree(filepath)
            self.log2(filename)
def delete_old_output(self):
    if os.path.isdir(self.output_folder):
        self.log("Deleting old output")
        shutil.rmtree(self.output_folder)
def build_tree(self, files_to_exclude=[]):
    self.log("Building tree")
    echibuilder_package_path = os.path.basename(os.path.dirname(sys.modules["echibuilder"].__file__))
    files_to_exclude.extend([echibuilder_package_path, self.output_folder])
    shutil.copytree(".", self.output_folder, ignore=lambda cd, files: files_to_exclude if cd == "." else [])
def compile_wiki(self, wiki_files):
    self.log("Compiling wiki files")
    for f in wiki_files:
        with open(f, "r", encoding="utf-8") as f_in:
            content = f_in.read()
        
        def link_callback (m):
            url = "http://" + m.group(1) if not m.group(1).startswith("http://") else m.group(1)
            return '<a href="{0}" target="_blank">{1}</a>'.format(url, m.group(1))
        
        content = re.sub("\*\*(.+?)\*\*", "<strong>\\1</strong>", content) # strong
        content = re.sub("\/\/(.+?)\/\/", "<em>\\1</em>", content) # em
        content = re.sub("__(.+?)__", "<span class=\"underlined\">\\1</span>", content) # underline
        content = re.sub(">>(.+?)<<",
                         lambda m: '<div style="text-align:center">{0}</div>'.format(m.group(1).strip()),
                         content, flags=re.DOTALL) # align center
        content = re.sub(">>(.+?)$",
                         lambda m: '<div style="text-align:right">{0}</div>'.format(m.group(1).strip()),
                         content) # align right
        content = re.sub("\[\[(.+?)\]\]", link_callback, content) # link
        content = re.sub("([-]{2,})", "&mdash;", content) # em dash
        content = re.sub('\s+', ' ', content).strip()
        
        with open(f, "w", encoding="utf-8") as f_out:
            f_out.write(content)
def compile_less_and_minify(self, less_files):
    self.log("Compiling LESS to minified CSS (requires `lessc` in PATH)")
    for filename in less_files:
        filepath = os.path.join(self.output_folder, filename)
        tmp_suffix = ".tmp"
        cmd = 'lessc -x "{0}" "{1}"'.format(filepath, filepath + tmp_suffix)
        os.system(cmd)
        shutil.move(filepath + tmp_suffix, filepath)
        self.log2(filename)
def minify_js(self, js_files):
    self.log("Minifying JS")
    for filename in js_files:
        filepath = os.path.join(self.output_folder, filename)
        tmp_suffix = ".tmp"
        cmd = 'java -jar "{1}" --js="{0}" --charset="utf-8" --js_output_file="{0}{2}" --compilation_level=SIMPLE_OPTIMIZATIONS'
        cmd = cmd.format(filepath, os.path.join(os.path.dirname(__file__), "compiler.jar"), tmp_suffix)
        os.system(cmd)
        with open(filepath + tmp_suffix, "r", encoding="utf-8") as f_in:
            with open(filepath, "w", encoding="utf-8") as f_out:
                f_out.write(f_in.read())
        os.remove(filepath + tmp_suffix)
        self.log2(filename)
def minify_css(self, css_files):
    self.log("Minifying CSS")
    from . import cssmin
    for filename in css_files:
        filepath = os.path.join(self.output_folder, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            css = f.read()
        css = cssmin.cssmin(css)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(css)
        self.log2(filename)
def cat(self, files):
    self.log("Concatenating files")
    for f in files:
        output_file = os.path.join(self.output_folder, f["output"])
        content = ""
        for input_file in f["input"]:
            with open(os.path.join(self.output_folder, input_file), "r", encoding="utf-8") as file:
                content = content + file.read()
        with open(output_file, "w", encoding="utf-8") as file:
            file.write(content)
        self.log2(f["output"] + " = " + " + ".join(f["input"]))

actions = [delete_useless, delete_old_output, build_tree,
           compile_wiki, compile_less_and_minify, minify_js,
           minify_css, cat]
