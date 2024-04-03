"""
The turtle_adventure module maintains all classes related to the Turtle's
adventure game.
"""
from random import randint, choice
from math import sqrt
from turtle import RawTurtle
from gamelib import Game, GameElement


class TurtleGameElement(GameElement):
    """
    An abstract class representing all game elemnets related to the Turtle's
    Adventure game
    """

    def __init__(self, game: "TurtleAdventureGame"):
        super().__init__(game)
        self.__game: "TurtleAdventureGame" = game

    @property
    def game(self) -> "TurtleAdventureGame":
        """
        Get reference to the associated TurtleAnvengerGame instance
        """
        return self.__game


class Waypoint(TurtleGameElement):
    """
    Represent the waypoint to which the player will move.
    """

    def __init__(self, game: "TurtleAdventureGame"):
        super().__init__(game)
        self.__id1: int
        self.__id2: int
        self.__active: bool = False

    def create(self) -> None:
        self.__id1 = self.canvas.create_line(0, 0, 0, 0, width=2, fill="green")
        self.__id2 = self.canvas.create_line(0, 0, 0, 0, width=2, fill="green")

    def delete(self) -> None:
        self.canvas.delete(self.__id1)
        self.canvas.delete(self.__id2)

    def update(self, delta_time) -> None:
        # there is nothing to update because a waypoint is fixed
        pass

    def render(self) -> None:
        if self.is_active:
            self.canvas.itemconfigure(self.__id1, state="normal")
            self.canvas.itemconfigure(self.__id2, state="normal")
            self.canvas.tag_raise(self.__id1)
            self.canvas.tag_raise(self.__id2)
            self.canvas.coords(self.__id1, self.x - 10, self.y - 10,
                               self.x + 10, self.y + 10)
            self.canvas.coords(self.__id2, self.x - 10, self.y + 10,
                               self.x + 10, self.y - 10)
        else:
            self.canvas.itemconfigure(self.__id1, state="hidden")
            self.canvas.itemconfigure(self.__id2, state="hidden")

    def activate(self, x: float, y: float) -> None:
        """
        Activate this waypoint with the specified location.
        """
        self.__active = True
        self.x = x
        self.y = y

    def deactivate(self) -> None:
        """
        Mark this waypoint as inactive.
        """
        self.__active = False

    @property
    def is_active(self) -> bool:
        """
        Get the flag indicating whether this waypoint is active.
        """
        return self.__active


class Home(TurtleGameElement):
    """
    Represent the player's home.
    """

    def __init__(self, game: "TurtleAdventureGame", pos: tuple[int, int],
                 size: int):
        super().__init__(game)
        self.__id: int
        self.__size: int = size
        x, y = pos
        self.x = x
        self.y = y

    @property
    def size(self) -> int:
        """
        Get or set the size of Home
        """
        return self.__size

    @size.setter
    def size(self, val: int) -> None:
        self.__size = val

    def create(self) -> None:
        self.__id = self.canvas.create_rectangle(0,
                                                 0,
                                                 0,
                                                 0,
                                                 outline="brown",
                                                 width=2)

    def delete(self) -> None:
        self.canvas.delete(self.__id)

    def update(self, delta_time) -> None:
        # there is nothing to update, unless home is allowed to moved
        pass

    def render(self) -> None:
        self.canvas.coords(self.__id, self.x - self.size / 2,
                           self.y - self.size / 2, self.x + self.size / 2,
                           self.y + self.size / 2)

    def contains(self, x: float, y: float):
        """
        Check whether home contains the point (x, y).
        """
        x1, x2 = self.x - self.size / 2, self.x + self.size / 2
        y1, y2 = self.y - self.size / 2, self.y + self.size / 2
        return x1 <= x <= x2 and y1 <= y <= y2


class Player(TurtleGameElement):
    """
    Represent the main player, implemented using Python's turtle.
    """

    def __init__(self,
                 game: "TurtleAdventureGame",
                 turtle: RawTurtle,
                 speed: float = 5):
        super().__init__(game)
        self.__speed: float = speed
        self.__turtle: RawTurtle = turtle

    def create(self) -> None:
        turtle = RawTurtle(self.canvas)
        turtle.getscreen().tracer(False)  # disable turtle's built-in animation
        turtle.shape("turtle")
        turtle.color("green")
        turtle.penup()

        self.__turtle = turtle

    @property
    def speed(self) -> float:
        """
        Give the player's current speed.
        """
        return self.__speed

    @speed.setter
    def speed(self, val: float) -> None:
        self.__speed = val

    def delete(self) -> None:
        pass

    def update(self, delta_time) -> None:
        # check if player has arrived home
        if self.game.home.contains(self.x, self.y):
            self.game.game_over_win()
        turtle = self.__turtle
        waypoint = self.game.waypoint
        if self.game.waypoint.is_active:
            turtle.setheading(turtle.towards(waypoint.x, waypoint.y))
            delta_dis = self.speed * delta_time
            turtle.forward(delta_dis)
            if turtle.distance(waypoint.x, waypoint.y) <= delta_dis:
                waypoint.deactivate()

    def render(self) -> None:
        self.__turtle.goto(self.x, self.y)
        self.__turtle.getscreen().update()

    # override original property x's getter/setter to use turtle's methods
    # instead
    @property
    def x(self) -> float:
        return self.__turtle.xcor()

    @x.setter
    def x(self, val: float) -> None:
        self.__turtle.setx(val)

    # override original property y's getter/setter to use turtle's methods
    # instead
    @property
    def y(self) -> float:
        return self.__turtle.ycor()

    @y.setter
    def y(self, val: float) -> None:
        self.__turtle.sety(val)


class Enemy(TurtleGameElement):
    """
    Define an abstract enemy for the Turtle's adventure game
    """

    def __init__(self, game: "TurtleAdventureGame", size: int, color: str, speed: float = 100):
        super().__init__(game)
        self.__size = size
        self.__color = color
        self.__speed = speed

    @property
    def speed(self) -> float:
        """
        Get the speed of the enemy
        """
        return self.__speed

    @property
    def size(self) -> float:
        """
        Get the size of the enemy
        """
        return self.__size

    @property
    def color(self) -> str:
        """
        Get the color of the enemy
        """
        return self.__color

    def hits_player(self):
        """
        Check whether the enemy is hitting the player
        """
        plr = self.game.player
        return (self.x-plr.x)**2 + (self.y-plr.y)**2 <= (self.size/2 + 9) ** 2


# TODO
# * Define your enemy classes
# * Implement all methods required by the GameElement abstract class
# * Define enemy's update logic in the update() method
# * Check whether the player hits this enemy, then call the
#   self.game.game_over_lose() method in the TurtleAdventureGame class.


class RandomWalkEnemy(Enemy):
    """
    Random Walk Enemy
    """

    __sprite: int
    __tarx: float
    __tary: float

    def __init__(self, game: "TurtleAdventureGame", size: int, color: str, speed: float):
        super().__init__(game, size, color, speed)
        self.x, self.y = randint(0, self.game.screen_width), randint(
            0, self.game.screen_height)
        self.__tarx, self.__tary = randint(0, self.game.screen_width), randint(
            0, self.game.screen_height)

    def create(self) -> None:
        self.__sprite = self.canvas.create_oval(self.x,
                                                self.y,
                                                self.x + self.size,
                                                self.y + self.size,
                                                width=0,
                                                fill=self.color)

    def update(self, delta_time) -> None:
        dif_x = self.__tarx - self.x
        dif_y = self.__tary - self.y
        dist_sq = dif_x**2 + dif_y**2
        if dist_sq < delta_time * self.speed**2:
            self.__tarx, self.__tary = randint(
                0, self.game.screen_width), randint(0, self.game.screen_height)
            return self.update(delta_time)
        dist = sqrt(dist_sq)
        self.x += (dif_x / dist) * delta_time * self.speed
        self.y += (dif_y / dist) * delta_time * self.speed
        if self.hits_player():
            self.game.game_over_lose()

    def render(self) -> None:
        self.canvas.coords(self.__sprite, self.x, self.y, self.x + self.size,
                           self.y + self.size)

    def delete(self) -> None:
        self.canvas.delete(self.__sprite)


class ChasingEnemy(Enemy):
    """
    Chasing Enemy
    """

    __sprite: int

    def __init__(self, game: "TurtleAdventureGame", size: int, color: str, speed: float):
        super().__init__(game, size, color, speed)
        self.x, self.y = randint(0, self.game.screen_width), randint(
            0, self.game.screen_height)

    def create(self) -> None:
        self.__sprite = self.canvas.create_oval(self.x,
                                                self.y,
                                                self.x + self.size,
                                                self.y + self.size,
                                                width=0,
                                                fill=self.color)

    def update(self, delta_time) -> None:
        plr = self.game.player
        dif_x = plr.x - self.x
        dif_y = plr.y - self.y
        dist = sqrt(dif_x**2 + dif_y**2)
        self.x += (dif_x / dist) * delta_time * self.speed
        self.y += (dif_y / dist) * delta_time * self.speed
        if self.hits_player():
            self.game.game_over_lose()

    def render(self) -> None:
        self.canvas.coords(self.__sprite, self.x, self.y, self.x + self.size,
                           self.y + self.size)

    def delete(self) -> None:
        self.canvas.delete(self.__sprite)


class FencingEnemy(Enemy):
    """
    Fencing Enemy
    """

    __sprite: int
    __tar_corner: int
    __dir: bool
    __radius: int

    def __init__(self, game: "TurtleAdventureGame", size: int, color: str, speed: float):
        super().__init__(game, size, color, speed)
        self.x, self.y = randint(0, self.game.screen_width), randint(
            0, self.game.screen_height)
        self.__tar_corner = randint(0, 3)
        self.__dir = choice((True, False))
        self.__radius = randint(60, 100)

    def create(self) -> None:
        self.__sprite = self.canvas.create_oval(self.x,
                                                self.y,
                                                self.x + self.size,
                                                self.y + self.size,
                                                width=0,
                                                fill=self.color)

    def update(self, delta_time) -> None:
        home = self.game.home
        dif_x = home.x + self.__radius*(-1, 1, 1, -1)[self.__tar_corner] - self.x
        dif_y = home.y + self.__radius*(-1, 1)[self.__tar_corner // 2] - self.y
        dist_sq = dif_x**2 + dif_y**2
        if dist_sq < delta_time * self.speed**2:
            self.__tar_corner = (self.__tar_corner + (1, -1)[self.__dir]) % 4
            return self.update(delta_time)
        dist = sqrt(dist_sq)
        self.x += (dif_x / dist) * delta_time * self.speed
        self.y += (dif_y / dist) * delta_time * self.speed
        if self.hits_player():
            self.game.game_over_lose()

    def render(self) -> None:
        self.canvas.coords(self.__sprite, self.x, self.y, self.x + self.size,
                           self.y + self.size)

    def delete(self) -> None:
        self.canvas.delete(self.__sprite)


class DemoEnemy(Enemy):
    """
    Demo enemy
    """

    def __init__(self, game: "TurtleAdventureGame", size: int, color: str):
        super().__init__(game, size, color)

    def create(self) -> None:
        pass

    def update(self, delta_time) -> None:
        pass

    def render(self) -> None:
        pass

    def delete(self) -> None:
        pass


# TODO
# Complete the EnemyGenerator class by inserting code to generate enemies
# based on the given game level; call TurtleAdventureGame's add_enemy() method
# to add enemies to the game at certain points in time.
#
# Hint: the 'game' parameter is a tkinter's frame, so it's after()
# method can be used to schedule some future events.


class EnemyGenerator:
    """
    An EnemyGenerator instance is responsible for creating enemies of various
    kinds and scheduling them to appear at certain points in time.
    """

    def __init__(self, game: "TurtleAdventureGame", level: int):
        self.__game: TurtleAdventureGame = game
        self.__level: int = level

    @property
    def game(self) -> "TurtleAdventureGame":
        """
        Get reference to the associated TurtleAnvengerGame instance
        """
        return self.__game

    @property
    def level(self) -> int:
        """
        Get the game level
        """
        return self.__level

    @level.setter
    def level(self, new_level: int) -> None:
        """
        Sets the game level.
        """
        self.__level = new_level

    def generate_spawnpos(self):
        """Generates enemy spawn position.
        """
        if choice((True, False)):
            x = choice((0, self.game.screen_width))
            return (x, randint(0, self.game.screen_height))
        y = choice((0, self.game.screen_height))
        return (randint(0, self.game.screen_width), y)

    def create_enemy(self) -> None:
        """
        Create a new enemy, possibly based on the game level
        """
        enemies_to_spawn = 3 * self.level
        if len(self.game.enemies) >= enemies_to_spawn:
            return
        delay = int(3000/enemies_to_spawn)
        enemy_type = choice((RandomWalkEnemy, ChasingEnemy, FencingEnemy))
        new_enemy = enemy_type(self.__game, choice((15, 20, 30)),
                               choice(("red", "green", "blue")), speed=150+randint(0, 30))
        new_enemy.x, new_enemy.y = self.generate_spawnpos()
        self.game.add_enemy(new_enemy)
        self.game.after(delay, self.create_enemy)


class TurtleAdventureGame(Game):  # pylint: disable=too-many-ancestors
    """
    The main class for Turtle's Adventure.
    """

    # pylint: disable=too-many-instance-attributes
    def __init__(self,
                 parent,
                 screen_width: int,
                 screen_height: int,
                 level: int = 1):
        self.level: int = level
        self.screen_width: int = screen_width
        self.screen_height: int = screen_height
        self.waypoint: Waypoint
        self.player: Player
        self.home: Home
        self.enemies: list[Enemy] = []
        self.enemy_generator: EnemyGenerator
        super().__init__(parent, 0)

    def init_game(self):
        self.canvas.config(width=self.screen_width, height=self.screen_height)
        turtle = RawTurtle(self.canvas)
        # set turtle screen's origin to the top-left corner
        turtle.screen.setworldcoordinates(0, self.screen_height - 1,
                                          self.screen_width - 1, 0)

        self.waypoint = Waypoint(self)
        self.add_element(self.waypoint)
        self.home = Home(self,
                         (self.screen_width - 100, self.screen_height // 2),
                         20)
        self.add_element(self.home)
        self.player = Player(self, turtle, speed=180)
        self.add_element(self.player)
        self.canvas.bind("<Button-1>",
                         lambda e: self.waypoint.activate(e.x, e.y))

        self.enemy_generator = EnemyGenerator(self, level=self.level)

    def start_game(self):
        """Starts the game.
        """
        self.player.x = 50
        self.player.y = self.screen_height // 2
        self.start()
        self.enemy_generator.create_enemy()

    def add_enemy(self, enemy: Enemy) -> None:
        """
        Add a new enemy into the current game
        """
        self.enemies.append(enemy)
        self.add_element(enemy)

    def game_over_win(self) -> None:
        """
        Called when the player wins the game and stop the game
        """
        self.stop()
        font = ("Arial", 36, "bold")
        text_id = self.canvas.create_text(self.screen_width / 2,
                                          self.screen_height / 2,
                                          text="You Win",
                                          font=font,
                                          fill="green")
        self.after(2000,
                   lambda: self.canvas.delete(text_id) or self.new_game())

    def new_game(self):
        """Starts a new game.
        """
        self.level += 1
        self.enemy_generator.level = self.level
        for enemy in self.enemies:
            self.delete_element(enemy)
        self.enemies.clear()
        self.enemy_generator.create_enemy()
        self.start_game()

    def game_over_lose(self) -> None:
        """
        Called when the player loses the game and stop the game
        """
        self.stop()
        self.render()
        font = ("Arial", 36, "bold")
        self.canvas.create_text(self.screen_width / 2,
                                self.screen_height / 2,
                                text="You Lose",
                                font=font,
                                fill="red")
