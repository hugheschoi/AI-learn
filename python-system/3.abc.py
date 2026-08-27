from abc import ABC, abstractmethod

# 继承 ABC 成为抽象基类
class Animal(ABC):
    # 子类必须实现 make_sound
    @abstractmethod
    def make_sound(self):
        pass

    # 子类必须实现 move
    @abstractmethod
    def move(self):
        pass

# 实现所有抽象方法的子类
class Dog(Animal):
    def make_sound(self):
        return "Woof!"

# print()(Dog().make_sound())  # TypeError: Can't instantiate abstract class Dog without an implementation for abstract method 'move'

