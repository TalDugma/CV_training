import numpy as np  
import shapes
from shapes import ShapeComponent
import cv2

class Board:
    def __init__(self):
        self.board_array = np.full((600, 800, 3), 255, dtype=np.uint8) 
    def draw(self, shapes : list[shapes.ShapeComponent]):
        for shape in shapes:
            shape.draw(self.board_array)
    def display(self):
        cv2.imshow("Board", self.board_array)
    def save(self, save_path : str):
        cv2.imwrite(save_path, self.board_array)