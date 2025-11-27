#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para preencher traduções reais do Capítulo 1
Execute: python tools/preencher_traducao_ch1.py
"""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from config import DIR_PROJETO

CAMINHO_LOCALES = os.path.join(DIR_PROJETO, "data", "locales")

# Traduções do Capítulo 1
TRADUCOES_CH1 = {
    "en": {
        "0_prologue": {
            "narrator": [
                "The city smells of old gasoline, street food, and burned dreams. Your car is part of it.",
                "You lost your job, lost your money. All that's left is a half-dead car and a name scribbled on a crumpled paper: CRANK.",
                "They say if anyone can make a dead engine roar again, it's him. They also say he's hell to deal with."
            ]
        },
        "1_crank_garage_intro": {
            "crank": [
                "...What the hell is this under the hood?",
                "I went to change the oil filter and found this stuck in the fuel line. Who built this engine, a bad internet tutorial?",
                "Okay. Let's pretend this is a car and not a mechanical homicide attempt. Why did you come here?"
            ],
            "choices": [
                "I want to race.",
                "I want money.",
                "I just want to get out of this life."
            ]
        },
        "1_crank_garage_after_choice": {
            "crank": [
                "Ambition I respect. Common sense... not so much.",
                "Down here you race in the mud. Higher up there are the mountains. Up top, Rex turns racing into a controlled show.",
                "But you're still at the 'remold tire and empty tank' level. Let's start right.",
                "You're going after an ogre named Boris, in the Rust Pit. We worked together at Iron Howl. Don't ask."
            ]
        },
        "2_mission_boris": {
            "crank": [
                "Tell him Crank sent you. He'll pretend he doesn't remember. He always does that."
            ],
            "narrator": [
                "New objective: find Boris in the Rust Pit."
            ]
        },
        "3_meet_boris": {
            "boris": [
                "Look what the toxic wind brought to my junkyard.",
                "You look like someone who thinks engines are magic. I like that. Stupid drivers are loyal customers."
            ],
            "choices": [
                "Crank sent me.",
                "I need parts."
            ]
        },
        "3_boris_crank_branch": {
            "boris": [
                "Crank, huh? Hahaha... so the old man is still breathing grease.",
                "At Iron Howl he built engines I still miss today. Until he decided that almost dying was 'irresponsible'.",
                "Here's the deal: I have ugly, cheap, and strong parts. Perfect for you."
            ]
        },
        "3_boris_no_crank_branch": {
            "boris": [
                "You didn't come here by accident. Nobody does.",
                "In the end, whoever pays calls the shots. I have ugly, cheap, and strong parts. Perfect for you."
            ]
        },
        "4_return_garage_upgrade": {
            "crank": [
                "I recognize that cheap junkyard smell. You really went to Boris.",
                "We raced together at Iron Howl. I built, he tried to kill the car on the track. A wall won the race.",
                "Show me the part. I'll install it. If this breaks in the middle of the straight, it's his fault, not mine."
            ]
        },
        "5_first_race_unlocked": {
            "crank": [
                "Done. The car is minimally acceptable so it won't fall apart at the start.",
                "That doesn't mean you'll win. It just means that if you lose, I can't blame the mechanics.",
                "Go to the training track. Beginner race. If you come back alive, we'll talk."
            ],
            "narrator": [
                "New race unlocked: Training Circuit."
            ]
        },
        "6_post_first_race_and_pixel": {
            "crank": [
                "You... won? Looks like you know the difference between accelerator and brake. Better than half the idiots.",
                "No trophy, but also no car broken in half. I've seen worse. Defeat is part of it."
            ]
        },
        "7_pixel_intro": {
            "pixel": [
                "Whoa! Calm down, it's not a virus. It's just me hacking into your panel a bit.",
                "Call me Pixel. I live in the wires and cameras of this city. And I'm watching you make a mess on the track.",
                "Up there, in the towers, they've already noticed you. Rex loves new people to test... or discard."
            ]
        }
    },
    "es": {
        "0_prologue": {
            "narrator": [
                "La ciudad huele a gasolina vieja, comida callejera y sueños quemados. Tu coche es parte de eso.",
                "Perdiste tu trabajo, perdiste tu dinero. Solo queda un coche medio muerto y un nombre garabateado en un papel arrugado: CRANK.",
                "Dicen que si alguien puede hacer rugir un motor muerto de nuevo, es él. También dicen que es un infierno de aguantar."
            ]
        },
        "1_crank_garage_intro": {
            "crank": [
                "...¿Qué diablos es esto debajo del capó?",
                "Fui a cambiar el filtro de aceite y encontré esto atascado en la línea de combustible. ¿Quién construyó este motor, un mal tutorial de internet?",
                "Bien. Vamos a fingir que esto es un coche y no un intento de homicidio mecánico. ¿Por qué viniste aquí?"
            ],
            "choices": [
                "Quiero correr.",
                "Quiero dinero.",
                "Solo quiero salir de esta vida."
            ]
        },
        "1_crank_garage_after_choice": {
            "crank": [
                "La ambición la respeto. El sentido común... no tanto.",
                "Aquí abajo corres en el barro. Más arriba están las montañas. Arriba, Rex convierte las carreras en un espectáculo controlado.",
                "Pero todavía estás en el nivel 'neumático recauchutado y tanque vacío'. Empecemos bien.",
                "Vas tras un ogro llamado Boris, en el Foso de Óxido. Trabajamos juntos en Iron Howl. No preguntes."
            ]
        },
        "2_mission_boris": {
            "crank": [
                "Dile que Crank te envió. Fingirá que no recuerda. Siempre hace eso."
            ],
            "narrator": [
                "Nuevo objetivo: encontrar a Boris en el Foso de Óxido."
            ]
        },
        "3_meet_boris": {
            "boris": [
                "Mira lo que el viento tóxico trajo a mi desguace.",
                "Tienes cara de quien piensa que los motores son magia. Me gusta eso. Los pilotos tontos son clientes fieles."
            ],
            "choices": [
                "Crank me envió.",
                "Necesito piezas."
            ]
        },
        "3_boris_crank_branch": {
            "boris": [
                "¿Crank? Jajaja... así que el viejo todavía respira grasa.",
                "En Iron Howl construía motores que todavía echo de menos. Hasta que decidió que casi morir era 'irresponsable'.",
                "Aquí está el trato: tengo piezas feas, baratas y fuertes. Perfectas para ti."
            ]
        },
        "3_boris_no_crank_branch": {
            "boris": [
                "No viniste aquí por accidente. Nadie lo hace.",
                "Al final, quien paga manda. Tengo piezas feas, baratas y fuertes. Perfectas para ti."
            ]
        },
        "4_return_garage_upgrade": {
            "crank": [
                "Reconozco ese olor a desguace barato. Realmente fuiste a Boris.",
                "Corrimos juntos en Iron Howl. Yo construía, él intentaba matar el coche en la pista. Un muro ganó la carrera.",
                "Muéstrame la pieza. La instalaré. Si esto se rompe en medio de la recta, es su culpa, no la mía."
            ]
        },
        "5_first_race_unlocked": {
            "crank": [
                "Listo. El coche es mínimamente aceptable para que no se desarme en la salida.",
                "Eso no significa que vayas a ganar. Solo significa que si pierdes, no puedo culpar a la mecánica.",
                "Ve a la pista de entrenamiento. Carrera de principiantes. Si vuelves vivo, hablamos."
            ],
            "narrator": [
                "Nueva carrera desbloqueada: Circuito de Entrenamiento."
            ]
        },
        "6_post_first_race_and_pixel": {
            "crank": [
                "¿Tú... ganaste? Parece que sabes diferenciar acelerador de freno. Mejor que la mitad de los idiotas.",
                "Sin trofeo, pero tampoco coche partido por la mitad. He visto peor. La derrota es parte de esto."
            ]
        },
        "7_pixel_intro": {
            "pixel": [
                "¡Vaya! Tranquilo, no es un virus. Solo soy yo hackeando un poco tu panel.",
                "Llámame Pixel. Vivo en los cables y cámaras de esta ciudad. Y estoy viendo que haces un desastre en la pista.",
                "Allá arriba, en las torres, ya te han notado. A Rex le encanta la gente nueva para probar... o descartar."
            ]
        }
    },
    "fr": {
        "0_prologue": {
            "narrator": [
                "La ville sent l'essence vieille, la friture de rue et les rêves brûlés. Votre voiture en fait partie.",
                "Vous avez perdu votre boulot, perdu votre argent. Il ne reste qu'une voiture à moitié morte et un nom griffonné sur un papier froissé : CRANK.",
                "On dit que si quelqu'un peut faire rugir un moteur mort à nouveau, c'est lui. On dit aussi qu'il est un enfer à supporter."
            ]
        },
        "1_crank_garage_intro": {
            "crank": [
                "...Qu'est-ce que c'est que ça sous le capot ?",
                "Je suis allé changer le filtre à huile et j'ai trouvé ça coincé dans la conduite de carburant. Qui a construit ce moteur, un mauvais tutoriel internet ?",
                "D'accord. Faisons comme si c'était une voiture et pas une tentative d'homicide mécanique. Pourquoi êtes-vous venu ici ?"
            ],
            "choices": [
                "Je veux courir.",
                "Je veux de l'argent.",
                "Je veux juste sortir de cette vie."
            ]
        },
        "1_crank_garage_after_choice": {
            "crank": [
                "L'ambition, je la respecte. Le bon sens... pas tant que ça.",
                "Ici en bas, vous courez dans la boue. Plus haut, il y a les montagnes. Là-haut, Rex transforme la course en spectacle contrôlé.",
                "Mais vous êtes encore au niveau 'pneu remoulé et réservoir vide'. Commençons bien.",
                "Vous allez voir un ogre nommé Boris, dans le Fosse de Rouille. On a travaillé ensemble à Iron Howl. Ne demandez pas."
            ]
        },
        "2_mission_boris": {
            "crank": [
                "Dites-lui que Crank vous a envoyé. Il fera semblant de ne pas s'en souvenir. Il fait toujours ça."
            ],
            "narrator": [
                "Nouvel objectif : trouver Boris dans la Fosse de Rouille."
            ]
        },
        "3_meet_boris": {
            "boris": [
                "Regardez ce que le vent toxique a apporté à ma casse.",
                "Vous avez l'air de quelqu'un qui pense que les moteurs sont de la magie. J'aime ça. Les pilotes stupides sont des clients fidèles."
            ],
            "choices": [
                "Crank m'a envoyé.",
                "J'ai besoin de pièces."
            ]
        },
        "3_boris_crank_branch": {
            "boris": [
                "Crank, hein ? Hahaha... donc le vieux respire encore la graisse.",
                "À Iron Howl, il construisait des moteurs qui me manquent encore aujourd'hui. Jusqu'à ce qu'il décide que presque mourir était 'irresponsable'.",
                "Voici le marché : j'ai des pièces laides, bon marché et solides. Parfaites pour vous."
            ]
        },
        "3_boris_no_crank_branch": {
            "boris": [
                "Vous n'êtes pas venu ici par accident. Personne ne le fait.",
                "À la fin, celui qui paie commande. J'ai des pièces laides, bon marché et solides. Parfaites pour vous."
            ]
        },
        "4_return_garage_upgrade": {
            "crank": [
                "Je reconnais cette odeur de casse bon marché. Vous êtes vraiment allé voir Boris.",
                "On a couru ensemble à Iron Howl. Je construisais, il essayait de tuer la voiture sur la piste. Un mur a gagné la course.",
                "Montrez-moi la pièce. Je vais l'installer. Si ça casse au milieu de la ligne droite, c'est de sa faute, pas de la mienne."
            ]
        },
        "5_first_race_unlocked": {
            "crank": [
                "Fait. La voiture est minimalement acceptable pour ne pas se désintégrer au départ.",
                "Ça ne veut pas dire que vous allez gagner. Ça veut juste dire que si vous perdez, je ne peux pas blâmer la mécanique.",
                "Allez sur la piste d'entraînement. Course de débutants. Si vous revenez vivant, on parlera."
            ],
            "narrator": [
                "Nouvelle course débloquée : Circuit d'Entraînement."
            ]
        },
        "6_post_first_race_and_pixel": {
            "crank": [
                "Vous... avez gagné ? On dirait que vous savez faire la différence entre l'accélérateur et le frein. Mieux que la moitié des idiots.",
                "Pas de trophée, mais aussi pas de voiture cassée en deux. J'ai vu pire. La défaite fait partie du jeu."
            ]
        },
        "7_pixel_intro": {
            "pixel": [
                "Oups ! Calmez-vous, ce n'est pas un virus. C'est juste moi qui pirate un peu votre tableau de bord.",
                "Appelez-moi Pixel. Je vis dans les fils et les caméras de cette ville. Et je vous regarde faire des dégâts sur la piste.",
                "Là-haut, dans les tours, ils vous ont déjà remarqué. Rex adore les nouvelles personnes à tester... ou à jeter."
            ]
        }
    }
}

def preencher_traducao_ch1():
    """Preenche as traduções do Capítulo 1 nos arquivos de locale"""
    
    for idioma in ["en", "es", "fr"]:
        caminho_locale = os.path.join(CAMINHO_LOCALES, f"{idioma}.json")
        
        with open(caminho_locale, 'r', encoding='utf-8') as f:
            locale_data = json.load(f)
        
        if "narrative" not in locale_data or "chapters" not in locale_data["narrative"]:
            print(f"ERRO: Estrutura de narrativa nao encontrada em {idioma}.json")
            continue
        
        if "ch1" not in locale_data["narrative"]["chapters"]:
            print(f"ERRO: Capítulo 1 nao encontrado em {idioma}.json")
            continue
        
        ch1_data = locale_data["narrative"]["chapters"]["ch1"]
        traducoes = TRADUCOES_CH1[idioma]
        
        # Preencher cada cena
        for scene_key, scene_traducoes in traducoes.items():
            if scene_key not in ch1_data["scenes"]:
                continue
            
            scene_data = ch1_data["scenes"][scene_key]
            
            # Preencher linhas
            for speaker, lines in scene_traducoes.items():
                if speaker == "choices":
                    # Preencher escolhas
                    if "choices" in scene_data and len(scene_data["choices"]) == len(lines):
                        for i, choice_text in enumerate(lines):
                            if i < len(scene_data["choices"]):
                                scene_data["choices"][i]["text"] = choice_text
                else:
                    # Preencher linhas de diálogo
                    if speaker in scene_data.get("lines", {}):
                        speaker_lines = scene_data["lines"][speaker]
                        for i, line_text in enumerate(lines):
                            if i < len(speaker_lines):
                                speaker_lines[i]["text"] = line_text
        
        # Salvar
        with open(caminho_locale, 'w', encoding='utf-8') as f:
            json.dump(locale_data, f, ensure_ascii=False, indent=2)
        
        print(f"OK: Traducoes do Capitulo 1 preenchidas em {idioma}.json")

if __name__ == "__main__":
    print("Preenchendo traducoes do Capitulo 1...")
    preencher_traducao_ch1()
    print("\nOK: Processo concluido!")

