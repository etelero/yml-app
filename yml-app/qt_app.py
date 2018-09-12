from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import Qt

from parser import InvalidEntry, ParserError


class OffersWidget(QtWidgets.QWidget):

    CATEGORY, NAME, PRICE = range(3)

    def __init__(self, redis_manager):
        self.redis = redis_manager
        super().__init__()

        self.init_ui()

    def init_ui(self):

        # self.setGeometry(310, 290, 300, 250)

        self.tree = QtWidgets.QTreeWidget()
        self.parent_item = QtWidgets.QTreeWidgetItem(self.tree)

        self.dataGroupBox = QtWidgets.QGroupBox("Offers")
        self.dataView = QtWidgets.QTreeView()
        self.dataView.setRootIsDecorated(False)
        self.dataView.setAlternatingRowColors(True)

        dataLayout = QtWidgets.QHBoxLayout()
        dataLayout.addWidget(self.dataView)
        self.dataGroupBox.setLayout(dataLayout)

        self.model = self.create_offer_model(self)
        self.dataView.setModel(self.model)
        self.entry_count = 0
        self.update_tree()

        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addWidget(self.dataGroupBox)
        self.setLayout(mainLayout)

        self.show()

    def update_tree(self):
        self.model.removeRows(0, self.entry_count)
        scan = self.redis.scan_iter("yml-offer_*")
        if scan:
            for key in scan:
                values = self.redis.get(key).split(":")
                self.add_offer(self.model, values[0], values[1], values[2])
                self.entry_count += 1

    def create_offer_model(self, parent):
        model = QtGui.QStandardItemModel(0, 3, parent)
        model.setHeaderData(self.CATEGORY, Qt.Horizontal, "Category")
        model.setHeaderData(self.NAME, Qt.Horizontal, "Name")
        model.setHeaderData(self.PRICE, Qt.Horizontal, "Price")
        return model

    def add_offer(self, model, category, name, price):
        model.insertRow(0)
        model.setData(model.index(0, self.CATEGORY), category)
        model.setData(model.index(0, self.NAME), name)
        model.setData(model.index(0, self.PRICE), price)


class Window(QtWidgets.QMainWindow):
    def __init__(self, redis_manager, parser):
        self.redis = redis_manager
        self.parser = parser
        super().__init__()

        self.init_ui()

    def init_ui(self):

        self.centralWidget = OffersWidget(self.redis)

        self.setCentralWidget(self.centralWidget)

        openFile = QtWidgets.QAction(QtGui.QIcon("open.png"), "Open", self)
        openFile.setShortcut("Ctrl+O")
        openFile.setStatusTip("Open new File")
        openFile.triggered.connect(self.open_file_dialog)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu("&File")
        fileMenu.addAction(openFile)

        # self.setGeometry(300, 300, 350, 300)
        self.setWindowTitle("File dialog")
        self.show()

    def open_file_dialog(self):
        file_name = QtWidgets.QFileDialog.getOpenFileName(self, "Open file", "/home")
        if file_name[0]:
            try:
                offers = self.parser.parse(file_name[0])
                for i in offers:
                    entry = i.construct()
                    self.redis.set(entry[0], ':'.join(list(entry[1])))

            except ParserError as err:
                self.show_error_message("Parser error: " + str(err))
            except InvalidEntry as err:
                self.show_error_message("Invalid Entry: " + str(err))

            self.centralWidget.update_tree()

    def show_error_message(self, msg):
        error_message = QtWidgets.QErrorMessage(self)
        error_message.showMessage(msg)
