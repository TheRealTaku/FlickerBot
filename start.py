from multiprocessing import Process
from start_admin import start as start_admin
from start_bot import start as start_bot

Process(target=start_admin).start()
Process(target=start_bot).start()
