import pandas as pd 
import os
import requests
import matplotlib.pyplot as plt 
import numpy as np
import matplotlib.dates as dates
import time
import math
import random

url="https://covid.ourworldindata.org/data/ecdc/full_data.csv"


def wget(url):
    r = requests.get(url, allow_redirects=True)
    with open(url[url.rfind('/') + 1::], 'wb') as f:
        f.write(r.content)

wget(url)


df=pd.read_csv("full_data.csv")

data=df.to_dict("list")

''' Obtencion de los paises disponibles en la base de datos'''
cant_paises=len(data["location"])

countries_availables=[]

for i in range(cant_paises):
    if data["location"][i-1] != data["location"][i]:
        countries_availables.append(data["location"][i].lower())


''' Obtencion de las fechas disponibles en la base de datos'''
date_available=[]

cant_fechas=len(data["date"])

for i in range(cant_fechas):
    if data["date"][i] not in date_available:
        date_available.append(data["date"][i])




def get_countries():
    '''Funcion de obtencion de la cantidad, el nombre de los paises, el nombre de guardado de la imagen generada (En caso de que el ususario quiera guardarla)
     y el periodo de tiempo a graficar'''

    tiempo_inicio=input("Ingrese fecha de inicio para el grafico en el formato: año-mes-dia\n")

    if tiempo_inicio not in date_available:
        print("Entrada Invalida. Fecha no Disponible")
        return 0

    tiempo_fin=input("Ingrese fecha de finalizacion para el grafico en el formato: año-mes-dia\n")

    if tiempo_fin not in date_available:
        print("Entrada Invalida.Fecha no Disponible")
        return 0

    respuesta=input("Deseas guardar la imagen final? Ingresa si o no\n")

    if respuesta.lower() == "si":
        nombre_archivo= input("Ingrese el nombre del archivo\n") + ".png"
    else:
        nombre_archivo="no"

    nombre_paises=[]

    nro_paises=0

    while True:
      pais=input("Ingrese el o los paises en forma individual. Cuando desee acabar ingrese quit\n\n")
      if pais !="quit" and pais.lower() in countries_availables:
        if pais not in nombre_paises:
          nombre_paises.append(pais)
          nro_paises+=1
      if pais=="quit" and len(nombre_paises)!=0:
        nombre_paises.sort()
        return nombre_paises,nro_paises,tiempo_inicio,tiempo_fin,nombre_archivo
      if pais !="quit" and pais.lower() not in countries_availables:
        print("Nombre de Pais invalido")
        return 0
      if pais=="quit" and len(nombre_paises)==0:
        print("Entrada Invalida. Debe ingresar los paises a graficar")
        return 0

    return nombre_paises,nro_paises,tiempo_inicio,tiempo_fin,nombre_archivo



def formato_nombres(list_paises):
  """Devuelve una nueva lista con los nombres de los paises en formato de la data, es decir, con la primera letra en mayuscula y el resto en minuscula"""
  new=[]
  for i in range(len(list_paises)):
    new.append(list_paises[i][0].upper()+list_paises[i][1: ])
  return new


def posicion_ini_fin_fechas(data_country,cant,fecha_ini,fecha_fin):
    """Devuelve las posiciones en que estan la fecha inicial: fecha_ini y la fecha final: fecha_fin en la data del pais seleccionado: data_country"""
    pos_ini=-1
    pos_fin=-1
    for i in range(cant):
        if data_country["date"][i]== fecha_ini:
            pos_ini=i
        if data_country["date"][i]== fecha_fin:
            pos_fin=i
    return pos_ini,pos_fin


def check_dates(pais,fecha_ini,fecha_fin):
    """Chequea que las fechas dadas que limitan el periodo de tiempo a analizar, esten disponibles para el pais escogido"""
    
    df_country_uno=df[df["location"]==pais]
    data_country_uno=df_country_uno.to_dict("list")
    cant_uno=len(data_country_uno["date"])

    pos_ini_uno, pos_fin_uno=posicion_ini_fin_fechas(data_country_uno,cant_uno,fecha_ini,fecha_fin)

    if pos_ini_uno==-1 or pos_fin_uno ==-1:
      return -1

    return 1


def cargar_datos(data_country,arreglo,dato,pos_ini,pos_fin):
    """Almacena en la lista: arreglo, los valores de la data: data_country, en el dato especificado entre las posiciones dadas"""
    for j in range(pos_ini,pos_fin+1):
        arreglo.append(data_country[dato][j])



def graph_pais(nombre_pais,fecha_ini,fecha_fin,nombre_archivo):
    """Grafica casos detectados y fallecimientos totales para el país con nombre nombre_pais en el periodo de tiempo comprendido
    entre la fecha inicial: fecha_ini y la fecha final: fecha_fin"""
    x=[]
    m=[]
    y=[]

    df_country=df[df["location"]==nombre_pais[0]]
    data_country=df_country.to_dict("list")
    cant=len(data_country["date"])

    pos_ini,pos_fin=posicion_ini_fin_fechas(data_country,cant,fecha_ini,fecha_fin)

    cargar_datos(data_country,x,"date",pos_ini,pos_fin)
    cargar_datos(data_country,y,"new_cases",pos_ini,pos_fin)
    cargar_datos(data_country,m,"new_deaths",pos_ini,pos_fin)

    plt.figure(figsize=(30, 10))

    plt.subplot(1, 2, 1) 
    plt.plot(x,y,"m-",label="Nuevos Casos")
    plt.legend()

    plt.xticks(rotation=60)
    plt.xticks(x[ : :math.floor((pos_fin-pos_ini)/7)])

    plt.subplot(1, 2, 2)
    plt.plot(x,m,"r-",label="Nuevos fallecimientos")
    plt.legend()

    plt.xticks(rotation=60)
    plt.xticks(x[ : :math.floor((pos_fin-pos_ini)/7)])

    plt.suptitle("COVID-19 EN {}".format(nombre_pais[0].upper()),fontsize=30)

    if nombre_archivo != "no":
      plt.savefig(nombre_archivo)

    plt.show()



def puntos_interseccion(array_fechas,array_uno,array_dos):
    """Calcula los valores comunes entre el array_uno y el array_dos, que los devuelve en el array new, aunado a las fechas donde ocurre esto, que se retornan en fechas_inter"""
    new=[]
    fechas_inter=[]
    for i in range(len(array_fechas)):
      if array_uno[i]==array_dos[i]:
        new.append(array_uno[i])
        fechas_inter.append(array_fechas[i])
    return new,fechas_inter


def graph_par_paises(nombre_paises,fecha_ini,fecha_fin,nombre_archivo):
    """ Graficar para los dos paises en list_paises la cantidad de casos y fallecimientos en dos gráficos con labels en el intervalo de tiempo comprendido entre la fecha inicial: 
    fecha_ini y la fecha final: fecha_fin y marca con un punto las intersecciónes entre gráficos si las hay"""

    x_fechas=[]

    y_casos_pais_uno=[]
    y_casos_pais_dos=[]
    y_muertes_pais_uno=[]
    y_muertes_pais_dos=[]

    fechas_interseccion_nuevos_casos=[]
    fechas_interseccion_nuevas_muertes=[]

    puntos_interseccion_nuevos_casos=[]
    puntos_interseccion_nuevas_muertes=[]

    #PAIS UNO
    df_country_uno=df[df["location"]==nombre_paises[0]]
    data_country_uno=df_country_uno.to_dict("list")
    cant_uno=len(data_country_uno["date"])

    pos_ini_uno, pos_fin_uno=posicion_ini_fin_fechas(data_country_uno,cant_uno,fecha_ini,fecha_fin)

    cargar_datos(data_country_uno,x_fechas,"date",pos_ini_uno,pos_fin_uno)
    x_fechas.sort()

    cargar_datos(data_country_uno,y_casos_pais_uno,"new_cases",pos_ini_uno,pos_fin_uno)

    cargar_datos(data_country_uno,y_muertes_pais_uno,"new_deaths",pos_ini_uno,pos_fin_uno)

    #PAIS DOS
    df_country_dos=df[df["location"]==nombre_paises[1]]
    data_country_dos=df_country_dos.to_dict("list")

    cant_dos=len(data_country_dos["date"])

    pos_ini_dos, pos_fin_dos=posicion_ini_fin_fechas(data_country_dos,cant_dos,fecha_ini,fecha_fin)

    cargar_datos(data_country_dos,y_casos_pais_dos,"new_cases",pos_ini_dos,pos_fin_dos)

    cargar_datos(data_country_dos,y_muertes_pais_dos,"new_deaths",pos_ini_dos,pos_fin_dos)

    puntos_interseccion_nuevos_casos,fechas_interseccion_nuevos_casos=puntos_interseccion(x_fechas,y_casos_pais_uno,y_casos_pais_dos)

    puntos_interseccion_nuevas_muertes,fechas_interseccion_nuevas_muertes=puntos_interseccion(x_fechas,y_muertes_pais_uno,y_muertes_pais_dos)

    plt.figure(figsize=(30, 10))

    plt.subplot(1, 2, 1) 
    plt.title("Nuevos Casos",fontsize=30)
    plt.plot(x_fechas,y_casos_pais_uno,"m-",label=nombre_paises[0])
    plt.plot(x_fechas,y_casos_pais_dos,"r-",label=nombre_paises[1])
    plt.legend()
    plt.xticks(rotation=60)
    plt.xticks(x_fechas[ : :math.floor((pos_fin_uno-pos_ini_uno)/7)])

    if len(fechas_interseccion_nuevos_casos)!=0:
      plt.plot(fechas_interseccion_nuevos_casos,puntos_interseccion_nuevos_casos,"ko")

    plt.subplot(1, 2, 2) 
    plt.title("Nuevos Fallecimientos",fontsize=30)
    plt.plot(x_fechas,y_muertes_pais_uno,"b-",label=nombre_paises[0])
    plt.plot(x_fechas,y_muertes_pais_dos,"y-",label=nombre_paises[1])
    plt.legend()
    plt.xticks(rotation=60)
    plt.xticks(x_fechas[ : :math.floor((pos_fin_uno-pos_ini_uno)/7)])

    if len(fechas_interseccion_nuevas_muertes)!=0:
      plt.plot(fechas_interseccion_nuevas_muertes,puntos_interseccion_nuevas_muertes,"ko")


    plt.suptitle("COVID-19 en {} - {}".format(nombre_paises[0],nombre_paises[1]),fontsize=30)

    if nombre_archivo != "no":
      plt.savefig(nombre_archivo)

    plt.show()



def graph_multiple_paises(nombre_paises,fecha_ini,fecha_fin,nombre_archivo):
    """Grafica la cantidad de casos en una escala logaritmica de los paises ingresados que estan en la lista:nombre_paises, en el intervalo de tiempo definido"""

    colores=["g-","r-","m-","y-","b-","k-"]

    plt.figure(figsize=(30, 10))

    for i in range(len(nombre_paises)):
      x_fechas=[]
      y_casos_pais_uno=[]

      df_country_uno=df[df["location"]==nombre_paises[i]]
      data_country_uno=df_country_uno.to_dict("list")
      cant_uno=len(data_country_uno["date"])

      pos_ini_uno, pos_fin_uno=posicion_ini_fin_fechas(data_country_uno,cant_uno,fecha_ini,fecha_fin)

      cargar_datos(data_country_uno,x_fechas,"date",pos_ini_uno,pos_fin_uno)
      x_fechas.sort()

      cargar_datos(data_country_uno,y_casos_pais_uno,"new_cases",pos_ini_uno,pos_fin_uno)

      if i>5:
        color=colores[random.randint(0,5)]
      else:
        color =colores[i]

      plt.plot(x_fechas,y_casos_pais_uno,color,label=nombre_paises[i])
      plt.yscale("log")
      plt.title("Nuevos Casos de COVID-19",fontsize=24)
      plt.grid()
      plt.legend()#Si es un grafico, es un solo plt.legend justo antes del show
      plt.xticks(rotation=60)
      
      plt.xticks(x_fechas[ : :math.floor((pos_fin_uno-pos_ini_uno)/7)])

    if nombre_archivo != "no":
      plt.savefig(nombre_archivo)
    
    plt.show()
    


def graph_covid(tupla):
    '''Genera el grafico final de acuerdo a el numero de paises ingresados '''
    if tupla == 0:
        return

    list_nombres_formato=formato_nombres(tupla[0])

    for i in range(tupla[1]):
      if check_dates(list_nombres_formato[i],tupla[2],tupla[3]) == -1:
        print("No esta toda la informacion en la base de datos de el o los paises para las fechas seleccionadasc")
        return

    if tupla[1]==1:
        graph_pais(list_nombres_formato,tupla[2],tupla[3],tupla[4])

    elif tupla[1]==2:
        graph_par_paises(list_nombres_formato,tupla[2],tupla[3],tupla[4])
        
    else:
        graph_multiple_paises(list_nombres_formato,tupla[2],tupla[3],tupla[4])


tupla=get_countries()
graph_covid(tupla)
