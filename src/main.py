import os
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame
from config import LARGURA, ALTURA, FPS
from core.pista import carregar_pista
from core.carro import Carro

def principal():
    pygame.init()
    tela = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("Corrida com Pista de Imagem")
    relogio = pygame.time.Clock()

    imagem_pista, superficie_mascara = carregar_pista()

    carro1 = Carro(570, 145, "red",  (pygame.K_w, pygame.K_d, pygame.K_a, pygame.K_s))
    carro2 = Carro(570, 190, "blue", (pygame.K_UP, pygame.K_RIGHT, pygame.K_LEFT, pygame.K_DOWN))

    rodando = True
    while rodando:
        relogio.tick(FPS)
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False

        teclas = pygame.key.get_pressed()
        carro1.atualizar(teclas, superficie_mascara)
        carro2.atualizar(teclas, superficie_mascara)

        tela.blit(imagem_pista, (0, 0))
        carro1.desenhar(tela)
        carro2.desenhar(tela)
        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    principal()
