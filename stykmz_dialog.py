# -*- coding: utf-8 -*-
import os
from qgis.PyQt import uic
from qgis.PyQt import QtWidgets

FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'stykmz_dialog_base.ui'))

class StyKMZDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        super(StyKMZDialog, self).__init__(parent)
        self.setupUi(self)
        self.listWidgetCapas.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
