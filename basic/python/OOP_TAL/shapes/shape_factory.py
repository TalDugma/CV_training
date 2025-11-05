import json
from shapes.basic_shapes import *
from shapes.shape_tree import *

__all__ = ["ShapeFactory"]

class ShapeFactory:
  _basic_shapes = {
    "point": Point,
    "line": Line,
    "triangle": Triangle,
    "rectangle": Rectangle,
    "circle": Circle,
  }

  @classmethod
  def create_shape(cls, shape_dict : dict):
    shape_name = shape_dict.pop("name", None)
    if shape_name == "composite":
      return cls.create_composite_shape(shape_dict)
    elif shape_name in cls._basic_shapes:
      return cls.create_basic_shape(shape_name, shape_dict)
    else:
      raise ValueError(f"Invalid/Missing shape name: {shape_name}.\n"
                       f"Valid names are: {list(cls._basic_shapes.keys()) + ['composite']}")
  
  @classmethod
  def create_basic_shape(cls, shape_name : str, shape_dict : dict):
    return cls._basic_shapes[shape_name](shape_dict)

  @classmethod
  def create_composite_shape(cls, shape_dict : dict):
    if "path" in shape_dict:
      return CompositeShape(cls.create_shapes_from_json(shape_dict["path"]))
    elif "shapes" in shape_dict:
      return CompositeShape(cls.create_shapes_from_shape_list(shape_dict["shapes"]))
    else:
      raise ValueError("Composite shape does not contain path and shape keys")
  
  @classmethod
  def create_shapes_from_json(cls, json_path : str) -> list[ShapeComponent]:
    with open(json_path, "r") as file:
      shape_list = json.load(file)
    return cls.create_shapes_from_shape_list(shape_list)
    
  
  @classmethod
  def create_shapes_from_shape_list(cls, shape_list : list[dict]) -> list[ShapeComponent]:
    shapes = []
    for shape_dict in shape_list:
      shapes.append(cls.create_shape(shape_dict))
    return shapes
          
    
   
