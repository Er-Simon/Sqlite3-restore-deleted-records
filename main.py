import database_parser
import extract_raw_data
import patterns_extractor
import record_parser

# path in cui è collocato il database
database_path = "msgstore.db"

# oggetto rappresentante il database
db = database_parser.database(database_path)

# funzione per ottenere i dati presenti nello spazio non allocato delle B-tree leaf pages e dei dati presenti nei freeblock
# inoltre sovrascrive o se non presente crea il file 'raw_data.tsv' contenente i dati grezzi ottenuti (printabili)
# restituisce due liste
unallocated_area, free_block_area = extract_raw_data.get_raw_data(db.size, db.stream, db.page_size)

# dizionario contenente le tabelle e la relativa struttura (campi e tipo dei campi)
patterns = patterns_extractor.get_patterns(database_path)

# tronco il file (se presente)
with open("result.tsv", "w"):
    pass

# itero su i dati delle diverse aree non allocate
for area in unallocated_area:
    # cerco possibili record
    record_parser.analyze_unallocated_area(area, patterns, db.text_encoding)

# itero su i dati trovati nei diversi freeblock
for area in free_block_area:
    record_parser.analyze_unallocated_area(area, patterns, db.text_encoding)

