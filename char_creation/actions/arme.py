class Arme():
    def __init__(self, nom, degat, description = ""):
        # définition des attributs d'une arme
        self.nom = nom
        self.degat = degat
        self.description = description

    def get_nom(self):
        return self.nom  

    def get_degat(self):
        return self.degat 

    def get_description(self):
        return self.description 

    def __str__(self):  
        # affichage d'une arme
        return "ARME:\n\x20\x20\x20\x20>nom:% s\n\x20\x20\x20\x20>dégât:% s\n\x20\x20\x20\x20>decription:% s" % (self.nom, self.degat, self.description)             
