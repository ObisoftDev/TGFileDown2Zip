import random
import zipfile
import os


files = []

def clear():
    files.clear()

class MultiFile(object):
    def __init__(self, file_name, max_file_size):
        self.current_position = 0
        self.file_name = file_name
        self.max_file_size = max_file_size
        self.current_file = None        
        self.open_next_file()

    @property
    def current_file_no(self):
            return self.current_position / self.max_file_size

    @property
    def current_file_size(self):
            return self.current_position % self.max_file_size

    @property
    def current_file_capacity(self):
            return self.max_file_size - self.current_file_size

    def open_next_file(self):
            file_name = "%s.%03d" % (self.file_name, self.current_file_no + 1)
            print ("* Opening file '%s'..." % file_name)
            if self.current_file is not None:
                self.current_file.close()
            self.current_file = open(file_name, 'wb')
            files.append(file_name)

    def tell(self):
            return self.current_position

    def write(self, data):
           # newdata = 
            start, end = 0, len(data)
            while start < end:
                current_block_size = min(end - start, self.current_file_capacity)
                self.current_file.write(data[start:start+current_block_size])
                print ("* Wrote %d bytes." % current_block_size)
                start += current_block_size
                self.current_position += current_block_size
                if self.current_file_capacity == self.max_file_size:
                    self.open_next_file()

    def flush(self):
            self.current_file.flush()

    def close(self):
        self.current_file.close()


#mult_file =  MultiFile('new.zip',1024 * 1024 * 1)
#zip = zipfile.ZipFile(mult_file,  mode='w', compression=zipfile.ZIP_DEFLATED)
#zip.write('file.exe')
#zip.close()