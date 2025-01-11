import requests
import json
from arme import Arme
import random
from personnage import Personnage
from googletrans import Translator

# url de l'api de dnd
url = "https://www.dnd5eapi.co"
headers = {"Accept": "application/json"}
# url de toutes les classes dispo dans dnd
url_classe = url + "/api/classes/"
# url des classes que l'on souhaite traités
url_nos_classes = []
# les infos de nos classes
nos_classes = [] 
# pv de nos classes dans le même ordre que précédemment (celui de l'api)
# soit Barbare(0), Rodeur(7) et Occultiste(10)
pv = [] 
# url des équipements en fonction des classes
# dans l'item 0 on a les équipements du barbare
# dans l'item 1 on a les équipements du rodeur
# dans l'item 2 on a les équipements de l'occultiste
url_equipements = []
# équipement de nos classes dans le même ordre que précédemment (celui de l'api)
# soit Barbare(0), Rodeur(7) et Occultiste(10)
equipements = []

slot_values = []

# ??
payload = {}
headers = {
  'Accept': 'application/json'
}

# récupère les classes que l'on va utiliser actuellement et leurs urls
# dans notre cas: BARBARE, RODEUR & OCCULTISTE
# on passe en entrée les index des classes à chopper
# ici 0, 7 & 10  
def get_classe(index):
  # on récupère la liste des classes dispo dans dnd
  response = requests.request("GET", url_classe, headers=headers, data=payload)
  response_json = response.json()
  for i in index:
    # on récupère via la requete l'url des classes que l'on veut traiter dans l'api dnd
    url_classe_index = url +  response_json['results'][i]['url']
    url_nos_classes.append(url_classe_index)
    # print(url_classe_index)
    # on récupère les infos de la classe à l'index désigné
    response_nos_classes = requests.request("GET", url_classe_index, headers=headers, data=payload)
    # print_json(response_nos_classes)
    nos_classes.append(response_nos_classes)
  return response_nos_classes

# récupère l'équipements de toutes les classes que l'on traite
def get_equipement():
  # pour toutes les classes que l'on veut traiter
  for i in range(len(nos_classes)):
    # on récupère le premier équipement dans les infos de la classe
    equipement = nos_classes[i].json()['starting_equipment_options']
    # si c'est un barbare
    if(i==0):
      url_arme_1,url_arme_2 = get_equipement_barbare(equipement)
    # si c'est un rodeur  
    elif(i==1):
      url_arme_1,url_arme_2 = get_equipement_rodeur(nos_classes[i].json())
    # si c'est un occultiste   
    else:
      get_equipement_occultiste(nos_classes[i].json())
  
    # si ça n'est pas un occultiste
    if(i!=2):
      url_equipements.append([])
      url_equipements[i].append(url_arme_1)
      url_equipements[i].append(url_arme_2)
      # print(url_equipements)

      # on récupère les infos sur les armes du barbare
      equipements.append([])
      arme_1 = get_arme(url_arme_1)
      if("axe" in arme_1.nom):
        res=arme_1.nom.split("axe")
        arme_1.nom=res[0]+" axe"
      elif("bow" in arme_1.nom):
        res=arme_1.nom.split("bow")
        arme_1.nom=res[0]+" bow"  
      # print(arme_1) 
      equipements[i].append(arme_1)
      arme_2 = get_arme_random(url_arme_2)
      if("axe" in arme_2.nom):
        res=arme_2.nom.split("axe")
        arme_2.nom=res[0]+" axe"
      elif("hammer" in arme_2.nom):
        res=arme_2.nom.split("hammer")
        arme_2.nom=res[0]+" hammer"
      # print(arme_2) 
      equipements[i].append(arme_2) 
  # print(equipements)  

def get_equipement_barbare(equipement):
  # on récupère les 2 urls: de la deuxième option d'armes
  #  >> pour avoir la hache à deux mains
  # et de la première option d'armes
  #  >> pour avoir une arme aléatoire dans les armes de guerre de corps à corps
  url_arme_1 = equipement[1]['from']['options'][0]['of']['url']
  url_arme_2 = equipement[0]['from']['options'][1]['choice']['from']['equipment_category']['url']
  # print(url_arme_1)
  # print(url_arme_2)
  return url_arme_1,url_arme_2

def get_equipement_rodeur(equipement):
  # on récupère les 2 urls: premièrement de l'item starting_equipement
  # on recupère la première cellule puis son item equipment et son url 
  #  >> pour avoir un arc long
  # et de la première option d'armes
  #  >> pour avoir une arme aléatoire dans les armes courante de corps à corps
  url_arme_1 = equipement['starting_equipment'][0]['equipment']['url']
  url_arme_2 = equipement['starting_equipment_options'][1]['from']['options'][1]['choice']['from']['equipment_category']['url']
  # print(url_arme_1)
  # print(url_arme_2)
  return url_arme_1,url_arme_2

def get_equipement_occultiste(equipement):
  # ici on considère que les sorts sont comme des équipements
  # on a choisi pour plus de simplicité des sorts
  url_sort_1 ="/api/spells/poison-spray"
  url_sort_2 ="/api/spells/burning-hands"

  url_equipements.append([])
  url_equipements[2].append(url_sort_1)
  url_equipements[2].append(url_sort_2)
  # print(url_equipements)
  
  # on récupère les infos sur les sorts de l'occultiste
  equipements.append([])
  sort_1 = get_sort(url_sort_1,"damage_at_character_level")
  # print(sort_1)
  equipements[2].append(sort_1)
  sort_2 = get_sort(url_sort_2,"damage_at_slot_level")
  # print(sort_2)
  equipements[2].append(sort_2)


def get_sort(url_sort,url_damage):
  # on récupère le détail de l'arme dispo dans dnd
  response = requests.request("GET", url + url_sort, headers=headers, data=payload)
  sort = response.json()
  # on récupère les infos du sort 1 soit son nom, son niveau qui correspondra
  # au niveau de dégat infligé et une description
  # on sépare la valeur du dés de dégas au niveau du char 'd'
  # le dé de dégas se présente: "1d6" après le split on a 1 et 6
  # on récupère ainsi le 6
  degat = sort["damage"][url_damage]["1"].split('d')
  # print(degat) 
  sort_1 = Arme(sort["name"], degat[1], sort["desc"][0])
  return sort_1


def get_arme(url_arme):
  # on récupère le détail de l'arme dispo dans dnd
  response = requests.request("GET", url + url_arme, headers=headers, data=payload)
  arme = response.json()
  # on sépare la valeur du dés de dégas au niveau du char 'd'
  # le dé de dégas se présente: "1d6" après le split on a 1 et 6
  # on récupère ainsi le 6
  degas = arme["damage"]["damage_dice"].split('d') 
  arme_1 = Arme(arme["name"], degas[1])
  return arme_1

def get_arme_random(url_arme):
  # on récupère la liste des armes dispo dans dnd
  response = requests.request("GET", url + url_arme, headers=headers, data=payload)
  arme = response.json()
  # on calcule le nb d'armes dispo dans la catégorie
  nb_armes = len(arme["equipment"])
  # on en choisi une au hasard
  hasard = random.randrange(nb_armes)
  arme_2_url = arme["equipment"][hasard]["url"]
  # on récupère les infos de l'arme sélectionné au hasard
  return get_arme(arme_2_url)

# récupère les pv de toutes les classes que l'on traite
# pour associer les bons pv aux bonnes classes (ici on en a 3)
def get_PV():
  # pour toutes les classes que l'on veut traiter
  for i in range(len(nos_classes)):
    # on récupère les pv dans les infos de la classe
    pv_classe = nos_classes[i].json()['hit_die']
    # print(pv_classe)
    pv.append(pv_classe)


def print_json(response):
  # affichage réponse obtenue via requete get
  if response.status_code == 200:
    print(response.json())
  else:
    print(f"Failed to retrieve data. Status code: {response.status_code}")

if __name__ == "__main__":
  # les index des classes que l'on veut dans /api/classes/
  # 0:Barbarian/Barbare, 7:Ranger/Rodeur & 10:Warlock/Occultiste
  response_nos_classes = get_classe([0,7,10])
  # afficher les classes que l'on a récupéré et leur info
  # print_json(response_nos_classes)

  get_PV()
  # print(pv)

  get_equipement()

  # creation des persos dispo
  personnages = []
  for i in range(len(nos_classes)):
    # print(nos_classes[i].json()["name"])
    personnages.append(Personnage(nos_classes[i].json()["name"],pv[i],equipements[i]))
    # print(personnages[i]) 
  
  # on met toutes les infos dans un JSON
  slot_values = {
      "classe_barbare": personnages[0].classe,
      "classe_rodeur": personnages[1].classe,
      "classe_occultiste": personnages[2].classe,
      "pv_barbare": personnages[0].pv,
      "pv_rodeur": personnages[1].pv,
      "pv_occultiste": personnages[2].pv,
      "force_barbare": personnages[0].force,
      "force_rodeur": personnages[1].force,
      "force_occultiste": personnages[2].force,
      "intelligence_barbare": personnages[0].intelligence,
      "intelligence_rodeur": personnages[1].intelligence,
      "intelligence_occultiste": personnages[2].intelligence,
      "agilite_barbare": personnages[0].agilite,
      "agilite_rodeur": personnages[1].agilite,
      "agilite_occultiste": personnages[2].agilite,
      "equipement_1_nom_barbare": personnages[0].equipements[0].nom,
      "equipement_1_nom_rodeur": personnages[1].equipements[0].nom,
      "equipement_1_nom_occultiste": personnages[2].equipements[0].nom,
      "equipement_2_nom_barbare": personnages[0].equipements[1].nom,
      "equipement_2_nom_rodeur": personnages[1].equipements[1].nom,
      "equipement_2_nom_occultiste": personnages[2].equipements[1].nom,
      "equipement_1_degat_barbare": personnages[0].equipements[0].degat,
      "equipement_1_degat_rodeur": personnages[1].equipements[0].degat,
      "equipement_1_degat_occultiste": personnages[2].equipements[0].degat,
      "equipement_2_degat_barbare": personnages[0].equipements[1].degat,
      "equipement_2_degat_rodeur": personnages[1].equipements[1].degat,
      "equipement_2_degat_occultiste": personnages[2].equipements[1].degat,
      "equipement_1_description_occultiste": personnages[2].equipements[0].description,
      "equipement_2_description_occultiste": personnages[2].equipements[1].description
  }

  # Define Rasa endpoint
  rasa_url = "http://localhost:5005/conversations/user123/tracker/events"

  # Initialize the Translator
  translator = Translator()
  
  # print("Original:", slot_values)

  for slot_name, slot_value in slot_values.items():
    if not str(slot_value).isdigit() and "classe" not in slot_name:
      print(slot_value)
      translation = translator.translate(slot_value, src='en', dest='fr')
      print(translation.text)
  # Automatically generate the "data" JSON
  data = [{"event": "slot", "name": slot_name, "value": slot_value} for slot_name, slot_value in slot_values.items()]

  # # Send the events to set the slots
  # response = requests.post(rasa_url, json=data)
  # print(response.status_code, response.json())

  # Output the translated text
  # print("Translated:", data)
