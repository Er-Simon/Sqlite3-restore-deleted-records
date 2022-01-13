import sqlite3

def get_patterns(database_file):

    # apro il file tramite il modulo sqlite3
    conn = sqlite3.connect(database_file)
    # cur mi permetterà di eseguire comandi sql
    cur = conn.cursor()

    # utilizzerò un dizionario per immagazzinare i pattern delle tabelle in modo da riconoscere a quale tabella appartiene un record
    # le chiavi saranno la lunghezza della tabella (il numero di campi in una tabella) e i valori una lista contenente dizionari 
    # in cui la chiave sarà il nome della tabella e i valori una lista di tuple rappresentanti i campi (nome, tipo, not null)
    pattern = dict()

    # ottengo una lista delle tabelle costituenti il database
    tables = [table[0] for table in cur.execute("SELECT name FROM sqlite_master WHERE type='table'")]

    # per ogni tabella ne ottengo la struttura
    for table in tables:

        # struttura della tabella
        # field number, field name, field type, field not null, NaN, field primary key
        results = cur.execute("PRAGMA table_info(" + table + ")").fetchall()
        length = len(results)

        if length not in pattern:
            pattern[length] = dict()

        pattern[length][table] = []

        for data in results:
            if data[2] == 'BLOB':
                type_ = 'TEXT'
            else:
                type_ = data[2]

            pattern[length][table].append((data[1],type_, data[3]))


    conn.close()

    return pattern


# esempio pattern[2] : tutte le tabelle che hanno due campi e le informazioni 

# 2: { 
#       'message_ftsv2_segments' : 
#           [('blockid', 'INTEGER', 0), ('block', 'BLOB', 0)], 
#      'message_ftsv2_docsize': 
#           [('docid', 'INTEGER', 0), ('size', 'BLOB', 0)]
#    }