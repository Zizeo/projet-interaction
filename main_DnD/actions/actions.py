# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormValidationAction
from rasa_sdk.events import FollowupAction
# git
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


from rasa_sdk.events import SlotSet

import random

from ... import main

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

        if combat_state == "ended":
            dispatcher.utter_message(text="Le combat est déjà terminé.")
            return []

        # Action du joueur
        if player_action == "attack":
            damage = random.randint(3, 5)
            enemy_hp -= damage
            dispatcher.utter_message(
                text=f"Vous attaquez et infligez {damage} points de dégâts à l'ennemi. Il lui reste {enemy_hp} points de vie."
            )
        elif player_action == "use_item":
            heal = random.randint(3, 5)
            player_hp += heal
            dispatcher.utter_message(
                text=f"Vous utilisez une potion et récupérez {heal} points de vie. Vous avez maintenant {player_hp} points de vie."
            )
        elif player_action == "spell":
            damage = random.randint(4, 7)
            enemy_hp -= damage
            dispatcher.utter_message(
                text=f"Vous lancez un sort et infligez {damage} points de dégâts à l'ennemi. Il lui reste {enemy_hp} points de vie."
            )
        elif player_action == "flee":
            return [
                SlotSet("combat_state", "fled"),
                FollowupAction("action_combat_end"),
            ]

        if enemy_hp <= 0:
            return [
                SlotSet("enemy_hp", 0),
                SlotSet("combat_state", "victory"),
                FollowupAction("action_combat_end"),
            ]

        # Action de l'ennemi
        enemy_action = random.choices(["attack", "wait"], weights=[0.8, 0.2])[0]
        if enemy_action == "attack":
            damage = random.randint(1, 4)
            player_hp -= damage
            dispatcher.utter_message(
                text=f"L'ennemi attaque et inflige {damage} points de dégâts. Il vous reste {player_hp} points de vie."
            )
        else:
            dispatcher.utter_message(text="L'ennemi attaque mais rate.")

        # Vérifier si le joueur est vaincu
        if player_hp <= 0:
            return [
                SlotSet("player_hp", 0),
                SlotSet("combat_state", "defeat"),
                FollowupAction("action_combat_end"),
            ]

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
        return [
            SlotSet("combat_state", "ongoing"),
            SlotSet("enemy_hp", 12),
            SlotSet("player_hp", 12),
            SlotSet("player_action", None),
            SlotSet("being_in_fight", 1),
        ]


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

        elif state == "defeat":
            dispatcher.utter_message(response="utter_defeat")

        elif state == "fled":
            dispatcher.utter_message(text="Vous avez fuis le combat.")

        else:
            dispatcher.utter_message(text="Le combat est terminé.")

        return [SlotSet("combat_state", "ended"), SlotSet("being_in_fight", 0)]


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
        print(player_intent)
        # Définir le slot `player_action` en fonction de l'intent
        return [SlotSet("player_action", player_intent)]


class ValidateCombatForm(FormValidationAction):
    def name(self) -> str:
        return "validate_combat_form"

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


class ActionClassResponse(Action):
    def name(self) -> Text:
        return "action_class_response"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        # Récupérer les valeurs des slots
        classe = tracker.get_slot("class")
        type_de = next(tracker.get_latest_entity_values("type_dé"), None)

        score = random.randint(1, 20)
        print(type_de)
        if type_de == "intelligence":
            print(score)
            # Vérifier les conditions
            if classe == "occultiste":
                if score > 10:
                    dispatcher.utter_message(
                        text="Vous avez réussi votre jet. Vous crochetez le cadenas et passez la porte."
                    )
                else:
                    dispatcher.utter_message(
                        text="Vous n’arrivez pas à crocheter le cadenas, quel dommage! avez vous une autre idée ?"
                    )
            elif classe in ["barbare", "rodeur"]:
                if score < 17:
                    dispatcher.utter_message(
                        text="Vous n’arrivez pas à crocheter le cadenas, quel dommage! avez vous une autre idée ? "
                    )
                else:
                    dispatcher.utter_message(
                        text="Vous avez réussi votre jet. Vous crochetez le cadenas et passez la porte."
                    )
        elif type_de == "dexterité":
            print(score)
            # Vérifier les conditions
            if classe == "rodeur":
                if score > 10:
                    dispatcher.utter_message(
                        text="Quel abilité ! Vous avez réussi votre jet. Vous sautez de plateforme en plateforme et atteignez les escaliers."
                    )
                else:
                    dispatcher.utter_message(
                        text="Vous tentez de passer les plateformes, mais vous trebuchez et vous tordez la cheville. Vous perdez 2 points de vie."
                    )
                    hp = tracker.get_slot("player_hp")
                    return [SlotSet("player_hp", hp - 2)]
            elif classe in ["barbare", "occultiste"]:
                if score < 17:
                    dispatcher.utter_message(
                        text="Vous tentez de passer les plateformes, mais vous trebuchez et vous tordez la cheville. Vous perdez 3 points de vie."
                    )
                    hp = tracker.get_slot("player_hp")
                    return [SlotSet("player_hp", hp - 3)]
                else:
                    dispatcher.utter_message(
                        text="Quel abilité ! Vous avez réussi votre jet. Vous sautez de plateforme en plateforme et atteignez les escaliers."
                    )

        elif type_de == "force":
            print(score)
            # Vérifier les conditions
            if classe == "barbare":
                if score > 10:
                    dispatcher.utter_message(
                        text="Grace à votre force vous infligez 3 dégats de plus."
                    )
                    enemy_hp = tracker.get_slot("enemy_hp")
                    return [SlotSet("enemy_hp", enemy_hp - 3)]
                else:
                    dispatcher.utter_message(
                        text="Toute cette aventure vous a fatigué..."
                    )
            elif classe in ["rodeur", "occultiste"]:
                if score < 17:
                    dispatcher.utter_message(
                        text="Toute cette aventure vous a fatigué..."
                    )
                else:
                    dispatcher.utter_message(
                        text="Grace à votre force vous infligez 2 dégats de plus."
                    )
                    enemy_hp = tracker.get_slot("enemy_hp")
                    return [SlotSet("enemy_hp", enemy_hp - 2)]

        else:
            dispatcher.utter_message(text="Je ne connais pas cette compétence.")

        return []


class ActionHelpingPlayer(Action):
    def name(self) -> Text:
        return "action_helping_player"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ):
        room = tracker.get_slot("current_room")
        print(room)
        if room == 0.0:
            classe = tracker.get_slot("class")
            print(classe)
            if classe == "rodeur":
                dispatcher.utter_message(
                    text="Vous vous trouvez dans la salle 0. Vous êtes un maître de la nature, armé de votre arc et de votre sens de l'orientation. Vous commencez dans la forêt enchantée de “Lórien”. Votre chat, habituellement à vos côtés, est introuvable. Déterminé, vous quittez la forêt pour le chercher."
                )
            elif classe == "occultiste":
                dispatcher.utter_message(
                    text="Vous vous trouvez dans la salle 0. Maître des arcanes, vous explorez les ombres et les secrets. Vous commencez dans une cave sous terre, perdu dans vos recherches mystiques. En sortant, vous apprenez que votre chat a été vu près d’un donjon. "
                )
            elif classe == "barbare":
                dispatcher.utter_message(
                    text="Vous vous trouvez dans la salle 0. Puissant et impétueux, votre force brute vous mène souvent au succès. Vous commencez dans une taverne bruyante et enfumée, entouré de rires gras et de chopes de bière. Alors que vous festoyez, un homme entre en trombe et vous informe que votre chat a été vu près d’une tour. Sans attendre, vous saisissez votre arme et partez. "
                )
        elif room == 1.0:
            print("1")
            dispatcher.utter_message(
                text="Vous vous trouvez dans la salle 1. Vous arrivez dans une vaste plaine. Devant vous, un chemin mène à un imposant donjon. En levant les yeux, vous apercevez votre chat, sa petite silhouette se détache près d'une fenêtre. Mais horreur… une queue de dragon se balance nonchalamment à ses côtés. Près de l'entrée, un garde imposant vous barre le passage. Vous avez le choix de le combattre, de tenter la diplomatie ou de fuir. "
            )
        elif room == 2.0:
            dispatcher.utter_message(
                text="Vous vous trouvez dans la salle 2. Devant vous se dresse une lourde porte ornée de sculptures mystérieuses et enlacée de lianes. Vous remarquez cependant qu’il vous est impossible d'escalader la tour avec les lianes. Vous remarquez un cadenas complexe comportant quatre boules de couleur. Pour avancer, vous devez déverrouiller ce cadenas. "
            )
        elif room == 3.0:
            being_in_fight = tracker.get_slot("being_in_fight")
            print(being_in_fight)
            if being_in_fight == 0.0:
                dispatcher.utter_message(
                    text="Vous vous trouvez dans la salle 3. Vous entrez dans une vaste salle. Le plafond est haut, et au fond, un escalier mène à l’étage supérieur. Mais alors que vous vous avancez, le sol commence à trembler violemment. Une grande partie s’effondre, ne laissant que quelques plateformes éparses pour traverser."
                )
            elif being_in_fight == 1.0:
                dispatcher.utter_message(
                    text="Vous vous trouvez dans la salle 3. Vous pouvez enfin pousser la porte de la tour du donjon."
                )
            elif being_in_fight == 2.0:
                dispatcher.utter_message(
                    text="Vous vous trouvez dans la salle 3. Essoufflé, vous atteignez le sommet des escaliers. Mais devant la porte de la tour, un autre garde se dresse, prêt à vous barrer la route. Vous sentez la fatigue peser sur vos épaules, mais vous ne pouvez pas abandonner maintenant. "
                )
        elif room == 4.0:
            dispatcher.utter_message(
                text="Vous vous trouvez dans la salle 4. Arrivé dans le donjon, vous tombez nez à nez avec votre chat et un dragon. Ce dernier est hypnotisant et majestueux, et son regard vous envoûte. Une confusion profonde s’empare de vous : pourquoi êtes-vous là ? Est-ce pour sauver un chat ? Protéger ce dragon ? Ou simplement fuir ? Vous devez prendre une décision."
            )
        print("fin")
        return []
