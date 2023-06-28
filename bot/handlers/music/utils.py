YDL_OPTIONS = {'format': 'bestaudio/best',
               'noplaylist': 'True', 'simulate': 'True', 'preferredquality': '192', 'preferredcodec': 'mp3', 'key': 'FFmpegExtractAudio'}
FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}


class Song:
    def __init__(self, url, title, duration, SourceUrl):
        self.url = url
        self.title = title
        self.duration = "%02d:%02d" % (duration // 60, duration % 60)
        self.SourceUrl = SourceUrl
