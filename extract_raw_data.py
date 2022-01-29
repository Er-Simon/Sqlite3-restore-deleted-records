
import os

# per maggiori informazioni riguardanti le b-tree pages consulatre la documentazione al seguente link:
# https://www.sqlite.org/fileformat.html#b_tree_pages

# restituisce una stringa costituita dai soli caratteri printabili
def remove_not_printable_characters(data):
    # Sqlite3 applica una codifica solo alle celle contenenti stringhe 
    return "".join([chr(c) for c in data if chr(c).isprintable()])

# restituisce due liste contenenti dati da cui è possibile ottenere dei record
def get_raw_data(file_size, stream, page_size):

    output = open("raw_data.tsv", "w")
    offset = 0

    unallocated_data, free_block_data = [], []

    # leggo il file incrementando page_size byte alla volta
    while offset < file_size:

        stream.seek(offset, os.SEEK_SET)

        # il valore reperito è utilizzato per indicare il tipo della b-tree page 
        flag = int.from_bytes(stream.read(1), "big")

        # Il valore 13 (0x0d) corrisponde al tipo leaf table b-tree page
        if flag == 13:

            # offset al primo freeblock della pagina
            freeblock_offset = int.from_bytes(stream.read(2), "big")
            # il numero di celle nella pagina
            num_cells = int.from_bytes(stream.read(2), "big")

            # l'inizio dell'area contenente le celle
            cell_offset = int.from_bytes(stream.read(2), "big")
            # leggo l'ultimo byte prima della fine dell'header della b-tree page (contenente il numero di byte liberi frammentati all'interno dell'area contenente le celle)
            int.from_bytes(stream.read(1), "big")

            # offset da dove inizia il contenuto (8 byte dell'header + (il numero di celle * 2 byte)(cell pointer array))
            start = 8 + (num_cells * 2)

            # lunghezza unallocated space
            length = cell_offset - start

            # mi colloco all'inizio dell'unallocated area
            stream.read(num_cells * 2)

            unallocated = stream.read(length)
            unallocated_data.append(unallocated)
            unallocated = remove_not_printable_characters(unallocated)

            if unallocated != "":
                output.write("unallocated\t"+ str(offset+start) + "\t" + str(length) + "\t" + unallocated + "\n")

            # se c'è un blocco libero nella pagina
            while freeblock_offset != 0:

                # mi sposto all'inizio del freeblock
                stream.seek(offset+freeblock_offset, os.SEEK_SET)
                
                # ottengo il prossimo blocco libero
                next_fb_offset = int.from_bytes(stream.read(2), "big")
            
                # ottengo la size del blocco (INCLUDE I 4 BYTE DELL'HEADER)
                free_block_size = int.from_bytes(stream.read(2), "big")
                
                # leggo il contenuto
                free_block = stream.read(free_block_size - 4)
                free_block_data.append(free_block)
                free_block  = remove_not_printable_characters(free_block)

                if free_block != "":
                    output.write("free block\t"+ str(offset+freeblock_offset) + "\t" + str(free_block_size) + "\t" + free_block + "\n")

                # passo al freeblock successivo
                freeblock_offset = next_fb_offset

        offset = offset + page_size

    output.close()

    return unallocated_data, free_block_data