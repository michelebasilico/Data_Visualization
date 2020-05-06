# Data Visualization

microGrid.py : Il codice permette di visualizzare una sequenza di grafici sulla base della cartella di simulazione. In particolare viene visualizzata energia e potenza di ogni consumatore e produttore, potenza consumata totale e prodotta totale, singole potenze consumate e infine autoconsumo. Il calcolo viene effettuato sulla giornata del 12/12/2015. Il path contenente le cartelle con i singoli dati deve essere il seguente "12/12/2015_116/output"

SingPotFigure: Crea su un'unica pagina più figure con le singole potenze Consumate e Prodotte. I file.csv devono essere all'interno di una cartella 'Energie'.I file.csv dei produttori devono contenere nel loro nome la parola chiave 'prod', verranno graficati in verde. Per i file.csv dei consumatori non è richiesto ma è consigliato che al loro interno contengano la parola chiave 'cons'. I file.csv dei prosumer vengono trattati a parte con un grafico di diverso colore e una label particolare, anche in tal caso è richiesto che il nome del file contenga la parola chiave 'prosumer'. 

self_Consumption.py: Viene generato un grafico ad aree che mostra Autoconsumo,Potenza Prodotta e Generata. E' richiesto che tutti i file.csv dei produttori si trovino all'interno di una cartella 'Produttori' mentre i file.csv dei consumatori all'interno di una cartella 'Consumatori'

Pot_totale: Viene mostrato su un unico grafico la somma di tutta la potenza consumata e la somma di tutta la potenza generata.
E' richiesto che i file.csv dei produttori siano all'interno di una cartella 'Produttori', mentre i file.csv dei Consumatori all'interno di una cartella 'Consumatori'. Le potenze Consumate saranno graficate in rosso, quelle Generate in verde.

Pot_ConsTot: vengono mostrate le singole potenze consumate da ogni dispositivo Consumatore. E' richiesto che tutti i file.csv si trovino all'interno di una cartella 'Consumatori'. Il nome del file viene mostrato nella legenda

power: Libreria contente i moduli per la conversione Unix->Datatime e Energia->Potenza. Inoltre sono state aggiunte le seguenti funzioni
1. data_cleaning(df,date,start='',end'',freq'') -> Per la pulizia dei dati. In ingresso vuole il dataframe da pulire. Date invece è un valore booleano. Se True, indicare deve essere indicata la data sulla quale pulire il dataframe, oltre alla frequenza per ogni campione
2. dfEnergy_to_dfPower(df) -> Trasforma un dataframe con data e energia in un dataframe con data e potenza. Vuole unicamente il dataframe da convertire
3. sum_power(list_df) -> Somma le potenze di una lista di dataframe in base alla sequenza di date uguali. Vuole la lista di dataframe da sommare
4. diff_power(df1,df2) -> Differenza di potenze tra due dataframe. Viene sottratto df2 da df1
5. self_consumption(df_ProdTot,df_ConsTot ) -> Calcolo dell'autoconsumo. Vuole in ingresso un dataframe con la somma delle potenze dei produttori ed un altro con la somma delle potenze consumate
