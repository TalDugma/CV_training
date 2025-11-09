import argparse
from board import Board
from shapes import ShapeFactory


def main(args):
    board = Board(args.background_color)
    shapes = ShapeFactory.create_shapes_from_json(args.json_path)
    board.draw(shapes)
    board.save("results/best_drawing_ever.png")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--json_path",
        default="configurations/my_drawing.json",
        help="Path to JSON file used for the drawing",
    )
    parser.add_argument(
        "--background_color",
        default=[255, 0, 0],
        help="BGR value of background color to board",
    )
    args = parser.parse_args()

    main(args)
