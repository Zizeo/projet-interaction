class Arme():
    def __init__(self, nom, degat, description = ""):
        self.nom = nom
        self.degat = degat
        self.description = description

    def get_nom(self):
        return self.nom  

    def get_degat(self):
        return self.degat 

    def __str__(self):  
        return "ARME:\n\x20\x20\x20\x20>nom:% s\n\x20\x20\x20\x20>dégât:% s\n\x20\x20\x20\x20>decription:% s" % (self.nom, self.degat, self.description)             
