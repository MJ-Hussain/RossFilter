from .calculator import RossFilterCalculator
from .gui import RossFilterGUI


def main() -> None:
    calculator = RossFilterCalculator()
    app = RossFilterGUI(calculator)
    app.run()


if __name__ == "__main__":
    main()
