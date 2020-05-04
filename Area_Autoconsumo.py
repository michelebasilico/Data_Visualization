from bokeh.plotting import figure,output_file,show,ColumnDataSource
from bokeh.models import DatetimeTickFormatter
import pandas
import datetime as dt
import os,os.path
import glob
import power as pw
import numpy as np

#Lettura dei file csv consumatori
csv_Cons = glob.glob('Dati/Consumatori' + "/*.csv")
n_Cons = len(csv_Cons)
df_Cons = [ pandas.read_csv(f,sep = ' ') for f in csv_Cons ]

#Lettura dei file csv produttori
csv_Prod = glob.glob('Dati/Produttori' + "/*.csv")
n_Prod = len(csv_Prod)
df_Prod = [ pandas.read_csv(f,sep = ' ') for f in csv_Prod ]

#Creazione datatimeIndex del range della giornata da visualizzare (Serve per avere tutti i punti delle ascisse per la giornata)
giornata = pandas.date_range(start='2015/12/12 00:00:00',end='2015/12/12 23:59:59',freq='1s')

"""
df_EV = pandas.read_csv('EV/eoutEV.csv',sep = ' ')
time = pw.Unix_to_hours(df_EV)
df_EV2 = df_EV.set_index('date').resample('1s').mean().interpolate('linear')
df_EV2 = df_EV2.reindex(giornata)
df_EV2 = df_EV2.fillna(0)
energy = df_EV2['energy'].tolist()
time = df_EV2.index.tolist()
power = pw.calc_Pot(time,energy)
ultimo_elemento = len(df_EV2) - 2
df_EV2 = df_EV2.drop([ultimo_elemento])
Creo il dataframe del singolo Consumatore e lo aggiungo alla lista
df_EV2 = df_EV2.reset_index()
data = {'date': df_EV2['index'][:-1], 'power': power}
dataframe = pandas.DataFrame(data)
dataframe = dataframe.set_index('date')
"""

#Creazione di una lista di dataframe di consumatori
#df_PCons = [dataframe]

df_PCons = []
for i in range(n_Cons):

    #Per BackGroundLoad che comincia da 0 -> Aggiungo la data del 12 dicembre 2015 00:00:00
    if(df_Cons[i]['date'][0] == 0):
        df_Cons[i]['date'] = df_Cons[i]['date'] + 1449882000
    #Per HeaterCooler che comincia nel 2016
    if(df_Cons[i]['date'][0] == 1475877600):
        df_Cons[i]['date'] = df_Cons[i]['date'] - 25999200
    #Genero la lista del tempo a partire dal dataframe
    time = pw.Unix_to_hours(df_Cons[i])
    #Genero la lista dell'energia //
    energy = df_Cons[i]['energy'].tolist()
    #Eseguo il calcolo della potenza
    power = pw.calc_Pot(time,energy)
    #Elimino l'utlima riga(La potenza ha una riga in meno dell'energia)
    ultimo_elemento = len(df_Cons[i]) - 1
    df_Cons[i] = df_Cons[i].drop([ultimo_elemento])
    #Creo il dataframe del singolo Consumatore e lo aggiungo alla lista
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

#Concateno i dataframe dei Consumatori
df_ConsTot = pandas.concat(df_PCons)
#Li raggruppo in base alla data e sommo le potenze(con data uguale)
df_ConsTot = df_ConsTot.groupby(df_ConsTot.index)[['power']].sum()
#La potenza dei consumatori diventa negativa in modo da effettuare il calcolo dell'autoconsumo
df_ConsTot["power"] *= -1

#Concateno i dataframe dei produttori
df_ProdTot = pandas.concat(df_PProd)
#Li raggruppo in base alla data e sommo le potenze(con data uguale)
df_ProdTot = df_ProdTot.groupby(df_ProdTot.index)[['power']].sum()

#Definiamo l'autoconsumo
#Creo una lista di dataframe contententi i dataframe dei consumatori e dei produttori
df_ConsProd = [df_ProdTot, df_ConsTot]
#creo un singolo dataframe concatenando quelli presenti in lista
df_Autoconsumo = pandas.concat(df_ConsProd)
#raggruppo per data e sommo(in realtà è una differenza)
df_Autoconsumo = df_Autoconsumo.groupby(df_Autoconsumo.index)[['power']].sum()
#Tutti gli elementi al di sotto dello 0 vengono sostituiti con lo 0
df_Autoconsumo['power'][ df_Autoconsumo['power'] < 0 ] = 0


#Rimetto la potenza dei consumatori positiva
df_ConsTot["power"] *= -1


#Genero il dataframe per il grafico ad aree
n = len(giornata)
zeros = [0]*n
data = {'x_values': giornata,'autoconsumo': df_Autoconsumo['power'],'generata': df_ProdTot['power'],'consumata': df_ConsTot['power'],'zeros': zeros}
source = ColumnDataSource(data = data)

#Costruiamo il plot
p = figure(

    plot_width = 1500,
    plot_height = 600,
    title = 'Autoconsumo: PotenzaGenerata-PotenzaConsumata',
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

#Creo la lista dei nomi per la leggenda e le colonne del ColumnDataSource
#names = ['generata','consumata']
#Creo il grafico ad aree
#p.varea_stack(stackers = names, x='x_values', color=['green','red'], legend_label=names, source=source,alpha = 0.8)

p.varea(x='x_values',y1 = 'zeros', y2 = 'generata',source = source, color = 'green', alpha = 0.8, legend_label = 'generata')
p.varea(x='x_values',y1 = 'zeros', y2 = 'consumata',source = source, color = 'red', alpha = 0.8, legend_label = 'consumata')

p.varea(x='x_values',y1 = 'zeros', y2 = 'autoconsumo',source = source, color = 'yellow', alpha = 0.7, legend_label = 'autoconsumo')


show(p)
