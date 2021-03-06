from choreo.dbmanager.initializer import *
from choreo.utils.reader import TxtReader
from choreo.utils.writer import TxtWriter
from glob import glob


class Dropper:
    @staticmethod
    def drop(choreo_id):
        for path in [F_ORG, F_SLICE]:
            try:
                for i in glob.glob("{}.*".format(path + choreo_id)):
                    os.remove(i)
            except:
                pass

        if os.path.isdir(F_SLICE + choreo_id):
            os.rmdir(F_SLICE + choreo_id)

        try:
            Initializer.choreo_metainfo_list.remove(choreo_id)
        except:
            pass

        # youtube-dl의 archive file reformat
        read = TxtReader().read("/home/jihee/choleor_media/audio/archive.txt")
        try:
            read.remove("youtube {}\n".format(choreo_id))
        except:
            pass
        TxtWriter().write("/home/jihee/choleor_media/audio/archive.txt", read)
        # self.audio_meta_list.remove(audio_id)
        # print(self.audio_meta_list)

# if __name__ == '__main__':
#     Initializer().drop("h5jz8xdpR0M")