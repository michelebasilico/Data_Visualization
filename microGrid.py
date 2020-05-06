from bokeh.plotting import figure,output_file,show,ColumnDataSource
from bokeh.models import DatetimeTickFormatter
import pandas
import datetime as dt
import os,os.path
import glob
import power as pw
import numpy as np
from bokeh.transform import linear_cmap
from bokeh.palettes import Dark2_5 as palette
import itertools

consumers = ['EV','WD','BG','HC']
df_EnProd,df_EnCons,nameProd,nameCons,df_EnCons_AllDay,df_EnProd_AllDay = [],[],[],[],[],[]
df_PwCons,df_PwCons_AllDay,df_PwProd,df_PwProd_AllDay = [],[],[],[]
start_day = '2015/12/12 00:00:00'
end_day = '2015/12/12 23:59:59'
freq = '5T'

#Acquisizione delle directory
nameDir = os.listdir('12_12_15_116/output')
n_Dir = len(nameDir)

x = y = 0
for i in range(n_Dir):

    #Lettura File della Directory
    csv_file = glob.glob('12_12_15_116/output/'+ nameDir[i] + "/*.csv")

    #Controllo Tipologia
    if('PV' in nameDir[i]):

        #Lettura file e pulizia dei dati
        df_EnProd += [ pw.data_cleaning(pandas.read_csv(f,sep = ' '),False) for f in csv_file ]
        #Pulizia dei dati rispetto l'intera giornata(Per le operazioni successive)
        df_EnProd_AllDay += [ pw.data_cleaning(df_EnProd[x],True,start_day,end_day,freq) ]
        #Salvataggio dei nomi
        nameProd += [os.path.basename(csv_file[0])]
        #Conversione Energia->Potenza
        df_PwProd += [pw.dfEnergy_to_dfPower(df_EnProd[x])]
        df_PwProd_AllDay += [pw.dfEnergy_to_dfPower(df_EnProd_AllDay[x])]

        sourceEn = ColumnDataSource(df_EnProd[x])
        sourcePw = ColumnDataSource(df_PwProd[x])

        output_file(nameProd[x][:-4] + '.html')

        p = figure(

            plot_width = 800,
            plot_height = 500,
            title = 'Single Device Energy/Power(' + nameProd[x][:-4] + ')',
            x_axis_label = 'Date',
            y_axis_label = 'Energy(kW/h),Power(kW)',
            x_axis_type = 'datetime'

        )
        p.xaxis.formatter = DatetimeTickFormatter(
    
            years="20%y/%m/%d %H:%M",
            days="20%y/%m/%d %H:%M",
            months="20%y/%m/%d %H:%M",
            hours="20%y/%m/%d %H:%M",
            minutes="20%y/%m/%d %H:%M"
            
        )

        p.line(

            x = 'date',
            y = 'energy',
            source = sourceEn,
            legend_label = 'Energy(kW/h)',
            line_width=4,
            color = 'red',
            alpha = 0.8

        )

        p.line(

            x = 'date',
            y = 'power',
            source = sourcePw,
            legend_label = 'Power(kW)',
            line_width=4,
            color = 'blue',
            alpha = 0.8

        )

        show(p)

        x += 1

    elif(any(consumer in nameDir[i] for consumer in consumers)):
        df_EnCons += [ pw.data_cleaning(pandas.read_csv(f,sep = ' '),False) for f in csv_file ]
        df_EnCons_AllDay += [ pw.data_cleaning(df_EnCons[y],True,start_day,end_day,freq) ]
        nameCons += [os.path.basename(csv_file[0])]
        df_PwCons += [pw.dfEnergy_to_dfPower(df_EnCons[y])]
        df_PwCons_AllDay += [pw.dfEnergy_to_dfPower(df_EnCons_AllDay[y])]

        sourceEn = ColumnDataSource(df_EnCons[y])
        sourcePw = ColumnDataSource(df_PwCons[y])

        output_file(nameCons[y][:-4] + '.html')

        p = figure(

            plot_width = 800,
            plot_height = 500,
            title = 'Single Device Energy/Power(' + nameCons[y][:-4] + ')',
            x_axis_label = 'Date',
            y_axis_label = 'Energy(kW/h),Power(kW)',
            x_axis_type = 'datetime'

        )
        p.xaxis.formatter = DatetimeTickFormatter(
    
            years="20%y/%m/%d %H:%M",
            days="20%y/%m/%d %H:%M",
            months="20%y/%m/%d %H:%M",
            hours="20%y/%m/%d %H:%M",
            minutes="20%y/%m/%d %H:%M"
            
        )

        p.line(

            x = 'date',
            y = 'energy',
            source = sourceEn,
            legend_label = 'Energy(kW/h)',
            line_width=4,
            color = 'red',
            alpha = 0.8

        )

        p.line(

            x = 'date',
            y = 'power',
            source = sourcePw,
            legend_label = 'Power(kW)',
            line_width=4,
            color = 'blue',
            alpha = 0.8

        )

        show(p)

        y += 1
        
#Totale Potenze consumate e prodotte

df_PwTotCons = pw.sum_power(df_PwCons_AllDay)
df_PwTotProd = pw.sum_power(df_PwProd_AllDay)

data = {'date': df_PwTotCons['date'], 'powerCons': df_PwTotCons['power'], 'powerProd': df_PwTotProd['power']}
source = ColumnDataSource(data=data)
output_file('totalpower.html')


#Costruiamo il plot
p = figure(

    plot_width = 800,
    plot_height = 500,
    title = 'Total Power',
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

#Visualizzo i consumatori
p.line(

        x = 'date',
        y = 'powerCons',
        source = source,
        line_width=4,
        color = 'red',
        alpha = 0.8,
        legend_label = 'Total Consumed Power'

    )

#Visualizzo i produttori
p.line(

        x = 'date',
        y = 'powerProd',
        source = source,
        line_width=4,
        color = 'green',
        alpha = 0.8,
        legend_label = 'Total Produced Power'

    )

show(p)

#Grafico Autoconsumo
output_file('self_consumption.html')
df_selfConsumption = pw.self_consumption(df_PwTotProd,df_PwTotCons)
#Creo un vettore di 0 della lunghezza della used_Day per il grafico ad area
n = len(df_selfConsumption['date'])
zeros = [0]*n
#Genero il dataframe per il grafico ad aree
data = {
    'date': df_selfConsumption['date'],
    'self_consumption': df_selfConsumption['power'],
    'produced': df_PwTotProd['power'],
    'consumed': df_PwTotCons['power'],
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
    x='date',
    y1 = 'zeros', 
    y2 = 'produced',
    source = source,
    fill_color = 'green',
    alpha = 0.8,
    legend_label = 'Produced_Pow'
    )

p.varea(
    x='date',
    y1 = 'zeros',
    y2 = 'consumed',
    source = source,
    fill_color = 'red', 
    alpha = 0.8, 
    legend_label = 'Consumed_Pow'
    )

p.varea(
    x='date',
    y1 = 'zeros', 
    y2 = 'self_consumption',
    source = source, 
    fill_color = 'yellow',
    alpha = 0.8, 
    legend_label = 'Self_Consumption'
    )

show(p)


output_file('consumedPower.html')

#Costruiamo il plot
p = figure(

    plot_width = 800,
    plot_height = 500,
    title = 'CONSUMED POWER(kW)',
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

colors = itertools.cycle(palette)    

for j,color in zip(range(len(df_PwCons_AllDay)),colors):
    
    source = ColumnDataSource(data=df_PwCons_AllDay[j])
   
    #Fissiamo il gliph da utilizzare, nel nostro caso una semplice linea
    p.line(

        x = 'date',
        y = 'power',
        source = source,
        line_width=4,
        color = color,
        alpha = 0.8,
        legend_label = 'Consumed Power(kW) from ' + nameCons[j][:-4]

    )

show(p)
