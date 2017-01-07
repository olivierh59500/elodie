import os
import shutil
import sys

def _decode(string, encoding='utf8'):
    if hasattr(string, 'decode'):
        return string.decode(encoding)

    return string


def copyfile(source, destination):
    """We increase buffer size for python2 but rely on shutil in python3
    
    The function times out in python3 using the open() approach.
    """
    if sys.version_info < (3,0):
        # shutil.copy seems slow.
        # This is a faster way to copy files but only works in python2.
        # It works by increasing the buffer size which applies to most
        #   media files.
        # filesystem.set_utime should be called by the calling code
        #   in order to set the appropriate file created/modified time.
        # Taken from http://stackoverflow.com/questions/22078621/python-how-to-copy-files-fast  #noqa
        # Currently not relying on sendfile since it is not supported on Windows.
        try:
            O_BINARY = os.O_BINARY
        except:
            O_BINARY = 0

        # Suggested optimimal size is 10MB but we want to optimize for
        #   smaller files.
        # http://blogs.blumetech.com/blumetechs-tech-blog/2011/05/faster-python-file-copy.html  #noqa
        TEN_MEGABYTES = 10485760
        BUFFER_SIZE = min(TEN_MEGABYTES, os.path.getsize(source))
        READ_FLAGS = os.O_RDONLY | O_BINARY
        WRITE_FLAGS = os.O_WRONLY | os.O_CREAT | os.O_TRUNC | O_BINARY

        try:
            fin = os.open(source, READ_FLAGS)
            stat = os.fstat(fin)
            fout = os.open(destination, WRITE_FLAGS, stat.st_mode)
            for x in iter(lambda: os.read(fin, BUFFER_SIZE), ""):
                os.write(fout, x)
        finally:
            try: os.close(fin)
            except: pass
            try: os.close(fout)
            except: pass
    else:
        # Do not use copy2(), will have an issue when copying to a network/mounted drive
        # network/mounted drive using copy and manual
        shutil.copy(source, destination)
