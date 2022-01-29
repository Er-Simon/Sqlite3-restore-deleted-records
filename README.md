<h1>SQLite3 - Restore Deleted Records</h1>

È uno script python che permette di recuperare i record cancellati, più nello specifico utilizza lo spazio non allocato delle leaf table B-tree pages e dei freeblocks presenti nelle pagine di questo tipo

Lo script è stato testato su file SQLite del formato 3

<h1>Esecuzione</h1>

<h3>- Collocare un file di tipo SQLite3 all'altezza del file main.py</h3>

<h3>- Rimuovere il file di esempio 'msgstore.db'</h3>

<h3>- Rinominare il file da noi collocato in 'msgstore.db'</h3>

<h3>- Esegui lo script</h3>
<pre>python3 main.py</pre>
  
