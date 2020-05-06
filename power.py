import pandas
import datetime as dt

#Definiamo una funzione in grado di convertire il tempo Unix in un formato Data e ritorna le ore di tale formato.In ingresso vuole un dataframe(Unix,Energia)
def Unix_to_hours(dataframe):
    #Convertiamo epochUnix nel formato data
    dataframe['date'] = pandas.to_datetime(dataframe['date'], origin='unix',unit = 's')

    #Estraggo le ore
    ore = dataframe['date'].dt.time

    return ore


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
    
    data = {'date': new_df['date'], 'energy': energy}
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
    data = {'date': new_df['date'], 'power': power}
    dataframe = pandas.DataFrame(data)
    return dataframe

def sum_power(list_df):
    #Somma di una lista di dataframe(sull'intera giornata)
    #Concateno i dataframe
    df_new = pandas.concat(list_df)

    #Li raggruppo in base alla data e sommo le potenze(con data uguale)
    df_new = df_new.groupby(df_new['date'],as_index=False,sort=True)[['power']].sum()

    return df_new

def diff_power(df1,df2):
    #Differenza tra potenze di due dataframe(sull'intera giornata)
    df2['power'] *= -1
    df_new = [df1,df2]
    df_final = sum_power(df_new)
    df2['power'] *= -1
    return df_final

def self_consumption(df_ProdTot,df_ConsTot):
    #Calcolo autoconsumo (PotenzaProdotta-PotenzaImmessaNellaRete)

    #Definisco la PotenzaImmessaNellaRete(PotenzaProdotto-PotenzaConsumata senza valori negativi)
    df_PotImm = diff_power(df_ProdTot,df_ConsTot)
    df_PotImm['power'] = df_PotImm['power'].mask(df_PotImm['power'] < 0, 0)
    #Calcolo Autoconsumo
    df_selfConsumption = diff_power(df_ProdTot,df_PotImm)
    return df_selfConsumption
