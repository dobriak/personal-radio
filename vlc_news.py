from os import listdir
from os.path import isfile, join, expanduser
import configparser
import time
import vlc

# Parse configuration
cfg = configparser.ConfigParser()
cfg.read("personal-radio.ini")
music_stream = cfg['Default']['music_stream']
news_directory = cfg['Default']['news_dir']

""" 
Watch a directory for new mp3 files. Poll every pollTime seconds
Upon a discovery of a new one, enqueue it in VLC.
"""
def watch_my_dir(news_dir: str, pollTime: int):
    while True:
        if 'watching' not in locals():
            previousFileList = fileInDirectory(news_dir)
            watching = 1
            print(previousFileList)
        
        time.sleep(pollTime)        
        newFileList = fileInDirectory(news_dir)
        fileDiff = listComparison(previousFileList, newFileList)
        previousFileList = newFileList
        if len(fileDiff) == 0: continue
        if ".mp3" in fileDiff[0]:
            insert_news(fileDiff[0])
        else:
            print(f"{fileDiff[0]} is not an mp3 file.")

""" 
Utility function to compare two lists of files
"""
def listComparison(OriginalList: list, NewList: list):
    differencesList = [x for x in NewList if x not in OriginalList]
    return(differencesList)

""" 
Utility function to return all files in a directory
"""
def fileInDirectory(news_dir: str):
    onlyfiles = [f for f in listdir(news_dir) if isfile(join(news_dir, f))]
    return(onlyfiles)

""" 
Insert the newly found mp3 file into the VLC playlist.
"""
def insert_news(news_file: str):
    print(f"New audio discovered in {news_directory}:")
    news_file = join(news_directory, news_file)
    new_mp.audio_set_volume(50)
    time.sleep(3)
    new_mp.audio_set_volume(99)
    media_player.stop()    
    news_media = player.media_new(news_file)
    while media_list.count() > 0:
        media_list.remove_index(0)
    media_list.add_media(news_media)
    media_list.add_media(music_media)
    media_player.play()    
    print(f"Added news into the music stream. {news_file}")

# Main entry
if __name__ == '__main__':
    media_player = vlc.MediaListPlayer()
    player = vlc.Instance()
    media_list = player.media_list_new()
    music_media = player.media_new(music_stream)
    media_list.add_media(music_media)
    media_player.set_media_list(media_list)
    new_mp = player.media_player_new()
    media_player.set_media_player(new_mp)
    new_mp.audio_set_volume(99)
    media_player.play()
    watch_my_dir(news_directory, 15)