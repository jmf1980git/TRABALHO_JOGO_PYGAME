
import pygame
import sys

# Inicialização
pygame.init()

# Configurações da tela
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Meu Jogo Demo")
clock = pygame.time.Clock()

# Cores
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Jogador
player = pygame.Rect(400, 500, 50, 50)
player_speed = 5

# Inimigo
enemy = pygame.Rect(100, 100, 50, 50)
enemy_speed = 3

# Pontuação
score = 0
font = pygame.font.Font(None, 36)

# Menu
menu_active = True

def show_menu():
    screen.fill(WHITE)
    title = font.render("MEU JOGO DEMO", True, (0,0,0))
    controls = font.render("SETAS - Mover | ESPAÇO - Pular", True, (0,0,0))
    start = font.render("Pressione ENTER para começar", True, (0,0,0))
    
    screen.blit(title, (WIDTH//2 - 100, 200))
    screen.blit(controls, (WIDTH//2 - 180, 300))
    screen.blit(start, (WIDTH//2 - 150, 400))
    pygame.display.flip()

# Loop principal
running = True
while running:
    if menu_active:
        show_menu()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    menu_active = False
        continue

    # Eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Controles
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player.x -= player_speed
    if keys[pygame.K_RIGHT]:
        player.x += player_speed
    if keys[pygame.K_UP]:
        player.y -= player_speed
    if keys[pygame.K_DOWN]:
        player.y += player_speed

    # Movimento inimigo
    enemy.x += enemy_speed
    if enemy.x > WIDTH - 50 or enemy.x < 0:
        enemy_speed *= -1

    # Colisão (vitória)
    if player.colliderect(enemy):
        score += 1
        enemy.x = 0
        
    # Condição de derrota (sair da tela)
    if player.x > WIDTH or player.x < 0 or player.y > HEIGHT or player.y < 0:
        print("Game Over!")
        running = False

    # Desenho
    screen.fill(WHITE)
    pygame.draw.rect(screen, RED, enemy)
    pygame.draw.rect(screen, BLUE, player)
    
    # Pontuação
    score_text = font.render(f"Pontos: {score}", True, (0,0,0))
    screen.blit(score_text, (10, 10))
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()