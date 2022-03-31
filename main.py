
import database_parser
import extract_raw_data
import patterns_extractor
import records_parser
import report_builder


# path in cui è collocato il database
database_path = "msgstore.db"

# oggetto rappresentante il database
db = database_parser.database(database_path)

# oggetto rappresentante le informazioni ottenute durante l'esecuzione dello script
report = report_builder.report(database_path, db.size, db.text_encoding)

# funzione per ottenere i dati presenti nello spazio non allocato delle B-tree leaf pages e dei dati presenti nei freeblock
# inoltre sovrascrive o se non presente crea il file 'raw_data.tsv' contenente i dati grezzi ottenuti (printabili)
# restituisce due liste
unallocated_area, free_block_area = extract_raw_data.get_raw_data(db.size, db.stream, db.page_size)

# dizionario contenente le tabelle e la relativa struttura (campi e tipo dei campi)
patterns = patterns_extractor.get_patterns(database_path)

# salvo nella variabile "data" della classe report la struttura delle tabelle e dei relativi campi
report.set_schema_info(patterns)
# recupero il dizionario in cui sono salvate le informazioni del report
data = report.get_data()

# tronco il file (se presente)
with open("result.tsv", "w"):
    pass 

# itero su i dati delle diverse aree non allocate
for area in unallocated_area:
    # cerco possibili record
    records_parser.parse_records(area, db.text_encoding, patterns, data)

# itero su i dati trovati nei diversi freeblock
for area in free_block_area:
    records_parser.parse_records(area, db.text_encoding, patterns, data)

# assegno il dizionario aggiornato contenente le informazioni sull'esecuzione alla variabile "data" della classe report
report.set_data(data)
# salvo il dizionario nel file "data.json", esso verrà utilizzato dalla pagina "report.html"
report.save_data()
