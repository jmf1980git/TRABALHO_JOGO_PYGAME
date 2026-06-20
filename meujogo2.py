import pygame
import sys
import random
import math

# Inicialização
pygame.init()
pygame.mixer.init()

# Configurações da tela
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Labirinto do Terror")
clock = pygame.time.Clock()

# Cores
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
GRAY = (128, 128, 128)
DARK_GRAY = (40, 40, 40)
ORANGE = (255, 165, 0)

# Configurações do jogador
PLAYER_SIZE = 30
PLAYER_SPEED = 3
BULLET_SPEED = 7
ENEMY_SIZE = 25
ENEMY_SPEED = 1.5

# Fontes
font_title = pygame.font.Font(None, 72)
font_large = pygame.font.Font(None, 48)
font_medium = pygame.font.Font(None, 36)
font_small = pygame.font.Font(None, 24)

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = PLAYER_SIZE
        self.health = 100
        self.max_health = 100
        self.speed = PLAYER_SPEED
        self.direction = "down"  # up, down, left, right
        self.shoot_cooldown = 0
        self.shoot_delay = 15
        self.alive = True
        
    def move(self, dx, dy, maze):
        new_x = self.x + dx
        new_y = self.y + dy
        
        # Verificar colisão com paredes
        if not self.check_collision(new_x, new_y, maze):
            self.x = new_x
            self.y = new_y
            
        # Atualizar direção
        if dx > 0:
            self.direction = "right"
        elif dx < 0:
            self.direction = "left"
        elif dy > 0:
            self.direction = "down"
        elif dy < 0:
            self.direction = "up"
            
    def check_collision(self, x, y, maze):
        player_rect = pygame.Rect(x, y, self.size, self.size)
        for row in range(len(maze)):
            for col in range(len(maze[row])):
                if maze[row][col] == 1:
                    wall_rect = pygame.Rect(col * 40, row * 40, 40, 40)
                    if player_rect.colliderect(wall_rect):
                        return True
        return False
        
    def shoot(self, bullets):
        if self.shoot_cooldown <= 0:
            bullet_x = self.x + self.size // 2 - 5
            bullet_y = self.y + self.size // 2 - 5
            
            # Direção baseada na orientação do jogador
            if self.direction == "up":
                dx, dy = 0, -BULLET_SPEED
            elif self.direction == "down":
                dx, dy = 0, BULLET_SPEED
            elif self.direction == "left":
                dx, dy = -BULLET_SPEED, 0
            else:  # right
                dx, dy = BULLET_SPEED, 0
                
            bullets.append(Bullet(bullet_x, bullet_y, dx, dy))
            self.shoot_cooldown = self.shoot_delay
            
    def update(self):
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
            
    def draw(self, screen):
        # Desenhar jogador como um círculo
        center_x = self.x + self.size // 2
        center_y = self.y + self.size // 2
        
        # Corpo
        pygame.draw.circle(screen, BLUE, (center_x, center_y), self.size // 2)
        
        # Olhos (indicam direção)
        eye_offset = 8
        if self.direction == "up":
            pygame.draw.circle(screen, WHITE, (center_x - 6, center_y - 6), 5)
            pygame.draw.circle(screen, WHITE, (center_x + 6, center_y - 6), 5)
            pygame.draw.circle(screen, BLACK, (center_x - 6, center_y - 8), 2)
            pygame.draw.circle(screen, BLACK, (center_x + 6, center_y - 8), 2)
        elif self.direction == "down":
            pygame.draw.circle(screen, WHITE, (center_x - 6, center_y + 6), 5)
            pygame.draw.circle(screen, WHITE, (center_x + 6, center_y + 6), 5)
            pygame.draw.circle(screen, BLACK, (center_x - 6, center_y + 8), 2)
            pygame.draw.circle(screen, BLACK, (center_x + 6, center_y + 8), 2)
        elif self.direction == "left":
            pygame.draw.circle(screen, WHITE, (center_x - 6, center_y - 6), 5)
            pygame.draw.circle(screen, WHITE, (center_x - 6, center_y + 6), 5)
            pygame.draw.circle(screen, BLACK, (center_x - 8, center_y - 6), 2)
            pygame.draw.circle(screen, BLACK, (center_x - 8, center_y + 6), 2)
        else:  # right
            pygame.draw.circle(screen, WHITE, (center_x + 6, center_y - 6), 5)
            pygame.draw.circle(screen, WHITE, (center_x + 6, center_y + 6), 5)
            pygame.draw.circle(screen, BLACK, (center_x + 8, center_y - 6), 2)
            pygame.draw.circle(screen, BLACK, (center_x + 8, center_y + 6), 2)

class Bullet:
    def __init__(self, x, y, dx, dy):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.size = 8
        self.active = True
        
    def update(self):
        self.x += self.dx
        self.y += self.dy
        
        # Verificar se saiu da tela
        if self.x < 0 or self.x > WIDTH or self.y < 0 or self.y > HEIGHT:
            self.active = False
            
    def draw(self, screen):
        pygame.draw.circle(screen, YELLOW, (int(self.x), int(self.y)), self.size // 2)
        # Efeito de brilho
        pygame.draw.circle(screen, ORANGE, (int(self.x), int(self.y)), self.size // 4)

class Enemy:
    def __init__(self, x, y, level):
        self.x = x
        self.y = y
        self.size = ENEMY_SIZE
        self.speed = ENEMY_SPEED + (level * 0.2)  # Aumenta velocidade com nível
        self.health = 1
        self.alive = True
        self.direction = random.choice(["up", "down", "left", "right"])
        self.move_timer = 0
        self.move_delay = random.randint(30, 90)
        self.damage = 20 + (level * 2)  # Aumenta dano com nível
        
    def update(self, player_x, player_y, maze):
        if not self.alive:
            return
            
        self.move_timer += 1
        
        # Mudar direção aleatoriamente
        if self.move_timer >= self.move_delay:
            self.direction = random.choice(["up", "down", "left", "right"])
            self.move_timer = 0
            self.move_delay = random.randint(30, 90)
            
        # Movimento baseado na direção (com chance de perseguir)
        chase_chance = 70  # 70% de chance de perseguir
        if random.randint(0, 100) < chase_chance:
            # Perseguir jogador
            dx = player_x - self.x
            dy = player_y - self.y
            distance = math.sqrt(dx**2 + dy**2)
            if distance > 0:
                dx = (dx / distance) * self.speed
                dy = (dy / distance) * self.speed
                new_x = self.x + dx
                new_y = self.y + dy
                
                if not self.check_collision(new_x, new_y, maze):
                    self.x = new_x
                    self.y = new_y
        else:
            # Movimento aleatório
            if self.direction == "up":
                new_y = self.y - self.speed
                if not self.check_collision(self.x, new_y, maze) and new_y > 0:
                    self.y = new_y
            elif self.direction == "down":
                new_y = self.y + self.speed
                if not self.check_collision(self.x, new_y, maze) and new_y < HEIGHT - self.size:
                    self.y = new_y
            elif self.direction == "left":
                new_x = self.x - self.speed
                if not self.check_collision(new_x, self.y, maze) and new_x > 0:
                    self.x = new_x
            elif self.direction == "right":
                new_x = self.x + self.speed
                if not self.check_collision(new_x, self.y, maze) and new_x < WIDTH - self.size:
                    self.x = new_x
                    
    def check_collision(self, x, y, maze):
        enemy_rect = pygame.Rect(x, y, self.size, self.size)
        for row in range(len(maze)):
            for col in range(len(maze[row])):
                if maze[row][col] == 1:
                    wall_rect = pygame.Rect(col * 40, row * 40, 40, 40)
                    if enemy_rect.colliderect(wall_rect):
                        return True
        return False
        
    def draw(self, screen):
        if not self.alive:
            return
            
        center_x = self.x + self.size // 2
        center_y = self.y + self.size // 2
        
        # Corpo do inimigo (vermelho com olhos)
        pygame.draw.circle(screen, RED, (center_x, center_y), self.size // 2)
        pygame.draw.circle(screen, BLACK, (center_x - 6, center_y - 4), 4)
        pygame.draw.circle(screen, BLACK, (center_x + 6, center_y - 4), 4)
        pygame.draw.circle(screen, WHITE, (center_x - 6, center_y - 4), 2)
        pygame.draw.circle(screen, WHITE, (center_x + 6, center_y - 4), 2)
        
        # Boca (dependendo da direção)
        if self.direction == "up":
            pygame.draw.line(screen, BLACK, (center_x - 5, center_y + 4), (center_x + 5, center_y + 4), 2)
        else:
            pygame.draw.line(screen, BLACK, (center_x - 5, center_y + 4), (center_x + 5, center_y + 4), 2)

class Exit:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 40
        self.animation_frame = 0
        
    def update(self):
        self.animation_frame += 1
        
    def draw(self, screen):
        # Efeito pulsante
        pulse = abs(math.sin(self.animation_frame * 0.05)) * 10
        
        # Porta
        rect = pygame.Rect(self.x + 5, self.y + 5, self.size - 10, self.size - 10)
        pygame.draw.rect(screen, GREEN, rect)
        pygame.draw.rect(screen, (0, 200, 0), rect, 3)
        
        # Brilho
        glow = pygame.Rect(self.x + 5 - pulse//2, self.y + 5 - pulse//2, 
                          self.size - 10 + pulse, self.size - 10 + pulse)
        pygame.draw.rect(screen, (0, 255, 0, 50), glow, 2)

class MazeGame:
    def __init__(self):
        self.level = 1
        self.max_level = 5
        self.game_state = "menu"  # menu, playing, game_over, victory
        self.maze = []
        self.player = None
        self.enemies = []
        self.bullets = []
        self.exit = None
        self.score = 0
        self.enemies_defeated = 0
        self.enemies_per_level = 3
        self.mouse_x = 0
        self.mouse_y = 0
        
    def generate_maze(self):
        # Maze 15x10 (cada célula = 40x40 pixels)
        cols, rows = 15, 10
        maze = [[1 for _ in range(cols)] for _ in range(rows)]
        
        # Algoritmo simples de geração (baseado em DFS)
        # Começar no centro
        start_x, start_y = 1, 1
        maze[start_y][start_x] = 0
        
        # Gerar caminhos aleatórios
        for _ in range(20 + self.level * 5):  # Mais caminhos com níveis mais altos
            x = random.randint(1, cols - 2)
            y = random.randint(1, rows - 2)
            maze[y][x] = 0
            
            # Conectar com vizinhos
            neighbors = []
            if x > 1 and maze[y][x-1] == 0:
                neighbors.append((x-1, y))
            if x < cols-2 and maze[y][x+1] == 0:
                neighbors.append((x+1, y))
            if y > 1 and maze[y-1][x] == 0:
                neighbors.append((x, y-1))
            if y < rows-2 and maze[y+1][x] == 0:
                neighbors.append((x, y+1))
                
            if neighbors:
                nx, ny = random.choice(neighbors)
                if nx < x:
                    maze[y][x-1] = 0
                elif nx > x:
                    maze[y][x+1] = 0
                elif ny < y:
                    maze[y-1][x] = 0
                elif ny > y:
                    maze[y+1][x] = 0
        
        # Garantir que há caminho até a saída
        exit_x, exit_y = cols-2, rows-2
        maze[exit_y][exit_x] = 0
        
        return maze
        
    def init_level(self):
        self.maze = self.generate_maze()
        
        # Encontrar posições válidas
        valid_positions = []
        for y in range(len(self.maze)):
            for x in range(len(self.maze[y])):
                if self.maze[y][x] == 0:
                    valid_positions.append((x * 40, y * 40))
        
        if not valid_positions:
            return
            
        # Posicionar jogador no início
        player_pos = valid_positions[0] if valid_positions else (40, 40)
        self.player = Player(player_pos[0] + 5, player_pos[1] + 5)
        
        # Posicionar saída no final
        exit_pos = valid_positions[-1] if len(valid_positions) > 1 else (560, 360)
        self.exit = Exit(exit_pos[0], exit_pos[1])
        
        # Remover posições ocupadas
        occupied = [player_pos, exit_pos]
        
        # Criar inimigos
        self.enemies = []
        num_enemies = self.enemies_per_level + (self.level - 1) * 2
        for i in range(min(num_enemies, len(valid_positions) - 2)):
            pos = random.choice(valid_positions)
            attempts = 0
            while pos in occupied and attempts < 100:
                pos = random.choice(valid_positions)
                attempts += 1
            if pos not in occupied:
                enemy = Enemy(pos[0] + 7, pos[1] + 7, self.level)
                self.enemies.append(enemy)
                occupied.append(pos)
                
        self.bullets = []
        self.enemies_defeated = 0
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            if event.type == pygame.MOUSEMOTION:
                self.mouse_x, self.mouse_y = event.pos
                
            if event.type == pygame.KEYDOWN:
                if self.game_state == "menu":
                    if event.key == pygame.K_RETURN:
                        self.game_state = "playing"
                        self.level = 1
                        self.score = 0
                        self.enemies_per_level = 3
                        self.init_level()
                        
                elif self.game_state == "game_over" or self.game_state == "victory":
                    if event.key == pygame.K_r:
                        self.game_state = "menu"
                        
                elif self.game_state == "playing":
                    if event.key == pygame.K_SPACE:
                        if self.player and self.player.alive:
                            self.player.shoot(self.bullets)
                            
        return True
        
    def update(self):
        if self.game_state != "playing":
            return
            
        if not self.player or not self.player.alive:
            self.game_state = "game_over"
            return
            
        # Controles do jogador (teclado)
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -self.player.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = self.player.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy = -self.player.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy = self.player.speed
            
        # Movimento diagonal normalizado
        if dx != 0 and dy != 0:
            dx *= 0.707
            dy *= 0.707
            
        self.player.move(dx, dy, self.maze)
        self.player.update()
        
        # Atirar com mouse (clique)
        if pygame.mouse.get_pressed()[0] and self.player.shoot_cooldown <= 0:
            self.player.shoot(self.bullets)
        
        # Atualizar balas
        for bullet in self.bullets[:]:
            bullet.update()
            if not bullet.active:
                self.bullets.remove(bullet)
                
        # Verificar colisão das balas com inimigos
        for bullet in self.bullets[:]:
            for enemy in self.enemies[:]:
                if enemy.alive:
                    bullet_rect = pygame.Rect(bullet.x, bullet.y, bullet.size, bullet.size)
                    enemy_rect = pygame.Rect(enemy.x, enemy.y, enemy.size, enemy.size)
                    if bullet_rect.colliderect(enemy_rect):
                        enemy.alive = False
                        bullet.active = False
                        self.enemies_defeated += 1
                        self.score += 10
                        
        # Remover balas inativas
        self.bullets = [b for b in self.bullets if b.active]
        
        # Atualizar inimigos
        for enemy in self.enemies:
            if enemy.alive:
                enemy.update(self.player.x, self.player.y, self.maze)
                
                # Colisão com jogador
                player_rect = pygame.Rect(self.player.x, self.player.y, self.player.size, self.player.size)
                enemy_rect = pygame.Rect(enemy.x, enemy.y, enemy.size, enemy.size)
                if player_rect.colliderect(enemy_rect):
                    self.player.health -= enemy.damage
                    if self.player.health <= 0:
                        self.player.health = 0
                        self.player.alive = False
                        self.game_state = "game_over"
        
        # Verificar colisão com saída
        if self.player and self.exit:
            player_rect = pygame.Rect(self.player.x, self.player.y, self.player.size, self.player.size)
            exit_rect = pygame.Rect(self.exit.x, self.exit.y, self.exit.size, self.exit.size)
            if player_rect.colliderect(exit_rect):
                if self.level < self.max_level:
                    self.level += 1
                    self.enemies_per_level += 1
                    self.init_level()
                    # Bônus por completar nível
                    self.score += 50 + (self.level * 10)
                else:
                    self.game_state = "victory"
                    self.score += 100
        
        # Atualizar saída
        if self.exit:
            self.exit.update()
        
        # Remover inimigos mortos
        self.enemies = [e for e in self.enemies if e.alive]
        
    def draw_menu(self):
        screen.fill(DARK_GRAY)
        
        # Título
        title = font_title.render("LABIRINTO DO TERROR", True, RED)
        title_rect = title.get_rect(center=(WIDTH//2, 100))
        screen.blit(title, title_rect)
        
        # Subtítulo
        subtitle = font_medium.render("Um jogo de sobrevivência", True, WHITE)
        subtitle_rect = subtitle.get_rect(center=(WIDTH//2, 160))
        screen.blit(subtitle, subtitle_rect)
        
        # Controles
        controls = [
            "CONTROLES:",
            "W/A/S/D ou SETAS - Mover",
            "ESPAÇO ou CLICK - Atirar",
            "Encontre a saída verde",
            "Elimine os inimigos vermelhos"
        ]
        
        y_pos = 230
        for text in controls:
            if text == "CONTROLES:":
                label = font_large.render(text, True, YELLOW)
            else:
                label = font_medium.render(text, True, WHITE)
            label_rect = label.get_rect(center=(WIDTH//2, y_pos))
            screen.blit(label, label_rect)
            y_pos += 45
            
        # Níveis
        level_text = font_medium.render(f"Níveis: 1 a {self.max_level}", True, GREEN)
        level_rect = level_text.get_rect(center=(WIDTH//2, y_pos + 30))
        screen.blit(level_text, level_rect)
        
        # Iniciar
        start = font_large.render("PRESSIONE ENTER PARA INICIAR", True, GREEN)
        start_rect = start.get_rect(center=(WIDTH//2, HEIGHT - 80))
        
        # Efeito de piscar
        if pygame.time.get_ticks() // 500 % 2 == 0:
            screen.blit(start, start_rect)
            
        # Versão
        version = font_small.render("v1.0 - Demo", True, GRAY)
        version_rect = version.get_rect(bottomright=(WIDTH - 20, HEIGHT - 20))
        screen.blit(version, version_rect)
        
    def draw_game(self):
        screen.fill(BLACK)
        
        # Desenhar labirinto
        for y in range(len(self.maze)):
            for x in range(len(self.maze[y])):
                if self.maze[y][x] == 1:
                    pygame.draw.rect(screen, (50, 50, 50), (x * 40, y * 40, 40, 40))
                    pygame.draw.rect(screen, (80, 80, 80), (x * 40, y * 40, 40, 40), 1)
                else:
                    pygame.draw.rect(screen, (20, 20, 20), (x * 40, y * 40, 40, 40))
        
        # Desenhar inimigos
        for enemy in self.enemies:
            enemy.draw(screen)
            
        # Desenhar balas
        for bullet in self.bullets:
            bullet.draw(screen)
            
        # Desenhar jogador
        if self.player:
            self.player.draw(screen)
            
        # Desenhar saída
        if self.exit:
            self.exit.draw(screen)
            
        # UI - Barra de vida
        health_width = 200
        health_height = 20
        health_x = 20
        health_y = 20
        
        # Fundo da barra
        pygame.draw.rect(screen, (60, 60, 60), (health_x, health_y, health_width, health_height))
        
        # Vida atual
        health_percent = self.player.health / self.player.max_health
        current_width = health_width * health_percent
        
        # Cor da vida (verde -> amarelo -> vermelho)
        if health_percent > 0.5:
            color = GREEN
        elif health_percent > 0.25:
            color = YELLOW
        else:
            color = RED
            
        pygame.draw.rect(screen, color, (health_x, health_y, current_width, health_height))
        pygame.draw.rect(screen, WHITE, (health_x, health_y, health_width, health_height), 2)
        
        # Texto da vida
        health_text = font_small.render(f"Vida: {self.player.health}/{self.player.max_health}", True, WHITE)
        screen.blit(health_text, (health_x + 5, health_y + 2))
        
        # UI - Pontuação e nível
        score_text = font_medium.render(f"Score: {self.score}", True, WHITE)
        screen.blit(score_text, (WIDTH - 200, 20))
        
        level_text = font_medium.render(f"Nível: {self.level}/{self.max_level}", True, WHITE)
        screen.blit(level_text, (WIDTH - 200, 60))
        
        enemies_text = font_medium.render(f"Inimigos: {len(self.enemies)}", True, RED)
        screen.blit(enemies_text, (WIDTH - 200, 100))
        
        # Controles na tela (mostrar sempre)
        controls_text = font_small.render("WASD/SETAS: Mover | ESPAÇO/CLICK: Atirar", True, GRAY)
        controls_rect = controls_text.get_rect(bottomright=(WIDTH - 20, HEIGHT - 20))
        screen.blit(controls_text, controls_rect)
        
    def draw_game_over(self):
        # Overlay escuro
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
        
        # Título
        title = font_title.render("GAME OVER", True, RED)
        title_rect = title.get_rect(center=(WIDTH//2, HEIGHT//2 - 100))
        screen.blit(title, title_rect)
        
        # Pontuação
        score_text = font_large.render(f"Pontuação: {self.score}", True, WHITE)
        score_rect = score_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 20))
        screen.blit(score_text, score_rect)
        
        # Nível
        level_text = font_medium.render(f"Você chegou ao nível {self.level}", True, YELLOW)
        level_rect = level_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 40))
        screen.blit(level_text, level_rect)
        
        # Reiniciar
        restart = font_large.render("PRESSIONE R PARA REINICIAR", True, GREEN)
        restart_rect = restart.get_rect(center=(WIDTH//2, HEIGHT//2 + 120))
        
        if pygame.time.get_ticks() // 500 % 2 == 0:
            screen.blit(restart, restart_rect)
            
    def draw_victory(self):
        # Overlay escuro
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
        
        # Título
        title = font_title.render("VITÓRIA!", True, GREEN)
        title_rect = title.get_rect(center=(WIDTH//2, HEIGHT//2 - 120))
        screen.blit(title, title_rect)
        
        # Subtitle
        subtitle = font_large.render("Parabéns! Você completou todos os níveis!", True, WHITE)
        subtitle_rect = subtitle.get_rect(center=(WIDTH//2, HEIGHT//2 - 50))
        screen.blit(subtitle, subtitle_rect)
        
        # Pontuação final
        score_text = font_large.render(f"Pontuação Final: {self.score}", True, YELLOW)
        score_rect = score_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 20))
        screen.blit(score_text, score_rect)
        
        # Estatísticas
        stats_text = font_medium.render(f"Inimigos derrotados: {self.enemies_defeated}", True, WHITE)
        stats_rect = stats_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 80))
        screen.blit(stats_text, stats_rect)
        
        # Reiniciar
        restart = font_large.render("PRESSIONE R PARA REINICIAR", True, GREEN)
        restart_rect = restart.get_rect(center=(WIDTH//2, HEIGHT//2 + 160))
        
        if pygame.time.get_ticks() // 500 % 2 == 0:
            screen.blit(restart, restart_rect)
        
    def run(self):
        running = True
        
        while running:
            running = self.handle_events()
            self.update()
            
            # Desenhar
            if self.game_state == "menu":
                self.draw_menu()
            elif self.game_state == "playing":
                self.draw_game()
            elif self.game_state == "game_over":
                self.draw_game()
                self.draw_game_over()
            elif self.game_state == "victory":
                self.draw_game()
                self.draw_victory()
                
            pygame.display.flip()
            clock.tick(60)
            
        pygame.quit()
        sys.exit()

# Ponto de entrada
if __name__ == "__main__":
    game = MazeGame()
    game.run()