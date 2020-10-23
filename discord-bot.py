import discord
import time
import requests
import json
import copy
from bs4 import BeautifulSoup

dict_requests_patterns = {}
default_settings = {"limit": 10,"complexity":3,
"from_date[day]":1,
"from_date[month]":	1,
"from_date[year]":1990,
"to_date[day]":	19,
"to_date[month]":6,
"to_date[year]":2020,
"op":"Получить пакет",
"form_build_id":"form-HV9cl-hkXg1JCmx30gSZ5D0iSxIWtRNjy5bK7QIjaFs",
"form_id":"chgk_db_get_random_form"}

def check_settings():
    return
questions = []

setting_flag = True
in_play = False
current_question = 0
right_answer = 0
wrong_answer = 0
answer_is_hidden = True
settings = copy.deepcopy(default_settings)


def print_headers(headers: dict):
    """
    Печатает заголовки запроса в окно вывода
    :param headers: словарь с заголовками
    :return:
    """
    for item in headers:
        print(item + ":" + headers[item])



def create_session():
    session = requests.session()
    home_page = send_request(dict_requests_patterns["Home_req"], session)
    if home_page.status_code == 200:
        print("home done")
    return session

def send_request(req: dict, session):
    """
    Отправляет все виды http запросов

    :param req: заголовки запроса
    :param session: объект сессии
    :return: возвращает ответ веб-ресурса
    """
    response = None
    if req["Request"] == "post":
        response = session.post(url=req["Url"], data=settings, headers=req["Headers"], verify=False)
    elif req["Request"] == "get":
        response = session.get(url=req["Url"], headers=req["Headers"], params=req["Payloads"], verify=False)
    elif req["Request"] == "head":
        response = session.head(url=req["Url"], headers=req["Headers"], params=req["Payloads"], verify=False)
  # self.print_info_request(response)
  # self.print_info_response(response)
    return response

def read_json(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        global dict_requests_patterns
        dict_requests_patterns = json.loads(file.read())

read_json("chgkbase_requests.txt");
session = create_session()
resp = send_request(dict_requests_patterns['random_packet'], session)
soup = BeautifulSoup(resp.text, 'html.parser')
'''
for foo in soup.find_all('div', attrs={'class': 'random-results'}):
    for bar in foo.find_all('div', attrs={'class': 'random_question'}):
        text = bar.get_text().split("...")
        item = {"question": text[0], "answer": text[1]}
        # print(bar)
        additional = bar.find_all('div', attrs={'class': 'razdatka'})
        if len(additional) != 0:
            print(bar)
            additional_text = additional[0].get_text()

        print(item)
'''



client = discord.Client()


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    global setting_flag
    global  in_play
    global current_question
    global right_answer
    global wrong_answer
    global answer_is_hidden
    global settings
    if message.author == client.user:
        return
    messages = message.content.split(" ")
    if messages[0].strip().startswith('..'):
        if len(messages)==1:
            await message.channel.send("Введите команду");


        elif messages[1] == "info":
            await message.channel.send("\n Что делает бот? С сайта https://db.chgk.info/ запрашивает случайный пакет вопросов в соотвест"
                                       "вие с настройкми, затем при переходе в режим игры выдаёт из этого пакета"
                                       "вопросы в общий чат. Считает количество правильных и неправильных ответов и"
                                       " выводит результат сессии после отыгранного пакета."
                                       "\n"
                                       "\n"
                                       "Какие есть команды? Прежде всего любую команду бота нужно начинать с '..'. Список команд\n"
                                       "1. Получение данных о текущих настройках - 'get settings'. Значения параметров \n"
                                       "\t limit - количество вопросов в пакете (от 0 до 100)\n"
                                       "\t complexity - сложность вопросов в пакете ( от 0 до 5)\n"
                                        " Далее настройка временного интервала вопросов\n"
                                       "\t from_date[day] - (от 1 до 31)\n"
                                       "\tfrom_date[month] - (от 1 до 12)\n"
                                       "\tfrom_date[year] -  (от 1990 до текущего)\n"
                                       "\tto_date[day] - (до текущего)\n"
                                       "\tto_date[month] - (до текущего)\n"
                                       "\tto_date[year] - (до текущего)\n"
                                       "2. Изменение настроек - 'set settings'. Пример : .. set settings complexity 2 limit 10\n"
                                       "3. Переход в режим игры - 'start'.\n"
                                       "4. Получение следующего вопроса - 'next' .\n"
                                       "5. Правильный ответ - + .\n"
                                       "6. Правильный ответ - + .\n"
                                       "7. Текущая статистка - 'stat'\n"
                                       "8. Сброс текущего пакета - 'reset\n"


                                       "\n\n"
                                    
                                       "Найденные ошибки, пожелания, предложения писать на почту kuzinmails@yandex.ru. Приятной игры!")
        elif messages[1].strip() == "set" and messages[2].strip()=="settings":
            if len(messages)!=3:
                for i in range(3, len(messages),2):
                    key = messages[i]
                    if(default_settings.get(key)!=None):
                        settings[key] = messages[i+1]
                check_settings()
            else:
                await message.channel.send("Настройки не введены")
        elif messages[1].strip() == "get" and messages[2].strip()=="settings":
            await message.channel.send(json.dumps(settings).encode('utf8'))
        elif messages[1].strip() == "start" and in_play!=True:
            if setting_flag:
                questions.clear()
                resp = send_request(dict_requests_patterns['random_packet'], session)
                if resp.status_code == 200:
                    in_play = True
                    soup = BeautifulSoup(resp.text, 'html.parser')
                    for foo in soup.find_all('div', attrs={'class': 'random-results'}):
                        for bar in foo.find_all('div', attrs={'class': 'random_question'}):
                            item = {"question": "" , "answer": ""}
                            img_tag = bar.find('img')
                            if img_tag!= None:
                                img_path = img_tag['src']
                                item["question"]+= img_path +'\n'

                            num_split  = bar.get_text().find('Ответ')
                            text = bar.get_text()
                            item["question"] += text[0:num_split]
                            item["answer"] += text[num_split:]

                            print(item)




                            questions.append(item)
                    await message.channel.send('Запрос успешно обработан')
                    await message.channel.send(questions[0]["question"])
            else:
                await message.channel.send('Корректно задайте настройки')
        elif messages[1].strip() == "reset":
            if in_play:
                current_question = 0
                questions.clear()
                in_play = False
                await message.channel.send('Пакет сброшен')
                await message.channel.send('Верных ответов {0}, неверных {1}'.format(right_answer,wrong_answer))
            else:
                await message.channel.send('Пакет и так был пуст')
        elif messages[1].strip() =="stat":
            await message.channel.send('Верных ответов {0}, неверных {1}'.format(right_answer,wrong_answer))

        elif messages[1].strip() =="answer" and in_play and answer_is_hidden:
            await message.channel.send(questions[current_question]["answer"])
            await message.channel.send('+  ответ верен, - не верен')
            answer_is_hidden = False
        elif messages[1].strip() == "+" and in_play and answer_is_hidden!= True:
            right_answer+=1
            print(right_answer)
            await message.channel.send("Cчётчик обновлён")
        elif messages[1].strip() == "-" and in_play and answer_is_hidden!=True:
            wrong_answer+=1
            print(wrong_answer)
            await message.channel.send("Cчётчик обновлён")
        elif messages[1].strip() =="next" and in_play:
            answer_is_hidden = True
            if current_question<len(questions)-1:
                current_question+=1
            else:
                await message.channel.send("Закончились вопросы")
            answer_is_hidden = True
            await message.channel.send(questions[current_question]["question"])
        elif messages[1].strip() == "uebi":
            await message.channel.send("uebal")






client.run('NzIzMzkwNjc5MDEwNzcwOTg4.Xuw_rg.LHztjaErBQiO1q_cgIt22f-IYEI')