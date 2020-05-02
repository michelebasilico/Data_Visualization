from bokeh.plotting import figure,output_file,show,ColumnDataSource
from bokeh.models import DatetimeTickFormatter
import pandas
import datetime as dt
import os,os.path
import glob
from bokeh.transform import linear_cmap
from bokeh.palettes import Dark2_5 as palette
import itertools
import power as pw


#Leggo i file nella cartella Consumatori e genero un dataframe per ognuno di essi, inserendoli all'interno di un dataframe
csv_file = glob.glob('Consumatori' + "/*.csv")
n_File = len(csv_file)
df = [ pandas.read_csv(f,sep = ' ') for f in csv_file ]
nameFile = os.listdir('Consumatori')

output_file('index4.html')

#Costruiamo il plot
p = figure(

    plot_width = 1500,
    plot_height = 600,
    title = 'Potenza Consumata per ogni dispostivo(kW)',
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


#Convertiamo il tempoUnix ed Estraiamo l'energia per il calcolo della potenza, calcoliamo quest'ultima e generiamo i plot per ogni
#dataframe. Utilizziamo la palette per il cambio di colore per ogni iterazione
timeList = []
energyList = []
powerList = []
df2 = df
colors = itertools.cycle(palette)    


for i,color in zip(range(n_File),colors):

    #Generiamo la lista del tempo utilizzando la funzione Unix_to_hours
    timeList = pw.Unix_to_hours(df[i])

    #Generiamo la lista dell'energia 
    energyList = df[i]['energy'].tolist()

    #Calcolo la lista della potenza per ogni dataframe e genero una lista di liste per il contenimento
    powerList += [pw.calc_Pot(timeList,energyList)]

    #Elimino l'ultimo elemento del dataframe da utilizzare sull'asse delle ascisse
    ultimo_elemento = len(df2[i]) - 1
    df2[i] = df2[i].drop([ultimo_elemento])
    
    #Genero i dati da passare a ColumnDataSource
    data = {'x_values': df2[i]['date'],
        'y_values': powerList[i]}
    source = ColumnDataSource(data=data)
   
    #Fissiamo il gliph da utilizzare, nel nostro caso una semplice linea
    p.line(

        x = 'x_values',
        y = 'y_values',
        source = source,
        line_width=4,
        color = color,
        alpha = 0.8,
        legend_label = 'Potenza Consumata(kW) da' + nameFile[i][:-4]

    )

show(p)