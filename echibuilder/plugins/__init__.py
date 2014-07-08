import os, glob, echibuilder
plugins = []
actions = []
for f in glob.glob(os.path.join(os.path.dirname(__file__), "*")):
    if os.path.basename(f) not in ["__init__.py", "__pycache__"]:
        splitext = os.path.splitext(os.path.basename(f))
        if (os.path.isfile(f) and splitext[1] == ".py") or os.path.isdir(f):
            plugins.append(splitext[0])
for plugin in plugins:
    module = __import__(plugin, globals(), locals(), [], 1)
    actions.extend(module.actions)
