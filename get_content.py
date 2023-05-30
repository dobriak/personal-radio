from datetime import datetime
import configparser
import feedparser
import openai
from os import rename, path 
import random
import re
import requests
import ssl
import tempfile as tmp
import yfinance as yf

# Parse configuration
cfg = configparser.ConfigParser()
cfg.read("personal-radio.ini")
# Configure ChatGPT
openai.organization = cfg['OpenAI']['organization']
openai.api_key = cfg['OpenAI']['api_key']
if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context

"""
Parse primary and secondary RSS newsfeeds URLs
Return the resulting news in a \n separated string
""" 
def get_newsfeeds():
    # Regular expression to remove html tags from text
    tag_remove = re.compile(r'(<!--.*?-->|<[^>]*>)')
    
    news = ""

    primary_feed   = feedparser.parse(cfg['NewsFeeds']['primary'])
    secondary_feed = feedparser.parse(cfg['NewsFeeds']['secondary'])

    for i in range(int(cfg['NewsFeeds']['primary_articles'])):
        e = primary_feed.entries[i]
        news = f"{news} {e.title} {tag_remove.sub('', e.description)}\n"

    for i in range(int(cfg['NewsFeeds']['secondary_articles'])):
        e = secondary_feed.entries[i]
        news = f"{news} {e.title} {tag_remove.sub('', e.description)}\n"
    
    return news

""" 
Query yahoo finance for a ticker of your choice, return as a string
that describes today's (or previous business day) session highs and lows.
"""
def get_markets():
    markets = ""
    today = datetime.now().strftime("%A %B %d %Y")

    ticker = yf.Ticker(cfg['MarketReport']['ticker'])
    markets = ( 
        f"Today {today}, {ticker.info['shortName']} stock is trading"
        f" between {ticker.info['regularMarketDayLow']} and "
        f"{ticker.info['regularMarketDayHigh']} dollars per share.\n"
    )
    return markets

""" 
Use ChatGPT to summarize the gathered news and format them for reading.
Returns a string.
"""
def ai_summary(news: str):

    messages = [
        {"role": "system", "content": "You are a news editor."},
        {"role": "user", "content": f"Summarize the following: {news}"},
    ]

    response = openai.ChatCompletion.create(
        model = "gpt-3.5-turbo",
        messages = messages,
        temperature = 0.1,
    )

    return response["choices"][0]["message"]["content"]

""" 
Select a random word from a list of AI terms and have ChatGPT define it for you.
Returns single sentence definition of the AI term of the day.
"""
def ai_term_of_day():
    ai_terms = []
    with open("aiterms.txt","r") as atf:
        ai_terms = atf.read().splitlines()

    term = random.choice(ai_terms)
    prompt = (
        f"Define in a single sentence the following term"
        f" from the AI domain: {term}"
    )

    messages = [
        {"role": "system", "content": "You are a news editor."},
        {"role": "user", "content": prompt},
    ]

    response = openai.ChatCompletion.create(
        model = "gpt-3.5-turbo",
        messages = messages,
        temperature = 0.1,
    )

    tod_definition = response["choices"][0]["message"]["content"]
    return f"And, finally, the AI term of the day is {term}: {tod_definition}"


""" 
Use ElevenLabs' API to read the generated content in natural voice. 
Saves the resulting file to a specified directory for VLC to insert in
its current playlist.
"""
def ai_voice_read(content: str):
    # Write to a temp directory, then move to news_dir
    temp_dir = tmp.TemporaryDirectory(prefix="personal_radio")
    file_name = f"news_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}.mp3"
    temp_file = path.join(temp_dir.name, file_name)
    news_file = path.join(cfg['Default']['news_dir'], file_name)
    
    url = (
        f"https://api.elevenlabs.io/v1/text-to-speech/"
        f"{cfg['ElevenLabs']['voice_id']}"
    )

    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": cfg['ElevenLabs']['api_key']
    }

    data = {
        "text": content,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.5
        }
    }

    response = requests.post(url, json=data, headers=headers)
    with open(temp_file, 'wb') as f:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)

    # Move from temp to news directory
    rename(temp_file, news_file)


# Main entrypoint
if __name__ == '__main__':
    print("Personal radio v0.1")
    print("Reading news feeds...")
    my_news = get_newsfeeds()
    print("Getting market data...")
    my_markets = get_markets()
    print("Summarizing news articles...")
    summarized = ai_summary(my_news)
    print("Getting the AI term of the day...")
    my_tod = ai_term_of_day()
    # Combine all content for voice reading
    my_content = f"{summarized}\n\n{my_markets}\n\n{my_tod}"
    print("Voice reading content...")    
    ai_voice_read(my_content)
    print("Done.")
