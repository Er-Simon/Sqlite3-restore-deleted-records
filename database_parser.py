
import os
import errno

# classe rappresentante l'oggetto database
# per informazioni relative all'header consultare la documentazione al seguente link:
# https://www.sqlite.org/fileformat.html#the_database_header
class database:

    file_path = None
    valid = False
    size = 0
    stream = None
    magic_header_string = None
    page_size = None
    text_encoding = ""

    general_exception = Exception("File di tipo invalido o di versione diversa da SQLite 3.x")

    def __init__(self, path):
        self.file_path = path    
        self.initialize()

    def __check_existence(self):
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), self.file_path)

    def __get_file_size(self):
        return os.stat(self.file_path).st_size

    def __get_file_stream(self):
        if os.access(self.file_path, os.R_OK):
            return open(self.file_path, "rb")
        raise PermissionError(errno.EACCES, os.strerror(errno.EACCES), self.file_path)

    def __get_database_header(self):
        self.stream.seek(0, os.SEEK_SET)

        # Every valid SQLite database file begins with the following 16 bytes (in hex): 53 51 4c 69 74 65 20 66 6f 72 6d 61 74 20 33 00. This byte sequence corresponds to the UTF-8 string "SQLite format 3" including the nul terminator character at the end.
        self.magic_header_string = self.stream.read(16)
      
        if self.magic_header_string.hex() != "53514c69746520666f726d6174203300":
            raise self.general_exception

        # The database page size
        self.page_size = int.from_bytes(self.stream.read(2), byteorder='big')
        self.stream.seek(56 , os.SEEK_SET)

        # The database text encoding. A value of 1 means UTF-8. A value of 2 means UTF-16le. A value of 3 means UTF-16be.
        # la codifica è utilizzata per tutte le stringhe presenti nel db
        text_encoding_value = int.from_bytes(self.stream.read(4), byteorder='big')

        if text_encoding_value == 1:
            self.text_encoding = "UTF-8"
        elif text_encoding_value == 2:
            self.text_encoding = "UTF-16le"
        elif text_encoding_value == 3:
            self.text_encoding = "UTF-16be"
        else:
            print("Codifica non riconosciuta per le stringhe immagazzinate nel database, non le codificherò")

    def close(self):
        if self.stream:
            self.stream.close()

    def initialize(self):
        # controllo il file al path specificato esista
        self.__check_existence()
        # ottendo la size del file in byte
        self.size = self.__get_file_size()

        # se non ci sono nemmeno i 100 byte dell'header del database
        if self.size < 100:
            raise self.general_exception

        # apro il file in modalita read binary
        self.stream = self.__get_file_stream()
        # ottengo le informazioni dall'header
        self.__get_database_header()

    def __del__(self):
        self.close()


