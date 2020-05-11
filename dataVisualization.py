from bokeh.plotting import figure,output_file,show,ColumnDataSource,save
from bokeh.models import DatetimeTickFormatter
import pandas
import datetime as dt
import os,os.path
import glob
import power as pw
import numpy as np
from bokeh.transform import linear_cmap,cumsum
from bokeh.palettes import Dark2_5 as palette
import itertools
from math import pi

consumers = ['EV','WD','BG','HC']
df_EnProd,df_EnCons,name_Cons,df_EnCons_AllDay,df_EnProd_AllDay = [],[],[],[],[]
df_PwCons,df_PwCons_AllDay,df_PwProd,df_PwProd_AllDay = [],[],[],[]
start_day = '2015/12/12 00:00:00'
end_day = '2015/12/12 23:59:59'
freq = '5T'

#Acquisizione delle directory
nameDir = os.listdir('12_12_15_116/output')
n_Dir = len(nameDir)

#Variabili per lo scorrimento delle case + n.di case
iProducer = iConsumer = n_home = 0

for i in range(n_Dir):

    #Lettura File della Directory
    csv_file = glob.glob('12_12_15_116/output/'+ nameDir[i] + "/*.csv")

    for f,i2 in zip(csv_file,range(len(csv_file))):

        #Lettura file
        df_start = pandas.read_csv(f,sep = ' ',header=None)

        #Rinomino le colonne
        df_start.rename(columns={ df_start.columns[0]: "date" }, inplace = True)
        df_start.rename(columns={ df_start.columns[1]: "energy" }, inplace = True)

        name_File = os.path.basename(csv_file[i2])
        id_home = int(name_File[0])

        #Controllo numero Home
        if( n_home < id_home ):
            n_home = id_home

        #Controllo Tipologia
        if('PV' in nameDir[i]):

            #Pulizia Dati
            df_EnProd += [ pw.data_cleaning(df_start,False) ]
            
            #Pulizia dei dati rispetto l'intera giornata(Per le operazioni successive)
            df_EnProd_AllDay += [ pw.data_cleaning(df_EnProd[iProducer],True,start_day,end_day,freq) ]

            df_EnProd[iProducer]['home'] = id_home
            df_EnProd_AllDay[iProducer]['home'] = id_home

            #Conversione Energia->Potenza
            df_PwProd += [pw.dfEnergy_to_dfPower(df_EnProd[iProducer])]
            df_PwProd_AllDay += [pw.dfEnergy_to_dfPower(df_EnProd_AllDay[iProducer])]
            

            sourceEn = ColumnDataSource(df_EnProd[iProducer])
            sourcePw = ColumnDataSource(df_PwProd[iProducer])

            iProducer += 1

        elif(any(consumer in nameDir[i] for consumer in consumers)):
            
            name_Cons += [os.path.basename(csv_file[i2])]
            #Pulizia Dati
            df_EnCons += [ pw.data_cleaning(df_start,False) ]
            
            df_EnCons_AllDay += [ pw.data_cleaning(df_EnCons[iConsumer],True,start_day,end_day,freq) ]

            df_EnCons[iConsumer]['home'] = id_home
            df_EnCons_AllDay[iConsumer]['home'] = id_home

            df_PwCons += [pw.dfEnergy_to_dfPower(df_EnCons[iConsumer])]
            df_PwCons_AllDay += [pw.dfEnergy_to_dfPower(df_EnCons_AllDay[iConsumer])]

            df_device = df_PwCons_AllDay.copy()
            df_device[iConsumer]['device'] = nameDir[i]

            sourceEn = ColumnDataSource(df_EnCons[iConsumer])
            sourcePw = ColumnDataSource(df_PwCons[iConsumer])

            iConsumer += 1

        
        output_file(name_File[0] + '_en.html')

        p = figure(
            plot_width = 800, plot_height = 500, title = nameDir[i] +' Energy(' + name_File[:-4] + ')',
            x_axis_label = 'Date', y_axis_label = 'Energy(kW/h)', x_axis_type = 'datetime'
        )
            
        pw.plot_axis_dateFormatter(p)

        p.line(
            x = 'date', y = 'energy', source = sourceEn, legend_label = 'Energy(kW/h)',
            line_width=4, color = 'red', alpha = 0.8
        )

        show(p)

        output_file(name_File[0] + '_pow.html')

        p2 = figure(
            plot_width = 800, plot_height = 500, title = 'Single Device Power(' + name_File[:-4] + ')',
            x_axis_label = 'Date', y_axis_label = 'Power(kW)', x_axis_type = 'datetime'
        )

        pw.plot_axis_dateFormatter(p2)

        p2.line(
            x = 'date', y = 'power', source = sourcePw, legend_label = 'Power(kW/h)',
            line_width=4, color = 'blue', alpha = 0.8
        )

        show(p2)

#Area Potenze Consumate sommate per categoria(EV,WD,ecc)

#Concateno i dataframe con la colonna per distinguere i device
newdf_device = pandas.concat(df_device)
colors = itertools.cycle(palette)

#Vicinato:
#Eseguo un raggruppamento per data e per device e sommo le potenze dei raggruppamenti
df_device_neigh = newdf_device.groupby([newdf_device['date'],newdf_device['device']],as_index=False,sort=True)[['power']].sum()
#Scompongo i dataframe per device utilizzando un dizionario
dict_of_device = dict(iter(df_device_neigh.groupby('device')))
output_file('neigh_category_sum.html')

pDevice = figure(
    plot_width = 800, plot_height = 500, title = 'Power(Sum for category) Neighborhood',
    x_axis_label = 'Date', y_axis_label = 'Power(kW)', x_axis_type = 'datetime'     
    )

pw.plot_axis_dateFormatter(pDevice)

#Loop per chiavi del dizionario(Ogni chiave corrisponde ad un device) 
for (key, value),color in zip(dict_of_device.items(),colors):

    n = value.shape[0]
    zeros = [0]*n
    data = { 'date': value['date'], 'consumed': value['power'], 'zeros': zeros  }
    source_Category = ColumnDataSource(data=data)

    pDevice.varea(
    x='date', y1 = 'zeros', y2 = 'consumed', source = source_Category, 
    fill_color = color, alpha = 0.8, legend_label = 'neigh_ConsPow_'+str(key) 
    )

show(pDevice)

#Home
#Raggruppo per data,device e sta volta anche per casa e sommo le potenze
df_device_home = newdf_device.groupby([newdf_device['home'],newdf_device['date'],newdf_device['device']],as_index=False,sort=True)[['power']].sum()
#Eseguo un loop per ogni casa
for home,df_HomeDevice in df_device_home.groupby('home'):
    #Creo un dizionario scomponendo i dataframe per device(appartenenti ad una home)
    dict_of_device_home = dict(iter(df_HomeDevice.groupby('device')))

    output_file(str(home)+'_category_sum.html')

    pDeviceHome = figure(
        plot_width = 800, plot_height = 500, title = 'Power(Sum for category) Home_'+str(home),
        x_axis_label = 'Date', y_axis_label = 'Power(kW)', x_axis_type = 'datetime'        
    )

    pw.plot_axis_dateFormatter(pDeviceHome) 

    #Eseguo un loop per ogni chiave del dizionario(per ogni device)
    for (key, value),color in zip(dict_of_device_home.items(),colors):

        n = value.shape[0]
        zeros = [0]*n
        data = {    'date': value['date'], 'consumed': value['power'], 'zeros': zeros   }
        source_CategoryHome = ColumnDataSource(data=data)

        pDeviceHome.varea(
            x='date', y1 = 'zeros', y2 = 'consumed', source = source_CategoryHome,
            fill_color = color, alpha = 0.8, legend_label = str(home)+'_ConsPow_'+str(key) 
        )

    show(pDeviceHome)


#Totale Potenze consumate e prodotte(NEIGHBORHOOD)

df_PwTotCons = pw.sum_pow_en(df_PwCons_AllDay,'power')
df_PwTotProd = pw.sum_pow_en(df_PwProd_AllDay,'power')

data = {'date': df_PwTotCons['date'], 'powerCons': df_PwTotCons['power'], 'powerProd': df_PwTotProd['power']}
source_Tot = ColumnDataSource(data=data)
output_file('neigh_total.html')

#Costruiamo il plot
pTot = figure(
    plot_width = 800, plot_height = 500, title = 'Total Power Neighborhood',
    x_axis_label = 'Date', y_axis_label = 'Power(kW)', x_axis_type = 'datetime'
)
pw.plot_axis_dateFormatter(pTot)

#Visualizzo i consumatori
pTot.line(
    x = 'date',y = 'powerCons', source = source_Tot,
    line_width=4, color = 'red', alpha = 0.8, legend_label = 'Total Consumed Power'
)

#Visualizzo i produttori
pTot.line(
    x = 'date', y = 'powerProd', source = source_Tot, line_width=4,
    color = 'green', alpha = 0.8, legend_label = 'Total Produced Power'
)
show(pTot)


#Totale Potenze consumate e prodotte + Autoconsumo (HOME)

df_EnHomeCons = pw.sum_pow_en(df_EnCons_AllDay,'energy',True)
df_EnHomeProd = pw.sum_pow_en(df_EnProd_AllDay,'energy',True)

df_PwHomeCons = pw.sum_pow_en(df_PwCons_AllDay,'power',True)
df_PwHomeProd = pw.sum_pow_en(df_PwProd_AllDay,'power',True)

for i in range(n_home+1):
    df_Pw_OneHomeCons = df_PwHomeCons[df_PwHomeCons['home'] == i]
    df_Pw_OneHomeProd = df_PwHomeProd[df_PwHomeProd['home'] == i]
    data = {    'date': df_Pw_OneHomeCons['date'], 'powerCons': df_Pw_OneHomeCons['power'],'powerProd': df_Pw_OneHomeProd['power']  }
    source_Home = ColumnDataSource(data=data)
    output_file(str(i)+'_total.html')
        
    #Costruiamo il plot
    pHome = figure(
        plot_width = 800, plot_height = 500, title = 'Total_Power_home'+str(i),
        x_axis_label = 'Date', y_axis_label = 'Power(kW)', x_axis_type = 'datetime'
    )
    pw.plot_axis_dateFormatter(pHome) 

    #Visualizzo i consumatori
    pHome.line(
        x = 'date', y = 'powerCons', source = source_Home,
        line_width=4, color = 'red', alpha = 0.8, legend_label = 'Total Consumed Power'
    )

    #Visualizzo i produttori
    pHome.line(
        x = 'date', y = 'powerProd', source = source_Home,
        line_width=4, color = 'green', alpha = 0.8, legend_label = 'Total Produced Power'
    )
    show(pHome)

    output_file(str(i)+'_self.html')

    #Attenzione il calcolo dell'autoconsumo comporta la perdita della colonna home
    df_power_selfConsumptionHome = pw.self_consumption(df_Pw_OneHomeProd,df_Pw_OneHomeCons,'power')
    #Aggiungiamo la colonna persa
    df_power_selfConsumptionHome['home'] = i
    
    #Creo un vettore di 0 della lunghezza della used_Day per il grafico ad area
    n = df_power_selfConsumptionHome.shape[0]
    zeros = [0]*n
    data = {
        'date': df_power_selfConsumptionHome['date'], 
        'consumed': df_Pw_OneHomeCons['power'],
        'produced': df_Pw_OneHomeProd['power'],
        'self_consumption': df_power_selfConsumptionHome['power'],
        'zeros': zeros
    }
    source_SelfHome = ColumnDataSource(data=data)
        
    #Costruiamo il plot
    pselfHome = figure(
        plot_width = 800, plot_height = 500, title = 'SELF-CONSUMPTION_Home'+str(i),
        x_axis_label = 'Date', y_axis_label = 'Power(kW)', x_axis_type = 'datetime'
    )
    pw.plot_axis_dateFormatter(pselfHome)

    pselfHome.varea(
        x='date', y1 = 'zeros', y2 = 'produced', source = source_SelfHome,
        fill_color = 'green', alpha = 0.8, legend_label = 'Produced_Pow'
    )

    pselfHome.varea(
        x='date', y1 = 'zeros', y2 = 'consumed', source = source_SelfHome,
        fill_color = 'red', alpha = 0.8, legend_label = 'Consumed_Pow'
    )

    pselfHome.varea(
        x='date', y1 = 'zeros', y2 = 'self_consumption', source = source_SelfHome, 
        fill_color = 'yellow', alpha = 0.8, legend_label = 'Self_Consumption'
    )
    show(pselfHome)

    #Torta Autoconsumo ed Energia riversata nella grid
    df_En_OneHomeCons = df_EnHomeCons[df_EnHomeCons['home'] == i]
    df_En_OneHomeProd = df_EnHomeProd[df_EnHomeProd['home'] == i]

    df_Energy_selfConsumptionHome = pw.self_consumption(df_En_OneHomeProd,df_En_OneHomeCons,'energy')
    #Aggiungiamo la colonna persa
    df_Energy_selfConsumptionHome['home'] = i

    df_storedEnergy = pw.stored_pow_en(df_En_OneHomeProd,df_En_OneHomeCons,'energy')
    storedEnergy_Home = df_storedEnergy['energy'].sum()
    energy_selfConsumption_Home = df_Energy_selfConsumptionHome['energy'].sum()

    output_file(str(i)+'_pie.html')

    x = {
        'Stored Energy': storedEnergy_Home,
        'Energy Self Consumption': energy_selfConsumption_Home,
    }

    data = pandas.Series(x).reset_index(name='value').rename(columns={'index':'power'})
    data['percent'] = data['value'] / data['value'].sum()  * 100
    data['angle'] = data['value']/data['value'].sum() * 2*pi
    data['color'] = ['green','yellow']

    pPie = figure(plot_height=350, title="EnergySelfConsumption and Stored Energy Home_"+str(i), tooltips="@power: @percent{0.2f} %",
            tools="hover", x_range=(-0.5, 1.0))

    pPie.wedge(x=0, y=1, radius=0.4,
            start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
            line_color="white",line_width = 2.5, fill_color='color', legend_field='power', source=data)

    pPie.axis.axis_label=None
    pPie.axis.visible=False
    pPie.grid.grid_line_color = None

    show(pPie)

    #Torta consumo totale e produzione pannello(energia)

    consumed = df_En_OneHomeCons['energy'].sum()
    produced = df_En_OneHomeProd['energy'].sum()

    output_file(str(i)+'_pie2.html')

    x = {   'Consumed Energy': consumed, 'Produced Energy': produced    }

    data = pandas.Series(x).reset_index(name='value').rename(columns={'index':'power'})
    data['percent'] = data['value'] / data['value'].sum()  * 100
    data['angle'] = data['value']/data['value'].sum() * 2*pi
    data['color'] = ['red','green']

    pPie2 = figure(plot_height=350, title="Consumed and Produced Energy Home_"+str(i), tooltips="@power: @percent{0.2f} %",
            tools="hover", x_range=(-0.5, 1.0))

    pPie2.wedge(x=0, y=1, radius=0.4,
            start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
            line_color="white",line_width = 2.5, fill_color='color', legend_field='power', source=data)

    pPie2.axis.axis_label=None
    pPie2.axis.visible=False
    pPie2.grid.grid_line_color = None

    show(pPie2)


#Grafico Autoconsumo(Autoconsumo neighborhood)
output_file('neigh_self.html')
#Attenzione il calcolo dell'autoconsumo comporta la perdita della colonna home(nel caso del vicinato non serve riaggiungerla)
df_selfConsumption = pw.self_consumption(df_PwTotProd,df_PwTotCons,'power')
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
source_Neigh = ColumnDataSource(data = data)

#Costruiamo il plot
pNeigh = figure(
    plot_width = 800, plot_height = 500, title = 'SELFCONSUMPTION NEIGHBORHOOD',
    x_axis_label = 'Date', y_axis_label = 'Power(kW)', x_axis_type = 'datetime'
)
pw.plot_axis_dateFormatter(pNeigh)

pNeigh.varea(
    x='date', y1 = 'zeros',  y2 = 'produced', source = source_Neigh,
    fill_color = 'green', alpha = 0.8, legend_label = 'Produced_Pow'
)
pNeigh.varea(
    x='date', y1 = 'zeros', y2 = 'consumed', source = source_Neigh,
    fill_color = 'red', alpha = 0.8, legend_label = 'Consumed_Pow'
)
pNeigh.varea(
    x='date', y1 = 'zeros', y2 = 'self_consumption', source = source_Neigh, 
    fill_color = 'yellow', alpha = 0.8, legend_label = 'Self_Consumption'
)
show(pNeigh)

#Potenze consumata(neighborhood)
output_file('neigh_consumed.html')

#Costruiamo il plot
pCons = figure(
    plot_width = 800, plot_height = 500, title = 'CONSUMED POWER(kW) NEIGHBORHOOD',
    x_axis_label = 'Date', y_axis_label = 'Power(kW)', x_axis_type = 'datetime'   
)
pw.plot_axis_dateFormatter(pCons) 

for j,color in zip(range(len(df_PwCons_AllDay)),colors):
    
    source_Cons = ColumnDataSource(data=df_PwCons_AllDay[j])
   
    #Fissiamo il gliph da utilizzare, nel nostro caso una semplice linea
    pCons.line(
        x = 'date', y = 'power', source = source_Cons,
        line_width=4, color = color, alpha = 0.8, legend_label = 'Consumed Power(kW) from ' + name_Cons[j][:-4]
    )

show(pCons)
