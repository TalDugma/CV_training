from abc import ABC, abstractmethod

__all__ = ['ShapeComponent', 'CompositeShape', 'BasicShape']

class ShapeComponent(ABC):
  
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
  def __init__(self, shape_list : list[ShapeComponent], shape_dict : dict = {}):
    self.shap_dict = shape_dict
    self.shapes = shape_list
    CompositeShape.__apply_manipulations(self)

  def __apply_manipulations(self):
    pass



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
  _optional_manipulations = {
      "translation" : [0,0],
      "rotation" : 0,
      "resize" : 1
  }

  def __init__(self, shape_dict : dict):
    required_args = self._required_args.copy()
    optional_args = BasicShape._optional_args | self._optional_args
    optional_manipulations = BasicShape._optional_manipulations | self._optional_manipulations
    BasicShape.__validate_shape_input(self, required_args, optional_args, shape_dict)
    BasicShape.__set_attributes(self, shape_dict, optional_args)
    BasicShape.__apply_manipulations(self, optional_manipulations)

  def __apply_manipulations(self, optional_manipulations : dict):
    # NOTE: This should be done if we want to keep open/closed principle right. 
    # for manipulation_name, value in optional_manipulations.items():
    #   manipulation = ManipulationFactory.create_manipulation(manipulation_name)
    #   manipulation.manipulate(self, value)

    # NOTE: This is what we should do if we just care about finishing it - functional programming
    # for manipulation_name, value in optional_manipulations.items():
    #   manipulation_mapping["manipulation_name"](self, value)



    pass

  def __validate_shape_input(self, required_args : set, optional_args : dict, shape_dict : dict):
    for key in shape_dict:
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
    

  def __repr__(self):
    attrs = ', '.join(f"{k}={v}" for k, v in vars(self).items())
    return f"{self.__class__.__name__}({attrs})"
