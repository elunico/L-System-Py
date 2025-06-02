import importlib
import math
import threading
import turtle
from enum import Enum
from turtle import Turtle, Screen

from lsystem import LSystem


class TurtleAdapter:
    def __init__(self, turtle: Turtle, lsystem: LSystem):
        self.screen = Screen()
        self.turtle = turtle
        self.turtle.speed(0)
        self.lsystem = lsystem
        self.exp = lsystem.expand()
        self.pos = [0, 0]
        self.heading = 90
        self.stack = []

    def forward(self, d):
        self.pos[0] += d * math.cos(math.radians(self.heading))
        self.pos[1] += d * math.sin(math.radians(self.heading))
        self.turtle.forward(d)
        print("Forward", d)

    def turn(self, d):
        self.heading += d
        self.turtle.right(d)
        print("Turn", d)

    def push(self):
        self.stack.append((self.pos[:], self.heading))

    def pop(self):
        self.pos, self.heading = self.stack.pop()
        self.turtle.pu()
        self.turtle.goto(self.pos[0], self.pos[1])
        self.turtle.setheading(self.heading)
        self.turtle.pd()

    def step(self):
        self.turtle.clear()
        for e in self.exp:
            print(e)
            for char in e:
                print(repr(char))
                if char == '+':
                    self.turn(90)
                elif char == '-':
                    self.turn(-90)
                elif char == '[':
                    self.push()
                elif char == ']':
                    self.pop()
                elif isinstance(char, Enum):
                    self.forward(10)
                print('----')

            input("Continue? ")
            self.turtle.clear()
            self.turtle.reset()

    def run(self):
        threading.Thread(target=self.step).start()
        self.screen.mainloop()
        self.screen.exitonclick()
