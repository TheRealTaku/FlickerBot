from multiprocessing import Process
import start_admin
import start_bot

Process(target=start_admin.start).start()
Process(target=start_bot.start).start()
