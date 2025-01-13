# This files contains your custom actions which can be used to run
# custom Python code.
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import json
from DnD_api import creation_slots_persos, traduction_slots

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

        # on récupère une liste contenant toutes nos entities
        entities = tracker.latest_message['entities']

        # on récupère les entities voulu pour créer notre perso
        for e in entities:
            if e['entity'] == "classe":
                entity_classe = e['value']
            elif e['entity'] == "pv":
                entity_pv = e['value']
            elif e['entity'] == "force":
                entity_force = e['value']
            elif e['entity'] == "intelligence":
                entity_intelligence = e['value']
            elif e['entity'] == "agilite":
                entity_agilite = e['value']
            elif e['entity'] == "equipement":
                entity_equipement= e['value']
            elif e['entity'] == "equipement_degat":
                entity_equipement_degat = e['value']
            elif e['entity'] == "equipement_description":
                entity_equipement_description = e['value']    


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
        json_string = json.dumps(slot_values, indent=4)
        chemin = "output/personnage.json"

        try:
            with open(chemin, "w") as json_file:
                json_file.write(json_string)
            
            dispatcher.utter_message(text=f"Fichier créé à {chemin}!")
        except Exception as e:
            dispatcher.utter_message(text=f"Une erreur est apparu: {str(e)}")

        return []    


class ActionBeginChat(Action):

    def name(self) -> Text:
        return "action_begin_chat"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        slots = creation_slots_persos()
        slots_traduit = traduction_slots(slots)

        slot_events = [SlotSet(slot, value) for slot, value in slots_traduit.items()]

        dispatcher.utter_message(text="Les slots ont été mis à jour")
        
        return slot_events   
