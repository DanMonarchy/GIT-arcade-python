import arcade
import time
import arcade.gui
import random
import math
from array import array
from dataclasses import dataclass
import arcade.gl

from arcade.experimental.lights import Light, LightLayer




SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 650
SCREEN_TITLE = "Сумеречная охота на монетки"
SPRITE_SCALING_PLAYER = 1
SPRITE_NATIVE_SIZE = 128
SPRITE_SIZE = int(SPRITE_NATIVE_SIZE * SPRITE_SCALING_PLAYER)

#cветик
VIEWPORT_MARGIN = 200
AMBIENT_COLOR = (10, 10, 10)

@dataclass
class Burst:
    buffer: arcade.gl.Buffer
    vao: arcade.gl.Geometry
    start_time: float

DEAD_ZONE=0.1
RIGHT_FACING=0
LEFT_FACING=1
DISTANCE_TO_CHANGE_TEXTURE=20

TILE_SCALING = 0.5

#монеточка
COIN_COUNT = 1
AL_COUNT = 5

PARTICLE_COUNT = 1000 # колличество частиц
MIN_FADE_TIME = 0.25
MAX_FADE_TIME = 3.5

#гравитация
GRAVITY = 2000

DEFAULT_DAMPING = 1.0
PLAYER_DAMPING = 0.4

PLAYER_FRICTION = 9
WALL_FRICTION = 99
DYNAMIC_ITEM_FRICTION = 99

PLAYER_MASS = 2.0

PLAYER_MAX_HORIZONTAL_SPEED = 450
PLAYER_MAX_VERTICAL_SPEED = 1600
PLAYER_MOVE_FORCE_ON_GROUND = 8000
PLAYER_JUMP_IMPULSE = 1800


class Settings(arcade.View):
    def __init__(self, game_view):
        super().__init__()
        self.background_sprite_list = None
        self.background_sprite_list = arcade.SpriteList()
        self.game_view = game_view
        sprite = arcade.Sprite("resources/settings.png")
        sprite.position = 500, 325
        self.background_sprite_list.append(sprite)

    def on_show_view(self):
        arcade.set_background_color(arcade.color.GRAY)

    def on_draw(self):
        self.clear()
        self.background_sprite_list.draw()

    def on_key_press(self, key, _modifiers):
        if key == arcade.key.ESCAPE:
            arcade.exit()
        elif key == arcade.key.ENTER:
            game = MenuView()
            self.window.show_view(game)


class ParticleBurstApp:
    def __init__(self, context):
        self.ctx = context # функции для графики
        self.burst_list = [] # всплески все, список

        # Load shaders
        self.program = self.ctx.load_program(
            vertex_shader="vertex_shader_v1.glsl",
            fragment_shader="fragment_shader.glsl",
        )
        self.ctx.enable_only(self.ctx.BLEND)

    def emit_burst(self, x, y): #функция для создания всплеска

        def _gen_initial_data(initial_x, initial_y):  # функция для генерации начальных данных для частиц
            for i in range(PARTICLE_COUNT):
                angle = random.uniform(0, 2 * math.pi)
                speed = abs(random.gauss(0, 9)) * 0.01
                dx = math.sin(angle) * speed
                dy = math.cos(angle) * speed
                red = random.uniform(0.1, 1.0)
                green = random.uniform(0, red)
                blue = 0
                fade_rate = random.uniform(1 / MAX_FADE_TIME, 1 / MIN_FADE_TIME)

                yield initial_x
                yield initial_y
                yield dx
                yield dy
                yield red
                yield green
                yield blue
                yield fade_rate

        # Transform mouse coordinates to OpenGL coordinates
        x2 = x / SCREEN_WIDTH * 2. - 1.
        y2 = y / SCREEN_HEIGHT * 2. - 1.

        initial_data = _gen_initial_data(x2, y2)
        buffer = self.ctx.buffer(data=array('f', initial_data))

        buffer_description = arcade.gl.BufferDescription(buffer,
                                                         '2f 2f 3f f',
                                                         ['in_pos', 'in_vel', 'in_color', 'in_fade_rate'])
        vao = self.ctx.geometry([buffer_description])
        burst = Burst(buffer=buffer, vao=vao, start_time=time.time())
        self.burst_list.append(burst)

    def draw(self):
        for burst in self.burst_list:
            self.program['time'] = time.time() - burst.start_time
            burst.vao.render(self.program, mode=self.ctx.POINTS)

    def update(self):
        temp_list = self.burst_list.copy()
        for burst in temp_list:
            if time.time() - burst.start_time > MAX_FADE_TIME:
                self.burst_list.remove(burst)

    class Settings(arcade.View):
        def __init__(self, game_view):
            super().__init__()
            self.game_view = game_view

        def on_show_view(self):
            arcade.set_background_color(arcade.color.GRAY)

        def on_draw(self):
            self.clear()
            arcade.draw_text("НАСТРОЙКИ", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 50,
                             arcade.color.WHITE, font_size=50, anchor_x="center")
            arcade.draw_text("Нажмите ESC для выхода",
                             SCREEN_WIDTH / 2,
                             SCREEN_HEIGHT / 2,
                             arcade.color.WHITE,
                             font_size=20,
                             anchor_x="center")
            arcade.draw_text("Нажмите Enter чтобы продолжить",
                             SCREEN_WIDTH / 2,
                             SCREEN_HEIGHT / 2 - 30,
                             arcade.color.WHITE,
                             font_size=20,
                             anchor_x="center")

        def on_key_press(self, key, _modifiers):
            if key == arcade.key.ESCAPE:
                self.game_view = MenuView()
                self.window.show_view(self.game_view)
            elif key == arcade.key.ENTER:
                game = GameView()
                self.window.show_view(game)
class PauseView(arcade.View):
    def __init__(self, game_view):
        super().__init__()
        self.game_view = game_view
        self.background_sprite_list = None
        self.background_sprite_list = arcade.SpriteList()
        sprite = arcade.Sprite("resources/Pause.png")
        sprite.position = 500, 325
        self.background_sprite_list.append(sprite)

    def on_show_view(self):
        arcade.set_background_color(arcade.color.GRAY)

    def on_draw(self):
        self.clear()
        self.background_sprite_list.draw()


    def on_key_press(self, key, _modifiers):
        if key == arcade.key.ESCAPE:
            self.game_view = MenuView()
            self.window.show_view(self.game_view)
        elif key == arcade.key.ENTER:
            game = GameView()
            self.window.show_view(game)

class MenuView(arcade.View):
    def on_show_view(self):
        self.background_sprite_list = None
        self.background_sprite_list = arcade.SpriteList()
        self.set_mouse_visible = True
        self.manager = arcade.gui.UIManager()
        self.manager.enable()
        arcade.set_background_color(arcade.color.GRAY)
        self.v_box = arcade.gui.UIBoxLayout()

        start_button = arcade.gui.UIFlatButton(text="Начать игру", width=200)
        self.v_box.add(start_button.with_space_around(bottom=20))

        settings_button = arcade.gui.UIFlatButton(text="Настройки", width=200)
        self.v_box.add(settings_button.with_space_around(bottom=20))


        quit_button = QuitButton(text="Выход", width=200)
        self.v_box.add(quit_button)


        start_button.on_click = self.on_click_start


        @settings_button.event("on_click")
        def on_click_settings(event):
            game_view = Settings(self)
            self.window.show_view(game_view)
            print("Settings:", event)

        self.manager.add(
            arcade.gui.UIAnchorWidget(
                anchor_x="center_x",
                anchor_y="center_y",
                child=self.v_box)
        )
        sprite = arcade.Sprite("resources/menu.png")
        sprite.position = 500, 325
        self.background_sprite_list.append(sprite)

    def on_draw(self):
        self.clear()
        self.background_sprite_list.draw()
        self.manager.draw()


    def on_click_start(self, event):
        game_view = GameView()
        self.window.show_view(game_view)
        self.manager.disable()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            arcade.exit()

class QuitButton(arcade.gui.UIFlatButton):
    def on_click(self, event: arcade.gui.UIOnClickEvent):
        arcade.exit()
class PlayerSprite(arcade.Sprite):
    def __init__(self):
        super().__init__()

        self.scale = SPRITE_SCALING_PLAYER
        main_path ="resources/male_person/malePerson"
        self.idle_texture_pair = arcade.load_texture_pair(f"{main_path}_idle.png")
        self.jump_texture_pair = arcade.load_texture_pair(f"{main_path}_jump.png")
        self.fall_texture_pair = arcade.load_texture_pair(f"{main_path}_fall.png")
        self.walk_textures = []
        for i in range(8):
            texture = arcade.load_texture_pair(f"{main_path}_walk{i}.png")
            self.walk_textures.append(texture)
        self.texture = self.idle_texture_pair[0]
        self.hit_box = self.texture.hit_box_points
        self.character_face_direction = RIGHT_FACING
        self.cur_texture = 0
        self.x_odometer = 0

    def pymunk_moved(self, physics_engine, dx, dy, d_angle):
        if dx < -DEAD_ZONE and self.character_face_direction ==RIGHT_FACING:
            self.character_face_direction = LEFT_FACING
        elif dx > DEAD_ZONE and self.character_face_direction ==LEFT_FACING:
            self.character_face_direction = RIGHT_FACING
        is_on_ground = physics_engine.is_on_ground(self)
        self.x_odometer += dx
        if not is_on_ground:
            if dy > DEAD_ZONE:
                self.texture = self.jump_texture_pair[self.character_face_direction]
                return
            elif dy < -DEAD_ZONE:
                self.texture = self.fall_texture_pair[self.character_face_direction]
                return
        if abs(dx) <= DEAD_ZONE:
            self.texture = self.idle_texture_pair[self.character_face_direction]
            return
        if abs(self.x_odometer) > DISTANCE_TO_CHANGE_TEXTURE:
            self.x_odometer = 0
            self.cur_texture += 1
            if self.cur_texture > 7:
                self.cur_texture = 0
            self.texture = self.walk_textures[self.cur_texture][self.character_face_direction]

class GameOverView(arcade.View):
    def on_show_view(self):
        self.set_mouse_visible = True
        self.manager = arcade.gui.UIManager()
        self.manager.enable()
        arcade.set_background_color(arcade.color.AIR_FORCE_BLUE)
        self.v_box = arcade.gui.UIBoxLayout()
        over_button = arcade.gui.UIFlatButton(text="Вы проиграли - кликните для выхода в меню!", width=2000)
        self.v_box.add(over_button.with_space_around(bottom=20))
        over_button.on_click = self.on_click_over
        self.manager.add(
            arcade.gui.UIAnchorWidget(
                anchor_x="center_x",
                anchor_y="center_y",
                child=self.v_box)
        )
    def on_draw(self):
        self.clear()
        self.manager.draw()


    def on_click_over(self, event):
        game_view = MenuView()
        self.window.show_view(game_view)

class GameWinView(arcade.View):
        def on_show_view(self):

            arcade.set_background_color(arcade.color.GLAUCOUS)

        def on_draw(self):
            self.clear()
            arcade.draw_text("Вы выиграли - кликните для выхода в меню!", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2,
                             arcade.color.WHITE, 30, anchor_x="center", )

        def on_mouse_press(self, _x, _y, _button, _modifiers):
            game_view = MenuView()
            self.window.show_view(game_view)



class GameView(arcade.View):
    def __init__(self):
        super().__init__()
        self.width = SCREEN_WIDTH
        self.height = SCREEN_HEIGHT
        self.background_sprite_list = None
        self.view_left = 0
        self.view_bottom = 0
        self.light_layer = None
        self.player_light = None
        self.set_mouse_visible = False
        self.manager = arcade.gui.UIManager()
        self.manager.disable()
        self.health = 100
        self.score = 0
        self.player = None
        self.money = arcade.sound.load_sound("sounds/coin5.wav")
        self.death = arcade.sound.load_sound("sounds/gameover2.wav")
        self.background_music = arcade.sound.load_sound('sounds/Home.wav')
        self.background_music_sound = arcade.sound.play_sound(self.background_music, 0.3)
        self.jump = arcade.sound.load_sound("sounds/jump1.wav")
        self.coin_list = None
        self.al_list = None
        self.enemy_list = None
        self.game_over = False
        self.player_sprite = PlayerSprite()
        self.player_list = None
        self.left_pressed = False
        self.right_pressed = False
        self.physics_engine = None
        self.enemy = None
        self.enemy_list = None
        self.game = True
        self.particle_burst = ParticleBurstApp(self.window.ctx)

    def on_show_view(self):
        self.setup()

    def setup(self):
        self.width = SCREEN_WIDTH
        self.height = SCREEN_HEIGHT
        self.score = 0
        self.health = 100
        self.background_sprite_list = arcade.SpriteList()
        self.coin_list = arcade.SpriteList()
        self.al_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()
        self.player_list = arcade.SpriteList()
        self.box_list = arcade.SpriteList()

        arcade.set_background_color(arcade.color.BABY_BLUE)

        self.wall_list = arcade.SpriteList(use_spatial_hash=True)
        self.box_list = arcade.SpriteList(use_spatial_hash=True)
        coordinate_list = [[512, 350], ]
        for coordinate in coordinate_list:
            box = arcade.Sprite("resources/boxCrate_double.png",
                                                               TILE_SCALING)
            box.position = coordinate
            self.wall_list.append(box)

        coordinate_list = [[450, 350], ]
        for coordinate in coordinate_list:
            box = arcade.Sprite("resources/boxCrate_double.png",
                                TILE_SCALING)
            box.position = coordinate
            self.wall_list.append(box)

        coordinate_list = [[650, 500], ]
        for coordinate in coordinate_list:
            box = arcade.Sprite("resources/boxCrate_double.png",
                                TILE_SCALING)
            box.position = coordinate
            self.wall_list.append(box)

        coordinate_list = [[710, 500], ]
        for coordinate in coordinate_list:
            box = arcade.Sprite("resources/boxCrate_double.png",
                                TILE_SCALING)
            box.position = coordinate
            self.wall_list.append(box)
        coordinate_list = [[770, 500], ]
        for coordinate in coordinate_list:
            box = arcade.Sprite("resources/boxCrate_double.png",
                                TILE_SCALING)
            box.position = coordinate
            self.wall_list.append(box)
        coordinate_list = [[230, 160], ]
        for coordinate in coordinate_list:
            box = arcade.Sprite("resources/boxCrate_double.png",
                                TILE_SCALING)
            box.position = coordinate
            self.wall_list.append(box)

        coordinate_list = [[290, 160], ]
        for coordinate in coordinate_list:
            box = arcade.Sprite("resources/boxCrate_double.png",
                                TILE_SCALING)
            box.position = coordinate
            self.wall_list.append(box)

        for x in range(0, 600, 95):
            wall = arcade.Sprite("resources/wall.png",
                                 SPRITE_SCALING_PLAYER)
            wall.center_x = 1
            wall.center_y = x
            self.wall_list.append(wall)
        for x in range(0, 600, 95):
            wall = arcade.Sprite("resources/wall.png",
                                 SPRITE_SCALING_PLAYER)
            wall.center_x = 995
            wall.center_y = x
            self.wall_list.append(wall)


        for x in range(0, SCREEN_WIDTH, SPRITE_SIZE):
            wall = arcade.Sprite("resources/grassMid.png", SPRITE_SCALING_PLAYER)
            wall.bottom = 0
            wall.left = x
            self.wall_list.append(wall)
        self.physics_engine = arcade.PhysicsEnginePlatformer(self.player, self.wall_list, gravity_constant=GRAVITY)

        for i in range(AL_COUNT):
            al = arcade.Sprite("resources/al_1.png",
                                 scale=0.8)
            al.center_x = 800
            al.center_y = 150
            self.al_list.append(al)

        for i in range(COIN_COUNT):
            coin = arcade.Sprite("resources/gold_1.png",
                                 scale=0.8)
            coin.center_x = 770
            coin.center_y = 570
            self.coin_list.append(coin)
        for i in range(COIN_COUNT):
            coin = arcade.Sprite("resources/gold_1.png",
                                 scale=0.8)
            coin.center_x = 500
            coin.center_y = 420
            self.coin_list.append(coin)
        for i in range(COIN_COUNT):
            coin = arcade.Sprite("resources/gold_1.png",
                                 scale=0.8)
            coin.center_x = 250
            coin.center_y = 230
            self.coin_list.append(coin)
        enemy = arcade.Sprite("resources/bee.png", scale=0.8)

        enemy.bottom = 150
        enemy.left = SPRITE_SIZE * 2.7
        enemy.change_x = 2
        self.enemy_list.append(enemy)

        grid_y = 1
        self.player_list = arcade.SpriteList()
        self.player_sprite.center_x = 150
        self.player_sprite.center_y = SPRITE_SIZE * grid_y + SPRITE_SIZE / 2
        self.player_list.append(self.player_sprite)

        sprite = arcade.Sprite("resources/fon.png")
        sprite.position = 500, 325
        self.background_sprite_list.append(sprite)

        radius = 150
        mode = 'soft'
        color = arcade.csscolor.WHITE
        self.player_light = Light(0, 0, radius, color, mode)

        self.physics_engine = arcade.PhysicsEngineSimple(self.player_sprite, self.wall_list)
        self.view_left = 0
        self.view_bottom = 0
        self.light_layer = LightLayer(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.light_layer.set_background_color(arcade.color.BLACK)
        damping = DEFAULT_DAMPING
        gravity = (0, -GRAVITY)
        self.physics_engine = arcade.PymunkPhysicsEngine(damping=damping,
                                                         gravity=gravity)

        self.physics_engine.add_sprite(self.player_sprite,
                                       friction=PLAYER_FRICTION,
                                       mass=PLAYER_MASS,
                                       moment=arcade.PymunkPhysicsEngine.MOMENT_INF,
                                       collision_type="player",
                                       max_horizontal_velocity=PLAYER_MAX_HORIZONTAL_SPEED,
                                       max_vertical_velocity=PLAYER_MAX_VERTICAL_SPEED)

        self.physics_engine.add_sprite_list(self.wall_list,
                                            friction=WALL_FRICTION,
                                            collision_type="wall",
                                            body_type=arcade.PymunkPhysicsEngine.STATIC)

        self.physics_engine.add_sprite_list(self.enemy_list,
                                            friction=DYNAMIC_ITEM_FRICTION,
                                            collision_type="enemy")


        def item_hit_handler(player, item_sprite, _arbiter, _space, _data):
            item_sprite.remove_from_sprite_lists()
            self.particle_burst.emit_burst(item_sprite.center_x, item_sprite.center_y)

        self.physics_engine.add_collision_handler("player", "item", post_handler=item_hit_handler)

        def enemy_hit_handler(player, enemy, _arbiter, _space, _data):
           t = time.time()
           if time.time() - t <=1:
               t = time.time()
               self.health -= 1

        self.physics_engine.add_collision_handler("player", "enemy", post_handler=enemy_hit_handler)

    def on_draw(self):
        self.clear()
        with self.light_layer:

            self.background_sprite_list.draw()
            self.coin_list.draw()
            self.al_list.draw()
            self.wall_list.draw()
            self.box_list.draw()
            self.enemy_list.draw()
            self.player_list.draw()
            self.particle_burst.draw()
        self.light_layer.draw(ambient_color=AMBIENT_COLOR)
        arcade.draw_text("Нажмите SPACE чтобы вкл/выкл свет",
                         250 + self.view_left, 40 + self.view_bottom,
                         arcade.color.WHITE, 20)

        score_text = f"Монеты: {self.score}"
        arcade.draw_text(score_text,
                         start_x=10,
                         start_y=10,
                         color=arcade.csscolor.WHITE,
                         font_size=18)
        health_text = f"Жизни: {self.health} % "
        arcade.draw_text(health_text,
                         start_x=10,
                         start_y=40,
                         color=arcade.csscolor.RED,
                         font_size=18)
    def on_resize(self, width, height):

        self.light_layer.resize(width, height)

    def on_key_press(self, key, modifiers):
        if key == arcade.key.P:
                arcade.stop_sound(self.background_music_sound)
                self.V = True
        if key == arcade.key.O and self.V == True:
                self.background_music_sound = arcade.sound.play_sound(self.background_music, 0.3)
                self.V = False
        if key == arcade.key.ESCAPE:
            arcade.stop_sound(self.background_music_sound)
            pause = PauseView(self)
            self.window.show_view(pause)


        if key == arcade.key.LEFT:
            self.left_pressed = True
        elif key == arcade.key.RIGHT:
            self.right_pressed = True
        elif key == arcade.key.UP:
            if self.physics_engine.is_on_ground(self.player_sprite):
                impulse = (0, PLAYER_JUMP_IMPULSE)
                arcade.sound.play_sound(self.jump)
                self.physics_engine.apply_impulse(self.player_sprite, impulse)
        elif key == arcade.key.SPACE:
            if self.player_light in self.light_layer:
                self.light_layer.remove(self.player_light)
            else:
                self.light_layer.add(self.player_light)




    def on_key_release(self, key, modifiers):
        if key == arcade.key.LEFT:
            self.left_pressed = False
        elif key == arcade.key.RIGHT:
            self.right_pressed = False


    def on_update(self, delta_time):

            if self.game:

                self.particle_burst.update()
                self.player_light.position = self.player_sprite.position
                hit_list = arcade.check_for_collision_with_list(self.player_sprite, self.coin_list)
                for coin in hit_list:
                    self.score += 1
                    coin.remove_from_sprite_lists()
                    arcade.sound.play_sound(self.money)

                hit_list = arcade.check_for_collision_with_list(self.player_sprite, self.al_list)
                for al in hit_list:
                    self.score += 5
                    al.remove_from_sprite_lists()
                    arcade.sound.play_sound(self.money) #поменять звук алмаза


                if self.left_pressed and not self.right_pressed:
                    force = (-PLAYER_MOVE_FORCE_ON_GROUND, 0)
                    self.physics_engine.apply_force(self.player_sprite, force)
                    self.physics_engine.set_friction(self.player_sprite, 0)
                elif self.right_pressed and not self.left_pressed:
                    force = (PLAYER_MOVE_FORCE_ON_GROUND, 0)
                    self.physics_engine.apply_force(self.player_sprite, force)
                    self.physics_engine.set_friction(self.player_sprite, 0)
                else:
                    self.physics_engine.set_friction(self.player_sprite, 1.0)
                self.physics_engine.step()
                if self.health == 1:
                    self.player_sprite.center_x = 150
                    self.player_sprite.center_y = SPRITE_SIZE * 1 + SPRITE_SIZE / 2


            if self.health == 0:

                    arcade.sound.play_sound(self.death)
                    arcade.stop_sound(self.background_music_sound)
                    game_over = GameOverView()
                    self.window.show_view(game_over)
                    return


            if len(self.coin_list) == 0:
                arcade.stop_sound(self.background_music_sound)
                view = GameWinView()
                self.window.show_view(view)

def main():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT,SCREEN_TITLE)
    menu_view = MenuView()
    window.show_view(menu_view)
    arcade.run()

if __name__ == "__main__":
    main()
