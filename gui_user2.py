#!/usr/bin/env python3
"""
GUI wrapper for User 2
Modifies the GUI to use nkas_user2 config
"""

import threading
from multiprocessing import Event, Process
from module.webui.setting import State

# Monkey patch before importing the app
import sys
import importlib.util

# Create a custom NikkeAutoScriptGUI class for User 2
class User2GUI:
    @staticmethod
    def patch():
        from module.webui.app import NikkeAutoScriptGUI as OriginalGUI
        from module.webui.base import Frame
        from module.config.config import NikkeConfig
        from module.config.utils import read_file, filepath_args, deep_iter
        from module.webui.process_manager import ProcessManager
        from module.webui.lang import t
        from module.logger import logger
        from pywebio.output import put_scope, put_scrollable, put_text
        from pywebio.session import run_js
        import queue
        
        class NikkeAutoScriptGUIUser2(OriginalGUI):
            def __init__(self):
                # Initialize Frame parent directly to avoid calling original __init__
                Frame.__init__(self)
                self.nkas_mod = "nkas"
                self.nkas_config = NikkeConfig("nkas_user2")  # Use nkas_user2 config
                self.modified_config_queue = queue.Queue()
                self.init()
                # Set nkas after initialization
                self._nkas = ProcessManager.get_manager('nkas_user2')
            
            @property
            def nkas(self):
                return self._nkas
                
            def nkas_set_group(self, task):
                """Modified version that reads nkas_user2 config"""
                put_scope("_groups",
                          [put_scrollable([put_scope("groups")], height=None, keep_bottom=False).style(
                              '--groups-scrollable--'), put_scope("navigator")])
                run_js(
                    '''
                    $("div[style*='--groups-scrollable--']").addClass('groups-scrollable');
                    $('.groups-scrollable > .webio-scrollable').addClass('_groups-scrollable');
                    '''
                )
                task_help = t(f"Task.{task}.help")
                if task_help:
                    put_scope(
                        "group__info",
                        scope="groups",
                        content=[put_text(task_help).style("font-size: 1rem")],
                    )

                # Use nkas_user2 config
                config = self.nkas_config.read_file('nkas_user2')
                for group, arg_dict in deep_iter(self.NKAS_ARGS[task], depth=1):
                    if self.set_group(group, arg_dict, config, task):
                        self.set_navigator(group)
                        
            def ui_dashboard(self):
                """Override to remove the self.nkas = assignment"""
                self.init_aside(name='Dashboard')
                self.dashboard_set_menu()
                self.dashboard_set_content()
        
        # Replace the original class
        import module.webui.app
        module.webui.app.NikkeAutoScriptGUI = NikkeAutoScriptGUIUser2
        return NikkeAutoScriptGUIUser2

# Apply the patch before anything else imports the app
User2GUI.patch()

def func(ev: threading.Event):
    import argparse
    import uvicorn
    
    State.restart_event = ev
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, help="Host to listen", default='localhost')
    parser.add_argument("-p", "--port", type=int, help="Port to listen", default=12272)
    args, _ = parser.parse_known_args()
    
    uvicorn.run("module.webui.app:app", host=args.host, port=args.port, factory=True)

if __name__ == '__main__':
    should_exit = False
    while not should_exit:
        event = Event()
        process = Process(target=func, args=(event,))
        process.start()
        while not should_exit:
            try:
                b = event.wait(1)
            except KeyboardInterrupt:
                should_exit = True
                break
            if b:
                process.kill()
                break
            elif process.is_alive():
                continue
            else:
                should_exit = True