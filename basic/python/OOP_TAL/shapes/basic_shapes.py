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

   def translate_shape(self, translation) -> None:
      super().translate_shape(translation)
      self.center = self.add_lists(self.center, translation)
   

   def rotate_shape(self, angle):
      return
   
   def resize_shape(self, scale):
      return
      

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

   def translate_shape(self, translation):
      super().translate_shape(translation)
      self.start_point = self.add_lists(self.start_point, translation)
      self.end_point = self.add_lists(self.end_point, translation)

   def rotate_shape(self, angle):
      matrix = self.convert_angle_to_translation_matrix(angle)
      self.start_point = self.start_point @ matrix
      self.end_point = self.end_point @ matrix

      
   def resize_shape(self, scale):
      return super().resize_shape(scale)
      
    
class Point(BasicShape):
   _required_args = {
      "position"
   }
   def draw(self, board : np):
      cv2.circle(board, center=self.position, radius=1, color=self.line_color, thickness=self.thickness)
      
   def calculate_bounding_rectangle(self):
      return [self.position, self.position]
      
   def translate_shape(self, translation):
      super().translate_shape(translation)
      self.position = self.add_lists(self.position, translation)

   def rotate_shape(self, angle):
      return
   
   def resize_shape(self, scale):
      return super().resize_shape(scale)
   
class Rectangle(BasicShape):
   _required_args = {
      "top_left",
      "bottom_right"
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
      points = np.array([self.p1, self.p2, self.p3, self.p4], dtype=np.int32)[:, np.newaxis]
      x, y, w, h = cv2.boundingRect(points)
      return [[x, y], [x+w, y+h]] 

   def _set_attributes(self, shape_dict : dict, optional_args : dict):
      for key, value in optional_args.items():
         setattr(self, key, value)  
      top_left = shape_dict["top_left"]
      bottom_right = shape_dict["bottom_right"]
      self.p1 = top_left
      self.p2 = [top_left[0], bottom_right[1]]
      self.p3 = [bottom_right[0], top_left[1]]
      self.p4 = bottom_right


   def translate_shape(self, translation):
      super().translate_shape(translation)
      self.p1 = self.add_lists(self.p1, translation)
      self.p2 = self.add_lists(self.p2, translation)
      self.p3 = self.add_lists(self.p3, translation)
      self.p4 = self.add_lists(self.p4, translation)

   def rotate_shape(self, angle):
      matrix = self.convert_angle_to_translation_matrix(angle)
      self.p1 = self.p1 @ matrix
      self.p2 = self.p2 @ matrix
      self.p3 = self.p3 @ matrix
      self.p4 = self.p4 @ matrix

   def resize_shape(self, scale):
      return super().resize_shape(scale)
   
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
   
   def calculate_bounding_rectangle(self):
      x_values = [self.p1[0], self.p2[0], self.p3[0]]
      y_values = [self.p1[1], self.p2[1], self.p3[1]]
      return [[min(x_values), min(y_values)],[max(x_values), max(y_values)]]
      
   def translate_shape(self, translation):
      super().translate_shape(translation)
      self.p1 = self.add_lists(self.p1, translation)
      self.p2 = self.add_lists(self.p2, translation)
      self.p3 = self.add_lists(self.p3, translation)

   def rotate_shape(self, angle):
      matrix = self.convert_angle_to_translation_matrix(angle)
      self.p1 = self.p1 @ matrix
      self.p2 = self.p2 @ matrix
      self.p3 = self.p3 @ matrix

      
   def resize_shape(self, scale):
      return super().resize_shape(scale)
   