# ESN
SingPotFigure: Crea su un'unica pagina più figure con le singole potenze Consumate e Prodotte. I file.csv devono essere all'interno di una cartella 'Energie'.I file.csv dei produttori devono contenere nel loro nome la parola chiave 'prod', verranno graficati in verde. Per i file.csv dei consumatori non è richiesto ma è consigliato che al loro interno contengano la parola chiave 'cons'. I file.csv dei prosumer vengono trattati a parte con un grafico di diverso colore e una label particolare, anche in tal caso è richiesto che il nome del file contenga la parola chiave 'prosumer'. 

AreaChart: Viene generato un grafico ad aree che mostra Autoconsumo,Potenza Prodotta e Generata. E' richiesto che tutti i file.csv dei produttori si trovino all'interno di una cartella 'Produttori' mentre i file.csv dei consumatori all'interno di una cartella 'Consumatori'

Pot_totale: Viene mostrato su un unico grafico la somma di tutta la potenza consumata e la somma di tutta la potenza generata.
E' richiesto che i file.csv dei produttori siano all'interno di una cartella 'Produttori', mentre i file.csv dei Consumatori all'interno di una cartella 'Consumatori'. Le potenze Consumate saranno graficate in rosso, quelle Generate in verde.

autoConsumo: viene mostrato un grafico ad aree con l'autoconsumo(potenza generata-consumata). E' richiesto che i file.csv dei produttori siano all'interno di una cartella 'Produttori', mentre i file.csv dei Consumatori all'interno di una cartella 'Consumatori'. 

Pot_ConsTot: vengono mostrate le singole potenze consumate da ogni dispositivo Consumatore. E' richiesto che tutti i file.csv si trovino all'interno di una cartella 'Consumatori'. Il nome del file viene mostrato nella legenda

power: Libreria contente i moduli per la conversione Unix->Datatime e Energia->Potenza
