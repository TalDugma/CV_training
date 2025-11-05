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
    ShapeComponent.__validate_shape_input(self, required_args.copy(), optional_args, kwargs)
    ShapeComponent.__set_attributes(self, kwargs, optional_args)

    self.bounding_rectangle = type(self).calculate_bounding_rectangle(self)
    ShapeComponent.__apply_manipulations(self, optional_args)
    

  
  def __validate_shape_input(self, required_args : set, optional_args : dict, kwargs : dict):
    for key in kwargs:
      if key in required_args:
        required_args.remove(key)
      elif key not in optional_args:
        raise ValueError(f"Invalid entrance for {self}: '{key}'")
    if required_args:
      raise ValueError(f"Failed drawing shape {self}, missing required argument(s): {required_args}")  

  def __set_attributes(self, shape_dict : dict, optional_args : dict):
    for key, value in optional_args.items():
      setattr(self, key, value)
    for key, value in shape_dict.items():
      setattr(self, key, value)

  @abstractmethod
  def calculate_bounding_rectangle(self):
    pass
  
  @abstractmethod  
  def __apply_manipulations(self, optional_args : dict):
    pass

  @abstractmethod
  def draw():
    pass
  
  @abstractmethod
  def resize(self, scale : float):
    pass
  
  @abstractmethod
  def rotation(self, angle: float):
    pass
  
  @abstractmethod
  def translation(self, x : float, y : float):
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
