import turtle
import py_trees

class Food():
    def __init__(self, stamp: int, x: float, y: float) -> None:
        self.stamp = stamp
        self._x = x
        self._y = y

    def pos(self) -> tuple:
        return self._x, self._y


class Feed():
    def __init__(self, t: turtle.Turtle, bb: py_trees.blackboard.Blackboard) -> None:
        t.hideturtle()
        t.penup()
        t.speed(10)
        t.shape("triangle")

        # All of the placed turtle food will be stored in this key
        bb.register_key(key="placed_food", access=py_trees.common.Access.WRITE)
        bb.placed_food = []

        # Feed handler
        bb.register_key(key="feed", access=py_trees.common.Access.WRITE)
        bb.feed = self

        self.t = t
        self.bb = bb

    def place(self, x, y) -> None:
        self.t.goto(x, y)
        new_food = Food(self.t.stamp(), x, y)
        self.bb.placed_food.append(new_food)

    def pos(self) -> tuple:
        return self.t.xcor(), self.t.ycor()

    def remove_food(self, food: Food) -> None:
        self.t.clearstamp(food.stamp)
        self.bb.placed_food.remove(food)
