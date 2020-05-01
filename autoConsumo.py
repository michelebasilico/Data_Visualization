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


output_file('index6.html')
#Per ogni dataframe Consumatore
df_PCons = []
for i in range(n_Cons):
    
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
    #Inserisco i dataframe all'interno della lista dei consumatori
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
    

#Concateno i dataframe dei consumatori
df_ConsTot = pandas.concat(df_PCons)
#Raggruppo i dataframe dei consumatori per data e li sommo(se la data è uguale). Vengono anche ordinati
df_ConsTot = df_ConsTot.groupby(df_ConsTot['date'],as_index=False,sort=True)[['power']].sum()

df_ProdTot = pandas.concat(df_PProd)
df_ProdTot = df_ProdTot.groupby(df_ProdTot['date'],as_index=False,sort=True)[['power']].sum()



#Calcolo Autoconsumo
#La potenza dei consumatori diventa negativa(in modo che la somma sia una differenza)
df_ConsTot["power"] *= -1
#Creo una lista con i dataframe dei consumi e delle produzioni
df_ConsProd = [df_ProdTot, df_ConsTot]
#Concateno i due dataframe
df_Autoconsumo = pandas.concat(df_ConsProd)
#Raggruppo in base alla data e somma la potenza degli elemetni con data uguale
df_Autoconsumo = df_Autoconsumo.groupby(df_Autoconsumo['date'],as_index=False,sort=True)[['power']].sum()
#Sostituisco gli elementi negativi con il valore 0(non fanno parte dell'autoconsumo)
df_Autoconsumo['power'][ df_Autoconsumo['power'] < 0 ] = 0


#Genero i dati da passare a ColumnDataSource
#Genero un vettore di 0 per la rappresenztazione ad area
zeros = [0] * df_Autoconsumo.shape[0]
datafinale = {'x_values': df_Autoconsumo['date'], 'y1': zeros ,'y2': df_Autoconsumo['power']}
source = ColumnDataSource(data=datafinale)


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

p.varea(

        x = 'x_values',
        y1 = 'y1',
        y2 = 'y2',
        source = source,
        color = 'yellow',
        alpha = 0.4,
        legend_label = 'Autoconsumo'
    )



show(p)