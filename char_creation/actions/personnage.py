class Personnage:
    def __init__(self, classe,pv,equipements):
        if(classe.lower() == "ranger"):
            self.classe = "rôdeur"
            self.force = 10
            self.intelligence = 12
            self.agilite = 18
        elif(classe.lower() == "warlock"):
            self.classe = "occultiste"
            self.force = 10
            self.intelligence = 18
            self.agilite = 12
        else:
            self.classe = "barbare"
            self.force = 18
            self.intelligence = 10
            self.agilite = 12
        self.pv = pv
        self.equipements = equipements

    

    def __str__(self):  
        return "Personnage:\n\x20\x20\x20\x20>classe:% s\n\x20\x20\x20\x20>force:% s\n\x20\x20\x20\x20>intelligence:% s\n\x20\x20\x20\x20>agilité:% s\n\x20\x20\x20\x20>équipements:% s" % (self.classe, self.force, self.intelligence, self.agilite, self.equipements)    
