from bokeh.plotting import figure,output_file,show,ColumnDataSource
from bokeh.models import DatetimeTickFormatter
import pandas
import datetime as dt
import os,os.path
import glob
import power as pw


#Leggo i file nella cartella Consumatori e genero un dataframe per ognuno di essi, inserendoli all'interno di un dataframe
csv_Cons = glob.glob('Consumatori' + "/*.csv")
n_Cons = len(csv_Cons)
df_Cons = [ pandas.read_csv(f,sep = ' ') for f in csv_Cons ]

csv_Prod = glob.glob('Produttori' + "/*.csv")
n_Prod = len(csv_Prod)
df_Prod = [ pandas.read_csv(f,sep = ' ') for f in csv_Prod ]

#Indichiamo un file di output
output_file('index6.html')


#Creaiamo una lista di dataframe con tutti i Consumatori
df_PCons = []
for i in range(n_Cons):
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
    df_PCons += [pandas.DataFrame(data)]

#Vedi sopra
df_PProd = []
for i in range(n_Prod):
    time = pw.Unix_to_hours(df_Prod[i])
    energy = df_Prod[i]['energy'].tolist()
    power = pw.calc_Pot(time,energy)
    ultimo_elemento = len(df_Prod[i]) - 1
    df_Prod[i] = df_Prod[i].drop([ultimo_elemento])
    data = {'date': df_Prod[i]['date'], 'power': power}
    df_PProd += [pandas.DataFrame(data)]
    

#Concateno i dataframe dei Consumatori
df_ConsTot = pandas.concat(df_PCons)
#Li raggruppo in base alla data e sommo le potenze(con data uguale)
df_ConsTot = df_ConsTot.groupby(df_ConsTot['date'],as_index=False,sort=True)[['power']].sum()
#La potenza dei consumatori diventa negativa in modo da effettuare il calcolo dell'autoconsumo
df_ConsTot["power"] *= -1

#Concateno i dataframe dei produttori
df_ProdTot = pandas.concat(df_PProd)
#Li raggruppo in base alla data e sommo le potenze(con data uguale)
df_ProdTot = df_ProdTot.groupby(df_ProdTot['date'],as_index=False,sort=True)[['power']].sum()



#Definiamo l'autoconsumo
#Creo una lista di dataframe contententi i dataframe dei consumatori e dei produttori
df_ConsProd = [df_ProdTot, df_ConsTot]
#creo un singolo dataframe concatenando quelli presenti in lista
df_Autoconsumo = pandas.concat(df_ConsProd)
#raggruppo per data e sommo(in realtà è una differenza)
df_Autoconsumo = df_Autoconsumo.groupby(df_Autoconsumo['date'],as_index=False,sort=True)[['power']].sum()
#Tutti gli elementi al di sotto dello 0 vengono sostituiti con lo 0
df_Autoconsumo['power'][ df_Autoconsumo['power'] < 0 ] = 0


#Rimetto la potenza dei consumatori positiva
df_ConsTot["power"] *= -1
#Genero il dataframe per il grafico ad aree
data = {'x_values': df_Autoconsumo['date'], 'autoconsumo': df_Autoconsumo['power'],'generata': df_ProdTot['power'],'consumata': df_ConsTot['power']}
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
names = ['autoconsumo','generata','consumata']
#Creo il grafico ad aree
p.varea_stack(stackers = names, x='x_values', color=['yellow','green','red'], legend_label=names, source=source,alpha = 0.8)

show(p)