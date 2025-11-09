from shapes.shape_tree import BasicShape
import cv2
import numpy as np
import warnings

warnings.filterwarnings("default")  # or "always"

__all__ = ["Circle", "Line", "Point", "Rectangle", "Triangle"]


class Circle(BasicShape):
    _required_args = {"center", "radius"}

    def draw(self, board: np.ndarray) -> None:
        if self.fill_color:
            cv2.circle(
                board,
                center=self.center,
                radius=self.radius,
                color=self.fill_color,
                thickness=-1,
            )
        cv2.circle(
            board,
            center=self.center,
            radius=self.radius,
            color=self.line_color,
            thickness=self.thickness,
        )

    def calculate_bbox_center(self) -> list[int, int]:
        return self.center

    def calculate_bbox(self) -> list[list[int, int], list[int, int]]:
        return [
            [self.center[0] - self.radius, self.center[1] - self.radius],
            [self.center[0] + self.radius, self.center[1] + self.radius],
        ]

    def translate_shape(self, translation: list[int, int]) -> None:
        self.center = self.add_lists(self.center, translation)

    def rotate_shape(self, angle: float) -> None:
        warnings.warn("Attempting rotation of a circle shape is redundant")
        return

    def resize_shape(self, scale: float) -> None:
        self.radius = round(self.radius * scale)


class Line(BasicShape):
    _required_args = {"start_point", "end_point"}

    def draw(self, board: np.ndarray) -> None:
        cv2.line(
            board,
            pt1=self.start_point,
            pt2=self.end_point,
            color=self.line_color,
            thickness=self.thickness,
        )

    def calculate_bbox_center(self) -> list[int, int]:
        bbox = self.calculate_bbox()
        return [int((bbox[0][0] + bbox[1][0]) / 2), int((bbox[0][1] + bbox[1][1]) / 2)]

    def calculate_bbox(self) -> list[list[int, int], list[int, int]]:
        x_values = [self.start_point[0], self.end_point[0]]
        y_values = [self.start_point[1], self.end_point[1]]
        return [[min(x_values), min(y_values)], [max(x_values), max(y_values)]]

    def translate_shape(self, translation: list[int, int]) -> None:
        self.start_point = self.add_lists(self.start_point, translation)
        self.end_point = self.add_lists(self.end_point, translation)

    def rotate_shape(self, angle: float) -> None:
        matrix = self.convert_angle_to_rotation_matrix(angle)
        self.start_point = (self.start_point @ matrix).round().astype(int)
        self.end_point = (self.end_point @ matrix).round().astype(int)

    def resize_shape(self, scale: float) -> None:
        matrix = self.convert_scale_to_scale_matrix(scale)
        self.start_point = (self.start_point @ matrix).round().astype(int)
        self.end_point = (self.end_point @ matrix).round().astype(int)


class Point(BasicShape):
    _required_args = {"position"}

    def draw(self, board: np.ndarray) -> None:
        cv2.circle(
            board,
            center=self.position,
            radius=1,
            color=self.line_color,
            thickness=self.thickness,
        )

    def calculate_bbox_center(self) -> list[int, int]:
        return self.position

    def calculate_bbox(self) -> list[list[int, int], list[int, int]]:
        return [self.position, self.position]

    def translate_shape(self, translation: list[int, int]) -> None:
        self.position = self.add_lists(self.position, translation)

    def rotate_shape(self, angle: float) -> None:
        warnings.warn("Attempting rotation of a point shape is redundant")
        return

    def resize_shape(self, scale: float) -> None:
        warnings.warn("Attempting resize of a point shape is redundant")
        return


class Rectangle(BasicShape):
    _required_args = {"top_left", "bottom_right"}

    def draw(self, board: np.ndarray) -> None:
        points = np.array([self.p1, self.p2, self.p3, self.p4], dtype=np.int32)
        rect = cv2.minAreaRect(points)
        box = cv2.boxPoints(rect)
        box = np.int32(box)
        if self.fill_color:
            cv2.fillPoly(board, [box], color=self.fill_color)
        cv2.polylines(
            board, [box], isClosed=True, color=self.line_color, thickness=self.thickness
        )

    def calculate_bbox_center(self) -> list[int, int]:
        bbox = self.calculate_bbox()
        return [int((bbox[0][0] + bbox[1][0]) / 2), int((bbox[0][1] + bbox[1][1]) / 2)]

    def calculate_bbox(self) -> list[list[int, int], list[int, int]]:
        points = np.array([self.p1, self.p2, self.p3, self.p4], dtype=np.int32)[
            :, np.newaxis
        ]
        x, y, w, h = cv2.boundingRect(points)
        return [[x, y], [x + w, y + h]]

    def _set_attributes(self, shape_dict: dict, optional_args: dict) -> None:
        top_left = shape_dict.pop("top_left")
        bottom_right = shape_dict.pop("bottom_right")
        self.p1 = top_left
        self.p2 = [top_left[0], bottom_right[1]]
        self.p3 = [bottom_right[0], top_left[1]]
        self.p4 = bottom_right
        super()._set_attributes(shape_dict, optional_args)

    def translate_shape(self, translation: list[int, int]) -> None:
        self.p1 = self.add_lists(self.p1, translation)
        self.p2 = self.add_lists(self.p2, translation)
        self.p3 = self.add_lists(self.p3, translation)
        self.p4 = self.add_lists(self.p4, translation)

    def rotate_shape(self, angle: float) -> None:
        matrix = self.convert_angle_to_rotation_matrix(angle)
        self.p1 = (self.p1 @ matrix).round().astype(int)
        self.p2 = (self.p2 @ matrix).round().astype(int)
        self.p3 = (self.p3 @ matrix).round().astype(int)
        self.p4 = (self.p4 @ matrix).round().astype(int)

    def resize_shape(self, scale: float) -> None:
        matrix = self.convert_scale_to_scale_matrix(scale)
        self.p1 = (self.p1 @ matrix).round().astype(int)
        self.p2 = (self.p2 @ matrix).round().astype(int)
        self.p3 = (self.p3 @ matrix).round().astype(int)
        self.p4 = (self.p4 @ matrix).round().astype(int)


class Triangle(BasicShape):
    _required_args = {"p1", "p2", "p3"}

    def draw(self, board: np.ndarray) -> None:
        points = [self.p1, self.p2, self.p3]
        Triangle.__draw_triangle_fill(self, board, points)
        Triangle.__draw_triangle_lines(self, board, points)

    def __draw_triangle_fill(self, board: np.ndarray, points: list[list[int]]) -> None:
        if self.fill_color:
            points = np.array(points, dtype=np.int32)[:, np.newaxis]
            cv2.fillPoly(board, pts=[points], color=tuple(self.fill_color))

    def __draw_triangle_lines(self, board: np.ndarray, points: list[list[int]]) -> None:
        cv2.line(
            board,
            pt1=points[0],
            pt2=points[1],
            color=self.line_color,
            thickness=self.thickness,
        )
        cv2.line(
            board,
            pt1=points[1],
            pt2=points[2],
            color=self.line_color,
            thickness=self.thickness,
        )
        cv2.line(
            board,
            pt1=points[2],
            pt2=points[0],
            color=self.line_color,
            thickness=self.thickness,
        )

    def calculate_bbox_center(self) -> list[int, int]:
        bbox = self.calculate_bbox()
        return [int((bbox[0][0] + bbox[1][0]) / 2), int((bbox[0][1] + bbox[1][1]) / 2)]

    def calculate_bbox(self) -> list[list[int, int], list[int, int]]:
        x_values = [self.p1[0], self.p2[0], self.p3[0]]
        y_values = [self.p1[1], self.p2[1], self.p3[1]]
        return [[min(x_values), min(y_values)], [max(x_values), max(y_values)]]

    def translate_shape(self, translation: list[int, int]) -> None:
        self.p1 = self.add_lists(self.p1, translation)
        self.p2 = self.add_lists(self.p2, translation)
        self.p3 = self.add_lists(self.p3, translation)

    def rotate_shape(self, angle: float) -> None:
        matrix = self.convert_angle_to_rotation_matrix(angle)
        self.p1 = (self.p1 @ matrix).round().astype(int)
        self.p2 = (self.p2 @ matrix).round().astype(int)
        self.p3 = (self.p3 @ matrix).round().astype(int)

    def resize_shape(self, scale: float) -> None:
        matrix = self.convert_scale_to_scale_matrix(scale)
        self.p1 = (self.p1 @ matrix).round().astype(int)
        self.p2 = (self.p2 @ matrix).round().astype(int)
        self.p3 = (self.p3 @ matrix).round().astype(int)
