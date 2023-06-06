# Personal Radio 
## Play music and news automatically.

This is a simple automated way to listen to your favorite web radiostation and insert news / weather / any other info on the fly.
News is gathered from RSS/Atom feeds of your choice. Other data is gathered / processed from public sources.
All gathered data is then summarized and augmented as needed by ChatGPT and converted into a news anchor type of script.
The script is then fed to a generative AI model by ElevenLabs that converts the text into natural sounding voice and the resulting audio is inserted into the stream you are listening to.

## Get started
* OpenAI account, your organization ID and api key (has a free tier)
* ElevenLabs account, api key (has a free tier)
* Python 3 and VLC, it will work on Mac/Linux/Windows

Clone the repo to your laptop, then provide all info in the config file. 
```
cd personal-radio
mkdir news
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp personal-radio.ini.example personal-radio.ini
```
Edit personal-radio.ini in your favorite text editor. Here are some suggestions, adjust to your liking:

```
[Default]
news_dir = news
music_stream = http://stream.radioparadise.com/aac-128 

...

[NewsFeeds]
primary            = https://feeds.npr.org/1001/rss.xml
secondary          = https://www.chicagotribune.com/arcio/rss/category/news/?query=display_date:[now-1d+TO+now]&sort=display_date:desc
primary_articles   = 3
secondary_articles = 2

[MarketReport]
ticker = AAPL
```
And to start enjoying your own web radio with personalized news, just run the vlc control program.
```
python3 vlc_news.py
```
Then in another terminal, run the news gathering / processing program. It will create an mp3 file with your news and deposit it into the `news_dir` directory. The vlc control program will then detect it and insert into the stream automatically.
```
source venv/bin/activate
python3 get_content.py
```

That is it! Enjoy being informed while being entertained.

_Coming next:_ filtering the news by keywords. Don't change the channel!
