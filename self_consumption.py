from bokeh.plotting import figure,output_file,show,ColumnDataSource
from bokeh.models import DatetimeTickFormatter
import pandas
import datetime as dt
import os,os.path
import glob
import power as pw
import numpy as np

#Lettura dei file csv
csv_file = glob.glob('Energy' + "/*.csv")
n_file = len(csv_file)
df_file = [ pandas.read_csv(f,sep = ' ') for f in csv_file ]
#Definisco i nomi dei file
nameFile = os.listdir('Energy')

#Definisco la used_Day da visualizzare
used_Day = pandas.date_range(start='2015/12/12 00:00:00',end='2015/12/12 23:59:59',freq='5T')

df_Cons = []
df_Prod = []
for i in range(n_file):
    new_df = []
    #Per BackGroundLoad che comincia da 0 -> Aggiungo la data del 12 dicembre 2015 00:00:00
    if(df_file[i]['date'][0] == 0):
        df_file[i]['date'] = df_file[i]['date'] + 1449882000
    #Per HeaterCooler che comincia nel 2016
    if(df_file[i]['date'][0] == 1475877600):
        df_file[i]['date'] = df_file[i]['date'] - 25999200
    #df_file[i]['date'] viene convertito in formato datetime e convertito dal formato epochUnix
    df_file[i][ 'date' ] = pandas.to_datetime(df_file[i]['date'], origin='unix',unit = 's')
    #Puliamo i dati per ogni frame attraverso un resample e un interpolazione(Ogni minuto un campione)
    new_df = df_file[i].set_index('date').resample('1T').mean().interpolate('linear')    
    #Aggiungo al dataframe gli indici di tutta la used_Day
    new_df = new_df.reindex(used_Day)
    #Gli indici senza valore sono NaN e li sostituiamo con uno 0
    new_df = new_df.fillna(0)
    #Resettiamo l'indice
    new_df.index.name = 'date'
    new_df = new_df.reset_index()
    #Genero la lista dell'energia(i dati sono puliti, per ogni minuto) e delle ore
    energy = new_df['energy'].tolist()
    time = new_df['date'].dt.time
    
    #Eseguo il calcolo della potenza
    power = pw.calc_Pot(time,energy)
    power = [0 if i < 0 else i for i in power]
    #Elimino l'utlima riga(La potenza ha una riga in meno dell'energia)
    ultimo_elemento = len(new_df) - 1
    new_df = new_df.drop([ultimo_elemento])
    #Creo il dataframe del singolo file e lo aggiungo alla lista a secondo della tipologia
    data = {'date': new_df['date'], 'power': power}
    dataframe = pandas.DataFrame(data)
    if ( 'PV' in nameFile[i]):
        df_Prod += [dataframe]
    else:
        df_Cons += [dataframe]


#Concateno i dataframe dei Consumatori
df_ConsTot = pandas.concat(df_Cons)
#Li raggruppo in base alla data e sommo le potenze(con data uguale)
df_ConsTot = df_ConsTot.groupby(df_ConsTot['date'],as_index=False,sort=True)[['power']].sum()
#La potenza dei consumatori diventa negativa in modo da effettuare il calcolo dell'autoconsumo
df_ConsTot["power"] *= -1

#Concateno i dataframe dei produttori
df_ProdTot = pandas.concat(df_Prod)
#Li raggruppo in base alla data e sommo le potenze(con data uguale)
df_ProdTot = df_ProdTot.groupby(df_ProdTot['date'],as_index=False,sort=True)[['power']].sum()

#Definiamo l'autoconsumo (PotenzaProdotta-PotenzaImmessaNellaRete)

#Definisco la PotenzaImmessaNellaRete(PotenzaProdotto-PotenzaConsumata senza valori negativi)
#Creo una lista di dataframe contententi i dataframe dei consumatori e dei produttori
df_ConsProd = [df_ProdTot, df_ConsTot]
#creo un singolo dataframe concatenando quelli presenti in lista
df_PotImm = pandas.concat(df_ConsProd)
#raggruppo per data e sommo(in realtà è una differenza)
df_PotImm = df_PotImm.groupby(df_PotImm['date'],as_index=False,sort=True)[['power']].sum()
#Tutti gli elementi al di sotto dello 0 vengono sostituiti con lo 0
df_PotImm['power'] = df_PotImm['power'].mask(df_PotImm['power'] < 0, 0)
#Inverto i valori della potenza Immessa nella rete per effettuare la differenza
df_PotImm['power'] *= -1

#Rimetto la potenza dei consumatori positiva
df_ConsTot["power"] *= -1

#Calcolo Autoconsumo
df_ProdImm = [df_ProdTot,df_PotImm]
df_SelfConsumption = pandas.concat(df_ProdImm)
df_SelfConsumption = df_SelfConsumption.groupby(df_SelfConsumption['date'],as_index=False,sort=True)['power'].sum()

# Creo un vettore di 0 della lunghezza della used_Day per il grafico ad area
n = len(used_Day[:-1])
zeros = [0]*n
#Genero il dataframe per il grafico ad aree
data = {
    'x_values': used_Day[:-1],
    'autoconsumo': df_SelfConsumption['power'],
    'generata': df_ProdTot['power'],
    'consumata': df_ConsTot['power'],
    'zeros': zeros
    }
source = ColumnDataSource(data = data)

#Costruiamo il plot
p = figure(

    plot_width = 800,
    plot_height = 500,
    title = 'SELF-CONSUMPTION',
    x_axis_label = 'Date',
    y_axis_label = 'Power(kW)',
    x_axis_type = 'datetime'
    

)

p.xaxis.formatter = DatetimeTickFormatter(
    
    years="20%y/%m/%d %H:%M",
    days="20%y/%m/%d %H:%M",
    months="20%y/%m/%d %H:%M",
    hours="20%y/%m/%d %H:%M",
    minutes="20%y/%m/%d %H:%M"
    
    ) 

p.varea(
    x='x_values',
    y1 = 'zeros', 
    y2 = 'generata',
    source = source,
    fill_color = 'green',
    alpha = 0.8,
    legend_label = 'Produced_Pow'
    )

p.varea(
    x='x_values',
    y1 = 'zeros',
    y2 = 'consumata',
    source = source,
    fill_color = 'red', 
    alpha = 0.8, 
    legend_label = 'Consumed_Pow'
    )

p.varea(
    x='x_values',
    y1 = 'zeros', 
    y2 = 'autoconsumo',
    source = source, 
    fill_color = 'yellow',
    alpha = 0.8, 
    legend_label = 'Self_Consumption'
    )

show(p)
