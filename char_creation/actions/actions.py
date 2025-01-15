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
from .DnD_api import creation_slots_persos, traduction_slots
# from rasa_sdk.forms import FormAction # a supprimer , ne fonctionne que sous rasa 2


# This is a simple example for a custom action which utters "Hello World!"
# class ActionHelloWorld(Action):
#     def name(self) -> Text:
#         return "action_hello_world"
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#         dispatcher.utter_message(text="Hello World!")
#         return []

class ActionEndChat(Action):

    def name(self) -> Text:
        return "action_end_chat"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print("action_end_chat")

        # on récupère tout les lsots
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
            response = "utter_which_class"
            print("pas de classe")
            dispatcher.utter_message(response=response)
            return []
        elif entity_equipement == "" or entity_equipement == None:  
            print("pas déquipement")  
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
            
        return [SlotSet(key="fin_discussion", value="1")]    


class ActionBeginChat(Action):

    def name(self) -> Text:
        return "action_begin_chat"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        slots = creation_slots_persos()
        # print(slots)
        slots_traduit = traduction_slots(slots)
        # print(slots_traduit)
        res = []
        for slot, value in slots_traduit.items():
            print("slot:",slot,", value:",value)
            res.append(SlotSet(key=slot, value=value))
        print("action_begin_chat")
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
        classe_choisi = tracker.get_slot("classe")
        print(classe_choisi)
        classes_dispo = [tracker.get_slot("classe_barbare"), tracker.get_slot("classe_rodeur"), tracker.get_slot("classe_occultiste")]
        res = []
        if classe_choisi in classes_dispo:
            force = "force_"+tracker.get_slot("classe")
            agilite = "agilite_"+tracker.get_slot("classe")
            intelligence = "intelligence_"+tracker.get_slot("classe")
            pv = "pv_"+tracker.get_slot("classe")
            res.append(SlotSet(key="force", value=tracker.get_slot(force)))
            res.append(SlotSet(key="agilite", value=tracker.get_slot(agilite)))
            res.append(SlotSet(key="intelligence", value=tracker.get_slot(intelligence)))
            res.append(SlotSet(key="pv", value=tracker.get_slot(pv)))
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
        # extraction de la classe choisi
        equipement_choisi = tracker.get_slot("numero_equipement")
        print(equipement_choisi)
        if equipement_choisi == "1" or equipement_choisi == "2":
            res = []
            nom_equipement = "equipement_"+equipement_choisi+"_nom_"+tracker.get_slot("classe")
            equipement_degat = "equipement_"+equipement_choisi+"_degat_"+tracker.get_slot("classe")
            equipement_description = "equipement_"+equipement_choisi+"_description_"+tracker.get_slot("classe")
            res.append(SlotSet(key="equipement", value=tracker.get_slot(nom_equipement)))
            res.append(SlotSet(key="equipement_degat", value=tracker.get_slot(equipement_degat)))
            res.append(SlotSet(key="equipement_description", value=tracker.get_slot(equipement_description)))
            return res
        else:
            # si la classe n'est pas dans celle dispo 
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

        if classe == "rodeur":
                pv = tracker.get_slot("pv_rodeur")
                force = tracker.get_slot("force_rodeur")
                intel = tracker.get_slot("intelligence_rodeur")
                agilite = tracker.get_slot("agilite_rodeur")
                dispatcher.utter_message(text="Les stats du rôdeur sont :")
        elif classe == "barbare":
                pv = tracker.get_slot("pv_barbare")
                force = tracker.get_slot("force_rodeur")
                intel = tracker.get_slot("intelligence_rodeur")
                agilite = tracker.get_slot("agilite_rodeur")
                dispatcher.utter_message(text="Les stats du barbare sont :")
        elif classe == "occultiste":
                pv = tracker.get_slot("pv_rodeur")
                force = tracker.get_slot("force_rodeur")
                intel = tracker.get_slot("intelligence_rodeur")
                agilite = tracker.get_slot("agilite_rodeur")
                dispatcher.utter_message(text="Les stats de l'occultiste sont : ")
        else:
                dispatcher.utter_message(text="je ne vois pas de quelle classe vous parlez donc je ne peux pas vous afficher ses statss")
        
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
        if classe_choisi == None:
            message = "Les équipements dépendent de la classe que vous choisirez. Il vous faut choisir une classe!\n"
        else:
            equipement1 = tracker.get_slot("equipement_1_nom_"+str(classe_choisi))
            print(equipement1)
            equipement2 = tracker.get_slot("equipement_2_nom_"+str(classe_choisi))
            print(equipement2)
            equipement1_degat = tracker.get_slot("equipement_1_degat_"+str(classe_choisi))
            print(equipement1_degat)
            equipement2_degat =   tracker.get_slot("equipement_2_degat_"+str(classe_choisi))
            print(equipement2_degat)
            if classe_choisi == "occultiste":  
                equipement1_description = tracker.get_slot("equipement_1_description_occultiste")
                print(equipement1_description)
                equipement2_description = tracker.get_slot("equipement_2_description_occultiste")  
                print(equipement2_description) 
                message = "Vous pouvez choisir un des équipements suivant (1 ou 2):\n 1)"+str(equipement1)+", dégats: "+str(equipement1_degat)+ ", description: "+str(equipement1_description)+"\n ou\n 2)"+str(equipement2)+", dégats: "+str(equipement2_degat)+ ", description: "+str(equipement2_description)
            else:
                message = "Vous pouvez choisir un des équipements suivant (1 ou 2):\n 1)"+str(equipement1)+", dégats: "+str(equipement1_degat)+"\n ou\n 2)"+str(equipement2)+", dégats: "+str(equipement2_degat)
        
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