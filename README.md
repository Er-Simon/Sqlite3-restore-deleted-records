<h1>SQLite3 - Restore Deleted Records</h1>

È uno script python che permette di recuperare i record cancellati, più nello specifico utilizza lo spazio non allocato delle leaf table B-tree pages e dei freeblocks presenti nelle pagine di questo tipo

Lo script è stato testato su file SQLite del formato 3

Al termine dell'esecuzione verrà generato un file "report.html" che permettera la visualizzazione dei record recuperati

<h1>Esecuzione</h1>

<h3>- Collocare un file di tipo SQLite3 all'altezza del file main.py</h3>

<h3>- Rimuovere il file di esempio 'msgstore.db'</h3>

<h3>- Rinominare il file da noi collocato in 'msgstore.db'</h3>

<h3>- Esegui lo script</h3>
<pre>python3 main.py</pre>

<h3>- Visualizzare i dati recuperati mediante il file 'report.html'</h3>
<h3>** La maggior parte dei browser per la politica di sicurezza non permettono il caricamento di file json in locale, per permettere di ignorare / modificare questa politica seguire la procedura in base al browser utilizzato:</h3> 
<p>
  - Google Chrome: google-chrome ./report.html --allow-file-access-from-files
  - Firefox: cercare about:config nella barra di ricerca e impostare a false la voce security.fileuri.strict_origin_policy
</p>

