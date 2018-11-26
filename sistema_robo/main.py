from dados import *
from com import *
from serial import *
from robo import *
from broadcast import *
from coordenadas import *
from ssCom import *
import globalsFlags
import time

import socket
import threading
import subprocess


globalsFlags.init()
porta = 62255
comSS = Com(porta)

#Divulga IP do robo por broadcast#
comSS.broadcast("mac|" + comSS.getMac()[0]['addr'], 65000)
msg = comSS.receber()
print(msg[0].decode())

##Coordenada Inicial Robo
coord = comSS.receber()
hostSS = coord[1]

def msgTrocada(dado,robo):
    while True:
        msgSS = comSS.receber()
        msg = msgSS[0].decode().split("|")
        if msg[0] == "mapa":
            listaAtual = msg[1]

            # Desserializar lista
            listaDesserealizada = serial.desserializa(listaAtual)
            dado.setListaDeCacas(listaDesserealizada)
            robo.atualizaLista(listaDesserealizada)


            # coordenadaAdv = msg[2]
            robo.setAutonomo(ssCom)
        elif msg[0] == "validada":
            listaAtual = msg[1]

            # Desserializar lista
            listaDesserealizada = serial.desserializa(listaAtual)
            dado.setListaDeCacas(listaDesserealizada)
            robo.atualizaLista(listaDesserealizada)

            # coordenadaAdv = msg2[2]
            # robo.setAutonomo(ssCom)
            globalsFlags.robo_event.set()
        elif msg[0] == "naoValidada":
            listaAtual = msg[1]

            # Desserializar lista
            listaDesserealizada = serial.desserializa(listaAtual)
            dado.setListaDeCacas(listaDesserealizada)
            robo.atualizaLista(listaDesserealizada)

            # coordenadaAdv = msg2[2]
            #robo.setAutonomo(ssCom)
            globalsFlags.robo_event.set()

        elif msg[0] == "continua":
            pass
        elif msg[0] == "pausa":
            pass
        elif msg[0] == "fimdejogo":
            pass
        elif msg[0] == "coordenada":
            comSS.enviar("coordenada|" + str(dado.getCoordenada().getX()) + str(dado.getCoordenada().getY()),hostSS)
        else:
            print("Mensagem não Esperada")
        pass


resposta = comSS.receber()
resposta = resposta[0].decode().split(",")

if(resposta[0] == "getid"):
    ##Enviar MAC do robo
    comSS.enviar(comSS.getMac()[0]['addr'],hostSS)

elif(resposta[0] == "auto"):
    resp = comSS.receber()
    print(resp[0].decode())

    split = resp[0].decode().split('|')

    i = 0
    cordInicial = coord[0].decode()
    listCord = []

    while(i < len(split)):
        if(split[i] == "lista"):
            i += 1
            cordenadas = split[i].split("/")
            print(cordenadas)
            j = 0
            while j < len(cordenadas):
                if (j == len(cordenadas)):
                    break
                else:
                    cordLista = []
                    cordLista.append(cordenadas[j][0])
                    cordLista.append(cordenadas[j][1])
                    cordenadasLista = Coordenadas(cordLista)
                    listCord.append(cordenadasLista)
                    j += 1
        i += 1
    print(cordInicial)
    print(listCord)

    coordenadaInicial = Coordenadas(cordInicial)

    ## Cord Inicial e Lista recebida
    #Chamar estrategia e comunicar com SS pela porta especifica

    dado = Dados(cordInicial, listCord)
    print(hostSS)
    ssCom = SSCom(comSS, hostSS, dado)
    robo = Robo(dado, ssCom)
    ##Thread ssCOM para enviar mensagem
    #
    #

    # Desserializar lista
    serial = Serial()

    msgSS = ("","")
    while msgSS == ("",""):
        robo.setAutonomo()
        msgSS = comSS.receber()
        msg = msgSS[0].decode().split("|")
        if(msg[0] == "confirmaMov"):
            listaAtual = msg[1]

            # Desserializar lista
            listaDesserealizada = serial.desserializa(listaAtual)
            dado.getListaDeCacas(listaDesserealizada)
            robo.atualizaLista(listaDesserealizada)

            #coordenadaAdv = msg[2]

            msgSS2 = comSS.receber()
            msg2 = msgSS[0].decode().split("|")
            if msg2[0] == "mapa":
                listaAtual = msg2[1]

                # Desserializar lista
                listaDesserealizada = serial.desserializa(listaAtual)
                dado.getListaDeCacas(listaDesserealizada)
                robo.atualizaLista(listaDesserealizada)

                #coordenadaAdv = msg2[2]
        elif msg[0] == "mapa":
                listaAtual = msg[1]

                #Desserializar lista
                listaDesserealizada = serial.desserializa(listaAtual)
                dado.getListaDeCacas(listaDesserealizada)
                robo.atualizaLista(listaDesserealizada)

                #coordenadaAdv = msg[2]
        elif msg[0] == "validada":
            listaAtual = msg[1]

            # Desserializar lista
            listaDesserealizada = serial.desserializa(listaAtual)
            dado.getListaDeCacas(listaDesserealizada)
            robo.atualizaLista(listaDesserealizada)

    # Desserializar lista
    serial = Serial()

    robo.setAutonomo(ssCom)
    Tauto = threading.Thread(target= msgTrocada(),args=(dado,robo,ssCom))
    Tauto.start()

    #msgSS = ("","")
    #while msgSS == ("",""):

elif(resposta[0] == "manual"):
    #Começar Pyro#
    lista = []
    dados = Dados(coord[0], lista)
    robo = Robo(dados)

    ssCom = SSCom(comSS, hostSS, dados)

    Tmanual = threading.Thread(target=msgTrocada(),args=(dados,robo,ssCom))
    Tmanual.start()

    comSS.rpc(dados,robo)
    uri = comSS.getURI()
    print("uri: " + str(uri))
    comSS.enviar("uri|" + str(uri),hostSS)
    comSS.start()

    sscom = SSCom(comSS, hostSS, dados)