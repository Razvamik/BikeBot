import telebot
import bs4
from bs4 import BeautifulSoup
import requests
import re
import pandas as pd

with open ('token.txt') as fh:
    token = fh.read().strip()
bot = telebot.TeleBot(token)

parsed = False
supported = ['161', '166', '412']

@bot.message_handler(commands=['start'])
def show_start(message):
    bot.send_message(message.from_user.id, 'Hello! Im BikeIsLoveBikeIsLife bot.\
 I search for info about bikes from https://www.velostok.ru.\
 Some usefull things like name, price e.t.c. To see commands type /help')
    
@bot.message_handler(commands=['help'])
def show_help(message):
    bot.send_message(message.from_user.id, '1) For parsing type /parse\
\n2) To find brand type /brand \n3) Get a file with selected data /file')

@bot.message_handler(commands=['siger'])
def ha_ha(message):
    bot.send_message(message.from_user.id, 'Haha!')
    
@bot.message_handler(commands=['brand'])
def show_brands(message):
    bot.send_message(message.from_user.id, 'I can find you one of these:\
 166 - roadbikes, 161 - double suspension bikes, 412 - cruiser bikes')                     
                     
@bot.message_handler(commands=['parse'])
def parse_site(message):
    global parsed
    parsed = False
    bot.send_message(message.from_user.id, 'Enter brand code')
    
@bot.message_handler(commands=['file'])
def get_file(message):
    global parsed
    if parsed:
        fh = open('data.csv', 'rb')
        bot.send_document(message.from_user.id, fh)
        fh.close()
    else:
        bot.send_message(message.from_user.id, "No data was parsed. Type /parse")
        
def get_mean(message):
    global parsed
    if parsed:
        data = pd.read_csv('data.csv', delimiter = ',')
        mean = data[1].mean()
        bot.send_message(message.from_user.id, f'Average price is {mean}')
    else:
        bot.send_message(message.from_user.id, "Парсинг не выполнен. Нажмите /parse чтобы это сделать")
    
@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    global parsed
    if not parsed:
        if message.text in supported:
            try:
                bot.send_message(message.from_user.id, 'Starting parsing')
            
                url = f'https://www.velostok.ru/ishop/{message}_0'
                bikes = []
                prices = []
                images = []
                
                page = requests.get(url)
                text = page.text
                soup = BeautifulSoup(text, "html.parser")
                
                for link in range(len(soup.find_all('a', {'itemprop' : 'name'}))):
                    bike = soup.find_all('a', {'itemprop' : 'name'})[link].attrs['href']
                    price = soup.find_all('meta', {'itemprop' : 'price'})[link].attrs['content']
                    image = soup.find_all('img', {'itemprop' : 'image'})[link + 1].attrs['src']
                    bikes.append(bike)
                    prices.append(price)
                    images.append(image)
                                
                with open('data.csv', 'w') as fh:
                    fh.write('bike name,price,image\n')
                    
                    for i in range(len(bikes)):
                        fh.write(f'{bikes[i]},{prices[i]},{images[i]}\n')
                parsed = True
                bot.send_message(message.from_user.id, 'Finished parsing, choose next operation:')
                bot.send_message(message.from_user.id, f'''/file - get file with the data\
                \n/mean - get average price \n/bike_info - get info about one bike in range {bikes[0]} - {bikes[-1]}''')
            
            except Exception:
                parsed = False
                bot.send_message(message.from_user.id, 'An error oqured during parsing. Please, try again or choose other brand')
        else:
            show_brands(message)   
            parse_site(message)
    else:
        bot.send_message(message.from_user.id, "Unknown command")
        bot.send_message(message.from_user.id, f'/file - get file with the data\
                 \n/mean - get average price\n/bike_info - get info about one bike in range {bikes[0]} - {bikes[-1]}')
        
bot.polling(none_stop=True, interval=0)