# This files contains your custom actions which can be used to run
# custom Python code.
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, FollowupAction
import json
import os
import asyncio
from .DnD_api import creation_slots_persos, traduction_slots
# from rasa_sdk.forms import FormAction # a supprimer , ne fonctionne que sous rasa 2

class ActionEndChat(Action):

    def name(self) -> Text:
        return "action_end_chat"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print("action_end_chat")

        # on récupère tout les slots qui dépendent des choix de l'utilisateur
        entity_classe = tracker.get_slot("classe")
        entity_pv = tracker.get_slot("pv")
        entity_force = tracker.get_slot("force")
        entity_intelligence = tracker.get_slot("intelligence")
        entity_agilite = tracker.get_slot("agilite")
        entity_equipement = tracker.get_slot("equipement")
        entity_equipement_degat = tracker.get_slot("equipement_degat")
        entity_equipement_description = tracker.get_slot("equipement_description")

        response = ""
        # on regarde si tout les slots sont remplis
        if entity_classe == "" or entity_classe == None:
            # si l'utilisateur n'a pas fait de choix de classe
            # on lui indique d'en choisir une
            dispatcher.utter_message(text="Il faut choisir une classe!")
            dispatcher.utter_message(response="utter_classes_available")
            response = "utter_which_class"
            print("pas de classe")
            dispatcher.utter_message(response=response)
            return []
        elif entity_equipement == "" or entity_equipement == None: 
            # si l'utilisateur n'a pas choisi d'équipement mais qu'il a une classe
            # on lui demande de choisir un équipement parmi ceux dispo
            # pour ce faire on lance l'action action_print_choice_equipement    
            print("pas déquipement")
            dispatcher.utter_message(text="Il faut choisir un equipement "+tracker.get_slot("classe")+"!")  
            response = "action_print_choice_equipment"
            return [FollowupAction(response)]
        # si tout les slots sont remplis
        # on met toutes les infos dans un JSON
        slot_values = {
            "classe": entity_classe,
            "pv": entity_pv,
            "force": entity_force,
            "intelligence": entity_intelligence,
            "agilite": entity_agilite,
            "equipement": entity_equipement,
            "equipement_degat": entity_equipement_degat,
            "equipement_description": entity_equipement_description
        }
        print(slot_values.items())
        json_string = json.dumps(slot_values, indent=4)
        chemin = "output/personnage.json"
        try:
            #on s'assure que le chemin existe
            os.makedirs(os.path.dirname(chemin), exist_ok=True)
            #on ecrit les info dans le fichier créé
            with open(chemin, "w") as json_file:
                json_file.write(json_string)
                # print(f"Fichier créé à {chemin}!")
        except Exception as e:
            print("Une erreur est apparu: " + str(e))
        dispatcher.utter_message(response="utter_goodbye")    
        return [SlotSet(key="fin_discussion", value="1")]    


class ActionBeginChat(Action):

    def name(self) -> Text:
        return "action_begin_chat"

    async def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # on lance la fonction de DnD_api.py qui permet de récupérer les info de l'API
        slots = creation_slots_persos()
        # print(slots)
        # on appelle la fonction qui traduit les slots et nous les renvoies dans un fichier JSON
        # avec la key qui correspond au nom du slot dans Rasa et la value qui correspond à la valeur du slot obtenue de l'API traduite
        slots_traduit = await traduction_slots(slots)
        # print(slots_traduit)
        res = []
        # on set tous les slots récupérés
        for slot, value in slots_traduit.items():
            print("slot:",slot,", value:",value)
            res.append(SlotSet(key=slot, value=value))
        # print("action_begin_chat")
        # on réponds à l'utilisateur avec un message de bienvenue expliquant le but du chatbot
        dispatcher.utter_message(response="utter_welcome")
        return res

class ActionSetClass(Action):
    def name(self) -> Text:
        return "action_set_class"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print("action_set_class")
        # extraction de la classe choisi
        classe_choisi = next(tracker.get_latest_entity_values("classe"), None)
        print(classe_choisi)
        classes_dispo = [tracker.get_slot("classe_barbare"), tracker.get_slot("classe_rodeur"), tracker.get_slot("classe_occultiste")]
        res = []
        # si la classe choisi est dans les classe disponible extraite de l'API
        if classe_choisi in classes_dispo and classe_choisi!=None:
            # on récupère les valeur de la classe
            classe = "classe_"+classe_choisi
            force = "force_"+classe_choisi
            agilite = "agilite_"+classe_choisi
            intelligence = "intelligence_"+classe_choisi
            pv = "pv_"+classe_choisi
            # on set les slots qui dépendent de la classe choisi par l'utilisateur
            res.append(SlotSet(key="classe", value=tracker.get_slot(classe)))
            res.append(SlotSet(key="force", value=tracker.get_slot(force)))
            res.append(SlotSet(key="agilite", value=tracker.get_slot(agilite)))
            res.append(SlotSet(key="intelligence", value=tracker.get_slot(intelligence)))
            res.append(SlotSet(key="pv", value=tracker.get_slot(pv)))
            # on répond à l'utilisateur en lui indiquant de choisir un équipement 
            dispatcher.utter_message(text="Très bien "+classe_choisi+"! Il te faut maintenant choisir un équipement!")
            return res
        else:
            # si la classe n'est pas dans celle dispo 
            dispatcher.utter_message(text="Je n'ai pas compris, veuillez choisir une classe disponible parmis celles ennoncés.")
        return res

class ActionSetEquipement(Action):
    def name(self) -> Text:
        return "action_set_equipement"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print("action_set_equipement")
        # extraction du numéro d'équipement choisi par l'utilisateur
        equipement_choisi = tracker.get_slot("numero_equipement")
        print(equipement_choisi)
        # si le numéro d'equipement correspond bien à ceux disponible
        if equipement_choisi == "1" or equipement_choisi == "2":
            res = []
            # on récupère les slot dépendant de l'équipement choisi
            nom_equipement = "equipement_"+equipement_choisi+"_nom_"+tracker.get_slot("classe")
            equipement_degat = "equipement_"+equipement_choisi+"_degat_"+tracker.get_slot("classe")
            equipement_description = "equipement_"+equipement_choisi+"_description_"+tracker.get_slot("classe")
            # on set les slots dépendant du choix de l'utilisateur et regardant l'équipement
            res.append(SlotSet(key="equipement", value=tracker.get_slot(nom_equipement)))
            res.append(SlotSet(key="equipement_degat", value=tracker.get_slot(equipement_degat)))
            res.append(SlotSet(key="equipement_description", value=tracker.get_slot(equipement_description)))
            dispatcher.utter_message(text="Tout est bon pour moi!")
            return res
        else:
            # si le numéro d'quipement n'est pas dans ceux dispo 
            dispatcher.utter_message(text="Je n'ai pas compris, veuillez choisir un équipement disponible parmis ceux ennoncés.")
         
        return []

class ActionDisplayStats(Action):
    def name(self)->Text:
        return "action_display_stats"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain : Dict[Text,Any]) -> List[Dict[Text, Any]]:
        # on récupère la valeur de l'entité classe pour laquelle on veut savoir les stats

        classe = next(tracker.get_latest_entity_values("classe"), None)
        print("classe demandé:",classe)
        if classe == None :
            pass
        else:

            pv = tracker.get_slot("pv_"+classe)
            force = tracker.get_slot("force_"+classe)
            agilite = tracker.get_slot("agilite_"+classe)
            intel = tracker.get_slot("intelligence_"+classe)

            dispatcher.utter_message(text=f"Les stats du {classe} sont :")

            dispatcher.utter_message(text=f"points de vie : {pv}")
            dispatcher.utter_message(text=f"force : {force}")
            dispatcher.utter_message(text=f"intelligence : {intel}")
            dispatcher.utter_message(text=f"agilite: {agilite}")
        
        return []

class ActionPrintChoiceEquipment(Action):
    def name(self) -> Text:
        return "action_print_choice_equipment"
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print("action_set_class")
        # extraction de la classe choisi
        classe_choisi = tracker.get_slot("classe")
        message = ""
        # si l'utilisateur n'a pas choisi de classe
        if classe_choisi == None:
            # on demande à l'utilisateur d'en choisir
            message = "Les équipements dépendent de la classe que vous choisirez. Il vous faut choisir une classe!\n"
        else:
            # sinon on récupère les infos des équipements dispo pour la classe
            equipement1 = tracker.get_slot("equipement_1_nom_"+str(classe_choisi))
            print(equipement1)
            equipement2 = tracker.get_slot("equipement_2_nom_"+str(classe_choisi))
            print(equipement2)
            equipement1_degat = tracker.get_slot("equipement_1_degat_"+str(classe_choisi))
            print(equipement1_degat)
            equipement2_degat =   tracker.get_slot("equipement_2_degat_"+str(classe_choisi))
            print(equipement2_degat)
            # si l'utilisateur a choisi de jouer un occultiste
            if classe_choisi == "occultiste": 
                # il y a une description alors on la récupère
                equipement1_description = tracker.get_slot("equipement_1_description_occultiste")
                print(equipement1_description)
                equipement2_description = tracker.get_slot("equipement_2_description_occultiste")  
                print(equipement2_description) 
                # on affiche tout les slots dépendant des équipements dispo
                message = "Vous pouvez choisir un des équipements suivant (1 ou 2):\n 1)"+str(equipement1)+", dégats: "+str(equipement1_degat)+ ", description: "+str(equipement1_description)+"\n ou\n 2)"+str(equipement2)+", dégats: "+str(equipement2_degat)+ ", description: "+str(equipement2_description)
            else:
                # on affiche tout les slots dépendant des équipements dispo
                message = "Vous pouvez choisir un des équipements suivant (1 ou 2):\n 1)"+str(equipement1)+", dégats: "+str(equipement1_degat)+"\n ou\n 2)"+str(equipement2)+", dégats: "+str(equipement2_degat)
        
        dispatcher.utter_message(text=message)
        return []
    
class ActionDescriptionClasse(Action):
    def name(self) -> Text:
        return "action_description_classe"
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print("action_description_classe")
        # extraction de la classe choisi
        classe_choisi = next(tracker.get_latest_entity_values("classe"), None)
        print(classe_choisi)
        message = ""
        if classe_choisi == None:
            message = "Je ne vois pas de quelle classe vous parler donc je ne peux pas vous renseigner\n"
        elif classe_choisi == tracker.get_slot("classe_barbare"):
            message = "Le barbare est un combattant qui se bat avec des armes de guerre \n"
        elif classe_choisi == tracker.get_slot("classe_rodeur"):
            message ="Le rôdeur est un archer furtif qui ne manque jamais ses cibles \n"
        elif classe_choisi == tracker.get_slot("classe_occultiste"):
            message ="L'occultiste est quelqu'un qui a fait un pacte avec une créature d'outre-tombe en échange de pouvoirs surnaturel \n"
        dispatcher.utter_message(text=message)
        return []

# class Action_form_perso(FormAction):
     
#     def name(self)->str:
#         return "action_form_perso"
     
#     @staticmethod
#     def required_slots(tracker: Tracker)->list:
#         return["classe","equipement_1","equipement_2"] # slots qui vont être retournés 
     
#     def request_next_slot(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict) -> None:
#         current_slot = self.get_missing_slots(tracker)

#         if current_slot == "classe":
#             dispatcher.utter_message(text="Quelle classe choisissez-vous ?")
#         elif current_slot == "equipement1":
#             dispatcher.utter_message(text="choisissez votre première arme")
#         elif current_slot == "equipement2":
#             dispatcher.utter_message(text="choisissez votre deuxième arme")
#     def validate_classe(self,value:str, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict )-> dict:
#         classe = next(tracker.get_latest_entity_values("classe"), None)

#         # Si l'entité existe, l'utiliser pour remplir le slot
#         if classe:
#             return {"classe": classe}
#         else: 
#         # Si la valeur fournie n'est pas valide, demander une nouvelle valeur
#             dispatcher.utter_message(text="La classe que vous avez choisie n'existe pas")
#             return {"classe": None}
#     def validate_equipement_1(self, value: str, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict) -> dict:
#         # Récupérer les entités dans le tracker
#         equipement_1 = next(tracker.get_latest_entity_values("equipement_1"), None)
        
#         # Si l'entité existe, l'utiliser pour remplir le slot
#         if equipement_1:
#             return {"equipement_1": equipement_1}
#         else:
#             # Si la valeur fournie n'est pas valide, demander une nouvelle valeur
#             dispatcher.utter_message(text="je n'ai pas compris votre choix ")
#             return {"equipement_1": None}
        
#     def validate_equipement_2(self, value: str, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict) -> dict:
#         # Récupérer les entités dans le tracker
#         equipement_2 = next(tracker.get_latest_entity_values("equipement_2"), None)
        
#         # Si l'entité existe, l'utiliser pour remplir le slot
#         if equipement_2:
#             return {"equipement_1": equipement_2}
#         else:
#             # Si la valeur fournie n'est pas valide, demander une nouvelle valeur
#             dispatcher.utter_message(text="je n'ai pas compris votre choix ")
#             return {"equipement_2": None}
