

import struct

# Per maggiori informazioni consultare le seguenti pagine della documentazione:
# https://www.sqlite.org/fileformat.html#b_tree_pages   (informazioni relative alle variabili varint)
# https://www.sqlite.org/fileformat.html#schema_layer

# a partire dal tipo di dati costituenti un record trova le tabelle aventi la stessa struttura e i nomi delle colonne
def patterns_finder(table_header, patterns):
    results = []
    length = len(table_header)

    try:
        for table in patterns[length]:
            flag = True

            for index in range(1, len(patterns[length][table])):
                if patterns[length][table][index][1] != table_header[index][0] and (table_header[index][0] != 'NULL_VALUE' and table_header[index][1] != 0):
                    flag = False
                    break

                if patterns[length][table][index][2] == 1 and len(table_header[index][1]) == 0:
                    flag = False
                    break

            if flag:
                results.append([field[0] for field in patterns[length][table]])
                results[-1].append(table)

    except:
        pass
    
    return results

# trasforma una variabile varint in un int
def varint_to_int(varint):
    value = 0
    varint = varint.split()
    length = len(varint)

    for var in varint[:-1]:
        value += (int(var, 16) - 128) * (128 ** (length - 1))
        length -= 1
    value += int(varint[-1], 16)

    return value

# a partire da una lista contenente valori esadecimali restituisce la loro rappresentazione in variabili varint
def transform_to_varint(data):
    varint = ""
    varints = []

    for hex in data:
        value = int(hex, 16)

        if value > 128:
            varint += hex + " "
        
        elif value == 0:

            if varint == "":
                varints.append((0, 1))
            
            else:
                varints.append((varint_to_int(varint), varint.count(" ")))
                varint = ""

        elif varint == "":
                varints.append((value, 1))
            
        else:
            varint += hex + " "
            varints.append((varint_to_int(varint), varint.count(" ")))
            varint = ""

    return varints

# a partire da variabili varint rappresentanti l'header della tabella (i campi)
# ne restituisce il tipo e la grandezza occupata in byte per ciascun campo
def parse_cell_type(value):
    d = dict()
    type_, size = "NULL", 0

    for val in range(len(value)):
        
        if value[val][0] == 0:
            type_, size = "null_value", 0
        elif value[val][0] == 1:
            type_, size = "int-8-bit", 1
        elif value[val][0] == 2:
            type_, size = "int-16-bit", 2
        elif value[val][0] == 3:
            type_, size = "int-24-bit", 3
        elif value[val][0] == 4:
            type_, size = "int-32-bit", 4
        elif value[val][0] == 5:
            type_, size = "int-48-bit", 6
        elif value[val][0] == 6:
            type_, size = "int-64-bit", 8
        elif value[val][0] == 7:
            type_, size = "floating-64-bit", 8
        elif value[val][0] == 8:
            type_, size = "int-0", 0
        elif value[val][0] == 9:
            type_, size = "int-1", 0
        elif value[val][0] == 10 or value[val][0] == 11:
            type_, size = "variabile", 0
        elif value[val][0] >= 12 and value[val][0] % 2 == 0:
            type_, size = "blob", (value[val][0] - 12) // 2
        elif value[val][0] >= 13 and value[val][0] % 2 == 1:
            type_, size = "string", (value[val][0] - 13) // 2
        else:
            print("Tipo cella non rilevato")

        d[val] = (type_, size)

    return d
# a partire dal tipo di celle e lo spazio occupato da ciascuna cella in byte restituisce il tipo generico (es. int-8-bit -> INTEGER) e il contenuto di ciascuna cella
def extract_cells(area, cells_type, encoding):
    row = []
    index = 0

    try:
        for cell in cells_type:
            if cells_type[cell][0] == 'null_value':
                row.append(("NULL_VALUE", ''))
            elif cells_type[cell][0] == 'int-8-bit':
                row.append(("INTEGER", int.from_bytes(area[index:index + cells_type[cell][1]], "big")))
            elif cells_type[cell][0] == 'int-16-bit':
                row.append(("INTEGER", int.from_bytes(area[index:index + cells_type[cell][1]], "big")))
            elif cells_type[cell][0] == 'int-24-bit':
                row.append(("INTEGER", int.from_bytes(area[index:index + cells_type[cell][1]], "big")))
            elif cells_type[cell][0] == 'int-32-bit':
                row.append(("INTEGER", int.from_bytes(area[index:index + cells_type[cell][1]], "big")))
            elif cells_type[cell][0] == 'int-48-bit':
                row.append(("INTEGER", int.from_bytes(area[index:index + cells_type[cell][1]], "big")))
            elif cells_type[cell][0] == 'int-64-bit':
                row.append(("INTEGER", int.from_bytes(area[index:index + cells_type[cell][1]], "big")))
            elif cells_type[cell][0] == "floating-64-bit":
                row.append(("REAL", struct.unpack('d', area[index:index + cells_type[cell][1]])))
            elif cells_type[cell][0] == "int-0":
                row.append(("INTEGER", 0))
            elif cells_type[cell][0] ==  "int-1":
                row.append(("INTEGER", 1))
            elif cells_type[cell][0] == "variabile":
                #print("Variabile (?) ATTENZIONE")
                pass
            elif cells_type[cell][0] == "blob":
                # ho messo "TEXT" anzichè blob perchè altrimenti non trovavo correttamente i record
                # ho applicato la stessa modifica a patterns_extractor
                row.append(("TEXT", area[index:index + cells_type[cell][1]]))
            elif cells_type[cell][0] == "string":
                row.append(("TEXT", area[index:index + cells_type[cell][1]].replace(b"\n", b" ").decode(encoding)))

            index += cells_type[cell][1]
    except:
        return None

    return row


def parse_record(data, area, patterns, encoding):
    
    # converto i valori esadecimali in varint
    varints = transform_to_varint(data)

    # se non ci sono almeno 3 varint allora non può essere un record
    if len(varints) < 3:
        return

    # Num of bytes del payload include overflow
    #print("Num of bytes del payload", varints[0][0], varints[0][1])
    #print("Row ID", varints[1][0], varints[1][1])
    
    # il payload (record) definisce una sequenza di valori corrispondenti alle colonne di una tabella spcificando il numero di colonne, il tipo di dati di ciascuna colonna e il contenuto di ciascuna colonna.
    # Un record contiene un' header e un corpo. L'header inizia con una varint che determina il numero totale di byte nell'intestazione. 
    # Il valore varint è la dimensione dell'intestazione in byte, inclusa la dimensione in byte occupata dall var varint stessa. 
    # A seguire ci sono una o più varint, una per colonna. 
    # Queste varint sono di tipo seriale e determinano il tipo di dati di ciascuna colonna
    # print("Dimensione del payload senza overflow:", varints[2][0], varints[2][1])

    if varints[0][0] == 0 or varints[1][0] == 0 or varints[2][0] == 0 or \
        len(area) < (varints[0][1] + varints[1][1] + varints[2][0]):
        return


    # 3 perchè prima delle varint nell'header relative alle celle ci sono 3 varint (payload_length, rowid, header_legnth_senza_overflow)
    # restituisce una lista contenente tuple ("tipo di dato", "dimensione occupata in byte")
    cells = parse_cell_type(varints[3:3 + len(transform_to_varint([hex(x) for x in area[varints[0][1] + varints[1][1] + varints[2][1] : varints[0][1] + varints[1][1] + varints[2][0]]]))])

    # restituisce il tipo e il contenuto di ciascuna cella del record
    row = extract_cells(area[varints[0][1] + varints[1][1] + varints[2][0]:], cells, encoding)

    if row == None:
        return

    table_header = "ID\t" + "".join([str(x[0]) + "\t" for x in row[1:]]) + str(len(row)) + "\t"

    # a partire una lista contenente tuple formate da ("TIPO DI DATO", "VALORE") restituisce le tabelle candidate (cioè a cui potrebbe potenzialmente appartenere il record)
    match = patterns_finder(row, patterns)

    if match == []: return

    row_data = str(varints[1][0]) + "\t"

    for index in range(1, len(row)):
        row_data += str(row[index][1]) + "\t"
        
    row_data = row_data[:-1]

    f_out = open("result.tsv", "a")

    f_out.write(table_header+"\n")

    for m in match:
        f_out.write("".join([field + "\t" for field in m])+"\n")

    f_out.write(row_data+"\n\n")

    f_out.close()

    return varints[0][0]


def analyze_unallocated_area(area, patterns, encoding):

    area_hex = [hex(byte) for byte in area]

    for index in range(len(area_hex)):

        # B-tree Cell Format
        # 1 - varint - Number of bytes of payload
        # 2 - varint - RowID
        # 3 - byte array - Payload
        # 4 - 4-byte integer -	Page number of first overflow page
        if area_hex[index] != "0x0":

            # parse_record mi restituirà il num di bytes da saltare se è riuscita a trovare un record
            flag = parse_record(area_hex[index:], area[index:], patterns, encoding)

            if flag != None:
                # rieseguo la funzione ridimensionado l'area da ispezionare
                return analyze_unallocated_area(area[index+flag:], patterns, encoding)
        

