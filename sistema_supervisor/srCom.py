import Pyro4

class SRcom:

    def __init__(self, uri):
        self.srcom = Pyro4.Proxy(uri)

    def setID(self, valor):
        pass

    def getPosInicial(self):
        return self.srcom.getPosInicial()

    def getSituacaoMapa(self):
        pass

    def setMover(self, direcao):
        pass

    def setTime(self):
        pass
