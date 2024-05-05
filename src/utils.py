import time
import turtle
import py_trees

import utils

def get_now_ms() -> int:
    return int(time.time() * 1000)

class Text():
    text = ""

    def __init__(self, t: turtle.Turtle, font=('Arial', 12, 'bold')) -> None:
        t.hideturtle()
        t.penup()
        t.speed(10)
        self._t = t
        self._font = font

    def write(self, pos: tuple, text: str) -> None:
        if self.text == text:
            return
        else:
            self.clear()
        
        self._t.goto(pos[0], pos[1])
        self._t.sety(pos[1] + 10)
        self._t.write(text, align='center', font=self._font)
        self.text = text

    def clear(self) -> None:
        self._t.clear()

class Timer(py_trees.behaviour.Behaviour):
    def __init__(self, name: str, ms: int):
        super().__init__(name)
        self.time_ms = utils.get_now_ms()
        self.ms = ms

    def setup(self):
        self.time_ms = utils.get_now_ms()

    def update(self) -> py_trees.common.Status:
        if utils.get_now_ms() - self.time_ms > self.ms:
            print(utils.get_now_ms() - self.time_ms, self.ms)
            return py_trees.common.Status.SUCCESS
        return py_trees.common.Status.RUNNING
