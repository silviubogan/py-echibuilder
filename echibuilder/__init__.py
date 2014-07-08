import os, glob, argparse
from . import plugins
from tkinter import *
from tkinter.ttk import *
from tkinter.scrolledtext import *

class Action:
    def __init__(self, func, name=None):
        self.func = func
        self.name = name if name is not None else func.__name__

class ActionManager:
    actions = []
    def __init__(self, base_args=[]):
        self.base_args = base_args
    def add(self, action):
        self.actions.append(action)
    def batch_add(self, action_functions):
        for func in action_functions:
            self.add(Action(func))
    def remove(self, action):
        self.actions.remove(action)
    def action(self, name=None, func=None):
        if name is not None:
            for a in self.actions:
                if a.name == name:
                    return a
        elif func is not None:
            for a in self.actions:
                if a.func == func:
                    return a
        else:
            raise Exception("ActionManager.action must be given at least one argument")
    def run(self, action, args):
        if args == ((),):
            final_args = self.base_args
        else:
            final_args = self.base_args + args
        action.func(*final_args)
    def names(self):
        return [a.name for a in self.actions]

class EchiBuilder:
    actions = []
    def __init__(self, output_folder="build", gui=False, gui_autostart=True):
        def init_argparse ():
            self.gui = gui
            self.gui_autostart = gui_autostart
            choices = self.actionmgr.names()
            metavar = "BUILD_STEPS"
            parser = argparse.ArgumentParser(description="A little build system",
                                             epilog="Tested on Windows 7 Ultimate x64",
                                             prog="echibuilder")
            parser.add_argument('--version', action='version', version='%(prog)s 1.0')
            
            group = parser.add_mutually_exclusive_group()
            group.add_argument("--skip", help="skip these build steps",
                              choices=choices, action="append", metavar=metavar)
            group.add_argument("--just", help="run only these build steps",
                              choices=choices, action="append", metavar=metavar)
            
            self.args = parser.parse_args()
        def init_actionmgr():
            self.actionmgr = ActionManager([self])
            self.actionmgr.batch_add(plugins.actions)
        self.output_folder = output_folder;
        init_actionmgr()
        init_argparse()
    def push(self, action, *args):
        self.actions.append([self.actionmgr.action(action), list(args)])
    def run(self):
        def run_build():
            if self.args.skip is not None:
                self.actions = [action for action in self.actions if action[0].name not in self.args.skip]
            elif self.args.just is not None:
                self.actions = [action for action in self.actions if action[0].name in self.args.just]
            for action in self.actions:
                self.actionmgr.run(action[0], action[1])
            self.log("Done")
        if self.gui:
            import threading
            thread = threading.Thread(target=run_build)
            def run_thread():
                thread.start()
            class Application(Frame):
                def createWidgets(self):
                    self.quit_button = Button(self)
                    self.quit_button["text"] = "Quit"
                    self.quit_button["command"] = self.quit
                    
                    self.build_button = Button(self)
                    self.build_button["text"] = "Build"
                    self.build_button["command"] = run_thread
                    
                    self.logging_widget = ScrolledText(self)
                    
                    self.quit_button.pack({"side": "top"})
                    self.build_button.pack({"side": "top"})
                    self.logging_widget.pack()
                def __init__(self, master=None):
                    Frame.__init__(self, master)
                    self.pack()
                    self.createWidgets()
            
            root = Tk()
            self.app = Application(master=root)
            self.app.mainloop()
            root.destroy()
        else:
            run_build()
    def log(self, msg):
        if self.gui:
            self.app.logging_widget.insert(END, "> {0}\n".format(msg), {})
        else:
            print(">", msg)
    def log2(self, msg):
        if self.gui:
            self.app.logging_widget.insert(END, "  > {0}\n".format(msg), {})
        else:
            print("  >", msg)
    def error(self, text):
        print(">> Error:", text)
    def output_glob(self, pattern):
        return [os.path.relpath(f, self.output_folder) for f in glob.glob(os.path.join(self.output_folder, pattern))]
    
