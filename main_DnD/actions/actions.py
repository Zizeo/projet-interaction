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
            damage = random.randint(10, 30)
            enemy_hp -= damage
            dispatcher.utter_message(
                text=f"Vous attaquez et infligez {damage} points de dégâts à l'ennemi."
            )
        elif player_action == "use_item":
            heal = random.randint(15, 25)
            player_hp += heal
            dispatcher.utter_message(
                text=f"Vous utilisez une potion et récupérez {heal} points de vie."
            )
        elif player_action == "flee":
            dispatcher.utter_message(text="Vous fuyez le combat !")
            return [SlotSet("combat_state", "fled")]

        if enemy_hp <= 0:
            dispatcher.utter_message(response="utter_victory")
            return [SlotSet("enemy_hp", 0), SlotSet("combat_state", "victory")]

        # Action de l'ennemi
        enemy_action = random.choices(["attack", "wait"], weights=[0.7, 0.3])[0]
        if enemy_action == "attack":
            damage = random.randint(10, 25)
            player_hp -= damage
            dispatcher.utter_message(
                text=f"L'ennemi attaque et inflige {damage} points de dégâts."
            )
        else:
            dispatcher.utter_message(text="L'ennemi observe vos mouvements.")

        # Vérifier si le joueur est vaincu
        if player_hp <= 0:
            dispatcher.utter_message(response="utter_defeat")
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
            dispatcher.utter_message(text="Vous avez vaincu l'ennemi !")
            return [SlotSet("combat_state", "ended")]
        elif state == "defeat":
            dispatcher.utter_message(text="Vous avez perdu contre l'ennemi.")
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
