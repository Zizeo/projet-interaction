import requests
from bs4 import BeautifulSoup
import sys
import pygame
from io import BytesIO

from gtts import gTTS
import speech_recognition as sr

import threading

from rasa.core.run import serve_application

scene = 0
# (numero de l'image, x, y,sizex,sizey)
list_objet = []
# (string, x, y, sizex, sizey)
list_object_scrapper = []
text_scene = "Bonjour"
text_utilisateur = ""
busy = False

running_principal = True

agent_create_personnage = ""
agent_scenario = ""

agent_principal = ""

########## action


class ActionPassageSecondRasa(Action):

    def name(self) -> Text:
        return "action_passage_second_rasa"

    def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        global agent_scenario
        global agent_principal

        agent_principal = agent_scenario

        requests.post("http://localhost:5005/shutdown")

        return []

class ActionFinProgramme(Action):
    def name(self) -> Text:
        return "action_fin_programme"

    def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        global running
        global running_principal

        running = False

        requests.post("http://localhost:5005/shutdown")
        requests.post("http://localhost:5006/shutdown")

        running_principal = False

        return []



###########

def draw_text(surface, text, font, color, x, y, max_width):
    words = text.split(' ')  
    lines = []
    current_line = []

    for word in words:
        test_line = ' '.join(current_line + [word])
        text_width, _ = font.size(test_line)
        if text_width <= max_width:
            current_line.append(word)
        else:
            lines.append(' '.join(current_line)) 
            current_line = [word] 

    if current_line:
        lines.append(' '.join(current_line))

    line_height = font.size("Tg")[1]
    for i, line in enumerate(lines):
        line_surface = font.render(line, True, color)
        surface.blit(line_surface,(x,y+i*50)) 

def scrape_image(query):
    search_url = f"https://opengameart.org/art-search?keys={query}"
    headers = {"User-Agent":"Mozilla/5.0"}
    response = requests.get(search_url,headers=headers)
    if response.status_code != 200:
        print("Echec requete")
        return

    soup = BeautifulSoup(response.text, 'html.parser')

    img_url = soup.find_all('img', {'alt': 'Preview'})[0]
    img_url = img_url['src']

    if not img_url.startswith('http'):
        img_url = requests.compat.url(search_url, img_url)

    img_data = requests.get(img_url).content
    image_surface = pygame.image.load(BytesIO(img_data))

    return image_surface

def change_text_scene(text):
    global text_scene
    global busy
    
    text_scene = text

    busy = True
    tts = gTTS(text=text_scene, lang='fr', slow=False)

    audio_data = BytesIO()
    tts.write_to_fp(audio_data)
    audio_data.seek(0)

    pygame.mixer.music.load(audio_data,"mp3")
    pygame.mixer.music.play()
    busy = False

def change_text_utilisateur(text):
    global text_utilisateur
    global scene

    text_utilisateur = text
    response = agent_principal.handle_text(text_utilisateur) #si bug passer en asynchrone

    tracker = agent.tracker_strore.retrieve("default")
    salle = tracker.get_slot("current_room")

    change_text_scene(response)

def listen_user():
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=2)
        
        while True:
            if busy == False:
                try:
                    audio = recognizer.listen(source, timeout=5)
                    text = recognizer.recognize_google(audio, language="fr-FR")
                    print(text)
                    change_text_utilisateur(text)
                except sr.UnknownValueError:
                    print("Je n'ai pas compris ce que vous avez dit.")
                except sr.RequestError as e:
                    print(f"Erreur lors de la requête au service de reconnaissance vocale : {e}")
                except sr.exceptions.WaitTimeoutError as e:
                    print("Parle un jour non")                    

def windows():
    global scene
    global text_scene
    global text_utilisateur
    global list_objet
    global list_object_scrapper
    
    list_salle = ["./image/dungeon.png","./image/dungeon_trap.png","./image/entree.png","./image/foret.png","./image/mine.png","./image/plaine.png","./image/taverne.png"]
    list_objet_path = ["./image/chat_joyeux.png","./image/chat_mefiant.png","./image/dragon.png","./image/dragon_dead.png","./image/garde.png","./image/garde_dead.png","./image/papier.png"]

    list_objet_path_loaded = []
    list_objet_scrapper_loaded = {}

    for i in list_objet_path:
        list_objet_path_loaded.append(pygame.image.load(i))

    for j in list_object_scrapper:
        if j[0] not in list_objet_scrapper_loaded.keys():
            list_objet_scrapper_loaded[j[0]] = scrape_image(j[0])
    
    pygame.init()

    screen = pygame.display.set_mode((1500,800))
    font = pygame.font.SysFont('Courier New', 24)
    input_box = pygame.Rect(810,500,680,250)
    color = (20,20,20)
    active = True
    text = ""

    running = True

    background_picture_loaded = []
    for i in list_salle:
      image = pygame.image.load(i).convert()
      background_picture_loaded.append(pygame.transform.smoothscale(image, (800, 800)))      

    while running:
        clavier = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    active = not active
            elif event.type == pygame.KEYDOWN:
                clavier = True
                if active:
                    if event.key == pygame.K_RETURN:
                        change_text_utilisateur(text)
                        text = ""
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        text += event.unicode
                        
        if clavier == False and text != text_utilisateur:
            text = text_utilisateur
        
        screen.fill((0,0,0))

        screen.blit(background_picture_loaded[scene], (0,0))

        for i in list_objet:
            if len(i)==5:
                screen.blit(pygame.transform.smoothscale(list_objet_path_loaded[i[0]],(i[3],i[4])), (i[1], i[2]))
            else:
                screen.blit(list_objet_path_loaded[i[0]], (i[1], i[2]))

        for i in list_object_scrapper:
            if len(i)==5:
                screen.blit(pygame.transform.smoothscale(list_objet_scrapper_loaded[i[0]],(i[3],i[4])), (i[1], i[2]))
            else:
                screen.blit(list_objet_scrapper_loaded[i[0]], (i[1], i[2]))

        color = (60,60,60) if active else (20,20,20)
        pygame.draw.rect(screen,color,input_box,2)

        draw_text(screen,text,font,(255,255,255),815,505,670)
        
        text_surface = draw_text(screen,text_scene,font,(255,255,255),800,20,700)
        
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__=="__main__":
    thread1 = threading.Thread(target=windows)
    thread1.start()

    agent_create_personnage = Agent.load("modelA")
    agent_scenario = Agent.load("modelB")

    agent_principal = agent_scenario

    serve_application(agent_create_personnage, http_port=5005)
    serve_application(agent_scenario,http_port=5006)

    while running_principal:
        listen_user()
