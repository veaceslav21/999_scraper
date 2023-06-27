import os
import schedule
from time import sleep


os.system('python tg_bot.py')  # Run tg bot
schedule.every().day.at('04:00').do(os.system, 'python scraper.py')

while True:
    schedule.run_pending()  # Constantly check if jobs need to be run
    sleep(3600)  # 3600 sec == 1h, This will pause running of the script/parser for 1h,
    # to avoid overload of CPU because of infinity loop

