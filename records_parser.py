import struct


# trovo possibili tabelle candidate sulla base della struttura del record trovato
def patterns_finder(table_header, patterns):
    results = []
    length = len(table_header)

    try:
        if length in patterns:
            #print(f"Tabelle candidate {patterns[length]}")

            for table in patterns[length]:

                #print(f"{table} {patterns[length][table]}")

                for field_index in range(len(patterns[length][table])):

                    #print(f"Confronto {table_header[field_index]} <--:--> {patterns[length][table][field_index]} ({length}, {field_index})")

                    if field_index == 0 and patterns[length][table][field_index][3] == 1 and table_header[field_index][0] != "NULL":
                        break

                    if table_header[field_index][0] == "NULL" and patterns[length][table][field_index][2] == 1:
                        break

                    if table_header[field_index][0] == "INTEGER" and patterns[length][table][field_index][1] == "REAL" and patterns[length][table][field_index][2] == 0:
                        pass

                    elif table_header[field_index][0] == "TEXT" and patterns[length][table][field_index][1] == "" and patterns[length][table][field_index][2] == 0:
                        pass

                    elif patterns[length][table][field_index][1] != table_header[field_index][0] and table_header[field_index][0] != "NULL":
                        break

                    if field_index == (length - 1):
                        results.append([field[0] for field in patterns[length][table]])
                        results[-1].append(table)
    except:
        pass            
                
    return results


# converto un array di bytes in un array di varint in cui ciascun elemento consiste in;
# (valore della var varint in int, num di bytes utilizzati per rappresentarla)
def bytes_to_varint(area):
    length = len(area)
    count = 0

    temp = []
    temp_length = 0
    temp_value = 0

    varints = []

    while count != length:

        if area[count] < 128:
            if temp == []:
                varints.append((area[count], 1))
            else:
                for x in range(temp_length):
                    temp_value += (temp[x] - 128) * (128**(temp_length-x))

                temp_value += area[count]
                varints.append((temp_value, temp_length+1))

                temp = []
                temp_length = 0
                temp_value = 0
                
        else:
            temp.append(area[count])
            temp_length += 1

        count+=1

    return varints

# a seconda del valore determino il tipo di dato e il num di byte
# https://www.sqlite.org/fileformat2.html#serialtype
def parse_serial_type(heading):

    serial_type = []

    for cell in heading:

        if cell == 0:
            serial_type.append(("NULL", 0))
        elif cell == 1:
            serial_type.append(("INTEGER", 1))
        elif cell == 2:
            serial_type.append(("INTEGER", 2))
        elif cell == 3:
            serial_type.append(("INTEGER", 3))
        elif cell == 4:
            serial_type.append(("INTEGER", 4))
        elif cell == 5:
            serial_type.append(("INTEGER", 6))
        elif cell == 6:
            serial_type.append(("INTEGER", 8))
        elif cell == 7:
            serial_type.append(("REAL", 8))
        elif cell == 8:
            serial_type.append(("INTEGER-0", 0))
        elif cell == 9:
            serial_type.append(("INTEGER-1", 0))
        elif cell >= 12 and cell % 2 == 0:
            serial_type.append(("BLOB", (cell-12) // 2))
        elif cell >= 13 and cell % 2 == 1:
            serial_type.append(("TEXT", (cell-13) // 2))
        else:
            #print("Serial Types riservati per uso interno {10, 11}\nThese serial type codes will never appear in a well-formed database file, but they might be used in transient and temporary database files that SQLite sometimes generates for its own use.")
            return None

    return serial_type

# a partire dall informazioni ottenute tramite l'header sulla struttura del record provo a recuperarne il contenuto di ciascuna cella
def parse_record_content(header, data, text_encoding):

    content = []
    count = 0

    try:
        for field in header:
            if field[0] == 'NULL':
                content.append((field[0], 0))
            elif field[0] == 'TEXT':
                content.append((field[0], data[count:count+field[1]].decode(text_encoding).replace("\n", " ")))
            elif field[0] == 'BLOB':
                content.append((field[0], data[count:count+field[1]]))
            elif field[0] == 'INTEGER':
                content.append((field[0], int.from_bytes(data[count:count+field[1]], "big", signed=True)))
            elif field[0] == 'REAL':
                content.append((field[0], struct.unpack('q', data[count:count+field[1]])))
            elif field[0] == 'INTEGER-0':
                content.append(('INTEGER', 0))
            elif field[0] == 'INTEGER-1':
                content.append(('INTEGER', 1))

            count += field[1]
    except Exception as e:
        #print(f"Non è stato possibile parsare il contenuto del record correttamente:\n{e}")
        pass

    return content


# funzione ausiliare per capire se il contenuto del record trovato sia vuoto
def is_empty(content):

    status = True

    for field in content:
        if type(field[1]) == int and field[1] != 0:
            status = False
            break

        if type(field[1]) == str and field[1] != '' and set(field[1]) != {'\x00'}:
            status = False
            break
    
        if type(field[1]) == bytes and int.from_bytes(field[1], 'big') != 0:
            status = False
            break

    return status

# ottenuto l'array contenente le variabili varint provo a ottenere un record
# ciascun record inizia con una varint che quantifica il num di bytes del payload del record
# una seconda varint che rappresenta la row_id del record
# un array di byte rappresentante il payload
def parse_varint_to_record(varints, area, text_encoding, patterns, data):

    #print(f"Number of bytes of payload {varints[0][0]}")

    if varints[3][0] == 0:
        #print(f"Row ID {varints[1][0]}")
        pass
    else:
        #print(f"SQLite auto Row ID {varints[1][0]}")
        pass
    
    #print(f"Number of bytes of header {varints[2][0]}")

    count = varints[2][0] - varints[2][1]

    header = []

    for var in varints[3:]:
        if count > 0:
            header.append(var[0])
            count -= var[1]

    #print(f"Record Header {header}")

    # il payload è costituito dall'header e dal body, converto l'header in tipi seriali
    # che non sono altro delle variabili varint che rappresentano il tipo di dato di un determinata colonna e 
    # il num di bytes utilizzati per rappresentare il contenuto
    header_serial_type = parse_serial_type(header)

    if not header_serial_type:
        return 0

    #print(f"Record Header Serial type {header_serial_type}")

    #print(f"Byte contenenti i dati {area[varints[0][1]+varints[1][1]+varints[2][0]:varints[0][1]+varints[1][1]+varints[2][0]+varints[0][0]]}")
    
    # ottengo il contenuto delle celle dal body sulla base delle informazioni ottenute tramite l'header
    record_content = parse_record_content(header_serial_type, area[varints[0][1]+varints[1][1]+varints[2][0]:varints[0][1]+varints[1][1]+varints[2][0]+varints[0][0]], text_encoding)

    if is_empty(record_content):
        return 0

    #print(f"Record content {record_content}")

    # controllo che la struttura del record trovato abbia qualche tabelle candidata
    match = patterns_finder(record_content, patterns)
    
    if match == []:
        return 0 

    # salvo le informazioni del record per le tabelle candidate
    for match_info in match:
        if "records" not in data["data"][match_info[-1]]:
            data["data"][match_info[-1]]["records"] = [[varints[1][0]]]
        else:
            data["data"][match_info[-1]]["records"].append([varints[1][0]])

        if record_content[0][0] == "NULL":
            start = 1
        else:
            start = 0

        for index in range(start, len(record_content)):
            if type(record_content[index][1]) == bytes:
                record_content[index] = (record_content[index][0], str(record_content[index][1]))

            data["data"][match_info[-1]]["records"][-1].append(record_content[index][1])

    return varints[0][0]


# ispeziono byte per byte l'array di byte "area" alla ricerca dei record
def parse_records(area, text_encoding, patterns, records):

    length = len(area)
    count = 0

    while count < length:

        if area[count] > 1:
            # converto un sub-array di byte in un array contenente variabili di tipo varint     https://www.sqlite.org/fileformat2.html#varint
            varints = bytes_to_varint(area[count:])

            # controllo che ci siano almeno 3 varint in quanto ogni record ne possiede almeno 3
            if len(varints) > 3 and varints[2][0] > 0:
                # provo a parsare un record, se ne trovassi uno incremento il contatore "count" tanti byte quanto è la lunghezza del record trovato
                count += parse_varint_to_record(varints, area[count:], text_encoding, patterns, records)

        count += 1


