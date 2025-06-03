import pygame

pygame.init()

W,H = 400,300

win = pygame.display.set_mode((W,H))

on_ground = False

mx,my,vy = 50,250,0

enemies = [
    {'rect':pygame.Rect(250,250,20,20),'dir':-2},
    {'rect':pygame.Rect(200,250,20,20),'dir':-1},
    {'rect':pygame.Rect(350,250,20,20),'dir':-2}]

clock = pygame.time.Clock()

while True:

    for e in pygame.event.get():exit() if e.type == pygame.QUIT else 0

    keys=pygame.key.get_pressed()

    mx += (keys[pygame.K_RIGHT]-keys[pygame.K_LEFT]) * 5

    if keys[pygame.K_SPACE] and on_ground: vy -= 15
    vy += 1
    my += vy
    on_ground = False

    if my >= 250:
        my = 250
        vy = 0
        on_ground = True

    for enemy in enemies:
        enemy['rect'].x +=enemy['dir']
        if enemy['rect'].left <= 0 or enemy['rect'].right>W:enemy['dir']*=-1
        if enemy['rect'].colliderect(pygame.Rect(mx,my,20,20)) and vy > 0:
            enemies.remove(enemy)
            vy = -10
        

    win.fill((135,206,235))
    pygame.draw.rect(win,(255,0,0),(mx,my,20,20))
    [pygame.draw.rect(win,(0,255,0),enemy['rect']) for enemy in enemies]
    pygame.display.flip()
    clock.tick(30)



