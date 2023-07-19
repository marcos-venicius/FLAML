# filename: game.py

import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Set up some constants
WIDTH = 800
HEIGHT = 600
BLOCK_SIZE = 50

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# Set up the player
player = pygame.Rect(WIDTH / 2, HEIGHT / 2, BLOCK_SIZE, BLOCK_SIZE)

# Set up the target
target = pygame.Rect(
    random.randint(0, WIDTH - BLOCK_SIZE), random.randint(0, HEIGHT - BLOCK_SIZE), BLOCK_SIZE, BLOCK_SIZE
)

# Set up the score
score = 0

# Set up the game clock
clock = pygame.time.Clock()

# Set up the font for the score display
font = pygame.font.Font(None, 36)

# Game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Fill the screen with white
    screen.fill((255, 255, 255))

    # Draw the player
    pygame.draw.rect(screen, (0, 0, 255), player)

    # Draw the target
    pygame.draw.rect(screen, (255, 0, 0), target)

    # Move the player
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player.x -= 5
    if keys[pygame.K_RIGHT]:
        player.x += 5
    if keys[pygame.K_UP]:
        player.y -= 5
    if keys[pygame.K_DOWN]:
        player.y += 5

    # Make sure the player stays on the screen
    if player.x < 0:
        player.x = 0
    if player.y < 0:
        player.y = 0
    if player.x > WIDTH - BLOCK_SIZE:
        player.x = WIDTH - BLOCK_SIZE
    if player.y > HEIGHT - BLOCK_SIZE:
        player.y = HEIGHT - BLOCK_SIZE

    # Check if the player has reached the target
    if player.colliderect(target):
        score += 1
        target.x = random.randint(0, WIDTH - BLOCK_SIZE)
        target.y = random.randint(0, HEIGHT - BLOCK_SIZE)

    # Display the score
    score_text = font.render("Score: " + str(score), True, (0, 0, 0))
    screen.blit(score_text, (10, 10))

    # Update the display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(60)
