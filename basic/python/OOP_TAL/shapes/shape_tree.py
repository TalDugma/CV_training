from abc import ABC, abstractmethod
import numpy as np

__all__ = ["ShapeComponent", "CompositeShape", "BasicShape"]


class ShapeComponent(ABC):
    _required_args = set()
    _optional_args = {"translation": [0, 0], "rotation": 0, "resize": 1}

    def __init__(self, **kwargs):
        required_args = set().union(
            *[
                cls._required_args
                for cls in type(self).__mro__
                if issubclass(cls, ShapeComponent)
            ]
        )
        optional_args = {
            k: v
            for cls in type(self).__mro__
            if issubclass(cls, ShapeComponent)
            for k, v in cls._optional_args.items()
        }
        self._validate_shape_input(required_args.copy(), optional_args, kwargs)
        self._set_attributes(kwargs, optional_args)

        self.bbox_center = self.calculate_bbox_center()
        self._apply_manipulations()

    def _validate_shape_input(
        self, required_args: set, optional_args: dict, kwargs: dict
    ) -> None:
        for key in kwargs:
            if key in required_args:
                required_args.remove(key)
            elif key not in optional_args:
                raise ValueError(f"Invalid entrance for {self}: '{key}'")
        if required_args:
            raise ValueError(
                f"Failed drawing shape {self}, missing required argument(s): {required_args}"
            )

    def _set_attributes(self, shape_dict: dict, optional_args: dict) -> None:
        for key, value in optional_args.items():
            setattr(self, key, value)
        for key, value in shape_dict.items():
            setattr(self, key, value)

    def calculate_bbox_center(self) -> list[int, int]:
        bbox = self.calculate_bbox()
        return [int((bbox[0][0] + bbox[1][0]) / 2), int((bbox[0][1] + bbox[1][1]) / 2)]

    def translate_bbox(self, translation: list[int, int]) -> None:
        self.bbox_center = self.add_lists(self.bbox_center, translation)

    def _apply_manipulations(self) -> None:
        self.translate_shape(self.translation)
        self.translate_bbox(self.translation)
        self.translate_shape(
            [-x for x in self.bbox_center]
        )  # Moves shape to center aligned axis
        self.rotate_shape(self.rotation)
        self.resize_shape(self.resize)
        self.translate_shape(self.bbox_center)  # Moves shape back to original axis

    @staticmethod
    def convert_angle_to_rotation_matrix(angle: float) -> np.ndarray:
        theta = np.radians(angle)
        return np.array(
            [[np.cos(theta), -np.sin(theta)], [np.sin(theta), np.cos(theta)]]
        )

    @staticmethod
    def convert_scale_to_scale_matrix(scale: float) -> np.ndarray:
        return np.array([[scale, 0], [0, scale]])

    @staticmethod
    def add_lists(a: list, b: list) -> list:
        return [x + y for x, y in zip(a, b)]

    @abstractmethod
    def draw():
        pass

    @abstractmethod
    def resize_shape(self, scale: float):
        pass

    @abstractmethod
    def rotate_shape(self, angle: float):
        pass

    @abstractmethod
    def translate_shape(self, translation: list[int, int]):
        pass


class CompositeShape(ShapeComponent):
    _required_args = {"shapes"}

    def resize_shape(self, scale: float) -> None:
        for shape in self.shapes:
            shape.resize_shape(scale)

    def rotate_shape(self, angle: float) -> None:
        for shape in self.shapes:
            shape.rotate_shape(angle)

    def translate_shape(self, translation: list[int, int]) -> None:
        for shape in self.shapes:
            shape.translate_shape(translation)

    def draw(self, board: np.ndarray) -> None:
        for shape in self.shapes:
            shape.draw(board)

    def calculate_bbox(self) -> list[list[int, int], list[int, int]]:
        shapes_bboxs = [shape.calculate_bbox() for shape in self.shapes]
        x_values = []
        y_values = []
        for bbox in shapes_bboxs:
            x_values.extend([bbox[0][0], bbox[1][0]])
            y_values.extend([bbox[0][1], bbox[1][1]])
        return [[min(x_values), min(y_values)], [max(x_values), max(y_values)]]


class BasicShape(ShapeComponent):
    _required_args = set()
    _optional_args = {
        "line_color": [255, 0, 0],
        "thickness": 2,
        "fill_color": None,
    }

    def __repr__(self):
        attrs = ", ".join(f"{k}={v}" for k, v in vars(self).items())
        return f"{self.__class__.__name__}({attrs})"
