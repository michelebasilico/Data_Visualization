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

#Leggo i file nella cartella Produttori e genero un dataframe per ognuno di essi, inserendoli all'interno di un dataframe
csv_Prod = glob.glob('Produttori' + "/*.csv")
n_Prod = len(csv_Prod)
df_Prod = [ pandas.read_csv(f,sep = ' ') for f in csv_Prod ]

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
#Creo i dati per la visualizzazione
datafinale1 = {'x_values': df_ConsTot['date'], 'y_values': df_ConsTot['power']}

#Vedi sopra
df_ProdTot = pandas.concat(df_PProd)
df_ProdTot = df_ProdTot.groupby(df_ProdTot['date'],as_index=False,sort=True)[['power']].sum()

datafinale2 = {'x_values': df_ProdTot['date'], 'y_values': df_ProdTot['power']}



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