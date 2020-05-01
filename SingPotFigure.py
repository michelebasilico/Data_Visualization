from bokeh.plotting import figure,output_file,show,ColumnDataSource
from bokeh.models import DatetimeTickFormatter
import pandas
import datetime as dt
import os
import power as pw
from bokeh.layouts import row,column
import os,os.path
import glob

#Leggo i file nella cartella Consumatori e genero un dataframe per ognuno di essi, inserendoli all'interno di un dataframe
csv_file = glob.glob('Energie' + "/*.csv")
n_csv = len(csv_file)
df_file = [ pandas.read_csv(f,sep = ' ') for f in csv_file ]
#Registro il nome del file per le verifiche successive
nameFile = os.listdir('Energie')

#Genero un file di output 
output_file('index5.html')


fig = []
#Per ogni dataframe Consumatore
for i in range(n_csv):
    time = []
    energy = []
    #Genero la lista tempo del Dispositivo Consumatore
    time = pw.Unix_to_hours(df_file[i])
    #Genero la lista energia del Dispositivo Consumatore
    energy = df_file[i]['energy'].tolist()
    #Genero la potenza del Dispositivo Consumatore
    power = pw.calc_Pot(time,energy)
    #Elimino l'ultimo elemento del tempo per la rappresentazione della potenza
    ultimo_elemento = len(df_file[i]) - 1
    df_file[i] = df_file[i].drop([ultimo_elemento])
    #Genero i dati per la creazione dei dataframe
    data = {'x_values': df_file[i]['date'], 'y_values': power}
    source = ColumnDataSource(data=data)

    #Costruiamo il plot
    p = figure(

        plot_width = 500,
        plot_height = 300,
        title = 'Potenza ' + nameFile[i][:-4],
        x_axis_label = 'Data',
        y_axis_label = 'Potenza(kW)',
        x_axis_type = 'datetime'
        

    )
    fig.append(p)

    fig[i].xaxis.formatter = DatetimeTickFormatter(
        
        years="20%y/%m/%d %H:%M",
        days="20%y/%m/%d %H:%M",
        months="20%y/%m/%d %H:%M",
        hours="20%y/%m/%d %H:%M",
        minutes="20%y/%m/%d %H:%M"
        
        )

    #Se il file è un tipo produttore uso il colore verde e cambio il valore della leggenda
    if ('prod' in nameFile[i]):

        fig[i].line(

            x = 'x_values',
            y = 'y_values',
            source = source,
            legend_label = 'Potenza Prodotta(kW)',
            line_width=4,
            color = 'green',
            alpha = 0.8

        )
    elif('prosumer' in nameFile[i]):
        

        #df1 = pandas.DataFrame(data=data)
        #df2 = pandas.DataFrame(columns=df1.columns)
        #print(df1)
        #cond = df1['y_values'] < 0
        #rows = df1.loc[cond, :]
        #df2 = df2.append(rows, ignore_index=True)
        #df1.drop(rows.index, inplace=True)
        

        #data1 = {'x_values': df1['x_values'], 'y_values': df1['y_values']}
        #source1 = ColumnDataSource(data=data1)

        #data2 = {'x_values': df2['x_values'], 'y_values': df2['y_values']}
        #source2 = ColumnDataSource(data=data2)


        fig[i].line(

            x = 'x_values',
            y = 'y_values',
            source = source,
            legend_label = '>0 : Prod,<0 : Cons',
            line_width=4,
            color = 'yellow',
            alpha = 0.9

        )
        #fig[i].line(

            #x = 'x_values',
            #y = 'y_values',
            #source = source2,
            #legend_label = 'Potenza Consumata(kW)',
            #line_width=4,
            #color = 'red',
            #alpha = 0.8

        #)
    else:
        #Se si tratta di un consumatore uso il colore rosso
        fig[i].line(

            x = 'x_values',
            y = 'y_values',
            source = source,
            legend_label = 'Potenza Consumata(kW)',
            line_width=4,
            color = 'red',
            alpha = 0.8

        )
    

#Mostro il grafico
cols = []
row_num = 3
for i in range(0, len(fig), row_num):
    r = row(fig[i: i + row_num])
    cols.append(r)
show(column(cols))