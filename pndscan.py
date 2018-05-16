#!/usr/bin/python3
 
#released under public domain
 
import time
import os
import decimal
import math
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging
from functools import wraps
try:
	from urllib.request import urlopen
except ImportError:
    from urllib2 import urlopen
import json
import smtplib
import datetime
import threading
from mwt import MWT
chatid = -1001227218211
l = []
d = {}
 
CHANGE = -0.02 #the sign is inverse so a positive number here actually looks for a decrease by that amount
CHANGEDOWN = 0.02
MINBTCVOLUME = 30
MARKET = "BTC-" #Can be ETH- LTC- etc.

def getData():
    try:
        summaries = urlopen("https://bittrex.com/api/v1.1/public/getmarketsummaries").read().decode("utf-8")
        summaries = json.loads(summaries)
        callResult = 1
        return(summaries)
    except:
        callResult = 0
        return callResult

def analizza(bot, update):
	print("Inizio scansione Bittrex..")
	while True:
		try:
			summaries = getData()
			if summaries != 0:
				if l == []:
					for _ in range(20):
						l.append(summaries)
			
				del(l[0])
				l.append(summaries)
				if not len(l[0]['result']) == len(l[19]['result']):
					print("Length of results not the same")
					#print("Sleeping")
					time.sleep(15)
					continue
			
				for x in range(len(l[19]['result'])):
					mn = l[19]['result'][x]['MarketName']
					bv = l[19]['result'][x]['BaseVolume']
					if mn in d.keys():
						if time.time() - d[mn] < 3600:
							#print("\nAlready alarmed for " + mn)
							continue
						else:
							del(d[mn])
					if not MARKET in mn or bv < MINBTCVOLUME:
						continue
				
					new_price = l[19]['result'][x]['Last']
			
					for z in range(19):
						old_price = l[z]['result'][x]['Last']
						if (old_price - new_price) / old_price  <= CHANGE:
							print('\x1b[6;30;42m'+"\nPUMP ALERT!!!"+ '\x1b[0m')
							print(mn + "\n" + mn)
							print("https://www.coinigy.com/main/markets/BTRX/" + mn.split("-")[1] + "/" + MARKET.split("-")[0])
							print("https://bittrex.com/Market/Index?MarketName=" + mn)
							print("https://www.tradingview.com/chart/?symbol=BITTREX:" + mn.split("-")[1]+"BTC")	
							print(round(decimal.Decimal(old_price), 5))
							print(round(decimal.Decimal(new_price), 5))
							ts = time.time()
							st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
							variazione = str(round(math.fabs(((old_price - new_price) / old_price)*100),4))
							notifica = "PUMP IN ACTION!!\n +" + variazione + "%\n https://www.tradingview.com/chart/?symbol=BITTREX:" + mn.split("-")[1]+"BTC\n"	
							#update.message.reply_text(notifica)
							bot.send_message(chat_id="@dustcrp", text=notifica)
							#bot.send_message(chat_id="@pndscanner", text=notifica)
							d[mn] = time.time()
							break
						if (old_price - new_price) / old_price  >= CHANGEDOWN:
							print('\x1b[7;31;47m'+"\nDROP ALERT!!!"+'\x1b[0m')
							print(mn + "\n" + mn)
							print("https://www.coinigy.com/main/markets/BTRX/" + mn.split("-")[1] + "/" + MARKET.split("-")[0])
							print("https://bittrex.com/Market/Index?MarketName=" + mn)
							print("https://www.tradingview.com/chart/?symbol=BITTREX:" + mn.split("-")[1]+"BTC")	
							print(round(decimal.Decimal(old_price), 5))
							print(round(decimal.Decimal(new_price), 5))
							ts = time.time()
							st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
							variazione = str(round(math.fabs(((old_price - new_price) / old_price)*100),4))
							notifica = "DROP IN ACTION!!\n -" + variazione + "%\n https://www.tradingview.com/chart/?symbol=BITTREX:" + mn.split("-")[1]+"BTC\n"	
							#update.message.reply_text(notifica)
							bot.send_message(chat_id="@dustcrp", text=notifica)
							#bot.send_message(chat_id="@pndscanner", text=notifica)
							d[mn] = time.time()
							break
			
			else:
				print("In errore... riavvio")
				bot.send_message(chat_id='@dustcrp',text="Errore...riavvio..")
				time.sleep(15)
				analizza(bot, update)
		except:
			analizza(bot, update)

def start(bot, update):
	if update.message.from_user.id in get_admin_ids(bot, "@dustcrp"):
		trh = threading.Thread(target=analizza, args=(bot, update))
		trh.daemon = True
		bot.send_message(chat_id='@dustcrp',text="Avvio...")
		print("Avvio thread..")
		trh.start()
		print("Bot avviato..")
	else:
		update.message.reply_text("Permission denied!")
	
def shutdown():
	updater.stop()
	updater.is_idle = False
	print("Bot spento..")

def stop(bot, update):
    threading.Thread(target=shutdown).start()

@MWT(timeout=60*60)
def get_admin_ids(bot, chat_id):
    """Returns a list of admin IDs for a given chat. Results are cached for 1 hour."""
    return [admin.user.id for admin in bot.get_chat_administrators(chat_id)]
	

	
bot = telegram.Bot(token= '477611075:AAE2oiys-eTaMQNa95y37_QVzdi6h7pEZXg')
updater = Updater("477611075:AAE2oiys-eTaMQNa95y37_QVzdi6h7pEZXg")
dp = updater.dispatcher
dp.add_handler(CommandHandler('start',start))
dp.add_handler(CommandHandler("help",help))
dp.add_handler(CommandHandler('stop', stop))
updater.start_polling()
updater.idle()
callResult = 0
updates = bot.get_updates()