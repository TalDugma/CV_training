import argparse
from Board import *
from shapes import ShapeFactory

def main(json_path):
    board = Board()
    shapes = ShapeFactory.create_shapes_from_json(json_path)
    board.draw(shapes)
    board.save("board.png")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "json_path",
        nargs="?",
        default="json_example.json",
        help="Path to JSON file used for the drawing",
    )
    args = parser.parse_args()

    main(args.json_path)