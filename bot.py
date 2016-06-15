
#!/usr/bin/env python
# -*- coding: utf-8 -*-

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from mcstatus import MinecraftServer
from geopy.geocoders import Nominatim

import forecastio

import logging
import sys
import os
import pickle
import time
import random

api_key = "key"
moduledir = "{0}/modules/".format(os.getcwd())
server = MinecraftServer.lookup("ip")
TOKEN = 'TOKEN'
forecast_info = {}
modules = {}
dp = ""

secret_words = ["unique", "keyboard", "computer", "certificate", "morning", "sunshine", "space", "display", "checker", "music", "pineapple", "insane", "massive", "nice"]


################
####  TODO  ####
################
#
# Todo list fucntion
#    - add and remove items
#    - mark as complete
#    - list items
#    - flags for importance
#
#
# Secret Word Game
#    - new word every 24 hrs
#    - leaderboard
#
# 
# Freedom Unit converter
#    - command for converting
#    - regex match for auto conversion
#    - inline bot command for quick conversion
#
#
# Weather/Forecast
#
#   - Feels like temp to current conditions
#
#

#Logging

root = logging.getLogger()
root.setLevel(logging.INFO)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
root.addHandler(ch)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

rw = random.choice(secret_words)
print "the random word is: {0}".format(rw)


def save_db(db):
    logger.info("Saving forecast DB")
    pickle.dump(db, open("locations.p", "wb"))


def load_db():
    logger.info("Loading forecast DB")
    db = pickle.load(open ("locations.p", "rb"))
    return db
    

def getLatLong(location):
    geolocator = Nominatim()
    location = geolocator.geocode(location)

    try:
        lat, lon = location.latitude, location.longitude
    except AttributeError as e:
        logger.error(e)
        return (None, None)
    return (lat, lon)


def toKM(d):
    # return distance converted to KM (2 decimal points)
    return "{0:.2f}".format(1.609 * d)


def getForecast(lat, lon, o, local):
    forecast = forecastio.load_forecast(api_key, lat, lon)
    if o == 'c' or not o:
        fcast = "It is currently: {0} \n"\
                "The temperature is: {1}".format(forecast.currently().summary, forecast.currently().temperature)
    elif o == 'h':
        fcast = forecast.hourly().data
    elif o == 'd':
        fcast = forecast.daily().summary
    elif o == 'w':
        try:
            stormdist = forecast.currently().nearestStormDistance
            if stormdist == 0:
                storm = "\nThere is currently a storm in your area."
            else:
                if getCountry(local) == "Canada":
                    storm = "\nThe nearest storm is {0}KM away".format(toKM(stormdist))
                else:
                    storm = "\nThe nearest storm is {0} miles away".format(stormdist)
        except:
            e = sys.exc_info()[0]
            logger.error(e)
            storm = ""
        ds = u"\N{DEGREE SIGN}"
        ws = "{0}mph".format(forecast.currently().windSpeed)
        at = "{0}{1}F".format(forecast.currently().temperature, ds.encode('utf-8'))
        flt = "{0}{1}F".format(forecast.currently().apparentTemperature, ds.encode('utf-8'))
        print getCountry(local)
        if getCountry(local) == "Canada":
            ws = "{0}km/h".format(toKM(forecast.currently().windSpeed))
            at = "{0}{1}C".format(forecast.currently().temperature, ds.encode('utf-8'))
            flt = "{0}{1}C".format(forecast.currently().apparentTemperature, ds.encode('utf-8'))

        fcast = "It is currently {0} and feels like {1}\n"\
                "The actual temperature is {2} with a windspeed of {3}{4}".format(forecast.currently().summary,
                                                                            flt, at, ws, storm)
        if at == flt:
            fcast = "It is currently {0} with a temperature of {1} and a windspeed of {2}{3}".format(forecast.currently().summary,
                                                                                                     at, ws, storm)
    return fcast


def help(bot, update):
    bot.sendMessage(update.message.chat_id, text='Available commands are:\n'
                    'memecraft - Diplays information about the memecraft server\n'
                    'forecast - Display weather information based on location')


def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))


def stats(bot, update):
    if update.message.text:
        if update.message.from_user.username:
            user = update.message.from_user.username
        else:
            user = update.message.from_user.first_name
        ts = time.strftime("%H:%M:%S")
        text = update.message.text
        print "{0} <{1}> {2}".format(ts, user, text)

        if rw in update.message.text.split():
            bot.sendMessage(update.message.chat_id, text='You said the secret word ({0}) Conrats! full marks.'.format(rw))


def getCountry(l):
    geolocator = Nominatim()
    location = geolocator.geocode(l)
    location = location.raw.get("display_name")
    country = location.split(", ")[-1]
    return country

    
def weather(bot, update):
    message = update.message.text

    if len(message.split()) > 1:
        local = message.split(' ', 1)[1]
        lat, lon = getLatLong(local)
        if lat == None:
            bot.sendMessage(update.message.chat_id, "That place does not exist in this reality.")
            return
        else:
            forecast = getForecast(lat, lon, "w", local)
            bot.sendMessage(update.message.chat_id, forecast)
    else:
        nm = update.message.from_user.id
        logger.info("Getting current weather info for {}".format(nm))
        local = forecast_info.get(nm)
        lat, lon = getLatLong(local)
        if (lat == None) or (local == None):
            logger.warn("No location saved or invalid location")
            bot.sendMessage(update.message.chat_id, "No location saved, use \"/setlocation <LOCATION>\" to set your default location.")
            return
        else:
            forecast = getForecast(lat, lon, "w", local)
            bot.sendMessage(update.message.chat_id, forecast)

            
def forecast(bot, update):
    message = update.message.text
    if len(message.split()) > 1:
        if message.split()[1].startswith('-'):
            o = message.split()[1][1]
            local = message.split(' ', 2)[2]
        else:
            o = None
            local = message.split(' ',1)[1]
        lat, lon = getLatLong(local)
        if lat == None:
            bot.sendMessage(update.message.chat_id, "That place does not exist in this reality.")
        else:
            forecast = getForecast(lat, lon, o, local)

            bot.sendMessage(update.message.chat_id, forecast)
    else:
        nm = update.message.from_user.id
        logger.info("Getting forecast info for {}".format(nm))
        local = forecast_info.get(nm)
        lat, lon = getLatLong(local)
        if (lat == None) or (local == None):
            logger.info("No locataion saved")
            bot.sendMessage(update.message.chat_id, "No location saved, use \"/setlocation <LOCATION>\" to set your default location.")
            return
        else:
            forecast = getForecast(lat, lon, "d", local)
            bot.sendMessage(update.message.chat_id, forecast)

        
def set_local(bot, update):
    global forecast_info
    message = update.message.text
    location = message.split(' ', 1)[1]
    user_id = update.message.from_user.id
    forecast_info[user_id] = location
    bot.sendMessage(update.message.chat_id, "Location saved as: {}".format(location))


def rehash(bot, update):
    """Reload modules."""
    if update.message.from_user.username == "SL0RD":
        loadmodules()
        reloadcommands()
        bot.sendMessage(update.message.chat_id, "Modules have been reloaded.")

        
def loadcommands():
    """Load commands into command handler."""
    for m, env in modules.items():
        myglobals, mylocals, = env
        commands = [(c, ref) for c, ref in mylocals.items()
                    if c.startswith("command_")]
        for (t, f) in commands:
            print "Loading command: {}".format(t[8:])
            dp.add_handler(CommandHandler(t[8:], f))


def reloadcommands():
    for m, env in modules.items():        
        myglobals, mylocals, = env
        commands = [(c, ref) for c, ref in mylocals.items()
                    if c.startswith("command_")]
        for (t, f) in commands:
            print "Unloading command: {}".format(t[8:])
            dp.remove_handler(CommandHandler(t[8:], f))
            print "Loading command: {}".format(t[8:])
            dp.add_handler(CommandHandler(t[8:], f))
                

def loadmodules():
    """Load modules for use"""
    for module in findmodules():
        env = {}
        logging.info("loading module - {}".format(module))
        execfile(os.path.join(moduledir, module), env, env)
        modules[module] = (env, env)
                 
    
def findmodules():
    """Find all modules"""
    modules = [m for m in os.listdir(moduledir)
               if m.startswith("module_") and m.endswith(".py")]
    return modules
        
def main():
    global forecast_info
    global dp
    
    loadmodules()

    forecast_info = load_db()
    updater = Updater(TOKEN)

    dp = updater.dispatcher

    loadcommands()
    
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("rehash", rehash))
    dp.add_handler(CommandHandler("forecast", forecast))
    dp.add_handler(CommandHandler("weather", weather))
    dp.add_handler(CommandHandler("setlocation", set_local))

    dp.add_handler(MessageHandler([Filters.text], stats))
    
    dp.add_error_handler(error)

    updater.start_polling(timeout=5)

    while True:
        text = raw_input()

        if text == 'stop':
            save_db(forecast_info)
            updater.stop()
            break
            
            
if __name__ == '__main__':
    main()
