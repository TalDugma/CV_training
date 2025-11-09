from abc import ABC, abstractmethod
import numpy as np

__all__ = ['ShapeComponent', 'CompositeShape', 'BasicShape']

class ShapeComponent(ABC):
  _required_args = set()
  _optional_args = {
    "translation" : [0,0],
    "rotation" : 0,
    "resize" : 1
  }
  
  def __init__(self, **kwargs):
    required_args = set().union(*[cls._required_args for cls in type(self).__mro__
                                  if issubclass(cls, ShapeComponent)])
    optional_args = {k: v for cls in type(self).__mro__
                      if issubclass(cls, ShapeComponent)
                      for k, v in cls._optional_args.items()
                    }
    self._validate_shape_input(required_args.copy(), optional_args, kwargs)
    self._set_attributes(kwargs, optional_args)

    self.bbox = self.calculate_bbox()
    self._apply_manipulations()
    

  
  def _validate_shape_input(self, required_args : set, optional_args : dict, kwargs : dict):
    for key in kwargs:
      if key in required_args:
        required_args.remove(key)
      elif key not in optional_args:
        raise ValueError(f"Invalid entrance for {self}: '{key}'")
    if required_args:
      raise ValueError(f"Failed drawing shape {self}, missing required argument(s): {required_args}")  

  def _set_attributes(self, shape_dict : dict, optional_args : dict):
    for key, value in optional_args.items():
      setattr(self, key, value)
    for key, value in shape_dict.items():
      setattr(self, key, value)

  
  @abstractmethod
  def calculate_bbox(self) -> list[list[int, int], list[int, int]]:
    pass

  def translate_bbox(self, translation : list[int, int]) -> None:
    self.bbox = [self.add_lists(self.bbox[0], translation), self.add_lists(self.bbox[1], translation)]
    
  def resize_bbox(self, scale : float):
    matrix = self.convert_scale_to_scale_matrix(scale)
    top_left = (np.array(self.bbox[0]) @ matrix).tolist()
    bottom_right = (np.array(self.bbox[1]) @ matrix).tolist()
    self.bbox = [top_left, bottom_right]

  def rotate_bbox(self, angle : float):
    matrix = self.convert_angle_to_rotation_matrix(angle)
    top_left = (np.array(self.bbox[0]) @ matrix).tolist()
    bottom_right = (np.array(self.bbox[1]) @ matrix).tolist()
    self.bbox = [top_left, bottom_right]


  def _apply_manipulations(self):
    bbox_center = [int((self.bbox[0][0] + self.bbox[1][0])/2),int((self.bbox[0][1] + self.bbox[1][1])/2)]
    self.translate_shape(self.translation)
    self.move_shape_to_center_aligned_axis([-x for x in bbox_center])
    self.resize_shape(self.resize)
    self.rotate_shape(self.rotation)
    self.move_shape_to_center_aligned_axis(bbox_center)
  

  @staticmethod
  def convert_angle_to_rotation_matrix(angle : float):
    theta = np.radians(angle)
    return np.array([[np.cos(theta), -np.sin(theta)], [np.sin(theta), np.cos(theta)]])

  @staticmethod
  def convert_scale_to_scale_matrix(scale : float):
    return np.array([[scale, 0], [0, scale]])
  
  @staticmethod
  def add_lists(a: list, b: list) -> list:
    return [x + y for x, y in zip(a, b)]

  
  def move_shape_to_center_aligned_axis(self, center : list[int, int]):
    self.translate_shape(center)
  
    
  @abstractmethod
  def draw():
    pass
  
  @abstractmethod
  def resize_shape(self, scale : float):
    self.resize_bbox(scale)
  
  @abstractmethod
  def rotate_shape(self, angle: float):
    self.rotate_bbox(angle)

  @abstractmethod
  def translate_shape(self, translation : list[int,int]):
    self.translate_bbox(translation)
  


class CompositeShape(ShapeComponent):
  _required_args = {
    "shapes"
  }

  def resize_shape(self, scale):
    return super().resize_shape(scale)
  
  def rotate_shape(self, angle):
    return super().rotate_shape(angle)
  
  def translate_shape(self, translation):
    return super().translate_shape(translation)

  def draw(self, board):
    for shape in self.shapes:
      shape.draw(board)

  def calculate_bbox(self): 
    shapes_bboxs = [shape.bbox for shape in self.shapes]
    x_values = []
    y_values = []
    for bbox in shapes_bboxs:
      x_values.extend([bbox[0][0], bbox[1][0]])
      y_values.extend([bbox[0][1], bbox[1][1]])
    return [[min(x_values), min(y_values)], [max(x_values), max(y_values)]]
      
  

class BasicShape(ShapeComponent):
  _required_args = set()
  _optional_args = {
      "line_color" : [255,0,0], 
      "thickness" : 2,
      "fill_color" : None,
  }

  def __apply_manipulations(self, optional_manipulations : dict):
    # NOTE: This should be done if we want to keep open/closed principle right. 
    # for manipulation_name, value in optional_manipulations.items():
    #   manipulation = ManipulationFactory.create_manipulation(manipulation_name)
    #   manipulation.manipulate(self, value)

    # NOTE: This is what we should do if we just care about finishing it - functional programming
    # for manipulation_name, value in optional_manipulations.items():
    #   manipulation_mapping["manipulation_name"](self, value)



    pass    

  def __repr__(self):
    attrs = ', '.join(f"{k}={v}" for k, v in vars(self).items())
    return f"{self.__class__.__name__}({attrs})"
