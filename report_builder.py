
from datetime import datetime
from json import dumps
import collections
import os

# classe rappresentante le informazioni ottenute durante l'esecuzione 
# che saranno utilizzate dal file "report.html"
class report:
    creation_time = None
    file_name = None
    file_path = None
    size = 0
    text_encoding = None
    data = dict()

    def __init__(self, path, size, hash, text_encoding):
        # tempo della creazione del report
        self.creation_time = datetime.now().replace(microsecond=0)
        # path in cui è situato il file e nome del file
        self.file_path, self.file_name = os.path.split(os.path.abspath(path))
        # dimensione in byte del file
        self.size = size
        # hash del file
        self.hash = hash
        # codifica utilizzata dal database per le stringhe
        self.text_encoding = text_encoding
        # salvo le informazioni nel dizionario "data"
        self.set_report_info()

    def set_report_info(self):
        self.data["report_info"] = dict()
        self.data["report_info"]["creation_time"] = self.creation_time.strftime("%m/%d/%Y, %H:%M:%S")
        self.data["report_info"]["file_name"] = self.file_name
        self.data["report_info"]["file_path"] = self.file_path
        self.data["report_info"]["size"] = self.size
        self.data["report_info"]["sha256sum"] = self.hash
        self.data["report_info"]["text_encoding"] = self.text_encoding
        self.data["data"] = dict()

    # a partire dal dizionario "patterns" rappresentante la struttura delle tabelle e dei loro campi,
    # salvo queste informazioni dentro il dizionario "data"
    def set_schema_info(self, patterns):

        for value in patterns:
            for table in patterns[value]:
                self.data["data"][table] = dict()
                self.data["data"][table]["schema"] = []

                flag = max(set(x[3] for x in patterns[value][table]))
                
                for field_ in patterns[value][table]:
                    field = dict()

                    if not flag:
                        field["WITHOUT ROWID"] = dict()
                        field["WITHOUT ROWID"]["type"] = "INTEGER"
                        field["WITHOUT ROWID"]["not_null"] = 0
                        field["WITHOUT ROWID"]["primary_key"] = 1
                        self.data["data"][table]["schema"].append(field)
                        field = dict()
                        flag = True

                    field[field_[0]] = dict()
                    field[field_[0]]["type"] = field_[1]
                    field[field_[0]]["not_null"] = field_[2]
                    field[field_[0]]["primary_key"] = field_[3]
                    self.data["data"][table]["schema"].append(field)

        # ordino le tabelle in ordine alfabetico
        self.data["data"] = collections.OrderedDict(sorted(self.data["data"].items()))


    def get_data(self):
        return self.data

    def set_data(self, data):
        self.data = data

    def save_data(self):
        for table in self.data["data"]:
            if "records" in self.data["data"][table]:
                # ordino i record trovati per ogni tabella in base alla chiave primaria
                self.data["data"][table]["records"] = sorted(self.data["data"][table]["records"], key=lambda x: x[0])

        # salvo il contenuto del dizionario data su un file chiamato "data.json"
        with open("data.json", "w") as f:
            f.write(dumps(self.data))
    