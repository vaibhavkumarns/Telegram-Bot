import firebase_admin
from datetime import datetime
from firebase_admin import credentials
from firebase_admin import db
cred = credentials.Certificate({
  '''add your firebase credentials here'''
#   "type":
#   "project_id": 
#   "private_key_id":
#   "private_key": 
#   "client_email": 
#   "auth_uri": 
#   "auth_provider_x509_cert_url": 
#   "client_x509_cert_url": 
})
firebase_admin.initialize_app(cred, {
    'databaseURL':'https://<your-database-name>.firebaseio.com/' #your database name
})
from datetime import date
import logging,telegram
from telegram.ext import (Updater, CommandHandler,CallbackQueryHandler, MessageHandler, Filters,
                          ConversationHandler)
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
import datetime
import calendar
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

NEWTASK,TASKUPDATE,DATE,FINAL,TIMING,SAVEEMP1,SAVEEMP2,CHANGEEMP= range(8)

today = date.today()
now = today.strftime("%d-%m-%Y")

def start(bot,update):
    user = update.message.from_user
    chat_id = str(update.message.chat_id)
    name=user.first_name
    print(chat_id)
    ref = db.reference('/admin') #database reference for admin's CHAT ID 
    a = ref.get()
    admin=a['chat_id']
    if chat_id==admin: #if admin. 
        custom_keyboard = [['ASSIGN NEW TASK'],
                           ['VIEW STATUS OF TASKS'],
                           ['CHANGE TIMINGS']]
        reply_markup = telegram.ReplyKeyboardMarkup(keyboard=custom_keyboard,
                                            resize_keyboard=True, one_time_keyboard=True)
        ref = db.reference('/')
        ref.child(now).child('assigned_by').set({"assigned_by": name})
        bot.send_message(chat_id=chat_id ,
                        text="Hello *"+user.first_name+"*! What would you like to do ?",
                        reply_markup= reply_markup,parse_mode=telegram.ParseMode.MARKDOWN)
        return NEWTASK
    else: #else employee
        user = update.message.from_user
        chat_id = str(update.message.chat_id)
        ref = db.reference('/')
        ref.child(now).child('employee').set({"employeename": name})
        update.message.reply_text("Tap on */morningreport* to Post new TASK\n\nTap on */eveningreport* to give status report on what you have done today.\n\nTap on */change* to change TEAM LEADER\n\n"
                                  "Tap on */mytask* to see your task.\n\nTap on */cancel* to END conversation",parse_mode=telegram.ParseMode.MARKDOWN)
        return SAVEEMP1

def create_callback_data(action, year, month, day):
    """ Create the callback data associated to each button"""
    return ";".join([action, str(year), str(month), str(day)])

def separate_callback_data(data):
    """ Separate the callback data"""
    return data.split(";")

def create_calendar(year=None, month=None): #Displaying calender for Due Date. 
    now = datetime.datetime.now()
    if year is None:
        year = now.year
    if month is None:
        month = now.month
    data_ignore = create_callback_data("IGNORE", year, month, 0)
    keyboard = []
    row = []
    row.append(InlineKeyboardButton(calendar.month_name[month] + " " + str(year), callback_data=data_ignore))
    keyboard.append(row)
    row = []
    for day in ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]:
        row.append(InlineKeyboardButton(day, callback_data=data_ignore))
    keyboard.append(row)
    my_calendar = calendar.monthcalendar(year, month)
    for week in my_calendar:
        row = []
        for day in week:
            if (day == 0):
                row.append(InlineKeyboardButton(" ", callback_data=data_ignore))
            else:
                row.append(InlineKeyboardButton(str(day), callback_data=create_callback_data("DAY", year, month, day)))
        keyboard.append(row)
    row = []
    row.append(InlineKeyboardButton("<", callback_data=create_callback_data("PREV-MONTH", year, month, day)))
    row.append(InlineKeyboardButton(" ", callback_data=data_ignore))
    row.append(InlineKeyboardButton(">", callback_data=create_callback_data("NEXT-MONTH", year, month, day)))
    keyboard.append(row)

    return InlineKeyboardMarkup(keyboard)

def process_calendar_selection(bot, update):
    ret_data = (False, None)
    query = update.callback_query
    (action, year, month, day) = separate_callback_data(query.data)
    curr = datetime.datetime(int(year), int(month), 1)
    if action == "IGNORE":
        bot.answer_callback_query(callback_query_id=query.id)
    elif action == "DAY":
        bot.edit_message_text(text=query.message.text,
                              chat_id=query.message.chat_id,
                              message_id=query.message.message_id
                              )
        ret_data = True, datetime.datetime(int(year), int(month), int(day))
    elif action == "PREV-MONTH":
        pre = curr - datetime.timedelta(days=1)
        bot.edit_message_text(text=query.message.text,
                              chat_id=query.message.chat_id,
                              message_id=query.message.message_id,
                              reply_markup=create_calendar(int(pre.year), int(pre.month)))
    elif action == "NEXT-MONTH":
        ne = curr + datetime.timedelta(days=31)
        bot.edit_message_text(text=query.message.text,
                              chat_id=query.message.chat_id,
                              message_id=query.message.message_id,
                              reply_markup=create_calendar(int(ne.year), int(ne.month)))
    else:
        bot.answer_callback_query(callback_query_id=query.id, text="Something went wrong!")

    return ret_data

def morningreport(bot,update): #Remainder
    user = update.message.from_user
    chat_id = update.message.chat_id
    markup = telegram.ReplyKeyboardRemove()
    bot.send_message(update.message.chat_id,
                     "Hello GOOD MORNING " + user.first_name + "! *What are you working on today?*",
                     reply_markup=markup,parse_mode=telegram.ParseMode.MARKDOWN)
    return SAVEEMP1

def eveningreport(bot,update): #Remainder
    user = update.message.from_user
    chat_id = update.message.chat_id
    markup = telegram.ReplyKeyboardRemove()
    bot.send_message(update.message.chat_id,
                     "Hello GOOD EVENING " + user.first_name + "! *What have you Accomplished today?*",
                     reply_markup=markup,parse_mode=telegram.ParseMode.MARKDOWN)
    return SAVEEMP2

def saveemp1(bot,update):#start for employer
    chat_id = update.message.chat_id
    update.message.reply_text("```   Saving...   ```\n",parse_mode=telegram.ParseMode.MARKDOWN)
    a = update.message.text
    update.message.reply_text("Your TASK is: *"+a+"*.",parse_mode=telegram.ParseMode.MARKDOWN)

    ref = db.reference('/')
    ref.child(now).child('employee').child('morningreport').set({"morningreport": a})
    from datetime import datetime
    now2 = datetime.now()
    mtime=now2.strftime("%I:%M %p")
    ref = db.reference('/')
    ref.child(now).child('employee').child('morningreport').child('mortime').set({"mortime":mtime })
    update.message.reply_text(
        "Tap on */eveningreport* to give status report on what have you done today.\nTap on */change* to change TEAM LEADER\n"
        "Tap on */mytask* to see your task.\nTap on */cancel* to END conversation",parse_mode=telegram.ParseMode.MARKDOWN)


def saveemp2(bot,update): #start for employer
    chat_id = update.message.chat_id
    update.message.reply_text("```   Saving...   ```\n",parse_mode=telegram.ParseMode.MARKDOWN)
    a = update.message.text
    update.message.reply_text("Your ACCOMPLISHMENT TODAY : *" + a + "*",parse_mode=telegram.ParseMode.MARKDOWN)
    ref = db.reference('/')
    ref.child(now).child('employee').child('eveningreport').set({"eveningreport": a})
    from datetime import datetime
    now2 = datetime.now()
    etime = now2.strftime("%I:%M %p")
    ref = db.reference('/')
    ref.child(now).child('employee').child('eveningreport').child('evetime').set({"evetime": etime})
    update.message.reply_text(
        "Tap on */morningreport* to Post new TASK\nTap on */change* to change TEAM LEADER\n"
        "Tap on */mytask* to see your task.\nTap on */cancel* to END conversation",parse_mode=telegram.ParseMode.MARKDOWN)


def change(bot,update): #changing admin
    chat_id = update.message.chat_id
    bot.send_message(chat_id=chat_id,
                     text="Please type and send the *CHAT-ID* of your *TEAM LEADER* \n Example: 123456789",parse_mode=telegram.ParseMode.MARKDOWN)
    return CHANGEEMP

def mytask(bot,update): #details for employer 
    chat_id = update.message.chat_id
    user_data = update.message.text
    update.message.reply_text(
            "``` Retrieving data. Please wait.```", parse_mode=telegram.ParseMode.MARKDOWN)
    try:
        ref = db.reference('/' + now)
        a = ref.get()
        fortask = a['task']
        forassign_by = a['assigned_by']
        forduedate = a['due_date']
        task = fortask['task']
        assigned_by = forassign_by['assigned_by']
        due_date = forduedate['due_date']
        update.message.reply_text(" *Here is the TASK assigned by TEAMLEADER*\n"
                                "TASK IS - *" + task +"*\nDUE DATE -   *" + due_date + "*\nASSIGNED BY TEAM LEADER - *" + assigned_by +"*",parse_mode=telegram.ParseMode.MARKDOWN)
        update.message.reply_text(
                "Tap on */morningreport* to Post new TASK\n\nTap on */eveningreport* to give status report on what have you done today.\n\nTap on */change* to change TEAM LEADER\n\n"
                "Tap on */cancel* to END conversation",parse_mode=telegram.ParseMode.MARKDOWN)
    except:
        update.message.reply_text("*Team Leader has not yet ASSIGNED You TASK. Please follow up Yesterday's TASK*"
            "Tap on */morningreport* to Post new TASK\n\nTap on */eveningreport* to give status report on what have you done today.\n\nTap on */change* to change TEAM LEADER\n\n"
            "Tap on */cancel* to END conversation", parse_mode=telegram.ParseMode.MARKDOWN)


def changeemp(bot,update):
    chat_id = update.message.chat_id
    print(chat_id)
    update.message.reply_text("```Saving...```",parse_mode=telegram.ParseMode.MARKDOWN)
    a=str(update.message.text)
    print(a)
    ref = db.reference('/admin')
    a = ref.set({"chat_id": a})
    update.message.reply_text("\n *CHAT-ID with: " +update.message.text+ " is your new TEAM LEADER.*")
    update.message.reply_text(
        "Tap on */morningreport* to Post new TASK\nTap on */eveningreport* to give status report on what have you done today.\n"

        "Tap on */mytask* to see your task.\nTap on */cancel* to END conversation",parse_mode=telegram.ParseMode.MARKDOWN)


def taskupdate(bot,update):
    chat_id = str(update.message.chat_id)
    update.message.reply_text("``` Saving... ```",parse_mode=telegram.ParseMode.MARKDOWN)
    a=update.message.text
    print(update.message.text)
    ref = db.reference('/')
    ref.child(now).child('task').set({"task": a})
    markup = telegram.ReplyKeyboardRemove()
    bot.send_message(update.message.chat_id,"Assigned TASK is - *"+a+"*.\nHas been saved.",
                     reply_markup=markup,parse_mode=telegram.ParseMode.MARKDOWN)
    custom_keyboard = [['/calendar']]
    reply_markup = telegram.ReplyKeyboardMarkup(keyboard=custom_keyboard,
                                                resize_keyboard=True, one_time_keyboard=True)
    update.message.reply_text('Please click on */calendar* to select *DUE DATE* for the TASK',
                              reply_markup=reply_markup,parse_mode=telegram.ParseMode.MARKDOWN)
    return DATE


def newtask(bot,update):
    chat_id = str(update.message.chat_id)
    user_data=update.message.text
    print(user_data)
    if user_data=='ASSIGN NEW TASK':
        custom_keyboard = [['EMPLOYEE 1'],
                           ['EMPLOYEE 2'],
                           ['EMPLOYEE 3']]
        reply_markup = telegram.ReplyKeyboardMarkup(keyboard=custom_keyboard,
                                                    resize_keyboard=True, one_time_keyboard=True)
        bot.send_message(chat_id=chat_id,
                         text="Select the EMPLOYEE to whom you want to ASSIGN TASK.",
                         reply_markup=reply_markup)
        return FINAL
    elif user_data=='VIEW STATUS OF TASKS':
        try:
            update.message.reply_text(
             "``` Retrieving data. Please wait.```",parse_mode=telegram.ParseMode.MARKDOWN)
            ref = db.reference('/' + now)
            a = ref.get()
            fortask = a['task']
            forassign_by=a['assigned_by']
            forassign_to=a['assigned_to']
            forassign_date=a['assigned_date']
            forduedate=a['due_date']
            task = fortask['task']
            assigned_by=forassign_by['assigned_by']
            assigned_to=forassign_to['assigned_to']
            assigned_date=forassign_date['assigned_date']
            due_date=forduedate['due_date']

            update.message.reply_text("***INFORMATION ABOUT TASK.***\n"
                                    "=============================\n"
                                     "TASK IS - *"+task+"*\nASSIGNED DATE - *"+assigned_date+"*\nASSIGNED TO - *"+assigned_to+"*\n"
                                        "DUE DATE -   *"+due_date+"*\nASSIGNED BY - *"+assigned_by+"*\n\n"
                                    ,parse_mode=telegram.ParseMode.MARKDOWN)

            custom_keyboard = [['/viewreport'],
                           ['/start'],
                           ['/cancel']]
            reply_markup = telegram.ReplyKeyboardMarkup(keyboard=custom_keyboard,
                                                    resize_keyboard=True, one_time_keyboard=True)
            bot.send_message(chat_id=chat_id,
                         text="Please select /viewreport to see EMPLOYEE reports\n Tap on /start for HOME MENU.\n Or select /cancel to END the conversation",
                         reply_markup=reply_markup)
        except:
            custom_keyboard = [['/start'],
                               ['/cancel']]
            reply_markup = telegram.ReplyKeyboardMarkup(keyboard=custom_keyboard,
                                                        resize_keyboard=True, one_time_keyboard=True)
            bot.send_message(chat_id=chat_id,
                             text="*YOU HAVE NOT ASSIGNED ANY TASKS YET!*\nTap on /start for HOME MENU.\n Or select /cancel to END the conversation",
                             reply_markup=reply_markup, parse_mode=telegram.ParseMode.MARKDOWN)

    else:
        update.message.reply_text("Please write me the timings of company.\n Example: If you want your OFFICE timing as 9 AM to 6:30 PM, then write it as '09:00-18:30'(use 24-hour clock) and send")
        return TIMING

def viewreport(bot,update):
    chat_id = update.message.chat_id
    try:
        empmor = db.reference('/' + now + '/employee/morningreport')
        empres = empmor.get()
        morrept = empres['morningreport']
        mor = db.reference('/' + now + '/employee/morningreport/mortime')
        mor1 = mor.get()
        mortime = mor1['mortime']

        empeve = db.reference('/' + now + '/employee/eveningreport')
        empres1 = empeve.get()
        everept = empres1['eveningreport']
        eve = db.reference('/' + now + '/employee/eveningreport/evetime')
        eve1 = eve.get()
        evetime = eve1['evetime']
        update.message.reply_text("*Reports of Employee*\n"
            "----------------------------------------\n"
            "MORNING REPORT of Employee - *" + morrept + "*\n Morning report TIME-*" + mortime + "*\n"
            "EVENING REPORT of Employee - *" + everept + "*\n Evening report TIME-*" + evetime + "*\n", parse_mode=telegram.ParseMode.MARKDOWN)
        custom_keyboard = [['/start'],
                           ['/cancel']]
        reply_markup = telegram.ReplyKeyboardMarkup(keyboard=custom_keyboard,
                                                    resize_keyboard=True, one_time_keyboard=True)
        bot.send_message(chat_id=chat_id,
                         text="Please select */start* for *HOME MENU*.\n Or select */cancel* to *END* the conversation",
                         reply_markup=reply_markup, parse_mode=telegram.ParseMode.MARKDOWN)

    except:
        update.message.reply_text("*There are NO REPORTS from Employees, Please check after office Timings*",
                                  parse_mode=telegram.ParseMode.MARKDOWN)
        custom_keyboard = [['/start'],
                           ['/cancel']]
        reply_markup = telegram.ReplyKeyboardMarkup(keyboard=custom_keyboard,
                                                    resize_keyboard=True, one_time_keyboard=True)
        bot.send_message(chat_id=chat_id,
                         text="Please select */start* for *HOME MENU*.\n Or select */cancel* to *END* the conversation",
                         reply_markup=reply_markup, parse_mode=telegram.ParseMode.MARKDOWN)

def timing(bot,update):
    from datetime import datetime
    chat_id = update.message.chat_id
    a=update.message.text
    b=a.split('-')
    try:
        d1 = datetime.strptime(b[0], "%H:%M")
        d11=d1.strftime("%I:%M %p")
        d2 = datetime.strptime(b[1], "%H:%M")
        d22=d2.strftime("%I:%M %p")
        stt=d1.strftime("%H:%M")
        stp = d2.strftime("%H:%M")
        isValid = True
        update.message.reply_text("``` Saving... ```",parse_mode=telegram.ParseMode.MARKDOWN)
        ref = db.reference('/')
        ref.child('office_time').child('start').set({"start": stt})
        ref = db.reference('/')
        ref.child('office_time').child('close').set({"close": stp})
        markup = telegram.ReplyKeyboardRemove()
        bot.send_message(update.message.chat_id,
                         "The timings have been changed.\n NEW OFFICE timing is *" + d11 + "* to *" + d22+"*",
                         reply_markup=markup,parse_mode=telegram.ParseMode.MARKDOWN)
        custom_keyboard = [['/start'],
                           ['/cancel']]
        reply_markup = telegram.ReplyKeyboardMarkup(keyboard=custom_keyboard,
                                                    resize_keyboard=True, one_time_keyboard=True)
        bot.send_message(chat_id=chat_id,
                         text="Employees will now get the *NOTIFICATIONS* on above specified time.\n Please select /start for HOME MENU.\n Or select /cancel to END the conversation",
                         reply_markup=reply_markup,parse_mode=telegram.ParseMode.MARKDOWN)
    except:
        custom_keyboard = [['/start']]
        reply_markup = telegram.ReplyKeyboardMarkup(keyboard=custom_keyboard,
                                                    resize_keyboard=True, one_time_keyboard=True)
        update.message.reply_text('*INCORRECT DATE!!*\nMust be in HH:MM-HH:MM format\n Please click on /start and select CHANGE TIMINGS.\n',
                                  reply_markup=reply_markup,parse_mode=telegram.ParseMode.MARKDOWN)

def selectemployee(bot,update):
    chat_id = update.message.chat_id
    user_data = update.message.text
    print(user_data)
    custom_keyboard = [['EMPLOYEE 1'],
                       ['EMPLOYEE 2'],
                       ['EMPLOYEE 3']]
    reply_markup = telegram.ReplyKeyboardMarkup(keyboard=custom_keyboard,
                                                resize_keyboard=True, one_time_keyboard=True)
    bot.send_message(chat_id=chat_id,
                     text="Select the EMPLOYEE to whom you want to ASSIGN TASK.",
                     reply_markup=reply_markup)
    return FINAL

def final(bot,update):
    chat_id = str(update.message.chat_id)
    user_data = update.message.text
    update.message.reply_text("```Saving...```",parse_mode=telegram.ParseMode.MARKDOWN)
    update.message.reply_text("\nYou have Assigned TASK to *"+user_data+"*",parse_mode=telegram.ParseMode.MARKDOWN)
    print(user_data)
    ref = db.reference('/')
    ref.child(now).child('assigned_to').set({"assigned_to": user_data})
    bot.send_message(chat_id=chat_id,
                     text="Please Type the TASK to proceed. \n For example: Work on some project.\n After typing Tap on send.")
    return TASKUPDATE

def calendar_handler(bot,update):
    update.message.reply_text("Please select *DUE DATE* for the TASK: ",
                        reply_markup=create_calendar(),parse_mode=telegram.ParseMode.MARKDOWN)
def inline_handler(bot,update):
    selected, date = process_calendar_selection(bot, update)
    if selected:
        today = date.today()
        now = today.strftime("%d,%m,%Y")
        tmp = date.strftime("%d,%m,%Y")
        tmp1 = date.strftime("%d-%m-%Y")
        print(tmp)
        if tmp > now:
            print("succes")
            chat_id = str(update.callback_query.from_user.id)
            bot.send_message(chat_id=update.callback_query.from_user.id,
                            text="DUE DATE for assigned WORK is- *%s*" % (date.strftime("%d / %m / %Y")),
                            reply_markup=ReplyKeyboardRemove(),parse_mode=telegram.ParseMode.MARKDOWN)
            today = date.today()
            now = today.strftime("%d-%m-%Y")
            ref = db.reference('/')
            ref.child(now).child('assigned_date').set({"assigned_date": now})
            ref.child(now).child('due_date').set({"due_date": tmp1})
            custom_keyboard = [['/start'],
                               ['/cancel']]
            reply_markup = telegram.ReplyKeyboardMarkup(keyboard=custom_keyboard,
                                                        resize_keyboard=True, one_time_keyboard=True)
            bot.send_message(chat_id=update.callback_query.from_user.id,
                             text="DONE.\nPlease select */start* for *HOME MENU*.\n Or select */cancel* to *END* the conversation",
                             reply_markup=reply_markup,parse_mode=telegram.ParseMode.MARKDOWN)

        else:
            bot.send_message(chat_id=update.callback_query.from_user.id,
                            text="*INCORRECT!!*,Please select the DATE again: ",
                                      reply_markup=create_calendar(),parse_mode=telegram.ParseMode.MARKDOWN)

def cancel(bot, update, user_data):
    user = update.message.from_user
    markup = telegram.ReplyKeyboardRemove()
    bot.send_message(update.message.chat_id, "Bye "+user.first_name+"! See you again later.",
                     reply_markup=markup)
    logger.info("User %s canceled the conversation." % user.first_name)
    user_data.clear()
    return ConversationHandler.END

def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    updater = Updater("<token>") ###################### Add your telegram token here. ##############################
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("calendar", calendar_handler))
    dp.add_handler(CallbackQueryHandler(inline_handler))
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            NEWTASK: [MessageHandler(Filters.regex('^(ASSIGN NEW TASK|VIEW STATUS OF TASKS|CHANGE TIMINGS)$'), newtask)],
            TASKUPDATE: [MessageHandler(Filters.text, taskupdate)],
            SAVEEMP1: [MessageHandler(Filters.text, saveemp1)],
            SAVEEMP2: [MessageHandler(Filters.text, saveemp2)],
            CHANGEEMP: [MessageHandler(Filters.text, changeemp)],
            FINAL: [MessageHandler(Filters.regex('^(EMPLOYEE 1|EMPLOYEE 2|EMPLOYEE 3)$'), final)],
            TIMING: [MessageHandler(Filters.text, timing)],
            DATE: [MessageHandler(Filters.text, calendar_handler)],
        },
        fallbacks=[CommandHandler('cancel', cancel,pass_user_data=True),
                   CommandHandler('start', start),
                   CommandHandler('viewreport', viewreport),
                   CommandHandler('selectemployee', selectemployee),
                   CommandHandler('mytask', mytask),
                   CommandHandler('morningreport', morningreport),
                   CommandHandler('eveningreport', eveningreport),
                   CommandHandler('change', change)]
    )
    dp.add_handler(conv_handler)
    dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()
if __name__ == '__main__':
    main()
