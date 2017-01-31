# -*- coding: utf-8 -*-

from telegram import (ReplyKeyboardMarkup, ReplyKeyboardHide)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler, ConversationHandler)
from apscheduler.schedulers.background import BackgroundScheduler
import sys
import logging
import datetime
import db_manager
import lessons

reload(sys)
sys.setdefaultencoding('utf8')

scheduler = BackgroundScheduler()

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

INSTITUTE, CATHEDRA, DIRECTION, GROUP = range(4)

daysOfWeek =  { "Monday":"Понедельник", 
                "Tuesday":"Вторник", 
                "Wednesday":"Среда", 
                "Thursday":"Четверг", 
                "Friday":"Пятница", 
                "Saturday":"Суббота", 
                "Sunday":"Воскресенье" }

lessonsTime = [
    "8.30-10.00",
    "10.10-11.40",
    "11.50-13.20",
    "13.50-15.20",
    "15.30-17.00",
    "17.10-18.40",
    "18.50-20.20",
    "20.30-22.00"
]

subjects = {
    "Институт экономики" : {
        "Кафедра внешнеэкономической деятельности": {
            "Внешнеэкономическая деятельность" : ["ВЭД-14", "ВЭД-15", "ВЭД-16-1,2"]  # ВЭД
        },
        #"Кафедра мировой экономики": {
        #    "Мировая экономика", #
        #},
        "Кафедра региональной, муниципальной экономики и управления": {
            "Региональная экономика" : ["РЭ-13", "РЭ-14", "РЭ-15"],
            "Экономика малого и среднего предпринимательства" : ["ЭМиСП-14", "ЭМиСП-16"],
            #"Экономика недвижимости",
            "Экономическая безопасность" : ["ЭБ-13", "ЭБ-14-1", "ЭБ-14-2", "ЭБ-15-1", "ЭБ-15-2", "ЭБ-16 (ФСП)", "ЭБ-16-1", "ЭБ-16-2,3"],
            #"Государственное и муниципальное управление",
            #"Экономика малого и среднего предпринимательства",
            "Землеустройство и кадастры": ["ЗК-13", "ЗК-14", "ЗК-15"]
            #"Государственное управление и местное самоуправление",
            #"Экономико-правовая безопасность",
            #"Экономика недвижимости и девелопмент территорий",
            #"Региональное управление и местное самоуправление",

        },
        "Кафедра экономики предприятий": {
            #"Экономика и организация пищевых производств",
            "Экономика предприятий и организаций": ["ЭП-13-1", "ЭП-13-2", "ЭП-14", "ЭП-14-1 2ВПО (веч)", "ЭП-15", "ЭП-16"]
        },
        #"Кафедра корпоративной экономики и управления бизнесом": {
        #    "Корпоративная экономика и управление бизнесом",
        #},
        #"Кафедра общей и экономической истории": {
#
        #},
        #"Кафедра делового иностранного языка": {
#
        #},
        "Кафедра логистики": {
            "Логистика": ["Лог-15", "Л-13", "Л-14", "Л-16"], #ЛОГ
        },
        #"Кафедра экономики жилищного, коммунального хозяйства и энергетики": {
#
        #},
        #"Кафедра государственного и муниципального управления": {
        #    "Государственная и муниципальная служба",
        #},
        "Кафедра экономики и права": {
            "Экономика и право": ["ЭКИП-13", "ЭКиП-14", "ЭКиП-15", "Экип-16"],
        }
    },
    "Институт менеджмента и информационных технологий": {
        "Кафедра статистики, эконометрики и информатики": {
            "Математическое обеспечение и администрирование информационных систем" : ["ЭМА-13", "ЭМА-14", "ЭМА-15", "ЭМА-16-1", "ЭМА-16-2"], # ЭМА
            "Информатика и вычислительная техника" : ["ИВТ-13", "ИВТ-14", "ИВТ-15", "ИВТ-16"], # ИВТ
            "Прикладная информатика" : ["ПИЭ-13-1", "ПИЭ-13-2", "ПИЭ-14-1", "ПИЭ-14-2", "ПиЭ-15", "ПИЭ-16-1,2"], # ПИЭ
        },
        "Кафедра бизнес-информатики": {
            "Информационная безопасность" : ["ИБ-14", "ИБ-15", "ИБ-16"], # ИБ
            "Бизнес-информатика": ["БИ-13", "БИ-14", "БИ-15", "БИ-16-1", "БИ-16-2"]
        },
        #"Кафедра менеджмента": {
        #    "Менеджмент в спорте",
        #    "Менеджмент организации",
        #    "Производственный менеджмент",
        #    "Управление малым бизнесом",
        #},
        "Кафедра маркетинга и международного менеджмента": {
            "Маркетинг" : ["МАР-13", "МАР-14", "Мар-15", "МАР-15 ФСП2", "Мар-16"],
            #"Маркетинг и реклама в сфере услуг",
            "Международный менеджмент" : ["ММ-13-1", "ММ-13-2", "ММ-13-3", "ММ-14-1", "ММ-14-2", "ММ-15-1", "ММ-15-2", "ММ-16-1,2"],
            #"Промышленный маркетинг",
            #"Рекламный менеджмент",
        },
        #"Кафедра прикладной математики": {
#
        #},
        #"Кафедра прикладной социологии": {
#
        #},
        #"Кафедра философии": {
#
        #},
        #"Кафедра экономики труда и управления персоналом": {
        #    "Экономика труда",
        #    "Управление персоналом",
#
        #},
        #"Кафедра физического воспитания и спорта": {
#
        #}
    },
    #"Институт торговли, пищевых технологий и сервиса" : {
    #    "Кафедра коммерции, логистики и экономики торговли": {
    #        #Торговое дело  Международная коммерция 
    #        #Экономика торговли и общественного питания
    #    },
    #    "Кафедра пищевой инженерии": {
    #        "Биотехнология"
    #    },
    #    "Кафедра технологии питания": {
    #        "Технология продукции и организации общественного питания"
    #    },
    #    "Кафедра товароведения и экспертизы": {
    #        "Товарный менеджмент",
    #        "Товароведение и экспертиза в сфере производства и обращения непродовольственных товаров и сырья",
    #        "Товароведение и экспертиза в сфере производства сельскохозяйственного сырья и продовольственных товаров",
    #        "Товароведение и экспертиза товаров в таможенной деятельности",
    #        "Товароведение"
    #    },
    #    "Кафедра туристического бизнеса и гостеприимства": {
    #        "Международный сервис" # Сервис
    #        "Туризм" #Базовый
    #        "Гостиничная деятельность" # Гостиничное дело
    #        "Ресторанная деятельность"
    #    },
    #    "Кафедра управления качеством": {
    #        "Управление качеством"
    #    },
    #    "Кафедра физики и химии": {
#
    #    },
    #    "Кафедра иностранных языков": {
#
    #    }
    #},
    "Институт финансов и права" : {
        'Кафедра финансовых рынков и банковского дела': {
            "Банковское дело" : ["БД-13-1", "БД-13-2", "БД-14", "БД-16"], # БД
            #"Финансовые рынки и биржевые технологии",
            #"Финансы и бухгалтерский учет",
            #"Финансы и кредит",

        },
        "Кафедра государственных и муниципальных финансов": {
            "Государственные и муниципальные финансы" : ["ГМФ-13", "ГМФ-14", "ГМФ-15"]
            #"Налогообложение и налоговое администрирование",
        },
        "Кафедра бухгалтерского учёта и аудита": {
            "Бухгалтерский учет, анализ и аудит" : ["БУА-13", "БУА-14-1", "БУА-14-1 2ВПО (веч)", "БУА-14-2", "БУА-15", "БУА-16"], # БУА
        },
        #"Кафедра финансового менеджмента": {
        #    "Финансовый менеджмент" : [],
#
        #},
        #"Кафедра публичного права": {
        #    "Правовое обеспечение деятельности государственных и муниципальных органов" : [],
        #},
        #"Кафедра теории государства и права": {
#
        #},
        #"Кафедра предпринимательского права": {
        #    "Коммерческо-правовой" : [],
        #},
        "Кафедра гражданского права": {
            #"Юриспруденция" : [],
            "Гражданско-правовой" : ["ГПЮ-15-1 (ФСП)", "ГПЮ-15-КиП (ФСП)", "ГПЮ-16 - КиП (ФСП)", "ГПЮ-16-1 (ФСП)", "ГПЮ-16-2 (ФСП)"],

        }
    },
    "Институт непрерывного образования" : {
        "Гостиничное дело" : ["ГД-13", "ГД-14", "ГД-15", "ГД-15 ФСП2", "ГД-16"],
        "Государственное и муниципальное управление": ["ГМС-13", "ГМС-14-1", "ГМС-14-2", "ГМС-15", "ГМС-16", "ГМУ-13", "ГМУ-15 ФСП2", "ГМУ-16 (ФСП)"],
    },
    "Департамент магистратуры" : {
        "Заочное отделение": {
            "Внешнеэкономическая деятельность предприятия" : ["ЗМ-ВЭД-16"],
            "Государственное управление и местное самоуправление": ["ЗМ-ГУМС-16"],
            "Конкурентная разведка в международном бизнесе" : ["ЗМ-КРМБ-16"],
            "Экономика и организация предпринимательской деятельности" : ["ЗМ-ОПД-16"],
            "Стратегическое планирование в сфере государственного управления" : ["ЗМ-СПГУ-16"],
            "Технологии государственного администрирования" : ["ЗМ-ТГА-16"],
            "Экономика и управление персоналом организации" : ["ЗМ-УП-16"],
            "Финансовый и банковский менеджмент" : ["ЗМ-ФиБМ-16"],
            "Финансовый, управленческий, налоговый учет, анализ и аудит" : ["ЗМ-ФУА-16"],
            "Экономика и право коммерческих и некоммерческих организаций" : ["ЗМ-ЭКиП-16"],
        },
        "Очное отделение": {
            "Безопасность государственного управления и противодействие коррупции": ["М-БГУ-15", "М-БГУ-15-3"],
            "Информационная бизнес-аналитика" : ["М-БИ-15-3", "М-БИ-16"],
            "Внешнеэкономическая деятельность предприятия" : ["М-ВЭД-15", "М-ВЭД-16-3"],
            "Государственный аудит в национальной экономике" : ["М-ГСА-15", "М-ГСА-15-3"],
            "Корпоративные информационные системы" : ["М-КИС-15", "М-КИС-16"],
            "Корпоративная экономика и управление" : ["М-КУ-16"],
            "Маркетинг и брендинг" : ["М-МиБ-15", "М-МиБ-15-3", "М-МиБ-16", "М-МиБ-16-3"],
            "Стратегическое планирование в сфере государственного управления" : ["М-СПГУ-15", "М-СПГУ-16-3"],
            "Стратегическое управление" : ["М-СУ-15", "М-СУ-16-3"],
            "Технологии государственного администрирования" : ["М-ТГА-15-3", ],
            "Товарный консалтинг и экспертиза во внутренней и внешней торговле" : ["М-ТК-16", ],
            "Организация производства и обслуживания на предприятиях общественного питания" : ["М-ТПП-15", "М-ТПП-16"],
            "Управление в логистических системах" : ["М-УЛС-15", "М-УЛС-15-3"],
            "Управление и экономика персонала" : ["М-УП-16"],
            "Управление проектами и программами" : ["М-УПР-15", "М-УПР-15-3", "М-УПР-16"],
            "Менеджмент в гостиничном и туристическом бизнесе" : ["М-УТиБ-15", "М-УТиБ-15-3", "М-УТиБ-16"],
            "Финансовый и банковский менеджмент" : ["М-ФиБМ-16", "М-ФиБМ-16-3"],
            "Финансовые рынки: участники, технологии, инструменты" : ["М-ФР-16"],
            "Финансовый и банковский менеджмент" : ["М-ФРиБД-15-3 (ФиБМ)", "М-ФРиБД-15-3 (ФК)"],
            "Финансовый, управленческий, налоговый учет, анализ и аудит" : ["М-ФУА-15", "М-ФУА-15-3", "М-ФУА-16-3"],
            "Экономика здравоохранения" : ["М-ЭЗ-15-3"],
            "Экономика и право деятельности коммерческих и некоммерческих организаций" : ["М-ЭиП-15-3"],
            "Экономика недвижимости и девелопмент территорий" : ["М-ЭНД-15", "М-ЭНД-15-3"],
            "Экономико-правовая безопасность" : ["М-ЭПБ-15", "М-ЭПБ-15-3", "М-ЭПБ-16"],
            "Экономика и управление персоналом" : ["М-ЭУП-15", "М-ЭУП-15-3"],
            "Экономика фирмы" : ["М-ЭФ-15", "М-ЭФ-16", "М-ЭФ-16-3"],
        }
    }
}

def start(bot, update, user_data):
    reply_keyboard = list([x] for x in subjects.keys())
    reply_keyboard.insert(0, ["Назад".decode("utf-8")])

    update.message.reply_text(
        'Выберите институт.',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False))
    return INSTITUTE

def institute_choice(bot, update, user_data):
    user = update.message.from_user
    #logger.info("Gender of %s: %s" % (user.first_name, update.message.text))
    msg = update.message.text.encode("utf-8")
    user_data["institute"] = msg

    if user_data["institute"] == "Институт непрерывного образования":
        directions = subjects.get(user_data["institute"])
        reply_keyboard = list([x.decode("utf-8")] for x in directions.keys())

        update.message.reply_text('Выберите направление.',
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False))
        return DIRECTION

    cathedrals = subjects.get(user_data["institute"])

    reply_keyboard = list([x.decode("utf-8")] for x in cathedrals.keys())
    reply_keyboard.insert(0, ["Назад".decode("utf-8")])

    update.message.reply_text('Выберите кафедру.',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False))

    return CATHEDRA

def cathedra_choice(bot, update, user_data):
    msg = update.message.text.encode("utf-8") # chosen cathedra

    if msg in subjects.get(user_data["institute"]):
        user_data["cathedra"] = msg
        print 'Chosen group' + msg
    else:
        print "No cathedra " + msg
        return CATHEDRA

    directions = subjects.get(user_data["institute"]).get(user_data["cathedra"])
    
    if len(directions) == 0:
        update.message.reply_text('Для этой кафедры пока нет расписания.')
        return CATHEDRA

    reply_keyboard = list([x.decode("utf-8")] for x in directions.keys())
    reply_keyboard.insert(0, ["Назад".decode("utf-8")])

    update.message.reply_text('Выберите направление.',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False))
    return DIRECTION

def direction_choice(bot, update, user_data):
    msg = update.message.text.encode("utf-8") # chosen direction

    if user_data["institute"] == "Институт непрерывного образования":
        s = subjects.get(user_data["institute"])
    else:
        s = subjects.get(user_data["institute"]).get(user_data["cathedra"])

    if msg in s:
        user_data["direction"] = msg
        print 'Chosen direction' + msg
    else:
        print "No direction " + msg
        return DIRECTION
    #logger.info("Gender of %s: %s" % (user.first_name, update.message.text))

    groups = s.get(user_data["direction"])

    reply_keyboard = list([x.decode("utf-8")] for x in groups)
    reply_keyboard.insert(0, ["Назад".decode("utf-8")])

    update.message.reply_text('Выберите группу.',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False))

    return GROUP

def group_choice(bot, update, user_data):
    msg = update.message.text.encode("utf-8") # chosen group

    if user_data["institute"] == "Институт непрерывного образования":
        s = subjects.get(user_data["institute"])
    else:
        s = subjects.get(user_data["institute"]).get(user_data["cathedra"])

    if msg in s.get(user_data["direction"]):
        user_data["group"] = msg
        print 'Chosen group' + msg
    else:
        print "No group " + msg
        return GROUP

    sendTimetable(user_data["group"], update)

    return GROUP

def sendTimetable(name, update):
    now = datetime.datetime.now()
    tt = db_manager.getTimetable(name)

    if tt is None or len(tt) == 0:
        update.message.reply_text('Нет расписания.')
        return GROUP

    assert(len(tt) == 2)

    tomorrow = (now + datetime.timedelta(days=1))

    timtableText = "Расписание для _" + name + ('_\n*На сегодня* (%s, %s):\n' % (daysOfWeek[now.strftime("%A")], now.strftime("%d.%m.%Y"))) + createTimetableText(tt[0]) + '*На завтра* (%s, %s):\n' % (daysOfWeek[tomorrow.strftime("%A")], tomorrow.strftime("%d.%m.%Y")) + createTimetableText(tt[1])
            
    update.message.reply_text(timtableText, parse_mode="Markdown")
    return

def createTimetableText(table):
    timtableText = ""
    n = 0
    for l in table:
        n = n + 1
        if l[0] == "null":
            continue
        timtableText = timtableText + ("  %d. %s - %s, %s, %s\n" % (n, lessonsTime[n], l[0], l[1], l[2]))
    if timtableText == "":
        return "  Неучебный день\n"
    return timtableText

def back_cathedra(bot, update, user_data):
    reply_keyboard = list([x] for x in subjects.keys())
    reply_keyboard.insert(0, ["Назад".decode("utf-8")])

    update.message.reply_text(
        'Выберите институт.',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False))
    return INSTITUTE

def back_direction(bot, update, user_data):
    if user_data["institute"] == "Институт непрерывного образования":
        return back_cathedra(bot, update, user_data)

    cathedrals = subjects.get(user_data["institute"])

    reply_keyboard = list([x.decode("utf-8")] for x in cathedrals.keys())
    reply_keyboard.insert(0, ["Назад".decode("utf-8")])

    update.message.reply_text('Выберите кафедру.',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False))

    return CATHEDRA

def back_group(bot, update, user_data):
    if user_data["institute"] == "Институт непрерывного образования":
        directions = subjects.get(user_data["institute"])
    else:
        directions = subjects.get(user_data["institute"]).get(user_data["cathedra"])

    reply_keyboard = list([x.decode("utf-8")] for x in directions.keys())
    reply_keyboard.insert(0, ["Назад".decode("utf-8")])

    update.message.reply_text('Выберите направление.',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard))

    return DIRECTION

def cancel(bot, update):
    user = update.message.from_user
    logger.info("User %s canceled the conversation." % user.first_name)
    update.message.reply_text('Bye! I hope we can talk again some day.',
                              reply_markup=ReplyKeyboardHide())

    return ConversationHandler.END

def timetable_command(bot, update, user_data):
    group = update.message.text[11:].strip().encode("utf-8") # group

    if group in db_manager.groupNames:
        sendTimetable(group, update)
    else:
        update.message.reply_text('Неверное название группы.')
    return

def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))


def main():
    db_manager.init()
    logger.info(daysOfWeek["Monday"])

    job = scheduler.add_job(lessons.updateAllTimeTable, 'interval', hours=3)
    scheduler.start()

    #lessons.updateAllTimeTable()

    logger.info("yolo")

    institutesRegex = ('^(' + '|'.join(str(x) for x in subjects.keys()) + ')$').decode("utf-8")
    backRegex = '^(Назад)$'.decode("utf-8")

    updater = Updater("315708415:AAFyAAFCl_IHd19hJbqWxaB65UNilzJsCX4")

    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points = [
            CommandHandler('start', start, pass_user_data=True),
            MessageHandler(Filters.text, start, pass_user_data=True)
        ],

        states = {
            INSTITUTE: [
                RegexHandler(institutesRegex, institute_choice, pass_user_data=True)
            ],
            CATHEDRA: [
                RegexHandler(backRegex, back_cathedra, pass_user_data=True),
                MessageHandler(Filters.text, cathedra_choice, pass_user_data=True)
            ],
            DIRECTION: [
                RegexHandler(backRegex, back_direction, pass_user_data=True),
                MessageHandler(Filters.text, direction_choice, pass_user_data=True)
            ],
            GROUP: [
                RegexHandler(backRegex, back_group, pass_user_data=True),
                MessageHandler(Filters.text, group_choice, pass_user_data=True)
            ],
        },

        fallbacks=[
            CommandHandler('cancel', cancel)
        ],

        allow_reentry = False
    )

    dp.add_handler(conv_handler)
    dp.add_handler(CommandHandler('timetable', timetable_command, pass_user_data=True))

    dp.add_error_handler(error)

    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()