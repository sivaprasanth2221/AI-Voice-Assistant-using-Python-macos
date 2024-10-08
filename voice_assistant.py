import os
import speech_recognition as sr
import datetime
from requests import get
import pywhatkit
import wikipedia
import json
import webbrowser
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from gtts import gTTS
import smtplib
from email.mime.text import MIMEText
from translate import Translator
import random
import time
import requests


# Speaking function using macOS `say` command
def speak(audio):
    print(audio)
    os.system(f'say -r 185 "{audio}"')  # Setting the rate to 185 wpm for quicker speech


# Function to speak text in a specific language
def speak_text_in_language(text, lang):
    lang_code = {
        'english': 'en',
        'french': 'fr',
        'spanish': 'es',
        'german': 'de',
        'japanese': 'ja',
        'chinese': 'zh',
        'korean': 'ko',
        'russian': 'ru'
    }.get(lang.lower(), 'en')  # Default to English if language not supported

    try:
        tts = gTTS(text=text, lang=lang_code)
        tts.save("temp.mp3")
        os.system("afplay temp.mp3")  # macOS command to play audio files
    except ValueError as e:
        speak(f'Sorry, the language you selected is not supported. {e}')


# Recognizing Function
def recognize():
    reco = sr.Recognizer()
    with sr.Microphone() as source:
        print('Listening..')
        reco.pause_threshold = 1
        audio = reco.listen(source, timeout=2, phrase_time_limit=5)

    try:
        print('Recognizing...')
        query = reco.recognize_google(audio, language='en-in')
        query = query.lower()
        if 'das' in query:
            query = query.replace('das', '')
        print('User said: ', query)
        return query
    except sr.UnknownValueError:
        speak('Sorry, I did not understand. Can you please repeat?')
    except sr.RequestError:
        speak('Network error. Please check your internet connection.')
    except Exception as e:
        speak(f'Sorry, something went wrong. {e}')
    return 'none'


# Wishing function
def wish():
    hour = datetime.datetime.now().hour
    if 0 <= hour < 12:
        speak('Good Morning')
    elif 12 <= hour < 18:
        speak('Good Afternoon')
    else:
        speak('Good Evening')

    speak('I am Das, your personal Assistant. How can I assist you today?')


# Function to write new words in the JSON file ("Brain")
def write(cmd, ans):
    with open('Brain.json') as jsonfile:
        brain_data = json.load(jsonfile)
    brain_data[cmd] = ans
    with open('Brain.json', 'w') as jsonfile:
        json.dump(brain_data, jsonfile, indent=5)


def find_most_similar_command(query):
    query_tfidf = vectorizer.transform([query])
    similarities = cosine_similarity(query_tfidf, tfidf_matrix).flatten()
    most_similar_index = similarities.argmax()

    if similarities[most_similar_index] > 0.7:
        return commands[most_similar_index]
    else:
        return None


# Fetch weather information
def get_weather():
    api_key = 'a6c2ac70c7249be4d5364b3cc9e41229'  # Replace with your OpenWeatherMap API key
    location = 'madurai'  # Replace with your location
    try:
        response = get(f'http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}')
        data = response.json()
        if data['cod'] == 200:
            weather_description = data['weather'][0]['description']
            temp = data['main']['temp'] - 273.15  # Convert from Kelvin to Celsius
            speak(f'The weather in {location} is {weather_description} with a temperature of {temp:.2f}°C')
        else:
            speak('Sorry, I could not fetch the weather information.')
    except Exception as e:
        speak(f'Sorry, I could not fetch the weather information. {e}')


# Set reminders
def set_reminder():
    speak('What should I remind you about?')
    reminder = recognize()
    if reminder == 'none':
        speak('No reminder set.')
        return
    speak('When should I remind you? Please specify the time in minutes.')
    try:
        minutes = int(recognize())
        if minutes == 'none':
            speak('No time specified.')
            return
        speak(f'Reminder set for {minutes} minutes. I will notify you then.')
        time.sleep(minutes * 60)
        speak(f'Reminder: {reminder}')
    except ValueError:
        speak('Invalid time format.')


# Send an email
def send_email():
    speak('Please provide the recipient email address.')
    recipient = recognize()
    if recipient == 'none':
        speak('No recipient specified.')
        return

    speak('What is the subject of the email?')
    subject = recognize()
    if subject == 'none':
        speak('No subject specified.')
        return

    speak('What is the body of the email?')
    body = recognize()
    if body == 'none':
        speak('No body specified.')
        return

    sender = 'your_email@gmail.com'  # Replace with your email address
    password = 'your_password'  # Replace with your email password

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = recipient

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender, password)
            server.sendmail(sender, recipient, msg.as_string())
            speak('Email sent successfully.')
    except Exception as e:
        speak(f'Sorry, I could not send the email. Error: {e}')

def get_news():
    api_key = '5290942623304f37b8ae6d4f22c81a76'  # Replace with your News API key
    url = f'https://newsapi.org/v2/top-headlines?country=in&apiKey={api_key}'
    try:
        response = requests.get(url)
        news_data = response.json()
        headlines = [article['title'] for article in news_data['articles'][:5]]
        speak("Here are the top headlines:")
        for i, headline in enumerate(headlines, 1):
            speak(f"{i}. {headline}")
    except Exception as e:
        speak(f'Sorry, I could not fetch the news. Error: {e}')
        
def get_stock_price():
    speak('Please tell me the stock symbol.')
    symbol = recognize()
    if symbol == 'none':
        speak('No symbol provided.')
        return

    try:
        stock_price = get(f'https://financialmodelingprep.com/api/v3/quote/{symbol}?apikey=your_api_key').json()[0]['price']
        speak(f'The current price of {symbol} is {stock_price} USD')
    except Exception as e:
        speak(f'Sorry, I could not fetch the stock price. Error: {e}')

# Translate text
def translate_text():
    speak('Which language do you want to translate to?')
    target_language = recognize()
    if target_language == 'none':
        speak('No language specified.')
        return

    speak('What text do you want to translate?')
    text = recognize()
    if text == 'none':
        speak('No text provided.')
        return

    translator = Translator(to_lang=target_language)
    try:
        translation = translator.translate(text)
        speak(f'Translated text: {translation}')

        # Speak the translated text in the target language
        speak_text_in_language(translation, target_language)
    except Exception as e:
        speak(f'Sorry, I could not translate the text. Error: {e}')


# Play local music
def play_music():
    speak('Which music file would you like to play?')
    file_name = recognize()
    if file_name == 'none':
        speak('No file specified.')
        return

    try:
        os.system(f'afplay "{file_name}"')  # macOS command to play audio files
    except Exception as e:
        speak(f'Sorry, I could not play the music. Error: {e}')


# Tell a joke
def tell_joke():
    jokes = [
        'Why don’t scientists trust atoms? Because they make up everything!',
        'What do you call fake spaghetti? An impasta!',
        'Why did the scarecrow win an award? Because he was outstanding in his field!',
    ]
    joke = random.choice(jokes)
    speak(joke)


# Simple calculator
def calculator():
    speak('Please tell me the arithmetic operation you want to perform.')
    operation = recognize()
    if operation == 'none':
        speak('No operation specified.')
        return

    try:
        result = eval(operation)
        speak(f'The result is {result}')
    except Exception as e:
        speak(f'Sorry, I could not perform the calculation. Error: {e}')


# Load the JSON data only once for efficiency
with open('Brain.json') as data:
    brain_data = json.load(data)

commands = list(brain_data.keys())
vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(commands)

# Main loop
if __name__ == '__main__':
    wish()
    while True:
        query = recognize()

        if query == 'none':
            continue

        # Exit command
        if 'exit' in query or 'goodbye' in query or 'stop' in query:
            speak('Goodbye! Have a nice day.')
            break

        # Handling specific commands
        if 'textedit' in query:  # TextEdit is a built-in text editor on macOS
            os.system('open -a TextEdit')
            continue

        if 'terminal' in query:
            os.system('open -a Terminal')
            continue

        if 'play' in query:
            query = query.replace('play', '')
            speak('Playing {}'.format(query))
            pywhatkit.playonyt(query)
            continue

        if 'ip address' in query:
            ip = get('https://api.ipify.org').text
            speak(f'Your IP Address is: {ip}')
            continue

        if 'time' in query:
            current_time = datetime.datetime.now().strftime('%I:%M %p')
            speak('The time is: ' + current_time)
            continue

        if 'tell me about' in query:
            person = query.replace('tell me about', '')
            info = wikipedia.summary(person, 1)
            speak(info)
            continue

        if 'open instagram' in query:
            webbrowser.open('www.instagram.com')
            continue

        if 'open browser' in query:
            speak('What do you want me to search?')
            search = recognize()
            webbrowser.open(f'www.google.com/search?q={search}')
            continue

        if 'weather' in query:
            get_weather()
            continue

        if 'reminder' in query:
            set_reminder()
            continue

        if 'send email' in query:
            send_email()
            continue

        if 'translate' in query:
            translate_text()
            continue

        if 'play music' in query:
            play_music()
            continue

        if 'joke' in query:
            tell_joke()
            continue

        if 'calculator' in query:
            calculator()
            continue
        
        if 'news' in query:
            get_news()
            continue
        
        if 'stock' in query:
            get_stock_price()
            continue

        # Handling unknown queries and learning new phrases
        similar_command = find_most_similar_command(query)
        if similar_command:
            speak(brain_data[similar_command])
        else:
            speak('I can\'t understand... Do you want me to save the phrase?')
            response = recognize().lower()
            if 'yes' in response:
                speak('Repeat the command, please.')
                cmd = recognize().lower()
                if cmd == 'none':
                    speak('Command not received. Moving on.')
                    continue
                speak('What reply should I give?')
                ans = recognize().lower()
                if ans == 'none':
                    speak('Reply not received. Moving on.')
                    continue
                write(cmd, ans)
                speak('Thank you for the information.')
            else:
                speak('Okay.')
