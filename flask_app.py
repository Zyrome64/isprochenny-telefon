from flask import Flask, request
import json
import random
import requests
import os

app = Flask(__name__)


LANG = 'ru'
languages = ['az', 'ml', 'sq', 'mt', 'am',
    'mk', 'en', 'mi', 'ar', 'mr', 'hy', 'af',
    'mn', 'eu', 'de', 'ba', 'ne', 'be', 'no',
    'bn', 'pa', 'my', 'bg', 'fa', 'bs', 'pl',
    'cy', 'pt', 'hu', 'ro', 'vi', 'ht', 'ms',
    'gl', 'sr', 'nl', 'si', 'sk', 'el', 'sl',
    'ka', 'sw', 'gu', 'su', 'da', 'tg', 'he',
    'th', 'yi', 'tl', 'id', 'ta', 'ga', 'tt',
    'it', 'te', 'is', 'tr', 'es', 'kk', 'uz',
    'kn', 'uk', 'ca', 'ur', 'ky', 'fi', 'zh',
    'fr', 'ko', 'hi', 'xh', 'hr', 'km', 'cs',
    'lo', 'sv', 'la', 'gd', 'lv', 'et', 'lt',
    'eo', 'lb', 'jv', 'mg', 'ja', 'ru']
languages.remove(LANG)

sessionStorage = {}


def translate(text, from_, to_):
    response = requests.get("https://translate.yandex.net/api/v1.5/tr.json/translate?key=trnsl.1.1.20190419T124114Z.94454a1d2b88dcac.b292147600fea7a8cc9935035923145b3e6688e6&text={0}&lang={1}-{2}".format(text, from_, to_)).json()
    if response is not None and 'text' in response.keys():
        return response['text'][0]
    return text


def chain_translate(text, lang):
    l = random.choice(languages)
    return translate(translate(text, lang, l), l, lang)



@app.route('/post', methods=['POST'])
def main():
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }
    handle_dialog(response, request.json)
    return json.dumps(response)


def handle_dialog(res, req):
    user_id = req['session']['user_id']
    if req['session']['new']:
        res['response']['text'] = 'Вы запустили навык "Испорченный телефон"! Чтобы начать, просто введите любое сообщение на русском и смотрите, как оно искажается!'
        sessionStorage[user_id] = {
            'corr_started': False,  # здесь информация о том, что пользователь начал игру. По умолчанию False
            'original_message': None,
            'message': None
        }
        res['response']['buttons'] = [
            {
                'title': 'Помощь',
                'hide': True
            },
            {
                'title': 'Что ты умеешь?',
                'hide': True
            },
            {
                'title': 'Выход',
                'hide': True
            }
        ]
        return
    if 'original_message' not in sessionStorage[user_id]:
        sessionStorage[user_id]['original_message'] = None
    if sessionStorage[user_id]['original_message'] is None:
        if req['request']['original_utterance'].lower() == 'выход':
            res['response']['text'] = 'Спасибо, что воспользовались этим навыком!'
            res['end_session'] = True
            return
        elif req['request']['original_utterance'].lower() in ['помощь', 'что ты умеешь', 'что ты умеешь?']:
            res['response']['text'] = 'Навык "Испорченный телефон", переводя ваше сообщение на разные языки, выдаёт интересный результат, поверьте, это весело! Навык расчитан на то, что вы будете использовать кнопки с предлагаемыми ответами. Введите любое предложение или слово, чтобы опробовать этот навык.'
            res['response']['buttons'] = [
                {
                    'title': 'Выход',
                    'hide': True
                }
            ]
        elif len(req['request']['original_utterance']) > 100:
            res['response']['text'] = 'Ваше сообщение слишком длинное, введите что-нибудь покороче!'
        else:
            sessionStorage[user_id]['original_message'] = req['request']['original_utterance']
            sessionStorage[user_id]['message'] = chain_translate(sessionStorage[user_id]['original_message'], LANG)
            res['response']['text'] = '[[' + sessionStorage[user_id]['message'] + ']]'
            res['response']['buttons'] = [
                {
                    'title': 'Ещё',
                    'hide': True
                },
                {
                    'title': 'Хватит',
                    'hide': True
                },
                {
                    'title': 'Ввести другой текст',
                    'hide': True
                },
                {
                    'title': 'Начать заново',
                    'hide': True
                }
            ]
        return
    else:
        if req['request']['original_utterance'].lower() == 'ещё':
            sessionStorage[user_id]['message'] = chain_translate(sessionStorage[user_id]['message'], LANG)
            res['response']['text'] = '[[' + sessionStorage[user_id]['message'] + ']]'
            res['response']['buttons'] = [
                {
                    'title': 'Ещё',
                    'hide': True
                },
                {
                    'title': 'Хватит',
                    'hide': True
                },
                {
                    'title': 'Ввести другой текст',
                    'hide': True
                },
                {
                    'title': 'Начать заново',
                    'hide': True
                }
            ]
            return
        elif 'хватит' in req['request']['nlu']['tokens']:
            res['response']['text'] = 'Спасибо, что воспользовались этим навыком!'
            res['end_session'] = True
            return
        elif req['request']['original_utterance'].lower() == 'ввести другой текст':
            sessionStorage[user_id]['original_message'] = None
            sessionStorage[user_id]['message'] = None
            res['response']['text'] = 'Введите любое сообщение на русском!'
        elif req['request']['original_utterance'].lower() == 'начать заново':
            sessionStorage[user_id]['message'] = sessionStorage[user_id]['original_message']
#            sessionStorage[user_id]['message'] = chain_translate(sessionStorage[user_id]['original_message'], LANG)
            res['response']['text'] = '[[' + sessionStorage[user_id]['message'] + ']]'
            res['response']['buttons'] = [
                {
                    'title': 'Ещё',
                    'hide': True
                },
                {
                    'title': 'Хватит',
                    'hide': True
                },
                {
                    'title': 'Ввести другой текст',
                    'hide': True
                },
                {
                    'title': 'Начать заново',
                    'hide': True
                }
            ]
            return
        else:
            res['response']['text'] = 'Чтобы продолжить, выберите один из предложенных ответов.'
            res['response']['buttons'] = [
                {
                    'title': 'Ещё',
                    'hide': True
                },
                {
                    'title': 'Хватит',
                    'hide': True
                },
                {
                    'title': 'Ввести другой текст',
                    'hide': True
                },
                {
                    'title': 'Начать заново',
                    'hide': True
                }
            ]
            return


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
