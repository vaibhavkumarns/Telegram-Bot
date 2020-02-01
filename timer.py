import schedule,time,requests,firebase_admin,os,logging
from telegram.ext import Updater
from firebase_admin import credentials,db
cred = credentials.Certificate('uuu.json')
firebase_admin.initialize_app(cred, {
    'databaseURL':'https://usertask-e1cc5.firebaseio.com/'
})
ref = db.reference('/office-time')
a=ref.get()
start=a['start']
close=a['close']
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger()
TOKEN = '910332789:AAElxdJpPZTRp4LmA1-bE8GfSr0qL4EtVHo'

def run(updater):
    PORT = int(os.environ.get("PORT", "8443"))
    #HEROKU_APP_NAME = os.environ.get("HEROKU_APP_NAME")
    updater.start_webhook(listen="0.0.0.0",
                            port=PORT,
                             url_path=TOKEN)
    updater.bot.set_webhook("https://{}.herokuapp.com/{}".format(HEROKU_APP_NAME, TOKEN))


def morningreport():
    bot_chatID = ['964783366']
    for i in bot_chatID:
        send_text = 'https://api.telegram.org/bot' + TOKEN + '/sendMessage?chat_id=' + str(
            i) + '&parse_mode=Markdown&text=' + "Good Morning, \n Tap on /morningreport to continue."
        response = requests.get(send_text).json()
        return response

def eveningreport():
    bot_chatID = ['964783366']
    for i in bot_chatID:
        send_text = 'https://api.telegram.org/bot' + TOKEN + '/sendMessage?chat_id=' + str(
            i) + '&parse_mode=Markdown&text=' + "Good Morning, \n Tap on /eveningreport to continue."
        response = requests.get(send_text).json()
        return response

if __name__ == '__main__':
    logger.info("Starting bot")

    updater = Updater(TOKEN)
    schedule.every().day.at(start).do(morningreport)
    schedule.every().day.at(close).do(eveningreport)
    # updater.dispatcher.add_handler(CommandHandler("start", start_handler))
    run(updater)

    #schedule.every().day.at(close).do(report2)

    while True:
        schedule.run_pending()
        time.sleep(1)