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
import json
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


class ActionCombatTurn(Action):
    """
    Action pour gérer un tour de combat.

    Cette action lit les slots `player_hp`, `enemy_hp`, `player_action` et `combat_state`.
    En fonction de la valeur de `player_action`, elle met à jour les slots `player_hp` et `enemy_hp`.
    Si la valeur de `combat_state` est "started", elle met cette valeur à "ongoing".
    Si le combat est terminé (i.e. si l'un des deux personnages a 0 point de vie ou moins), elle met la valeur de `combat_state` à "ended".
    simplifié pour terminer dans les temps.
    """

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
            FollowupAction("action_player_choice"),
        ]


class ActionCombatStart(Action):
    """
    Démarre le combat.

    Fait choisir au joueur ce qu'il fait au premier tour.
    assigne les points de vie aux personnages.
    Met à jour le slot `combat_state` à "started".
    """

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
        if enemy_hp <= 0:
            enemy_hp = 12
        dispatcher.utter_message(
            text=f"Le combat commence ! Vous avez {player_hp} points de vie. L'ennemi a {enemy_hp} points de vie."
        )
        return [
            SlotSet("combat_state", "ongoing"),
            SlotSet("enemy_hp", enemy_hp),
            SlotSet("player_hp", player_hp),
            SlotSet("player_action", None),
            SlotSet("being_in_fight", 1),
            FollowupAction("action_player_choice"),
        ]


class ActionCombatEnd(Action):
    """
    Action pour terminer le combat.

    Selon l'état du combat, renvoie un message de victoire, défaite ou fuite.
    Met à jour le slot `combat_state` à "ended".
    """

    def name(self) -> str:
        return "action_combat_end"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ):
        state = tracker.get_slot("combat_state")
        room = tracker.get_slot("current_room")
        if state == "ongoing":
            dispatcher.utter_message(text="Le combat est toujours en cours.")
            return []
        elif state == "victory":
            dispatcher.utter_message(response="utter_victory")
            if room == 1:
                dispatcher.utter_message(response="utter_step1_success")
            if room == 3:
                dispatcher.utter_message(response="utter_step3_success")
            if room == 4:
                dispatcher.utter_message(response="utter_step4_sauver_chat_succes")
        elif state == "defeat":
            dispatcher.utter_message(response="utter_defeat")
            if room == 1:
                dispatcher.utter_message(response="utter_step1_fail")
            if room == 3:
                dispatcher.utter_message(response="utter_step3_fail")
            if room == 4:
                dispatcher.utter_message(response="utter_step4_sauver_chat_echec")

        elif state == "fled":
            dispatcher.utter_message(text="Vous avez fuit le combat.")

        else:
            dispatcher.utter_message(text="Le combat est terminé.")

        return [
            SlotSet("combat_state", "ended"),
            SlotSet("being_in_fight", 0),
            FollowupAction("action_change_room"),
        ]


class ActionPlayerChoice(Action):
    """
    Demande au joueur ce qu'il fait pendant le combat.
    Vide le slot player_action pour enlever l'action du tour precedent.
    """

    def name(self) -> str:
        return "action_player_choice"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ):
        player_action = tracker.get_slot("player_action")
        # if player_action is None:
        dispatcher.utter_message(
            text="Veuillez choisir une action.(attaquer, utiliser un item, utiliser un sort ou fuir)"
        )
        # return [[SlotSet("player_action", None)]]
        return [SlotSet("player_action", None)]


class ActionSetPlayerAction(Action):
    """
    Enregistre l'action du joueur pendant le combat.
    Met à jour le slot player_action avec l'action du joueur en checkant le dernier message de l'utilisateur.
    Se place après ActionPlayerChoice.
    """

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


class ActionSkillCheck(Action):
    """
    Vérifie si le joueur a réussi son test de compétence.
    Demande le score de compétence actuel et le compare au score aléatoire du dé.
    Si le score du dé est supérieur au score de compétence, le test est réussi.
    Sinon, le test est échoué.
    Met à jour le slot skill_check_result avec le résultat du test.

    N'a pas été utilisé par manque de temps.
    """

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


class ValidateCombatForm(FormValidationAction):
    """
    Valide le formulaire pour le combat.
    Vérifie si le combat est terminé.
    Si oui, met le slot "combat_state" à "ended".
    Sinon, laisse le slot "combat_state" à None.
    Permet du boucler sur le combat un nombre indéfinie de fois.
    """

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


class ActionChangeRoom(FormValidationAction):
    """
    Action pour changer de salle.

    Récupère la salle actuelle via le slot "current_room" et l'incrémente de 1.
    Met à jour le slot "current_room" pour passer à la salle suivante.
    N'a pas d'effet de bord.

    N'a pas été utilisé par manque de temps.
    """

    def name(self) -> str:
        return "action_change_room"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ):
        # Récupère la salle actuelle via le slot "current_room".
        room = tracker.get_slot("current_room")

        # Met à jour le slot "current_room" pour passer à la salle suivante en incrémentant sa valeur de 1.
        return [SlotSet("current_room", room + 1)]


class ActionClassResponse(Action):
    """
    Action qui renvoie une réponse en fonction de la classe de personnage que le joueur a choisi.

    Récupère la classe du joueur via le slot "player_class" et l'utilise pour choisir une réponse appropriée.
    Utilise la fonction "class_response" pour générer une réponse en fonction de la classe du joueur.
    """

    def name(self) -> Text:
        return "action_class_response"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        # Récupère les slots et entités nécessaires pour la logique.
        classe = tracker.get_slot(
            "player_class"
        )  # Classe du joueur (occultiste, barbare, etc.).
        type_de = next(
            tracker.get_latest_entity_values("type_dé"), None
        )  # Type de compétence (intelligence, force, etc.).
        room = tracker.get_slot(
            "current_room"
        )  # Salle actuelle où se trouve le joueur.
        score = random.randint(
            1, 20
        )  # Génère un score aléatoire pour simuler un jet de dé.

        # Vérifie si le type de compétence est "intelligence".
        if type_de == "intelligence":
            if room != 2:
                # Si la salle n'est pas la salle 2, avertir que cette compétence n'est pas utile ici.
                dispatcher.utter_message(
                    text="Utiliser votre intelligence ici ne vous aidera pas."
                )
            else:
                # Gestion des conditions selon la classe du joueur.
                if classe == "occultiste":
                    if score > 10:
                        # Succès : l'occultiste crochette le cadenas et passe la porte.
                        dispatcher.utter_message(
                            text="Vous avez réussi votre jet. Vous crochetez le cadenas et passez la porte."
                        )
                        return [FollowupAction("action_change_room")]
                    else:
                        # Échec : l'occultiste n'arrive pas à crocheter le cadenas.
                        dispatcher.utter_message(
                            text="Vous n’arrivez pas à crocheter le cadenas, quel dommage! avez vous une autre idée ?"
                        )
                elif classe in ["barbare", "rodeur"]:
                    if score < 17:
                        # Échec : le barbare ou rodeur échoue au jet.
                        dispatcher.utter_message(
                            text="Vous n’arrivez pas à crocheter le cadenas, quel dommage! avez vous une autre idée ? "
                        )
                    else:
                        # Succès : crochetage réussi.
                        dispatcher.utter_message(
                            text="Vous avez réussi votre jet. Vous crochetez le cadenas et passez la porte."
                        )
                        return [FollowupAction("action_change_room")]

        # Vérifie si le type de compétence est "dexterité".
        elif type_de == "dexterité":
            if room != 3:
                # Si la salle n'est pas la salle 3, avertir que cette compétence n'est pas utile ici.
                dispatcher.utter_message(
                    text="Utiliser votre dextérité ici ne vous aidera pas."
                )
            else:
                # Gestion des conditions selon la classe.
                if classe == "rodeur":
                    if score > 10:
                        # Succès : le rodeur traverse les plateformes avec agilité.
                        dispatcher.utter_message(
                            text="Quel abilité ! Vous avez réussi votre jet. Vous sautez de plateforme en plateforme et atteignez les escaliers."
                        )
                    else:
                        # Échec : chute et perte de points de vie.
                        dispatcher.utter_message(
                            text="Vous tentez de passer les plateformes, mais vous trebuchez et vous tordez la cheville. Vous perdez 2 points de vie."
                        )
                        dispatcher.utter_message(
                            text="Essoufflé, vous atteignez le sommet des escaliers. Mais devant la porte de la tour, un autre garde se dresse, prêt à vous barrer la route. Vous sentez la fatigue peser sur vos épaules, mais vous ne pouvez pas abandonner maintenant."
                        )
                        hp = tracker.get_slot("player_hp")
                        return [SlotSet("player_hp", hp - 2)]
                elif classe in ["barbare", "occultiste"]:
                    if score < 17:
                        # Échec : perte de 3 points de vie.
                        dispatcher.utter_message(
                            text="Vous tentez de passer les plateformes, mais vous trebuchez et vous tordez la cheville. Vous perdez 3 points de vie."
                        )
                        dispatcher.utter_message(
                            text="Essoufflé, vous atteignez le sommet des escaliers. Mais devant la porte de la tour, un autre garde se dresse, prêt à vous barrer la route. Vous sentez la fatigue peser sur vos épaules, mais vous ne pouvez pas abandonner maintenant."
                        )
                        hp = tracker.get_slot("player_hp")
                        return [SlotSet("player_hp", hp - 3)]
                    else:
                        # Succès : le joueur atteint les escaliers.
                        dispatcher.utter_message(
                            text="Quel abilité ! Vous avez réussi votre jet. Vous sautez de plateforme en plateforme et atteignez les escaliers."
                        )
                dispatcher.utter_message(
                    text="Essoufflé, vous atteignez le sommet des escaliers. Mais devant la porte de la tour, un autre garde se dresse, prêt à vous barrer la route. Vous sentez la fatigue peser sur vos épaules, mais vous ne pouvez pas abandonner maintenant."
                )

        # Vérifie si le type de compétence est "force".
        elif type_de == "force":
            if room == 2:
                # Si la salle est la salle 2, avertir que cette compétence n'est pas utile ici.
                dispatcher.utter_message(
                    text="Utiliser votre force ici ne vous aidera pas."
                )
            else:
                # Gestion des conditions selon la classe.
                if classe == "barbare":
                    if score > 10:
                        # Succès : inflige des dégâts supplémentaires.
                        dispatcher.utter_message(
                            text="Grace à votre force vous infligez 3 dégats de plus."
                        )
                        enemy_hp = tracker.get_slot("enemy_hp")
                        return [SlotSet("enemy_hp", enemy_hp - 3)]
                    else:
                        # Échec : pas assez de force.
                        dispatcher.utter_message(
                            text="Vous n'avez pas frappé assez fort..."
                        )
                elif classe in ["rodeur", "occultiste"]:
                    if score < 17:
                        # Échec : pas assez de force.
                        dispatcher.utter_message(
                            text="Vous n'avez pas frappé assez fort..."
                        )
                    else:
                        # Succès : inflige des dégâts supplémentaires.
                        dispatcher.utter_message(
                            text="Grace à votre force vous infligez 2 dégats de plus."
                        )
                        enemy_hp = tracker.get_slot("enemy_hp")
                        return [SlotSet("enemy_hp", enemy_hp - 2)]

        else:
            # Cas où le type de compétence est inconnu.
            dispatcher.utter_message(text="Je ne connais pas cette compétence.")

        return []  # Retourne une liste vide par défaut.


class ActionHelpingPlayer(Action):
    """
    Cette classe permet de fournir des informations supplémentaires au joueur
    en fonction de sa classe et de la salle dans laquelle il se trouve.
    """

    def name(self) -> Text:
        return "action_helping_player"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ):
        room = tracker.get_slot("current_room")
        if room == 0.0:
            classe = tracker.get_slot("class")
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
        return []


class ActionStartGame(Action):
    """
    Action pour lancer le jeu.

    Cette action est appelée lorsque l'utilisateur tape "commencer" ou "lancer".
    Elle envoie un message de bienvenue et met à jour le slot "current_room" pour indiquer que le joueur est dans la salle 1.
    """

    def name(self) -> Text:
        return "action_start_game"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ):
        dispatcher.utter_message(text="Bienvenue dans Donjons et Dragons")
        with open("data.json") as f:
            data = json.load(f)
            slot_values = data["slot_values"]
            return [SlotSet(slot, value) for slot, value in slot_values.items()]


class ActionPrintStatuts(Action):
    """
    Action qui envoie le statut actuel du joueur (PV, equipement, etc.).
    """

    def name(self) -> Text:
        return "action_print_statuts"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ):
        player_hp = tracker.get_slot("player_hp")
        player_force = tracker.get_slot("player_force")
        player_intelligence = tracker.get_slot("player_intelligence")
        player_agility = tracker.get_slot("player_agility")
        player_class = tracker.get_slot("class")
        equipement = tracker.get_slot("equipement")
        equipement_description = tracker.get_slot("equipement_description")
        equipement_degat = tracker.get_slot("equipement_degat")
        dispatcher.utter_message(
            text=f"Voici vos statistiques :\n"
            f"- Vous avez {player_hp} points de vie\n"
            f"- vous avez {player_force} en force\n"
            f"- vous avez {player_intelligence} en intelligence\n"
            f"- vous avez {player_agility} en dexterité\n"
            f"- Vous avez {player_class} comme classe\n"
            f"- Vous avez {equipement} comme equipement\n"
            f"- L'equipement {equipement} vous inflige {equipement_degat} de dommages\n"
            f"- L'equipement {equipement} vous donne {equipement_description}"
        )
