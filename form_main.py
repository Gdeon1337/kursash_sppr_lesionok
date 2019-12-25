from datetime import datetime

from PyQt5 import QtWidgets, QtCore
import os

from view_main import Ui_MainWindow
from PyQt5.QtGui import QPixmap
from arrima import get_plot
from PyQt5.QtWidgets import QFileDialog, QTableWidgetItem, QHeaderView
from statsmodels.tsa.arima_model import ARIMAResults


class ClassMain(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.path_csv = None
        self.model_fit = None
        self.pushButton.clicked.connect(self.file_dailog)
        self.pushButton_2.clicked.connect(self.train)
        self.pushButton_3.clicked.connect(self.save_model)
        self.pushButton_4.clicked.connect(self.load_model)
        self.tableWidget.setColumnCount(3)
        self.tableWidget.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        self.tableWidget.verticalHeader().hide()
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.tableWidget.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.tableWidget.setHorizontalHeaderLabels(["Дата", "Данные", "Предикт"])
        self.tableWidget.horizontalHeaderItem(0).setToolTip("Дата")
        self.tableWidget.horizontalHeaderItem(1).setToolTip("Изначальные данные")
        self.tableWidget.horizontalHeaderItem(2).setToolTip("Данные полученные спомощью временного ряда")

    def save_model(self):
        if self.model_fit:
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            fname, _ = QFileDialog.getSaveFileName(self, "QFileDialog.getSaveFileName()", "",
                                                   "All Files (*);;PKL Files (*.pkl)", options=options)
            if fname:
                self.model_fit.save(str(fname))

    def load_model(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        path_model = QFileDialog.getOpenFileName(
            self, "Open File", os.getcwd(), "Pkl Files (*.pkl)", options=options)
        if path_model[0] != '' and path_model:
            self.model_fit = ARIMAResults.load(path_model[0])

    def file_dailog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        self.path_csv = QFileDialog.getOpenFileName(
            self, "Open File", os.getcwd(), "CSV Files (*.csv)", options=options)

    def train(self):
        if self.path_csv[0] != '' and self.path_csv:
            plot_image, image_error, logger, self.model_fit = get_plot(self.path_csv[0], self.model_fit)
            pm = QPixmap()
            pm.loadFromData(plot_image)
            self.label.setPixmap(pm.scaled(
                self.label.width(), self.label.height(), QtCore.Qt.KeepAspectRatio))
            pm_ = QPixmap()
            pm_.loadFromData(image_error)
            self.label_3.setPixmap(pm_.scaled(
                self.label_3.width(), self.label_3.height(), QtCore.Qt.KeepAspectRatio))
            self.tableWidget.setRowCount(len(logger))
            for i in range(len(logger)):
                self.tableWidget.setItem(i, 0, QTableWidgetItem(datetime.strftime(logger[i].get('date'), '%d:%m:%Y')))
                self.tableWidget.setItem(i, 1, QTableWidgetItem(str(logger[i].get('value'))))
                self.tableWidget.setItem(i, 2, QTableWidgetItem(str(logger[i].get('predict_value'))))
            self.tableWidget.resizeColumnsToContents()
