from qgis.core import QgsExpression
from qgis.server import (
    QgsRequestHandler,
    QgsServerFilter,
    QgsServerInterface,
)

from .gridlabelfunctions import (
    get_grid_interval,
    get_grid_label
)


class CustomGridLabelServer:

    def __init__(self, serverIface):
        serverIface.registerFilter(CustomGridLabelRequestFilter(
            serverIface), 100)


class CustomGridLabelRequestFilter(QgsServerFilter):

    def __init__(self, serverIface: QgsServerInterface):
        super().__init__(serverIface)

    def requestReady(self):
        request: QgsRequestHandler = self.serverInterface().requestHandler()
        params = request.parameterMap()
        if params.get('REQUEST', '').upper() == 'GETPRINT':
            QgsExpression.registerFunction(
                get_grid_interval, transferOwnership=True)
            QgsExpression.registerFunction(
                get_grid_label, transferOwnership=True)
