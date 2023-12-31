import time
import traceback
from views.pricing.components.ui_newofferdialog import Ui_Dialog
from PyQt5.QtCore import Qt, QThread, QObject, pyqtSignal
from PyQt5.QtWidgets import QDialog, QMessageBox
from jinja2 import Environment, FileSystemLoader
from utils.general import findi, find
from utils.log import *
import utils.glo as glo
from utils.exceptions import AuthenticationError
from components.logindialog import LoginDialogLogic

class NewOfferDialog(QDialog, Ui_Dialog):

    def __init__(self, parent=None):
        super(NewOfferDialog, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("Create New Offer")
        self.groupNameMap = {}  # GroupName: (GroupId, unitCost)
        self.lowestPrice = -1
        self.productId = ""

    def addShippingGroupItem(self, groupName, groupId, unitCost):
        self.groupNameMap[groupName] = (groupId, unitCost)
        self.shippingGroup.addItem(groupName)

    def setProductId(self, productId):
        self.productId = productId

    def setNewOffer(self, price, quantity, shippingGroupId):
        self.unitPrice.setValue(price)
        self.quantity.setValue(quantity)
        groupName = find(self.groupNameMap.keys(), key=lambda k: self.groupNameMap[k][0] == shippingGroupId)
        i = self.shippingGroup.findText(groupName)
        if i != -1:
            self.shippingGroup.setCurrentText(groupName)

    def getOfferFromUserInput(self):
        unitPrice = self.unitPrice.value()
        quantity = self.quantity.value()
        groupName = self.getShippingGroupName()
        groupId = self.groupNameMap[groupName][0]
        return (unitPrice, quantity, groupId)

    def setTextBrowser(self, html):
        self.textBrowser.setText(html)

    def setProductName(self, productName):
        self.productName.setText(productName)

    def setLowestPrice(self, price):
        self.lowestPrice = price

    def getShippingGroupName(self):
        groupName = self.shippingGroup.currentText()
        return groupName

    def getShippingGroupId(self):
        groupName = self.getShippingGroupName()
        return self.groupNameMap[groupName][0]

    def getUnitPrice(self):
        return self.unitPrice.value()

    @property
    def profit(self):
        return self.totalPrice - self.lowestPrice

    @property
    def totalPrice(self):
        unitPrice = self.getUnitPrice()
        groupName = self.getShippingGroupName()
        return float(unitPrice) + self.groupNameMap[groupName][1]
# ============= Logic =====================

class Communication(QObject):
    sg_shippinggroups = pyqtSignal(dict)

class ShippingGroupThread(QThread):

    GET_LIST = 0

    def __init__(self, parent=None, api=None, task=0):
        super(ShippingGroupThread, self).__init__(parent)
        self.api = api
        self.parent = parent
        self.task = task
        self.data = []

    def run(self) -> None:
        if self.task == self.GET_LIST:
            data = self.api.fetchListShippingGroup()
            self.data = data
            self.parent.communication.sg_shippinggroups.emit(data)

class NewOfferDialogLogic(NewOfferDialog):

    def __init__(self, parent=None, api=None):
        super(NewOfferDialogLogic, self).__init__(parent)
        self.api = api
        self.communication = Communication()
        self.communication.sg_shippinggroups.connect(self.addShippingGroupItemsToComboBox)
        self.confirmBox.accepted.connect(self.onClickButtonConfirm)
        self.shippingGroup.currentTextChanged.connect(self.onComboboxChanged)
        self.unitPrice.textChanged.connect(self.onChangedUnitPrice)
        thread = ShippingGroupThread(self, api, task=ShippingGroupThread.GET_LIST)
        thread.start()
        thread.wait()
        self.addShippingGroupItemsToComboBox(thread.data)
        pass

    def addShippingGroupItemsToComboBox(self, data):
        for sg in data['data']:
            self.addShippingGroupItem(sg['groupName'], sg['id'], sg['unitCost'])
        # self.renderTextBrowser()

    def onClickButtonConfirm(self):
        unitPrice, quantity, groupId = self.getOfferFromUserInput()
        token = glo.getValue("token")
        print("|".join((self.productId,
                        str(unitPrice), str(quantity),
                        groupId, token)))
        payload = dict(productId=self.productId, price=unitPrice,
                       quantity=quantity, shippingGroupId=groupId,
                       token=token)
        try:
            self.api.postNewOffer(payload)
            QMessageBox.information(self, "Info", "New offer has been updated.")
        except AuthenticationError as e:
            QMessageBox.critical(self, "Error", "Please login.")
            log_stdout(e)
            log_error(e)
            dialog = LoginDialogLogic(self, self.api)
            dialog.exec_()
        pass

    def onChangedUnitPrice(self):
        if self.getShippingGroupName() != "":
            self.renderTextBrowser()

    def __getShippingGroupDetail(self):
        data = self.api.fetchShippingGroupById(self.getShippingGroupId())
        if data is not None:
            if data['code'] == 20000:
                sg = data['data']
                self.groupNameMap[self.getShippingGroupName()] = (sg['id'], sg['unitCost'])
        else:
            log_stdout("Network error")
        return self.groupNameMap[self.getShippingGroupName()]

    def onComboboxChanged(self):
        data = self.__getShippingGroupDetail()
        print(self.getShippingGroupName(), self.getShippingGroupId(), self.totalPrice)
        self.renderTextBrowser()

    def renderTextBrowser(self):
        env = Environment(loader=FileSystemLoader('./'))
        template = env.get_template("assets/newofferdetails.html")
        content = template.render(lprice= f"{self.lowestPrice: .2f}",
                                  profit=f"{self.profit: .2f}",
                                  total=f"{self.totalPrice: .2f}",
                                  productId=self.productId)
        self.setTextBrowser(content)

    def exec_(self) -> tuple:
        reply = super(NewOfferDialogLogic, self).exec_()
        if reply == 1:
            unitPrice, quantity, groupId = self.getOfferFromUserInput()
            log_stdout(unitPrice, quantity, groupId)
            log_info(f"New offer: {unitPrice} {quantity} {groupId}")
            return (unitPrice, quantity, self.getShippingGroupName())
        return None

