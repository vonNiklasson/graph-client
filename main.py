import os
import sys
import math
import warnings

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

print("Starting %d processes" % thread_count)

processes = []

for i in range(0, thread_count):
    print("Process %d started" % (i+1))
    processes.append(Process(target=GraphThread.start_thread, args=(base_url, client_name, (i+1))))
    processes[i].start()

for process in processes:
    process.join()
