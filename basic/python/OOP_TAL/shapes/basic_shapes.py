from shapes.shape_tree import BasicShape
import cv2
import numpy as np

__all__ = ["Circle", "Line", "Point", "Rectangle", "Triangle"]

class Circle(BasicShape):
   _required_args = {
      "center",
      "radius"
   }
      
   def draw(self, board : np) -> np:
      if self.fill_color:
         cv2.circle(board, center=self.center, radius=self.radius, color=self.fill_color, thickness=-1)
      cv2.circle(board, center=self.center, radius=self.radius, color=self.line_color, thickness=self.thickness)   

   def calculate_bounding_rectangle(self):
      return [[self.center[0] - self.radius, self.center[1] - self.radius], [self.center[0] + self.radius, self.center[1] + self.radius]]

   def translation(self, x, y):
      return super().translation(x, y)
   def rotation(self, angle):
      return super().rotation(angle)
   def resize(self, scale):
      return super().resize(scale)
      
class Line(BasicShape):
   _required_args = {
      "start_point",
      "end_point"
   }                    
   def draw(self, board : np) -> np:
      cv2.line(board, pt1=self.start_point, pt2=self.end_point, color=self.line_color, thickness=self.thickness)

   def calculate_bounding_rectangle(self):
      x_values = [self.start_point[0], self.end_point[0]]
      y_values = [self.start_point[1], self.end_point[1]]
      return [[min(x_values), min(y_values)],[max(x_values), max(y_values)]]

   def translation(self, x, y):
      return super().translation(x, y)
   def rotation(self, angle):
      return super().rotation(angle)
   def resize(self, scale):
      return super().resize(scale)
    
class Point(BasicShape):
   _required_args = {
      "position"
   }
   def draw(self, board : np):
      cv2.circle(board, center=self.position, radius=1, color=self.line_color, thickness=self.thickness)
      
   def calculate_bounding_rectangle(self):
      return [self.position, self.position]
      
   def translation(self, x, y):
      return super().translation(x, y)
   def rotation(self, angle):
      return super().rotation(angle)
   def resize(self, _scale):
      return 
   
class Rectangle(BasicShape):
   _required_args = {
      "p1",
      "p2",
      "p3",
      "p4"
   }
   def draw(self, board):
      points = np.array([self.p1, self.p2, self.p3, self.p4], dtype=np.int32)
      rect = cv2.minAreaRect(points)
      box = cv2.boxPoints(rect)
      box = np.int32(box)
      if self.fill_color:
         cv2.fillPoly(board, [box], color=self.fill_color)
      cv2.polylines(board, [box], isClosed=True, color=self.line_color, thickness=self.thickness)
   
   def calculate_bounding_rectangle(self):
      return
   
   def translation(self, x, y):
      return super().translation(x, y)
   def rotation(self, angle):
      return super().rotation(angle)
   def resize(self, scale):
      return super().resize(scale)
   
class Triangle(BasicShape):
   _required_args = {
      "p1",
      "p2",
      "p3"
   }
   
   def draw(self, board : np):
      points = [self.p1 , self.p2 , self.p3]
      Triangle.__draw_triangle_fill(self, board, points)
      Triangle.__draw_triangle_lines(self, board, points)

   def __draw_triangle_fill(self, board : np, points : list[list[int]]):
      if self.fill_color:
         points = np.array(points, dtype=np.int32)[:, np.newaxis]
         cv2.fillPoly(board, pts=[points], color=tuple(self.fill_color))

   def __draw_triangle_lines(self, board : np, points : list[list[int]]):
      cv2.line(board, pt1=points[0], pt2=points[1], color=self.line_color, thickness=self.thickness)
      cv2.line(board, pt1=points[1], pt2=points[2], color=self.line_color, thickness=self.thickness)
      cv2.line(board, pt1=points[2], pt2=points[0], color=self.line_color, thickness=self.thickness)
         
   def translation(self, x, y):
      return super().translation(x, y)
   def rotation(self, angle):
      return super().rotation(angle)
   def resize(self, scale):
      return super().resize(scale)   