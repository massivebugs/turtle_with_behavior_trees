import turtle
import math
import time
import py_trees

import utils
import turtle_food
import constants


class Bot():
    velocity = 3
    speech_bubble = utils.Text(turtle.Turtle())
    hunger_state = "normal"
    last_time_without_food_ms = utils.get_now_ms()
    current_closest_food: turtle_food.Food = None

    def __init__(self, t: turtle.Turtle) -> None:
        t.shape("turtle")
        self.t = t

    def get_eat_distance_threshold(self) -> int:
        # **2 since we are only using distance for comparison
        return self.velocity ** 2

    def move(self, pos: tuple) -> None:
        current_pos = self.pos()
        angle = self.t.towards(pos[0], pos[1])
        self.t.setheading(angle)
        x = current_pos[0] + math.cos(math.radians(angle)) * self.velocity
        y = current_pos[1] + math.sin(math.radians(angle)) * self.velocity
        self.t.goto(x, y)

    def pos(self) -> tuple:
        return self.t.xcor(), self.t.ycor()

    def calculate_step_position(self, pos: tuple) -> tuple:
        [bot_x, bot_y] = self.pos()
        angle = self.t.towards(pos[0], pos[1])

        x = bot_x + math.cos(math.radians(angle)) * self.velocity
        y = bot_y + math.sin(math.radians(angle)) * self.velocity

        return angle, x, y

    def get_closest_food(self, food: list) -> int | None:
        if len(food) == 0:
            return None

        current = food[0]
        current_dist = self.get_distance_from_food(food[0])
        for f in food[1:]:
            dist = self.get_distance_from_food(f)

            if current_dist > dist:
                current = f
                current_dist = dist

        return current

    def get_distance_from_food(self, food: turtle_food.Food) -> float:
        [t_x, t_y] = self.pos()
        [f_x, f_y] = food.pos()
        # We are only going to compare the distances so sqrt is unnecessary
        # return math.sqrt((t_x - f_x) ** 2 + (t_y - f_y) ** 2)
        distance_squared = (t_x - f_x) ** 2 + (t_y - f_y) ** 2
        return distance_squared

    def eat(self, food: turtle_food.Food) -> bool:
        dist = self.get_distance_from_food(food)
        if dist <= self.get_eat_distance_threshold():
            return True
        return False

    def get_time_without_food_ms(self) -> float:
        return utils.get_now_ms() - self.last_time_without_food_ms

    def do_turtle_thing(self, feed: turtle_food.Feed) -> bool:
        closest_food = self.get_closest_food(feed.placed_food)
        now_ms = time.time()

        if (self.last_time_without_food == 0):
            self.last_time_without_food = now_ms

        no_food_ms = self.time_without_food_ms(now_ms)

        if closest_food != None:
            self.speech_bubble.clear()
            self.move(closest_food.pos())

            eaten = self.eat(closest_food)
            if eaten:
                feed.remove_food(closest_food)
                self.speech_bubble.write(self.pos(), "うまい！٩(ˊᗜˋ*)و")
                self.last_time_without_food = now_ms
                self.hunger_state = "normal"
                self.velocity = 3

        elif no_food_ms > 20 and self.hunger_state == "hungry":
            self.speech_bubble.clear()
            self.speech_bubble.write(self.pos(), "お腹すいて死にそうだよおおお( ´༎ຶㅂ༎ຶ`)")
            self.hunger_state = "dying"
            self.velocity = 10

        elif no_food_ms > 5 and self.hunger_state == "normal":
            self.speech_bubble.clear()
            self.speech_bubble.write(self.pos(), "お腹すいた！ご飯くれる？(´ﾟωﾟ｀)")
            self.hunger_state = "hungry"
            self.velocity = 5


class TurtleFindClosestFood(py_trees.behaviour.Behaviour):
    def __init__(self, name: str, bot: Bot):
        super().__init__(name)
        self.bot = bot
        self.bb = self.attach_blackboard_client(name=constants.BLACKBOARD_NAME)
        self.bb.register_key("placed_food", access=py_trees.common.Access.READ)


    def update(self) -> py_trees.common.Status:
        placed_food = self.bb.placed_food

        if len(placed_food) == 0:
            self.bot.current_closest_food = None
            return py_trees.common.Status.FAILURE

        current = placed_food[0]
        current_dist = self.bot.get_distance_from_food(placed_food[0])
        for f in placed_food[1:]:
            dist = self.bot.get_distance_from_food(f)

            if current_dist > dist:
                current = f
                current_dist = dist

        self.bot.current_closest_food = current
        return py_trees.common.Status.SUCCESS


class TurtleMoveToClosestFood(py_trees.behaviour.Behaviour):
    def __init__(self, name: str, bot: Bot):
        super().__init__(name)
        self.bot = bot
        self.bb = self.attach_blackboard_client(name=constants.BLACKBOARD_NAME)

    def update(self) -> py_trees.common.Status:
        if self.bot.current_closest_food == None:
            return py_trees.common.Status.FAILURE
        
        self.bot.speech_bubble.clear()

        food_pos = self.bot.current_closest_food.pos()
        [angle, x, y] = self.bot.calculate_step_position(food_pos)

        self.bot.t.setheading(angle)

        self.bot.t.goto(x, y)
        return py_trees.common.Status.SUCCESS

class TurtleCheckIfFoodIsWithinEatingRange(py_trees.behaviour.Behaviour):
    def __init__(self, name: str, bot: Bot):
        super().__init__(name)
        self.bot = bot
        self.bb = self.attach_blackboard_client(name=constants.BLACKBOARD_NAME)

    def update(self) -> py_trees.common.Status:
        if self.bot.current_closest_food == None:
            return py_trees.common.Status.FAILURE

        dist = self.bot.get_distance_from_food(self.bot.current_closest_food)
        if dist <= self.bot.get_eat_distance_threshold():
            return py_trees.common.Status.SUCCESS
        return py_trees.common.Status.FAILURE

class TurtleEatFood(py_trees.behaviour.Behaviour):
    def __init__(self, name: str, bot: Bot):
        super().__init__(name)
        self.bot = bot
        self.bb = self.attach_blackboard_client(name=constants.BLACKBOARD_NAME)
        self.bb.register_key("feed", access=py_trees.common.Access.READ)

    def update(self) -> py_trees.common.Status:
        if self.bot.current_closest_food == None:
            return py_trees.common.Status.FAILURE

        self.bb.feed.remove_food(self.bot.current_closest_food)
        return py_trees.common.Status.SUCCESS

class TurtleResetTimeWithoutFood(py_trees.behaviour.Behaviour):
    def __init__(self, name: str, bot: Bot):
        super().__init__(name)
        self.bot = bot
        self.bb = self.attach_blackboard_client(name=constants.BLACKBOARD_NAME)

    def update(self) -> py_trees.common.Status:
        self.bot.last_time_without_food_ms = utils.get_now_ms()
        return py_trees.common.Status.SUCCESS

class TurtleCheckLastTimeWithoutFood(py_trees.behaviour.Behaviour):
    def __init__(self, name: str, bot: Bot, ms_start: int, ms_end):
        super().__init__(name)
        self.bot = bot
        self.ms_start = ms_start
        self.ms_end = ms_end

    def update(self) -> py_trees.common.Status:
        t = self.bot.get_time_without_food_ms()
        if t >= self.ms_start and t < self.ms_end:
            return py_trees.common.Status.SUCCESS
        return py_trees.common.Status.FAILURE

class TurtleSpeak(py_trees.behaviour.Behaviour):
    def __init__(self, name: str, bot: Bot, message: str):
        super().__init__(name)
        self.bot = bot
        self.message = message

    def update(self) -> py_trees.common.Status:
        self.bot.speech_bubble.write(self.bot.pos(), self.message)
        return py_trees.common.Status.SUCCESS
