""" Initialization """
import sys
from PyQt5.QtWidgets import QApplication

from qt_app import Window
from redis_manager import RedisManager
from parser import Parser, Offer


def main():
    redis_manager = RedisManager()
    parser = Parser()

    app = QApplication(sys.argv)
    window = Window(redis_manager, parser)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
