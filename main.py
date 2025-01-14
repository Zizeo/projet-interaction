import requests
from bs4 import BeautifulSoup
import sys
import pygame
from io import BytesIO

from gtts import gTTS
import speech_recognition as sr

import threading

scene = -1
classe_personnage = 2
pv = 0
# (numero de l'image, x, y,sizex,sizey)
list_objet = []
# (string, x, y, sizex, sizey)
list_object_scrapper = []
text_scene = "Bonjour"
text_utilisateur = ""
busy = False
speak_text = False

running_principal = True

########## action

def change_to_second(Action):
    global agent_scenario
    global agent_principal_port

    agent_principal_port = 5006

    return []

def close_all_rasa_model():
   global running
   global running_principal

   running = False
   running_principal = False


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
    global list_objet
    global scene
    global classe_personnage
    
    text_scene = text

    #busy = True
    #tts = gTTS(text=text_scene, lang='fr', slow=False)

    #audio_data = BytesIO()
    
    
    #tts.write_to_fp(audio_data)
    #audio_data.seek(0)

    #pygame.mixer.music.load(audio_data,"mp3")
    #pygame.mixer.music.play()
    #busy = False
    
    url = "http://localhost:"+str(agent_principal_port)+"/conversations/user/tracker"

    response = requests.get(url)
    
    if response.status_code == 200:
        slots = response.json()['slots']
        print(slots)
        scene = slots["current_room"]
        pv = slots["player_hp"]
        classe = slots["class"]
        mort_scene_zero = 0 #slots["mort_zero"]
        being_in_fight = 0 #slots["being_in_fight"]
    else:
        scene = -1
        pv = 12
        classe = 1
        mort_scene_zero = 0
        being_in_fight = 1

    print(scene)

    if classe == "rodeur":
        classe_personnage = 0
    elif classe == "barbare":
        classe_personnage = 1
    elif classe == "occultiste":
        classe_personnage = 2

    list_objet = []
    list_object_scrapper = []

    if scene == 0:
        if mort_scene_zero == 2:
            list_objet.append((3,400,200,400,400))
        else:
            list_objet.append((2,400,200,400,400))

        if mort_scene_zero == 1:
            list_objet.append((11,400,400,200,200))
        else:
            list_objet.append((1,400,400,200,200))
        
        list_objet.append((8+classe_personnage,150,400,300,400))

    elif scene == 1:
        print("here")
        if being_in_fight == 2:
            list_objet.append((4,400,200,400,400))
        elif being_in_fight == 1:
            list_objet.append((5,400,200,400,400))

        list_objet.append((8+classe_personnage,150,400,300,400))

    elif scene == 2:
        list_objet.append((7,350,500,100,100))

        if print_papier == 1:
             list_objet.append((6,400,700,50,50))


        list_objet.append((8+classe_personnage,150,500,300,400))

    elif scene == 3 or scene == 4 or scene == 6:
        list_objet.append((8+classe_personnage,150,500,300,400))
    elif scene == 5:
        if mort_garde == 1:
            list_objet.append((4,400,400,200,200))
        elif mort_garde == 0:
            list_objet.append((5,400,400,200,200))

        list_objet.append((8+classe_personnage,150,500,300,400))

    '''
    with open('./personnage.json','r',encoding='utf-8') as fichier:
        donnees = json.load(fichier)

        for i,j in enumerate(donnees["equipement"]):
            list_object_scrapper.append((j,50+i*50,200,50,50))
   '''

def change_text_utilisateur(text):
    global text_utilisateur
    global scene
    global pv
    global classe_personnage
    global speak_text

    if text == "":
        return

    text_utilisateur = text
    
    payload = {
    	"sender":"user",
    	"message":text_utilisateur
    }
    
    header = {
    	"Content-Type":"application/json"
    }
    
    response = requests.post("http://localhost:"+str(agent_principal_port)+"/webhooks/rest/webhook",json=payload,headers=header)
    
    data = response.json()[0]["text"]

    change_text_scene(data)

def listen_user():
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=2)
        
        while True:
            if busy == False:
                try:
                    audio = recognizer.listen(source, timeout=5)
                    text_second = recognizer.recognize_google(audio, language="fr-FR")
                    change_text_utilisateur(text_second)
                    speak_text = True
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
    global classe_personnage
    global pv
    global speak_text
    
    list_salle = ["./image/dungeon.png","./image/dungeon_trap.png","./image/entree.png","./image/foret.png","./image/mine.png","./image/plaine.png","./image/taverne.png"]
    list_objet_path = ["./image/chat_joyeux.png", #0
                       "./image/chat_mefiant.png", #1
                       "./image/dragon.png", #2
                       "./image/dragon_dead.png", #3
                       "./image/garde.png", #4
                       "./image/garde_dead.png", #5
                       "./image/papier.png", #6
                       "./image/cadenas.png", #7
                       "./image/rodeur_jeu.png", #8
                       "./image/barbare_jeu.png", #9
                       "./image/occultiste_jeu.png"] #10
    list_classe_personnage = ["./image/rodeur.png","./image/barbare.png","./image/occutilste.png"]

    list_objet_path_loaded = []
    list_avatar_path_loaded = []
    list_objet_scrapper_loaded = {}

    for i in list_objet_path:
        list_objet_path_loaded.append(pygame.image.load(i))
    list_objet_path_loaded.append(pygame.transform.flip(list_objet_path_loaded[1], False, True))

    for j in list_object_scrapper:
        if j[0] not in list_objet_scrapper_loaded.keys():
            list_objet_scrapper_loaded[j[0]] = scrape_image(j[0])
    
    for i in list_classe_personnage:
        list_avatar_path_loaded.append(pygame.image.load(i))

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
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    active = not active
            elif event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        change_text_utilisateur(text)
                        text = ""
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        text += event.unicode
                        
        
        if speak_text == True:
           text = text_utilisateur
           speak_text = False
        
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

        screen.blit(pygame.transform.smoothscale(list_avatar_path_loaded[classe_personnage],(100,100)), (50, 50))

        health_text = font.render(f"Pv: {pv}", True, (255, 255, 255))
        screen.blit(health_text,(50,160))

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

    agent_principal_port = 5005

    while running_principal:
        #listen_user()
        pass

