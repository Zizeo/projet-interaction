# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
#
#
# class ActionHelloWorld(Action):
#
#     def name(self) -> Text:
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         dispatcher.utter_message(text="Hello World!")
#
#         return []


from rasa_sdk import Action
from rasa_sdk.events import SlotSet

import random


class ActionCombatTurn(Action):
    def name(self) -> str:
        return "action_combat_turn"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ):
        player_hp = tracker.get_slot("player_hp")
        enemy_hp = tracker.get_slot("enemy_hp")
        player_action = tracker.get_slot("player_action")
        combat_state = tracker.get_slot("combat_state")

        if combat_state != "ongoing":
            dispatcher.utter_message(text="Le combat est déjà terminé.")
            return []

        # Action du joueur
        if player_action == "attack":
            damage = random.randint(10, 20)
            enemy_hp -= damage
            dispatcher.utter_message(
                text=f"Vous attaquez et infligez {damage} points de dégâts à l'ennemi."
            )
        elif player_action == "use_item":
            heal = random.randint(10, 20)
            player_hp += heal
            dispatcher.utter_message(
                text=f"Vous utilisez une potion et récupérez {heal} points de vie."
            )
        elif player_action == "flee":
            return [SlotSet("combat_state", "fled")]

        if enemy_hp <= 0:
            return [SlotSet("enemy_hp", 0), SlotSet("combat_state", "victory")]

        # Action de l'ennemi
        enemy_action = random.choices(["attack", "wait"], weights=[0.8, 0.2])[0]
        if enemy_action == "attack":
            damage = random.randint(3, 12)
            player_hp -= damage
            dispatcher.utter_message(
                text=f"L'ennemi attaque et inflige {damage} points de dégâts."
            )
        else:
            dispatcher.utter_message(text="L'ennemi observe vos mouvements.")

        # Vérifier si le joueur est vaincu
        if player_hp <= 0:
            return [SlotSet("player_hp", 0), SlotSet("combat_state", "defeat")]

        # Mise à jour des slots
        return [
            SlotSet("player_hp", player_hp),
            SlotSet("enemy_hp", enemy_hp),
            SlotSet("player_action", None),
        ]


class ActionCombatStart(Action):
    def name(self) -> str:
        return "action_combat_start"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ):
        player_hp = tracker.get_slot("player_hp")
        enemy_hp = tracker.get_slot("enemy_hp")
        dispatcher.utter_message(
            text=f"Le combat commence ! Vous avez {player_hp} points de vie. L'ennemi a {enemy_hp} points de vie."
        )
        return [SlotSet("combat_state", "ongoing")]


class ActionCombatEnd(Action):
    def name(self) -> str:
        return "action_combat_end"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ):
        state = tracker.get_slot("combat_state")
        if state == "ongoing":
            dispatcher.utter_message(text="Le combat est toujours en cours.")
            return []
        elif state == "victory":
            dispatcher.utter_message(response="utter_victory")
            return [SlotSet("combat_state", "ended")]
        elif state == "defeat":
            dispatcher.utter_message(response="utter_defeat")
            return [SlotSet("combat_state", "ended")]
        elif state == "fled":
            dispatcher.utter_message(text="Vous avez fuis le combat.")
            return [SlotSet("combat_state", "ended")]
        else:
            dispatcher.utter_message(text="Le combat est terminé.")
            return [SlotSet("combat_state", "ended")]


class ActionPlayerChoice(Action):
    def name(self) -> str:
        return "action_player_choice"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ):
        player_action = tracker.get_slot("player_action")
        if player_action is None:
            dispatcher.utter_message(text="Veuillez choisir une action.")
            return []
        return [SlotSet("player_action", player_action)]


class ActionSkillCheck(Action):
    def name(self) -> str:
        return "action_skill_check"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ):
        skill_check = tracker.get_slot("skill_check")
        skill_check_result = False
        dice_result = random.randint(1, 20)
        if dice_result > skill_check:
            dispatcher.utter_message(text="Le test de skill a reussi !")
            skill_check_result = True
        else:
            dispatcher.utter_message(text="Le test de skill a echoué !")
        return [
            SlotSet("skill_check", skill_check),
            SlotSet("skill_check_result", skill_check_result),
        ]


class ActionSetPlayerAction(Action):
    def name(self) -> str:
        return "action_set_player_action"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ):
        # Récupérer l'intent capturé
        player_intent = tracker.latest_message["intent"]["name"]

        # Définir le slot `player_action` en fonction de l'intent
        return [SlotSet("player_action", player_intent)]


class ValidateCombatForm(Action):
    def name(self) -> str:
        return "action_validate_combat_form"

    def validate_combat_state(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        if slot_value == "ended":
            return {"combat_state": "ended"}
        else:
            return {"combat_state": None}


class ActionSetPlayerAction(Action):
    def name(self) -> str:
        return "action_set_player_action"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ):
        # Récupérer l'intent capturé
        player_intent = tracker.latest_message["intent"]["name"]

        # Définir le slot `player_action` en fonction de l'intent
        return [SlotSet("player_action", player_intent)]


class ActionClassResponse(Action):
    def name(self) -> Text:
        return "action_class_response"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Récupérer les valeurs des slots
        classe = tracker.get_slot("class")
        type_de = next(tracker.get_latest_entity_values("type_dé"), None)

        score = random.randint(1,20)
        print(type_de)
        if type_de == "intelligence":
                print(score)
                # Vérifier les conditions
                if classe == "occultiste":
                        if score > 10:
                                dispatcher.utter_message(text="Vous avez réussi votre jet. Vous crochetez le cadenas et passez la porte.")
                        else:
                                dispatcher.utter_message(text="Vous n’arrivez pas à crocheter le cadenas, quel dommage! avez vous une autre idée ?")
                elif classe in ["barbare", "rodeur"]:
                        if score < 17:
                                dispatcher.utter_message(text="Vous n’arrivez pas à crocheter le cadenas, quel dommage! avez vous une autre idée ? ")
                        else:
                                dispatcher.utter_message(text="Vous avez réussi votre jet. Vous crochetez le cadenas et passez la porte.")
        elif type_de == "dexterité":
                print(score)
                # Vérifier les conditions
                if classe == "rodeur":
                        if score > 10:
                                dispatcher.utter_message(text="Quel abilité ! Vous avez réussi votre jet. Vous sautez de plateforme en plateforme et atteignez les escaliers.")
                        else:
                                dispatcher.utter_message(text="Vous tentez de passer les plateformes, mais vous trebuchez et vous tordez la cheville. Vous perdez 2 points de vie.")
                                return [SlotSet("player_hp", hp-2)]
                elif classe in ["barbare", "occultiste"]:
                        if score < 17:
                                dispatcher.utter_message(text="Vous tentez de passer les plateformes, mais vous trebuchez et vous tordez la cheville. Vous perdez 3 points de vie.")
                                hp = tracker.get_slot("player_hp")
                                return [SlotSet("player_hp", hp-3)]
                        else:
                                
                                dispatcher.utter_message(text="Quel abilité ! Vous avez réussi votre jet. Vous sautez de plateforme en plateforme et atteignez les escaliers.")
                                
        elif type_de == "force":
                print(score)
                # Vérifier les conditions
                if classe == "barbare":
                        if score > 10:
                                dispatcher.utter_message(text="Grace à votre force vous infligez 3 dégats de plus.")
                                enemy_hp = tracker.get_slot("enemy_hp")
                                return [SlotSet("enemy_hp", enemy_hp-3)]
                        else:
                                dispatcher.utter_message(text="Toute cette aventure vous a fatigué...")
                elif classe in ["rodeur", "occultiste"]:
                        if score < 17:
                                dispatcher.utter_message(text="Toute cette aventure vous a fatigué...")
                        else:
                                dispatcher.utter_message(text="Grace à votre force vous infligez 2 dégats de plus.")
                                enemy_hp = tracker.get_slot("enemy_hp")
                                return [SlotSet("enemy_hp", enemy_hp-2)]
		    
        else:
            dispatcher.utter_message(text="Je ne connais pas cette compétence.")
        
        return []
