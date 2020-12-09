from configuration import config
import youtube_dlc


def write_from_link(download_url):
    try:
        with youtube_dlc.YoutubeDL(config.ydl_options) as ydl:
            meta = ydl.extract_info(download_url, download=True)
            if meta['formats'][0]['filesize'] > config.max_file_size:
                raise Exception("File too large")
            print(meta)
            return meta['id'], meta['title'], meta['duration']
    except Exception as e:
        print('error', e)


def get_video_fps(download_url):
    try:
        with youtube_dlc.YoutubeDL(config.ydl_options) as ydl:
            return ydl.extract_info(download_url, download=False)['fps']
    except Exception as e:
        print('error', e)

