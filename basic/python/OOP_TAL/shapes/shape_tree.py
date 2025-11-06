from abc import ABC, abstractmethod

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

    self.bounding_rectangle = self.calculate_bounding_rectangle()
    self._apply_manipulations(optional_args)
    

  
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
  def calculate_bounding_rectangle(self):
    pass
  
  def _apply_manipulations(self, optional_args : dict):
    self.translate_shape(optional_args["translation"])
    self.resize_shape(optional_args["resize"])
    self.rotate_shape(optional_args["rotation"])


  @abstractmethod
  def draw():
    pass
  
  @abstractmethod
  def resize_shape(self, scale : float):
    pass
  
  @abstractmethod
  def rotate_shape(self, angle: float):
    pass

  @abstractmethod
  def translate_shape(self, x : float, y : float):
    pass
  


class CompositeShape(ShapeComponent):
  _required_args = {
    "shapes"
  }

  def resize(self, scale):
    for shape in self.shapes:
      shape.resize(scale)

  def rotation(self, angle: float):
    for shape in self.shapes:
      shape.rotation(angle)
  
  def translation(self, x : float, y : float):
    for shape in self.shapes:
      shape.translation(x, y)
  

  def draw(self, board):
    for shape in self.shapes:
      shape.draw(board)

  def calculate_bounding_rectangle(self) -> list[list[int, int], list[int, int]]: 
    shapes_bounding_rectangles = [shape.bounding_rectangle for shape in self.shapes]
    x_values = []
    y_values = []
    for bounding_rectangle in shapes_bounding_rectangles:
      x_values.extend([bounding_rectangle[0][0], bounding_rectangle[1][0]])
      y_values.extend([bounding_rectangle[0][1], bounding_rectangle[1][1]])
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
