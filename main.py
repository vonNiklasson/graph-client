import os
import sys
import time
import warnings
import logging

from dotenv import load_dotenv

from utils.GraphThread import GraphThread
from utils.ServerUtil import ServerUtil
from multiprocessing import Process

# Suppress complex numbers
warnings.filterwarnings('ignore')

load_dotenv()

if __name__ != "__main__":
    exit(0)


if os.getenv('VERSION') != '1.0':
    print("Please run 'python setup.py' before starting the client.")
    exit(1)

client_name = os.getenv('CLIENT_NAME')
base_url = os.getenv('BASE_URL')
thread_count = int(os.getenv('THREAD_COUNT'))

arg: str
for arg in sys.argv[1:]:
    if arg.startswith('-t='):
        thread_count = int(arg[3:])

print("Closing previous unfinished work")
server = ServerUtil(base_url)
server.close_previous_workers(client_name)

print("Starting %d processes" % thread_count)

colors = [
    '\033[92m',
    '\033[94m',
    '\033[95m',
    '\033[96m',
    '\033[97m',
    '\033[93m',
    '\033[90m',
    '\033[91m',
]

processes = []

logging.basicConfig(filename='client.log', level=logging.INFO)

for i in range(0, thread_count):
    processes.append(Process(target=GraphThread.start_thread, args=(base_url, client_name, (i+1), colors[i%8])))
    processes[i].start()
    print("Process %d started" % (i+1))
    time.sleep(0.5)

for process in processes:
    process.join()
