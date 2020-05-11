import pandas
import datetime as dt
from bokeh.models import DatetimeTickFormatter

#Definiamo una funzione per il calcolo della potenza
def calc_Pot(tempo,energia):

    #Ora Iniziale
    d0 = dt.timedelta(hours=tempo[0].hour, minutes=tempo[0].minute, seconds=tempo[0].second, microseconds=tempo[0].microsecond)

    #Inizializzo la lista della potenza
    potenza = [0]

    #Calcolo della potenza
    for i in range(len(tempo)-2):
        
        #Differenza Ora corrente-Ora Iniziale
        d1 = dt.timedelta(hours=tempo[i+1].hour, minutes=tempo[i+1].minute, seconds=tempo[i+1].second, microseconds=tempo[i+1].microsecond)
        dx = d1 -d0

        #Conversione secondi->ore
        sectohour = (dx.total_seconds())/3600

        # Calcolo Potenza(kW) da Energia(kWH)
        potenza += [(energia[i+1]-energia[i])/sectohour]
        d0 = d1

    return potenza

def data_cleaning(df,date,start = '',end = '',freq = '5T'):

    #Per BackGroundLoad che comincia da 0 -> Aggiungo la data del 12 dicembre 2015 00:00:00
    if(df['date'][0] == 0):
        df['date'] = df['date'] + 1449882000
    #Per HeaterCooler che comincia nel 2016
    if(df['date'][0] == 1475877600):
        df['date'] = df['date'] - 25999200
    #df_file[i]['date'] viene convertito in formato datetime e convertito dal formato epochUnix
    df[ 'date' ] = pandas.to_datetime(df['date'], origin='unix',unit = 's')
    #Puliamo i dati per ogni frame attraverso un resample e un interpolazione(Ogni minuto un campione)
    new_df = df.set_index('date').resample('1T').mean().interpolate('linear')    
    if(date == True):
        used_Day = pandas.date_range(start='{}'.format(start),end='{}'.format(end),freq='{}'.format(freq))
        #Aggiungo al dataframe gli indici di tutta la used_Day
        new_df = new_df.reindex(used_Day)
        #Gli indici senza valore sono NaN e li sostituiamo con uno 0
        new_df = new_df.fillna(0)
    #Resettiamo l'indice
    new_df.index.name = 'date'
    new_df = new_df.reset_index()
    #Genero la lista dell'energia(i dati sono puliti, per ogni minuto) e delle ore
    energy = new_df['energy'].tolist()
    
    data = {'date': new_df['date'], 'energy': energy }
    dataframe = pandas.DataFrame(data)
    return dataframe

def dfEnergy_to_dfPower(df):
    new_df = df
    time = new_df['date'].dt.time
    energy = new_df['energy'].tolist()
    #Eseguo il calcolo della potenza
    power = calc_Pot(time,energy)
    power = [0 if i < 0 else i for i in power]
    #Elimino l'utlima riga(La potenza ha una riga in meno dell'energia)
    ultimo_elemento = len(new_df) - 1
    new_df = new_df.drop([ultimo_elemento])
    #Creo il dataframe del singolo file e lo aggiungo alla lista a secondo della tipologia
    data = {'home': new_df['home'],'date': new_df['date'], 'power': power }
    dataframe = pandas.DataFrame(data)
    return dataframe

def sum_pow_en(list_df,powORen,home = False):
    #Somma di una lista di dataframe(sull'intera giornata)
    #Concateno i dataframe
    df_new = pandas.concat(list_df)
    if(home):
        df_new = df_new.groupby([df_new['home'],df_new['date']],as_index=False,sort=True)[[powORen]].sum()
    else:
        #Resolution Bug -> Potrebbe avere effetti collaterali 
        df_new = df_new.fillna(0)
        #Attenzione elimina la colonna home dal dataframe. Si cade in questo caso solo quando si effettuano calcoli sul vicinato. In
        #tal senso la colonna home non ha più nessun valore. Attenziona all'utilizzo del dataframe che ritorna
        df_new = df_new.groupby(df_new['date'],as_index=False,sort=True)[[powORen]].sum()

    return df_new

def diff_pow_en(df1,df2,powORen):
    #Differenza tra potenze di due dataframe(sull'intera giornata)
    df2_new = df2.copy()
    df2_new[powORen] *= -1
    df_new = [df1,df2_new]
    df_final = sum_pow_en(df_new,powORen)
    return df_final

def stored_pow_en(df_ProdTot,df_ConsTot,powORen):
   #Definisco la PotenzaImmessaNellaRete(PotenzaProdotta-PotenzaConsumata senza valori negativi)
   #Diff chiama anche la somma. Questa somma, chiamata senza home, fa perdere la colonna al dataframe
    df_Stored = diff_pow_en(df_ProdTot,df_ConsTot,powORen)
    df_Stored[powORen] = df_Stored[powORen].mask(df_Stored[powORen] < 0, 0)
    return df_Stored

def self_consumption(df_ProdTot,df_ConsTot,powORen):
    #Attenzione!! Il calcolo dell'autoncosumo comporta la perdita della colonna home
    #Calcolo autoconsumo (PotenzaProdotta-PotenzaImmessaNellaRete)
    #Potenza Immessa nella rete
    df_Stored = stored_pow_en(df_ProdTot,df_ConsTot,powORen)
    #Calcolo Autoconsumo
    df_selfConsumption = diff_pow_en(df_ProdTot,df_Stored,powORen)
    return df_selfConsumption

def plot_axis_dateFormatter(plot_Figure):
    #Imposta il formato data per l'ascisse del grafico passato come argomento
    plot_Figure.xaxis.formatter = DatetimeTickFormatter(
        
            years="20%y/%m/%d %H:%M",
            days="20%y/%m/%d %H:%M",
            months="20%y/%m/%d %H:%M",
            hours="20%y/%m/%d %H:%M",
            minutes="20%y/%m/%d %H:%M"
                
        )