"""Restarts the current program, with file objects and descriptors cleanup"""
import os
import sys
import logging
import psutil

def restart_program():
    """Restart function"""
    try:
        process_param = psutil.Process(os.getpid())
        for handler in process_param.connections():
            os.close(handler.fd)
    except Exception as error:
        logging.error(error)

    python = sys.executable
    os.execl(python, python, *sys.argv)

if __name__=='__main__':
    restart_program()
