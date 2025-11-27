#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para preencher traduções reais de todos os capítulos
Execute: python tools/preencher_traducao_completa.py
"""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from config import DIR_PROJETO

CAMINHO_LOCALES = os.path.join(DIR_PROJETO, "data", "locales")

# Traduções completas de todos os capítulos
TRADUCOES_COMPLETAS = {
    "en": {
        "ch1": {
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
        "ch2": {
            "1_crank_talks_barrier": {
                "crank": [
                    "You've already proven you're not a complete disaster. Congratulations, you're a partial disaster.",
                    "There's a circuit higher up, the Industrial Belt. Bigger prize, paid entry.",
                    "Your car can handle it. Your wallet, not so much. Unless you do what the last generation did... and regret it later.",
                    "I'm talking about the Baron."
                ]
            },
            "2_barao_appears": {
                "barao": [
                    "Mrrr... did someone say my name? How rude not to invite me.",
                    "I just offer opportunities, dear. With small interest rates."
                ],
                "crank": [
                    "I knew it. Like a cockroach when it sees the light going out."
                ],
                "choices": []
            },
            "3_barao_offer": {
                "barao": [
                    "I put credit in your hand now. Upgrade, entry to big race...",
                    "In return, you pay me later. With interest. Every race you do, the debt breathes."
                ],
                "crank": [
                    "Interest that becomes a chain. I've seen promising drivers become just another entry in his notebook."
                ],
                "choices": [
                    "Accept loan",
                    "Refuse"
                ]
            },
            "4_loan_accepted": {
                "barao": [
                    "I knew you had good instinct. Courage and recklessness go hand in hand.",
                    "It's all recorded. I'm a man of my word. You're the ones who usually fail with yours."
                ],
                "crank": [
                    "You just put a collar around your neck. He'll tighten it every time you slip up."
                ]
            },
            "5_loan_refused": {
                "barao": [
                    "Refusing? Interesting. Self-control is rare around here.",
                    "That's fine. The city breaks you slowly. I'll come back later, with higher interest."
                ],
                "crank": [
                    "This time you made the right choice. If you're going to rise, let it be on your own wheels."
                ]
            },
            "6_pixel_reacts": {
                "pixel": [
                    "I detected a weird movement in your account. Big deposit, invisible withdrawal. The Baron's signature.",
                    "Alright, you got yourself into this. Now use that money right, or it becomes an avalanche.",
                    "You said NO to the Baron. That's big. It'll be harder, but at least your soul is yours."
                ]
            },
            "7_boris_reacts": {
                "boris": [
                    "You've been buying good stuff and not crying about price... the Baron passed by here, didn't he?",
                    "I already raced for him. Each part was a new knot in the rope. If you're going to sink in debt, at least make noise.",
                    "You still pay everything out of your own pocket? Brave... or stubborn. Crank must be proud."
                ]
            },
            "8_unlock_industrial": {
                "crank": [
                    "With these parts and what you've saved, you can face the Industrial Belt.",
                    "There the audience is less drunk and more cruel. And the drivers have already learned to hate losing."
                ]
            }
        },
        "ch3": {
            "1_crank_to_mountain": {
                "crank": [
                    "You've already shown you know how to step on it. Now you need to show you know how to let off.",
                    "Up there is the mountain. Narrow curves, ungrateful track. Akira runs things there.",
                    "She almost died in a circus manipulated by Rex. After that, she disappeared from down here."
                ]
            },
            "2_pixel_route": {
                "pixel": [
                    "New route unlocked on your improvised GPS: Akira's Mountain.",
                    "Just be careful: she doesn't like people who smell like a contract with the Baron."
                ]
            },
            "3_meet_akira": {
                "akira": [
                    "...",
                    "You brought another noisy car to my mountain.",
                    "At least it arrived in one piece. That already says something about you.",
                    "Your car is asking for help. You drive it with anger... or with fear.",
                    "Crank sent you, didn't he?"
                ]
            },
            "4_akira_past": {
                "akira": [
                    "Crank built my first car. I raced on the streets, like you.",
                    "A special race, sponsored, flexible rules... and manipulated. The corp wanted spectacle, not competition.",
                    "The Baron financed desperate drivers. The bigger the debt, the prettier the fall.",
                    "I survived. Many didn't. Crank got a ghost. I got a mountain."
                ]
            },
            "5_test_briefing": {
                "akira": [
                    "I don't train just anyone. So let's test.",
                    "One lap. No audience, no prize, no corporate tricks. Just you, the car, and the curves.",
                    "If you treat the track as an enemy, it returns the favor. If you listen to its rhythm... maybe you have a future."
                ],
                "narrator": [
                    "New objective: Mountain Flow Test."
                ]
            },
            "6_test_result": {
                "akira": [
                    "You're still rough, but I saw moments of harmony. Some curves were dance, not fight.",
                    "You survived, but didn't learn. You still fight against the car, all the time.",
                    "Come back whenever you want. The mountain is patient. More than the city."
                ]
            },
            "7_crank_reacts": {
                "crank": [
                    "So, you survived Akira?",
                    "If she didn't kick you out of there, she saw something good.",
                    "By the way you look, I think she sent you back early. No problem. We fix things down here."
                ]
            },
            "8_pixel_wrap": {
                "pixel": [
                    "Now you have three worlds: rust with Boris, industry in the Belt, tense silence with Akira.",
                    "When you start winning in all three, Rex won't be able to pretend you don't exist."
                ]
            }
        },
        "ch4": {
            "1_pixel_rex_watch": {
                "pixel": [
                    "Your data exploded on the servers. Until now, you were noise. Now you're an interesting pattern.",
                    "This only happens when Rex thinks: 'Maybe I can use this... or destroy it.'"
                ]
            },
            "2_rex_observes": {
                "rex": [
                    "From down there, this driver shouldn't have made it past the first junkyard. But they got here.",
                    "High adaptability. Improbable paths. This amuses me.",
                    "Predictable. Still gives good ratings, but doesn't promise much."
                ]
            },
            "3_crank_suspicious": {
                "crank": [
                    "The races are weird. Too much audience, too many cameras, too many bets.",
                    "When Rex decides to play producer, nothing is by chance."
                ]
            },
            "4_meet_slick": {
                "slick": [
                    "Greetings, high-risk bipedal unit.",
                    "I sell things that don't exist in your junkyard store. Upgrades that border on impossible.",
                    "You call it an upgrade. I call it a field experiment."
                ]
            },
            "5_meet_glub": {
                "glub": [
                    "Oooooh! Smell of tired metal!",
                    "I'm Glub. I eat scrap. Mainly scrap with stories.",
                    "If you have old parts, I pay. I eat. You get space and money."
                ]
            },
            "6_barao_reacts": {
                "barao": [
                    "You've been making peculiar friends. Aliens, slimes... but your debt is still with me.",
                    "You rose without owing me anything. Impressive. But time is long. Almost every driver falls into some contract."
                ]
            },
            "7_rex_direct_call": {
                "rex": [
                    "Good evening.",
                    "You already know who I am. When races grow too much, there's always someone watching from above.",
                    "Keep racing on all fronts. When I think you deserve it, I'll send an invitation you can't refuse."
                ]
            }
        },
        "ch5": {
            "1_rex_invite_circuit": {
                "sistema": [
                    "Invitation: Crown Circuit – Official Rex Series."
                ],
                "rex": [
                    "The time has come. You raced through alleys, rust, industry, and mountain. Now I want to see you under the spotlight.",
                    "Accept and enter the Crown Circuit: multiple stages, broadcast to the entire city."
                ],
                "choices": [
                    "Accept Crown Circuit"
                ]
            },
            "2_crank_iron_howl": {
                "crank": [
                    "Crown Circuit... last time I heard that name was with Iron Howl.",
                    "I built the cars. Boris was the brute. Baron financed. Rex produced the spectacle.",
                    "In the end, half broke, went bankrupt, or disappeared. Those who rose too high, fell harder."
                ]
            },
            "3_akira_reacts": {
                "akira": [
                    "I felt the noise, even up here. Rex opened the Circuit.",
                    "Down there, they'll mess with everything for ratings. Layout, weather, rules.",
                    "The only thing that's still yours is how you take the curves."
                ]
            },
            "4_preps": {
                "boris": [
                    "Going to Rex's stage, huh? Now there'll be noise.",
                    "If you're going into this circus, go in with a car that can take hits. I have parts from the Iron Howl era."
                ]
            },
            "4b_slick_prep": {
                "slick": [
                    "The big event has arrived. Want a turbo that gets stronger the closer it gets to catastrophe?"
                ]
            },
            "4c_glub_prep": {
                "glub": [
                    "Big circuit means LOTS of scrap. If you have old parts, bring them to me first!"
                ]
            },
            "4d_barao_prep": {
                "barao": [
                    "My investment reached the main stage. During the Circuit, I expect to see that debt go down.",
                    "Each prize, I take a bite. Don't try to be creative.",
                    "You got here without owing me anything. Rare. I'll watch with interest."
                ]
            },
            "5_stage1_intro": {
                "pixel": [
                    "Packed stands, camera drones, announcer screaming. Welcome to the Crown Circus."
                ],
                "narrator": [
                    "Stage 1: Urban Circuit – High speed."
                ]
            },
            "5_stage1_post": {
                "crank": [
                    "You didn't freeze in front of the cameras. Half of the rookies freeze.",
                    "First stage and you stumbled. You can turn it around, but the pressure only increases."
                ]
            },
            "5_stage2_intro": {
                "pixel": [
                    "I'm seeing weird stuff: container moved, oil where it shouldn't be. Rex is editing the track live."
                ],
                "narrator": [
                    "Stage 2: Manipulated Industrial Zone."
                ]
            },
            "5_stage2_post": {
                "rex": [
                    "Good adaptability. You gave me great scenes.",
                    "Predictable. Useful for the show, not for the final result."
                ]
            },
            "5_stage3_intro": {
                "pixel": [
                    "Part of this track passes through Akira's region. That was intentional."
                ],
                "akira": [
                    "Do you feel it? The city screams, the mountain watches."
                ]
            },
            "5_stage3_post": {
                "crank": [
                    "Even with the manipulated track, it was still you who chose the path.",
                    "You stepped exactly where Rex wanted. He'll repeat that in the edit."
                ]
            },
            "6_pre_final_rex": {
                "rex": [
                    "You made it to the final. Many bet you'd break before.",
                    "The Baron talks a lot about you. If you win, you pay him and rise. If you lose, he still profits from your fall.",
                    "Last race. It's not just about being fast. It's about bearing the weight of knowing the entire city is watching you."
                ]
            },
            "7_post_final_epilogue": {
                "pixel": [
                    "It's over. You're no longer the same driver who entered Crank's garage with a dying car."
                ],
                "crank": [
                    "I saw you grow, make mistakes, almost give up. You still gave me a reason to keep working on engines."
                ],
                "akira": [
                    "You danced with the track on a stage that wanted to see you stumble."
                ]
            },
            "8_rex_close": {
                "rex": [
                    "Regardless of victory or defeat, you proved one thing: it's impossible to ignore you.",
                    "Now you choose: accept the role I gave you on this board... or try to flip the board."
                ]
            }
        }
    },
    "es": {
        "ch1": {
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
        "ch2": {
            "1_crank_talks_barrier": {
                "crank": [
                    "Ya has demostrado que no eres un desastre completo. Felicidades, eres un desastre parcial.",
                    "Hay un circuito más arriba, el Cinturón Industrial. Premio mayor, entrada pagada.",
                    "Tu coche puede aguantarlo. Tu cartera, no tanto. A menos que hagas lo que hizo la generación pasada... y te arrepientas después.",
                    "Estoy hablando del Barón."
                ]
            },
            "2_barao_appears": {
                "barao": [
                    "Mrrr... ¿alguien dijo mi nombre? Qué falta de educación no invitarme.",
                    "Solo ofrezco oportunidades, querido. Con pequeños intereses."
                ],
                "crank": [
                    "Lo sabía. Como una cucaracha cuando ve la luz apagándose."
                ],
                "choices": []
            },
            "3_barao_offer": {
                "barao": [
                    "Pongo crédito en tu mano ahora. Mejora, inscripción en carrera grande...",
                    "A cambio, me pagas después. Con intereses. Cada carrera que hagas, la deuda respira."
                ],
                "crank": [
                    "Intereses que se convierten en cadena. He visto pilotos prometedores convertirse en solo otra ficha en su cuaderno."
                ],
                "choices": [
                    "Aceptar préstamo",
                    "Rechazar"
                ]
            },
            "4_loan_accepted": {
                "barao": [
                    "Sabía que tenías buen instinto. El coraje y la imprudencia van de la mano.",
                    "Está todo registrado. Soy un hombre de palabra. Ustedes son los que suelen fallar con la suya."
                ],
                "crank": [
                    "Acabas de poner una correa en el cuello. Él la apretará cada vez que vaciles."
                ]
            },
            "5_loan_refused": {
                "barao": [
                    "¿Rechazando? Interesante. El autocontrol es raro por aquí.",
                    "Está bien. La ciudad te rompe lentamente. Después vuelvo, con intereses mayores."
                ],
                "crank": [
                    "Esta vez hiciste la elección correcta. Si vas a subir, que sea con tus propias ruedas."
                ]
            },
            "6_pixel_reacts": {
                "pixel": [
                    "Detecté un movimiento raro en tu cuenta. Entrada grande, salida invisible. La firma del Barón.",
                    "Bien, te metiste en esto. Ahora usa ese dinero bien, o se convierte en avalancha.",
                    "Le dijiste NO al Barón. Eso es grande. Será más difícil, pero al menos tu alma es tuya."
                ]
            },
            "7_boris_reacts": {
                "boris": [
                    "Has estado comprando cosas buenas y no lloras por el precio... el Barón pasó por aquí, ¿verdad?",
                    "Ya corrí para él. Cada pieza era un nudo nuevo en la cuerda. Si vas a hundirte en deuda, al menos haz ruido.",
                    "¿Todavía pagas todo de tu propio bolsillo? Valiente... o terco. Crank debe estar orgulloso."
                ]
            },
            "8_unlock_industrial": {
                "crank": [
                    "Con estas piezas y lo que has ahorrado, puedes enfrentar el Cinturón Industrial.",
                    "Allí el público es menos borracho y más cruel. Y los pilotos ya aprendieron a odiar perder."
                ]
            }
        },
        "ch3": {
            "1_crank_to_mountain": {
                "crank": [
                    "Ya mostraste que sabes pisar. Ahora necesitas mostrar que sabes soltar.",
                    "Allá arriba está la montaña. Curvas estrechas, pista ingrata. Akira manda allí.",
                    "Casi murió en un circo manipulado por Rex. Después de eso, desapareció de aquí abajo."
                ]
            },
            "2_pixel_route": {
                "pixel": [
                    "Nueva ruta liberada en tu GPS improvisado: Montaña de Akira.",
                    "Solo cuidado: a ella no le gusta mucho quien llega oliendo a contrato con el Barón."
                ]
            },
            "3_meet_akira": {
                "akira": [
                    "...",
                    "Trajiste otro coche ruidoso a mi montaña.",
                    "Al menos llegó entero. Eso ya dice algo sobre ti.",
                    "Tu coche está pidiendo ayuda. Lo conduces con rabia... o con miedo.",
                    "Crank te envió, ¿verdad?"
                ]
            },
            "4_akira_past": {
                "akira": [
                    "Crank construyó mi primer coche. Corría en las calles, como tú.",
                    "Una carrera especial, patrocinada, reglas flexibles... y manipuladas. La corporación quería espectáculo, no competencia.",
                    "El Barón financiaba pilotos desesperados. Cuanto mayor la deuda, más bonita la caída.",
                    "Sobreviví. Mucha gente no. Crank ganó un fantasma. Yo gané una montaña."
                ]
            },
            "5_test_briefing": {
                "akira": [
                    "No entreno a cualquiera. Así que vamos a probar.",
                    "Una vuelta. Sin público, sin premio, sin trucos corporativos. Solo tú, el coche y las curvas.",
                    "Si tratas la pista como enemiga, te devuelve el favor. Si escuchas su ritmo... tal vez tengas futuro."
                ],
                "narrator": [
                    "Nuevo objetivo: Prueba de Flujo de la Montaña."
                ]
            },
            "6_test_result": {
                "akira": [
                    "Todavía eres bruto, pero vi momentos de armonía. Algunas curvas fueron danza, no pelea.",
                    "Sobreviviste, pero no aprendiste. Todavía luchas contra el coche, todo el tiempo.",
                    "Vuelve cuando quieras. La montaña es paciente. Más que la ciudad."
                ]
            },
            "7_crank_reacts": {
                "crank": [
                    "Entonces, ¿sobreviviste a Akira?",
                    "Si ella no te echó de allí, vio algo bueno.",
                    "Por tu manera, creo que te devolvió temprano. Sin problema. Arreglamos cosas aquí abajo."
                ]
            },
            "8_pixel_wrap": {
                "pixel": [
                    "Ahora tienes tres mundos: óxido con Boris, industria en el Cinturón, silencio tenso con Akira.",
                    "Cuando empieces a ganar en los tres, Rex no podrá fingir que no existes."
                ]
            }
        },
        "ch4": {
            "1_pixel_rex_watch": {
                "pixel": [
                    "Tus datos explotaron en los servidores. Hasta ahora, eras ruido. Ahora eres un patrón interesante.",
                    "Esto solo pasa cuando Rex piensa: 'Tal vez pueda usar esto... o destruirlo.'"
                ]
            },
            "2_rex_observes": {
                "rex": [
                    "Desde abajo, este piloto no debería haber pasado del primer desguace. Pero llegó hasta aquí.",
                    "Alta adaptabilidad. Caminos improbables. Esto me divierte.",
                    "Predecible. Todavía da audiencia, pero no promete mucho."
                ]
            },
            "3_crank_suspicious": {
                "crank": [
                    "Las carreras están raras. Demasiado público, demasiadas cámaras, demasiadas apuestas.",
                    "Cuando Rex decide jugar a productor, nada es por casualidad."
                ]
            },
            "4_meet_slick": {
                "slick": [
                    "Saludos, unidad bípeda de alto riesgo.",
                    "Vendo cosas que no existen en tu tienda de desguace. Mejoras que rozan lo imposible.",
                    "Tú lo llamas mejora. Yo lo llamo experimento de campo."
                ]
            },
            "5_meet_glub": {
                "glub": [
                    "¡Oooooh! ¡Olor a metal cansado!",
                    "Soy Glub. Como chatarra. Principalmente chatarra con historias.",
                    "Si tienes piezas viejas, pago. Como. Tú ganas espacio y dinero."
                ]
            },
            "6_barao_reacts": {
                "barao": [
                    "Has estado haciendo amigos peculiares. Alienígenas, babosas... pero tu deuda sigue siendo conmigo.",
                    "Subiste sin deberme nada. Impresionante. Pero el tiempo es largo. Casi todo piloto cae en algún contrato."
                ]
            },
            "7_rex_direct_call": {
                "rex": [
                    "Buenas noches.",
                    "Ya sabes quién soy. Cuando las carreras crecen demasiado, siempre hay alguien observando desde arriba.",
                    "Sigue corriendo en todos los frentes. Cuando piense que lo mereces, enviaré una invitación que no puedes rechazar."
                ]
            }
        },
        "ch5": {
            "1_rex_invite_circuit": {
                "sistema": [
                    "Invitación: Circuito de la Corona – Serie Oficial Rex."
                ],
                "rex": [
                    "Ha llegado el momento. Corriste por callejones, óxido, industria y montaña. Ahora quiero verte bajo los focos.",
                    "Acepta y entra al Circuito de la Corona: varias etapas, transmisión a toda la ciudad."
                ],
                "choices": [
                    "Aceptar Circuito de la Corona"
                ]
            },
            "2_crank_iron_howl": {
                "crank": [
                    "Circuito de la Corona... la última vez que oí ese nombre fue con Iron Howl.",
                    "Yo construía los coches. Boris era el bruto. Barón financiaba. Rex producía el espectáculo.",
                    "Al final, la mitad se rompió, quebró o desapareció. Quienes subieron demasiado, cayeron más fuerte."
                ]
            },
            "3_akira_reacts": {
                "akira": [
                    "Sentí el ruido, incluso aquí arriba. Rex abrió el Circuito.",
                    "Allá abajo, van a tocar todo por audiencia. Trazado, clima, reglas.",
                    "Lo único que todavía es tuyo es cómo tomas las curvas."
                ]
            },
            "4_preps": {
                "boris": [
                    "¿Vas al escenario de Rex? Ahora sí habrá ruido.",
                    "Si vas a entrar en este circo, entra con coche que aguante golpes. Tengo piezas de la época de Iron Howl."
                ]
            },
            "4b_slick_prep": {
                "slick": [
                    "El gran evento ha llegado. ¿Quieres un turbo que se vuelve más fuerte cuanto más cerca de la catástrofe?"
                ]
            },
            "4c_glub_prep": {
                "glub": [
                    "Circuito grande significa MUCHA chatarra. Si tienes piezas viejas, ¡tráemelas primero!"
                ]
            },
            "4d_barao_prep": {
                "barao": [
                    "Mi inversión llegó al escenario principal. Durante el Circuito, espero ver esa deuda bajar.",
                    "Cada premio, muerdo una parte. No intentes ser creativo.",
                    "Llegaste aquí sin deberme nada. Raro. Voy a ver con interés."
                ]
            },
            "5_stage1_intro": {
                "pixel": [
                    "Gradas llenas, drones de cámara, narrador gritando. Bienvenido al Circo de la Corona."
                ],
                "narrator": [
                    "Etapa 1: Circuito Urbano – Alta velocidad."
                ]
            },
            "5_stage1_post": {
                "crank": [
                    "No te congelaste frente a las cámaras. La mitad de los novatos se congelan.",
                    "Primera etapa y tropezaste. Puedes darle la vuelta, pero la presión solo aumenta."
                ]
            },
            "5_stage2_intro": {
                "pixel": [
                    "Estoy viendo cosas raras: contenedor movido, aceite donde no debería. Rex está editando la pista en vivo."
                ],
                "narrator": [
                    "Etapa 2: Zona Industrial Manipulada."
                ]
            },
            "5_stage2_post": {
                "rex": [
                    "Buena adaptabilidad. Me diste escenas geniales.",
                    "Predecible. Útil para el show, no para el resultado final."
                ]
            },
            "5_stage3_intro": {
                "pixel": [
                    "Parte de esta pista pasa por la región de Akira. Eso fue intencional."
                ],
                "akira": [
                    "¿Lo sientes? La ciudad grita, la montaña observa."
                ]
            },
            "5_stage3_post": {
                "crank": [
                    "Incluso con la pista manipulada, fuiste tú quien eligió el camino.",
                    "Pisaste exactamente donde Rex quería. Él repetirá eso en la edición."
                ]
            },
            "6_pre_final_rex": {
                "rex": [
                    "Llegaste a la final. Mucha gente apostó que te romperías antes.",
                    "El Barón habla mucho de ti. Si ganas, le pagas y subes. Si pierdes, él aún gana con tu caída.",
                    "Última carrera. No es solo sobre ser rápido. Es sobre aguantar el peso de saber que toda la ciudad te está viendo."
                ]
            },
            "7_post_final_epilogue": {
                "pixel": [
                    "Se acabó. Ya no eres el mismo piloto que entró al garaje de Crank con un coche muriendo."
                ],
                "crank": [
                    "Te vi crecer, cometer errores, casi rendirte. Todavía me diste una razón para seguir trabajando en motores."
                ],
                "akira": [
                    "Bailaste con la pista en un escenario que quería verte tropezar."
                ]
            },
            "8_rex_close": {
                "rex": [
                    "Independientemente de victoria o derrota, probaste una cosa: es imposible ignorarte.",
                    "Ahora eliges: acepta el papel que te di en este tablero... o intenta voltear el tablero."
                ]
            }
        }
    },
    "fr": {
        "ch1": {
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
        },
        "ch2": {
            "1_crank_talks_barrier": {
                "crank": [
                    "Vous avez déjà prouvé que vous n'êtes pas un désastre complet. Félicitations, vous êtes un désastre partiel.",
                    "Il y a un circuit plus haut, la Ceinture Industrielle. Prix plus gros, entrée payée.",
                    "Votre voiture peut le supporter. Votre portefeuille, pas tant que ça. À moins que vous fassiez ce que la génération passée a fait... et que vous le regrettiez après.",
                    "Je parle du Baron."
                ]
            },
            "2_barao_appears": {
                "barao": [
                    "Mrrr... quelqu'un a dit mon nom ? Quel manque d'éducation de ne pas m'inviter.",
                    "Je n'offre que des opportunités, cher. Avec de petits intérêts."
                ],
                "crank": [
                    "Je le savais. Comme un cafard quand il voit la lumière s'éteindre."
                ],
                "choices": []
            },
            "3_barao_offer": {
                "barao": [
                    "Je mets du crédit dans votre main maintenant. Amélioration, inscription à une grande course...",
                    "En retour, vous me payez plus tard. Avec intérêts. Chaque course que vous faites, la dette respire."
                ],
                "crank": [
                    "Des intérêts qui deviennent une chaîne. J'ai vu des pilotes prometteurs devenir juste une autre entrée dans son carnet."
                ],
                "choices": [
                    "Accepter le prêt",
                    "Refuser"
                ]
            },
            "4_loan_accepted": {
                "barao": [
                    "Je savais que vous aviez bon instinct. Le courage et l'imprudence vont de pair.",
                    "Tout est enregistré. Je suis un homme de parole. C'est vous qui échouez habituellement avec la vôtre."
                ],
                "crank": [
                    "Vous venez de mettre un collier autour du cou. Il le resserrera à chaque fois que vous vacillerez."
                ]
            },
            "5_loan_refused": {
                "barao": [
                    "Refuser ? Intéressant. La maîtrise de soi est rare par ici.",
                    "Très bien. La ville vous brise lentement. Je reviendrai plus tard, avec des intérêts plus élevés."
                ],
                "crank": [
                    "Cette fois, vous avez fait le bon choix. Si vous allez monter, que ce soit sur vos propres roues."
                ]
            },
            "6_pixel_reacts": {
                "pixel": [
                    "J'ai détecté un mouvement bizarre dans votre compte. Gros dépôt, retrait invisible. La signature du Baron.",
                    "D'accord, vous vous êtes mis dans le pétrin. Maintenant, utilisez cet argent correctement, ou ça devient une avalanche.",
                    "Vous avez dit NON au Baron. C'est énorme. Ce sera plus difficile, mais au moins votre âme est à vous."
                ]
            },
            "7_boris_reacts": {
                "boris": [
                    "Vous avez acheté de bonnes choses et ne pleurez pas sur le prix... le Baron est passé par ici, n'est-ce pas ?",
                    "J'ai déjà couru pour lui. Chaque pièce était un nouveau nœud dans la corde. Si vous allez vous enfoncer dans la dette, faites au moins du bruit.",
                    "Vous payez encore tout de votre propre poche ? Courageux... ou têtu. Crank doit être fier."
                ]
            },
            "8_unlock_industrial": {
                "crank": [
                    "Avec ces pièces et ce que vous avez économisé, vous pouvez affronter la Ceinture Industrielle.",
                    "Là-bas, le public est moins ivre et plus cruel. Et les pilotes ont déjà appris à détester perdre."
                ]
            }
        },
        "ch3": {
            "1_crank_to_mountain": {
                "crank": [
                    "Vous avez déjà montré que vous savez appuyer. Maintenant, vous devez montrer que vous savez relâcher.",
                    "Là-haut, il y a la montagne. Courbes étroites, piste ingrate. Akira dirige là-bas.",
                    "Elle a failli mourir dans un cirque manipulé par Rex. Après ça, elle a disparu d'ici en bas."
                ]
            },
            "2_pixel_route": {
                "pixel": [
                    "Nouvelle route débloquée sur votre GPS improvisé : Montagne d'Akira.",
                    "Juste attention : elle n'aime pas beaucoup ceux qui arrivent en sentant le contrat avec le Baron."
                ]
            },
            "3_meet_akira": {
                "akira": [
                    "...",
                    "Vous avez apporté une autre voiture bruyante à ma montagne.",
                    "Au moins, elle est arrivée en un seul morceau. Cela dit déjà quelque chose sur vous.",
                    "Votre voiture demande de l'aide. Vous la conduisez avec colère... ou avec peur.",
                    "Crank vous a envoyé, n'est-ce pas ?"
                ]
            },
            "4_akira_past": {
                "akira": [
                    "Crank a construit ma première voiture. Je courais dans les rues, comme vous.",
                    "Une course spéciale, sponsorisée, règles flexibles... et manipulées. La corp voulait du spectacle, pas de la compétition.",
                    "Le Baron finançait des pilotes désespérés. Plus la dette était grande, plus la chute était belle.",
                    "J'ai survécu. Beaucoup ne l'ont pas fait. Crank a gagné un fantôme. J'ai gagné une montagne."
                ]
            },
            "5_test_briefing": {
                "akira": [
                    "Je n'entraîne pas n'importe qui. Alors testons.",
                    "Un tour. Pas de public, pas de prix, pas de trucs d'entreprise. Juste vous, la voiture et les courbes.",
                    "Si vous traitez la piste comme une ennemie, elle vous le rend. Si vous écoutez son rythme... peut-être avez-vous un avenir."
                ],
                "narrator": [
                    "Nouvel objectif : Test de Flux de la Montagne."
                ]
            },
            "6_test_result": {
                "akira": [
                    "Vous êtes encore brut, mais j'ai vu des moments d'harmonie. Certaines courbes étaient de la danse, pas de la bagarre.",
                    "Vous avez survécu, mais n'avez pas appris. Vous luttez encore contre la voiture, tout le temps.",
                    "Revenez quand vous voulez. La montagne est patiente. Plus que la ville."
                ]
            },
            "7_crank_reacts": {
                "crank": [
                    "Alors, vous avez survécu à Akira ?",
                    "Si elle ne vous a pas viré de là, elle a vu quelque chose de bien.",
                    "À votre façon, je pense qu'elle vous a renvoyé tôt. Pas de problème. On répare les choses ici en bas."
                ]
            },
            "8_pixel_wrap": {
                "pixel": [
                    "Maintenant, vous avez trois mondes : rouille avec Boris, industrie dans la Ceinture, silence tendu avec Akira.",
                    "Quand vous commencerez à gagner dans les trois, Rex ne pourra plus prétendre que vous n'existez pas."
                ]
            }
        },
        "ch4": {
            "1_pixel_rex_watch": {
                "pixel": [
                    "Vos données ont explosé sur les serveurs. Jusqu'à présent, vous étiez du bruit. Maintenant, vous êtes un modèle intéressant.",
                    "Cela n'arrive que lorsque Rex pense : 'Peut-être que je peux utiliser ça... ou le détruire.'"
                ]
            },
            "2_rex_observes": {
                "rex": [
                    "D'en bas, ce pilote n'aurait pas dû dépasser la première casse. Mais il est arrivé ici.",
                    "Haute adaptabilité. Chemins improbables. Cela m'amuse.",
                    "Prévisible. Donne encore de l'audience, mais ne promet pas grand-chose."
                ]
            },
            "3_crank_suspicious": {
                "crank": [
                    "Les courses sont bizarres. Trop de public, trop de caméras, trop de paris.",
                    "Quand Rex décide de jouer au producteur, rien n'est par hasard."
                ]
            },
            "4_meet_slick": {
                "slick": [
                    "Salutations, unité bipède à haut risque.",
                    "Je vends des choses qui n'existent pas dans votre magasin de casse. Des améliorations qui frôlent l'impossible.",
                    "Vous appelez ça une amélioration. J'appelle ça une expérience sur le terrain."
                ]
            },
            "5_meet_glub": {
                "glub": [
                    "Oooooh ! Odeur de métal fatigué !",
                    "Je suis Glub. Je mange de la ferraille. Principalement de la ferraille avec des histoires.",
                    "Si vous avez de vieilles pièces, je paie. Je mange. Vous gagnez de l'espace et de l'argent."
                ]
            },
            "6_barao_reacts": {
                "barao": [
                    "Vous vous êtes fait des amis particuliers. Des extraterrestres, des slimes... mais votre dette est toujours avec moi.",
                    "Vous êtes monté sans me devoir quoi que ce soit. Impressionnant. Mais le temps est long. Presque tous les pilotes tombent dans un contrat."
                ]
            },
            "7_rex_direct_call": {
                "rex": [
                    "Bonsoir.",
                    "Vous savez déjà qui je suis. Quand les courses grandissent trop, il y a toujours quelqu'un qui observe d'en haut.",
                    "Continuez à courir sur tous les fronts. Quand je penserai que vous le méritez, j'enverrai une invitation que vous ne pourrez pas refuser."
                ]
            }
        },
        "ch5": {
            "1_rex_invite_circuit": {
                "sistema": [
                    "Invitation : Circuit de la Couronne – Série Officielle Rex."
                ],
                "rex": [
                    "Le moment est venu. Vous avez couru dans les ruelles, la rouille, l'industrie et la montagne. Maintenant, je veux vous voir sous les projecteurs.",
                    "Acceptez et entrez dans le Circuit de la Couronne : plusieurs étapes, diffusion à toute la ville."
                ],
                "choices": [
                    "Accepter le Circuit de la Couronne"
                ]
            },
            "2_crank_iron_howl": {
                "crank": [
                    "Circuit de la Couronne... la dernière fois que j'ai entendu ce nom, c'était avec Iron Howl.",
                    "Je construisais les voitures. Boris était le brute. Le Baron finançait. Rex produisait le spectacle.",
                    "À la fin, la moitié s'est cassée, a fait faillite ou a disparu. Ceux qui sont montés trop haut sont tombés plus fort."
                ]
            },
            "3_akira_reacts": {
                "akira": [
                    "J'ai senti le bruit, même ici en haut. Rex a ouvert le Circuit.",
                    "Là-bas, ils vont tout modifier pour l'audience. Traçage, météo, règles.",
                    "La seule chose qui est encore à vous, c'est la façon dont vous prenez les courbes."
                ]
            },
            "4_preps": {
                "boris": [
                    "Vous allez sur la scène de Rex ? Maintenant, il y aura du bruit.",
                    "Si vous allez dans ce cirque, entrez avec une voiture qui peut encaisser. J'ai des pièces de l'ère Iron Howl."
                ]
            },
            "4b_slick_prep": {
                "slick": [
                    "Le grand événement est arrivé. Vous voulez un turbo qui devient plus fort plus il se rapproche de la catastrophe ?"
                ]
            },
            "4c_glub_prep": {
                "glub": [
                    "Grand circuit signifie BEAUCOUP de ferraille. Si vous avez de vieilles pièces, apportez-les-moi d'abord !"
                ]
            },
            "4d_barao_prep": {
                "barao": [
                    "Mon investissement est arrivé sur la scène principale. Pendant le Circuit, j'espère voir cette dette diminuer.",
                    "Chaque prix, je prends une bouchée. N'essayez pas d'être créatif.",
                    "Vous êtes arrivé ici sans me devoir quoi que ce soit. Rare. Je vais regarder avec intérêt."
                ]
            },
            "5_stage1_intro": {
                "pixel": [
                    "Gradins pleins, drones de caméra, commentateur qui crie. Bienvenue au Cirque de la Couronne."
                ],
                "narrator": [
                    "Étape 1 : Circuit Urbain – Haute vitesse."
                ]
            },
            "5_stage1_post": {
                "crank": [
                    "Vous ne vous êtes pas figé devant les caméras. La moitié des débutants se figent.",
                    "Première étape et vous avez trébuché. Vous pouvez vous retourner, mais la pression ne fait qu'augmenter."
                ]
            },
            "5_stage2_intro": {
                "pixel": [
                    "Je vois des trucs bizarres : conteneur déplacé, huile où il ne devrait pas y en avoir. Rex édite la piste en direct."
                ],
                "narrator": [
                    "Étape 2 : Zone Industrielle Manipulée."
                ]
            },
            "5_stage2_post": {
                "rex": [
                    "Bonne adaptabilité. Vous m'avez donné de superbes scènes.",
                    "Prévisible. Utile pour le spectacle, pas pour le résultat final."
                ]
            },
            "5_stage3_intro": {
                "pixel": [
                    "Une partie de cette piste passe par la région d'Akira. C'était intentionnel."
                ],
                "akira": [
                    "Vous le sentez ? La ville crie, la montagne observe."
                ]
            },
            "5_stage3_post": {
                "crank": [
                    "Même avec la piste manipulée, c'était encore vous qui avez choisi le chemin.",
                    "Vous avez marché exactement où Rex voulait. Il répétera ça au montage."
                ]
            },
            "6_pre_final_rex": {
                "rex": [
                    "Vous êtes arrivé à la finale. Beaucoup ont parié que vous vous casseriez avant.",
                    "Le Baron parle beaucoup de vous. Si vous gagnez, vous le payez et montez. Si vous perdez, il profite encore de votre chute.",
                    "Dernière course. Ce n'est pas seulement une question de vitesse. C'est supporter le poids de savoir que toute la ville vous regarde."
                ]
            },
            "7_post_final_epilogue": {
                "pixel": [
                    "C'est fini. Vous n'êtes plus le même pilote qui est entré dans le garage de Crank avec une voiture mourante."
                ],
                "crank": [
                    "Je vous ai vu grandir, faire des erreurs, presque abandonner. Vous m'avez encore donné une raison de continuer à travailler sur les moteurs."
                ],
                "akira": [
                    "Vous avez dansé avec la piste sur une scène qui voulait vous voir trébucher."
                ]
            },
            "8_rex_close": {
                "rex": [
                    "Indépendamment de la victoire ou de la défaite, vous avez prouvé une chose : il est impossible de vous ignorer.",
                    "Maintenant, vous choisissez : acceptez le rôle que je vous ai donné sur ce plateau... ou essayez de retourner le plateau."
                ]
            }
        }
    }
}

def preencher_traducao_completa():
    """Preenche todas as traduções nos arquivos de locale"""
    
    for idioma in ["en", "es", "fr"]:
        caminho_locale = os.path.join(CAMINHO_LOCALES, f"{idioma}.json")
        
        with open(caminho_locale, 'r', encoding='utf-8') as f:
            locale_data = json.load(f)
        
        if "narrative" not in locale_data or "chapters" not in locale_data["narrative"]:
            print(f"ERRO: Estrutura de narrativa nao encontrada em {idioma}.json")
            continue
        
        traducoes = TRADUCOES_COMPLETAS[idioma]
        
        # Preencher cada capítulo
        for chapter_id, chapter_traducoes in traducoes.items():
            if chapter_id not in locale_data["narrative"]["chapters"]:
                continue
            
            chapter_data = locale_data["narrative"]["chapters"][chapter_id]
            
            # Preencher cada cena
            for scene_key, scene_traducoes in chapter_traducoes.items():
                if scene_key not in chapter_data.get("scenes", {}):
                    continue
                
                scene_data = chapter_data["scenes"][scene_key]
                
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
                            # Mapear cada linha de tradução para a linha correspondente no JSON
                            for i, line_text in enumerate(lines):
                                if i < len(speaker_lines):
                                    speaker_lines[i]["text"] = line_text
                        else:
                            # Se o speaker não existe nas linhas, pode ser que precise criar
                            # Por enquanto, apenas pular
                            pass
        
        # Salvar
        with open(caminho_locale, 'w', encoding='utf-8') as f:
            json.dump(locale_data, f, ensure_ascii=False, indent=2)
        
        print(f"OK: Traducoes completas preenchidas em {idioma}.json")

if __name__ == "__main__":
    print("Preenchendo todas as traducoes...")
    preencher_traducao_completa()
    print("\nOK: Processo concluido!")

