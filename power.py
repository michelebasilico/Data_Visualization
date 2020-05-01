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