#!/usr/bin/env python3
"""
GUI wrapper for User 1
Uses the default nkas config
"""

import threading
from multiprocessing import Event, Process
from module.webui.setting import State

def func(ev: threading.Event):
    import argparse
    import uvicorn
    
    State.restart_event = ev
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, help="Host to listen", default='localhost')
    parser.add_argument("-p", "--port", type=int, help="Port to listen", default=12271)
    args, _ = parser.parse_known_args()
    
    # Run with default config (nkas)
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