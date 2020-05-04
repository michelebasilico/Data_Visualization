from bokeh.plotting import figure,output_file,show,ColumnDataSource
from bokeh.models import DatetimeTickFormatter
import pandas
import datetime as dt
import os,os.path
import glob
import power as pw


#Leggo i file nella cartella Consumatori e genero un dataframe per ognuno di essi, inserendoli all'interno di un dataframe
csv_Cons = glob.glob('Dati/Consumatori' + "/*.csv")
n_Cons = len(csv_Cons)
df_Cons = [ pandas.read_csv(f,sep = ' ') for f in csv_Cons ]

#Leggo i file nella cartella Produttori e genero un dataframe per ognuno di essi, inserendoli all'interno di un dataframe
csv_Prod = glob.glob('Dati/Produttori' + "/*.csv")
n_Prod = len(csv_Prod)
df_Prod = [ pandas.read_csv(f,sep = ' ') for f in csv_Prod ]

#Creazione datatimeIndex del range della giornata da visualizzare (Serve per avere tutti i punti delle ascisse per la giornata)
giornata = pandas.date_range(start='2015/12/12 00:00:00',end='2015/12/12 23:59:59',freq='1s')

#Per ogni dataframe Consumatore
df_PCons = []
for i in range(n_Cons):
    if(df_Cons[i]['date'][0] == 0):
        df_Cons[i]['date'] = df_Cons[i]['date'] + 1449882000
    #Per HeaterCooler che comincia nel 2016
    if(df_Cons[i]['date'][0] == 1475877600):
        df_Cons[i]['date'] = df_Cons[i]['date'] - 25999200
    #Genero la lista tempo del Dispositivo Consumatore
    time = pw.Unix_to_hours(df_Cons[i])
    #Genero la lista energia del Dispositivo Consumatore
    energy = df_Cons[i]['energy'].tolist()
    #Genero la potenza del Dispositivo Consumatore
    power = pw.calc_Pot(time,energy)
    #Elimino l'ultimo elemento del tempo per la rappresentazione della potenza
    ultimo_elemento = len(df_Cons[i]) - 1
    df_Cons[i] = df_Cons[i].drop([ultimo_elemento])
    #Genero i dati per la creazione dei dataframe
    data = {'date': df_Cons[i]['date'], 'power': power}
    dataframe = pandas.DataFrame(data)
    #I dati vengono acquisiti senza una frequenza fissata e questo comporta diversi problemi. Creiamo un nuovo dataframe con 
    #un campione ogni secondo. I valori vengono riempiti attraverso l'interpolazione lineare tra i campioni esistenti
    dataframeNuovo = dataframe.set_index('date').resample('1s').mean().interpolate('linear')
    #Aggiorniamo l'indice con quello della giornata intera, in modo da avere una riga per ogni secondo della giornata
    #I vecchi valori rimangono uguali, quelli che vengono aggiunti, vengono immessi con valore NaN
    dataframeNuovo = dataframeNuovo.reindex(giornata)
    #Sostituiamo tutti i valori NaN con 0
    dataframeNuovo = dataframeNuovo.fillna(0)
    #Aggiungiamo il dataframe creato in ogni ciclo alla lista
    df_PCons += [dataframeNuovo]

#Vedi sopra
df_PProd = []
for i in range(n_Prod):
    if(df_Prod[i]['date'][0] == 0):
        df_Prod[i]['date'] = df_Prod[i]['date'] + 1449878400
    time = pw.Unix_to_hours(df_Prod[i])
    energy = df_Prod[i]['energy'].tolist()
    power = pw.calc_Pot(time,energy)
    ultimo_elemento = len(df_Prod[i]) - 1
    df_Prod[i] = df_Prod[i].drop([ultimo_elemento])
    data = {'date': df_Prod[i]['date'], 'power': power}
    dataframe = pandas.DataFrame(data)
    dataframeNuovo = dataframe.set_index('date').resample('1s').mean().interpolate('linear')
    dataframeNuovo = dataframeNuovo.reindex(giornata)
    dataframeNuovo = dataframeNuovo.fillna(0)
    df_PProd += [dataframeNuovo]
    

#Concateno i dataframe dei consumatori
df_ConsTot = pandas.concat(df_PCons)
#Raggruppo i dataframe dei consumatori per data e li sommo(se la data è uguale). Vengono anche ordinati
df_ConsTot = df_ConsTot.groupby(df_ConsTot.index)[['power']].sum()
#Creo i dati per la visualizzazione
datafinale1 = {'x_values': giornata, 'y_values': df_ConsTot['power']}

#Vedi sopra
df_ProdTot = pandas.concat(df_PProd)
df_ProdTot = df_ProdTot.groupby(df_ProdTot.index)[['power']].sum()
datafinale2 = {'x_values': giornata, 'y_values': df_ProdTot['power']}



#Creo due ColumnDataSource per la visualizzazione di consumatori e produttori
source1 = ColumnDataSource(data=datafinale1)
source2 = ColumnDataSource(data=datafinale2)

#Costruiamo il plot
p = figure(

    plot_width = 1500,
    plot_height = 600,
    title = 'Potenza Totale',
    x_axis_label = 'Data',
    y_axis_label = 'Potenza(kW)',
    x_axis_type = 'datetime'
    

)

p.xaxis.formatter = DatetimeTickFormatter(
    
    years="20%y/%m/%d %H:%M",
    days="20%y/%m/%d %H:%M",
    months="20%y/%m/%d %H:%M",
    hours="20%y/%m/%d %H:%M",
    minutes="20%y/%m/%d %H:%M"
    
    ) 

#Visualizzo i consumatori
p.line(

        x = 'x_values',
        y = 'y_values',
        source = source1,
        line_width=4,
        color = 'red',
        alpha = 0.8,
        legend_label = 'Potenza consumata totale'

    )

#Visualizzo i produttori
p.line(

        x = 'x_values',
        y = 'y_values',
        source = source2,
        line_width=4,
        color = 'green',
        alpha = 0.8,
        legend_label = 'Potenza generata totale'

    )

show(p)