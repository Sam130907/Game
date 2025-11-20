import pygame
import sys
import random

def show_title_screen(game):
    font = pygame.font.SysFont(None, 56)
    btn_font = pygame.font.SysFont(None, 36)
    main_options = ["Play", "Quit"]
    difficulty_options = ["Easy", "Normal", "Hard", "Impossible"]
    values = {"Easy": 1, "Normal": 5, "Hard": 15, "Impossible": 100}

    menu_w, menu_h = 760, 400
    main_btn_w = 200
    main_spacing = 60
    main_total_w = main_btn_w * len(main_options) + main_spacing * (len(main_options) - 1)
    main_start_x = (menu_w - main_total_w) // 2

    diff_btn_w = 160
    diff_spacing = 40
    diff_total_w = diff_btn_w * len(difficulty_options) + diff_spacing * (len(difficulty_options) - 1)
    diff_start_x = (menu_w - diff_total_w) // 2

    menu_x = (game.screen.get_width() - menu_w) // 2
    menu_y = 160

    selected_difficulty = "Normal"
    game.enemies_per_spawner = values[selected_difficulty]

    while True:

        game.display.fill((0, 0, 0, 0))
        game.display_2.fill((0, 0, 0))
        game.display_2.blit(game.assets['background'], (0, 0))
        game.clouds.update()
        game.clouds.render(game.display_2)


        menu_surf = pygame.Surface((menu_w, menu_h), pygame.SRCALPHA)
        menu_surf.fill((20, 20, 20, 180))


        title_surf = font.render("Ninja Game", True, (255, 255, 255))
        title_rect = title_surf.get_rect(center=(menu_w // 2, 60))
        menu_surf.blit(title_surf, title_rect)

        mouse_pos = pygame.mouse.get_pos()
        relative_mouse_pos = (mouse_pos[0] - menu_x, mouse_pos[1] - menu_y)


        for i, opt in enumerate(main_options):
            cx = main_start_x + i * (main_btn_w + main_spacing) + main_btn_w // 2
            cy = 160
            btn_rect = pygame.Rect(cx - main_btn_w // 2, cy - 24, main_btn_w, 48)
            hover = btn_rect.collidepoint(relative_mouse_pos)
            color = (255, 255, 0) if hover else (200, 200, 200)
            txt = btn_font.render(opt, True, color)
            txt_rect = txt.get_rect(center=(cx, cy))
            menu_surf.blit(txt, txt_rect)

            if hover and pygame.mouse.get_pressed()[0]:
                if opt == "Play":
                    game.enemies_per_spawner = values[selected_difficulty]
                    

                    fade_steps = 30
                    for i in range(fade_steps):

                        game.display.fill((0, 0, 0, 0))
                        game.display_2.fill((0, 0, 0))
                        game.display_2.blit(game.assets['background'], (0, 0))
                        game.clouds.update()
                        game.clouds.render(game.display_2)
                        game.screen.blit(pygame.transform.scale(game.display_2, game.screen.get_size()), (0, 0))
                        

                        transition_surf = pygame.Surface(game.screen.get_size())
                        transition_surf.fill((0, 0, 0))
                        alpha = int((i / fade_steps) * 255)
                        transition_surf.set_alpha(alpha)
                        game.screen.blit(transition_surf, (0, 0))
                        
                        pygame.display.flip()
                        game.clock.tick(60)
                    

                    game.screen.fill((0, 0, 0))
                    pygame.display.flip()
                    

                    game.level = 0
                    game.load_level(0)
                    

                    for _ in range(60):

                        game.clouds.update()
                        game.player.update(game.tilemap, movement=(0, 0))
                        for enemy in game.enemies:
                            enemy.update(game.tilemap, (0, 0))
                        

                        game.display.fill((0, 0, 0, 0))
                        game.display_2.fill((0, 0, 0))
                        game.display_2.blit(game.assets['background'], (0, 0))
                        game.clouds.render(game.display_2, offset=game.scroll)
                        

                        game.tilemap.render(game.display, offset=game.scroll)
                        for enemy in game.enemies:
                            enemy.render(game.display, offset=game.scroll)
                        game.player.render(game.display, offset=game.scroll)
                        

                        for projectile in game.projectiles:
                            projectile.render(game.display, offset=game.scroll)
                        for spark in game.sparks:
                            spark.render(game.display, offset=game.scroll)
                        for particle in game.particles:
                            particle.render(game.display, offset=game.scroll)
                            

                        game.screen.fill((0, 0, 0))
                        pygame.display.flip()
                        game.clock.tick(60)
                    

                    game.transition = -60
                    

                    while game.transition < 0:
                        game.transition += 1
                        

                        game.display.fill((0, 0, 0, 0))
                        game.display_2.fill((0, 0, 0))
                        game.display_2.blit(game.assets['background'], (0, 0))
                        game.clouds.update()
                        game.clouds.render(game.display_2)
                        game.tilemap.render(game.display, offset=(0,0))
                        game.player.render(game.display, offset=(0,0))
                        for enemy in game.enemies:
                            enemy.render(game.display, offset=(0,0))
                        game.display_2.blit(game.display, (0, 0))
                        game.screen.blit(pygame.transform.scale(game.display_2, game.screen.get_size()), (0, 0))
                        

                        transition_surf = pygame.Surface(game.screen.get_size())
                        transition_surf.fill((0, 0, 0))
                        alpha = min(255, -game.transition * (255 // 30))
                        transition_surf.set_alpha(alpha)
                        game.screen.blit(transition_surf, (0, 0))
                        
                        pygame.display.flip()
                        game.clock.tick(60)
                    
                    return
                elif opt == "Quit":
                    pygame.quit()
                    sys.exit()


        diff_title = btn_font.render("Difficulty:", True, (200, 200, 200))
        diff_title_rect = diff_title.get_rect(center=(menu_w // 2, 260))
        menu_surf.blit(diff_title, diff_title_rect)


        for i, opt in enumerate(difficulty_options):
            cx = diff_start_x + i * (diff_btn_w + diff_spacing) + diff_btn_w // 2
            cy = 300
            btn_rect = pygame.Rect(cx - diff_btn_w // 2, cy - 20, diff_btn_w, 40)
            hover = btn_rect.collidepoint(relative_mouse_pos)
            
            if hover:
                color = (255, 255, 0)
            elif opt == selected_difficulty:
                color = (100, 255, 100)
            else:
                color = (200, 200, 200)
                
            txt = btn_font.render(opt, True, color)
            txt_rect = txt.get_rect(center=(cx, cy))
            menu_surf.blit(txt, txt_rect)

            if hover and pygame.mouse.get_pressed()[0]:
                selected_difficulty = opt
                game.enemies_per_spawner = values[opt]


        game.screen.blit(pygame.transform.scale(game.display_2, game.screen.get_size()), (0, 0))
        game.screen.blit(menu_surf, (menu_x, menu_y))
        pygame.display.flip()


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        game.clock.tick(60)
                        
def show_pause_menu(game):
    font = pygame.font.SysFont(None, 48)
    btn_font = pygame.font.SysFont(None, 36)
    options = ["Play", "Settings", "Quit"]

    menu_w, menu_h = 320, 220
    menu_x = game.screen.get_width() - menu_w - 40
    start_y = -menu_h
    end_y = 40


    def animate_menu_drop():
        drop_duration = 0.4
        start_t = pygame.time.get_ticks() / 1000.0
        while True:
            now = pygame.time.get_ticks() / 1000.0
            t = min(1.0, (now - start_t) / drop_duration)
            ease = 1 - (1 - t) ** 3
            menu_y = int(start_y + (end_y - start_y) * ease)


            game.screen.blit(pygame.transform.scale(game.display_2, game.screen.get_size()), (0, 0))
            game.screen.blit(pygame.transform.scale(game.display, game.screen.get_size()), (0, 0))

            menu_surf = pygame.Surface((menu_w, menu_h), pygame.SRCALPHA)
            pygame.draw.rect(menu_surf, (30, 30, 30, 230), (0, 0, menu_w, menu_h), border_radius=24)
            title_surf = font.render("Paused", True, (255, 255, 255))
            title_rect = title_surf.get_rect(center=(menu_w // 2, 40))
            menu_surf.blit(title_surf, title_rect)

            mouse_pos = pygame.mouse.get_pos()
            for i, opt in enumerate(options):
                rect = pygame.Rect(30, 80 + i * 48, menu_w - 60, 40)
                hover = rect.move(menu_x, menu_y).collidepoint(mouse_pos)
                color = (255, 255, 0) if hover else (200, 200, 200)
                txt = btn_font.render(opt, True, color)
                menu_surf.blit(txt, txt.get_rect(center=rect.center))

            game.screen.blit(menu_surf, (menu_x, menu_y))
            pygame.display.flip()

            if t >= 1.0:
                return  
            game.clock.tick(60)


    def animate_menu_slide_up():
        slide_duration = 0.4
        start_t = pygame.time.get_ticks() / 1000.0
        while True:
            now = pygame.time.get_ticks() / 1000.0
            t = min(1.0, (now - start_t) / slide_duration)
            ease = t ** 3
            menu_y_local = int(end_y + (start_y - end_y) * ease)

            game.screen.blit(pygame.transform.scale(game.display_2, game.screen.get_size()), (0, 0))
            game.screen.blit(pygame.transform.scale(game.display, game.screen.get_size()), (0, 0))

            menu_surf_local = pygame.Surface((menu_w, menu_h), pygame.SRCALPHA)
            pygame.draw.rect(menu_surf_local, (30, 30, 30, 230), (0, 0, menu_w, menu_h), border_radius=24)
            title_surf = font.render("Paused", True, (255, 255, 255))
            title_rect_local = title_surf.get_rect(center=(menu_w // 2, 40))
            menu_surf_local.blit(title_surf, title_rect_local)
            for i, opt in enumerate(options):
                rect = pygame.Rect(30, 80 + i * 48, menu_w - 60, 40)
                txt = btn_font.render(opt, True, (200, 200, 200))
                menu_surf_local.blit(txt, txt.get_rect(center=rect.center))

            game.screen.blit(menu_surf_local, (menu_x, menu_y_local))
            pygame.display.flip()

            if t >= 1.0:
                return
            game.clock.tick(60)


    def show_settings(menu_y_current):
        text = "sorry there are no settings"
        text_surf = btn_font.render(text, True, (220, 220, 220))
        padding = 48
        msg_w = max(menu_w, text_surf.get_width() + padding)
        msg_h = max(80, text_surf.get_height() + 24)
        msg_x = menu_x - (msg_w - menu_w) // 2
        msg_start_y = menu_y_current + menu_h
        msg_end_y = msg_start_y + 8


        def draw_menu_and_panel(panel_y, panel_alpha=255):
            game.screen.blit(pygame.transform.scale(game.display_2, game.screen.get_size()), (0, 0))
            game.screen.blit(pygame.transform.scale(game.display, game.screen.get_size()), (0, 0))

            menu_surf_local = pygame.Surface((menu_w, menu_h), pygame.SRCALPHA)
            pygame.draw.rect(menu_surf_local, (30, 30, 30, 230), (0, 0, menu_w, menu_h), border_radius=24)
            title_surf = font.render("Paused", True, (255, 255, 255))
            menu_surf_local.blit(title_surf, title_surf.get_rect(center=(menu_w // 2, 40)))
            for i, opt in enumerate(options):
                rect = pygame.Rect(30, 80 + i * 48, menu_w - 60, 40)
                txt = btn_font.render(opt, True, (200, 200, 200))
                menu_surf_local.blit(txt, txt.get_rect(center=rect.center))
            game.screen.blit(menu_surf_local, (menu_x, menu_y_current))

            panel = pygame.Surface((msg_w, msg_h), pygame.SRCALPHA)
            pygame.draw.rect(panel, (40, 40, 40, 240), (0, 0, msg_w, msg_h), border_radius=12)
            panel.blit(text_surf, text_surf.get_rect(center=(msg_w // 2, msg_h // 2)))
            panel.set_alpha(panel_alpha)
            game.screen.blit(panel, (msg_x, panel_y))


        duration = 0.25
        start_t = pygame.time.get_ticks() / 1000.0
        while True:
            now = pygame.time.get_ticks() / 1000.0
            tt = min(1.0, (now - start_t) / duration)
            ease = 1 - (1 - tt) ** 3
            current_y = int(msg_start_y + (msg_end_y - msg_start_y) * ease)

            draw_menu_and_panel(current_y)
            pygame.display.flip()

            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                    animate_panel_hide(current_y, msg_start_y, msg_x, msg_w, msg_h, text_surf, menu_y_current)
                    return
                if ev.type == pygame.KEYDOWN and ev.key == pygame.K_p:
                    animate_panel_hide(current_y, msg_start_y, msg_x, msg_w, msg_h, text_surf, menu_y_current)
                    return

            if tt >= 1.0:
                break
            game.clock.tick(60)


        while True:
            draw_menu_and_panel(msg_end_y)
            pygame.display.flip()
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                    animate_panel_hide(msg_end_y, msg_start_y, msg_x, msg_w, msg_h, text_surf, menu_y_current)
                    return
                if ev.type == pygame.KEYDOWN and ev.key == pygame.K_p:
                    animate_panel_hide(msg_end_y, msg_start_y, msg_x, msg_w, msg_h, text_surf, menu_y_current)
                    return
            game.clock.tick(60)


    def animate_panel_hide(from_y, hidden_y, panel_x, panel_w, panel_h, text_surf, menu_y_current):
        hide_duration = 0.22
        start_t = pygame.time.get_ticks() / 1000.0
        start_y = from_y
        while True:
            now = pygame.time.get_ticks() / 1000.0
            t = min(1.0, (now - start_t) / hide_duration)
            ease = t ** 3
            panel_y = int(start_y + (hidden_y - start_y) * ease)
            panel_alpha = int(255 * (1 - ease * 0.6))


            game.screen.blit(pygame.transform.scale(game.display_2, game.screen.get_size()), (0, 0))
            game.screen.blit(pygame.transform.scale(game.display, game.screen.get_size()), (0, 0))

            menu_surf_local = pygame.Surface((menu_w, menu_h), pygame.SRCALPHA)
            pygame.draw.rect(menu_surf_local, (30, 30, 30, 230), (0, 0, menu_w, menu_h), border_radius=24)
            title_surf = font.render("Paused", True, (255, 255, 255))
            menu_surf_local.blit(title_surf, title_surf.get_rect(center=(menu_w // 2, 40)))
            for i, opt in enumerate(options):
                rect = pygame.Rect(30, 80 + i * 48, menu_w - 60, 40)
                txt = btn_font.render(opt, True, (200, 200, 200))
                menu_surf_local.blit(txt, txt.get_rect(center=rect.center))
            game.screen.blit(menu_surf_local, (menu_x, menu_y_current))

            panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
            pygame.draw.rect(panel, (40, 40, 40, 240), (0, 0, panel_w, panel_h), border_radius=12)
            panel.blit(text_surf, text_surf.get_rect(center=(panel_w // 2, panel_h // 2)))
            panel.set_alpha(panel_alpha)
            game.screen.blit(panel, (panel_x, panel_y))

            pygame.display.flip()

            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            if t >= 1.0:
                return
            game.clock.tick(60)

    animate_menu_drop()


    while True:
        game.screen.blit(pygame.transform.scale(game.display_2, game.screen.get_size()), (0, 0))
        game.screen.blit(pygame.transform.scale(game.display, game.screen.get_size()), (0, 0))

        menu_surf = pygame.Surface((menu_w, menu_h), pygame.SRCALPHA)
        pygame.draw.rect(menu_surf, (30, 30, 30, 230), (0, 0, menu_w, menu_h), border_radius=24)
        title_surf = font.render("Paused", True, (255, 255, 255))
        title_rect = title_surf.get_rect(center=(menu_w // 2, 40))
        menu_surf.blit(title_surf, title_rect)

        mouse_pos = pygame.mouse.get_pos()
        option_rects = []
        for i, opt in enumerate(options):
            rect = pygame.Rect(30, 80 + i * 48, menu_w - 60, 40)
            hover = rect.move(menu_x, end_y).collidepoint(mouse_pos)
            color = (255, 255, 0) if hover else (200, 200, 200)
            txt = btn_font.render(opt, True, color)
            menu_surf.blit(txt, txt.get_rect(center=rect.center))
            option_rects.append(rect.move(menu_x, end_y))

        game.screen.blit(menu_surf, (menu_x, end_y))
        pygame.display.flip()

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_p:

                animate_menu_slide_up()
                return
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                for i, rect in enumerate(option_rects):
                    if rect.collidepoint(mouse_pos):
                        if options[i] == "Play":
                            animate_menu_slide_up()
                            return
                        if options[i] == "Quit":
                            pygame.quit()
                            sys.exit()
                        if options[i] == "Settings":

                            show_settings(end_y)
        game.clock.tick(60)