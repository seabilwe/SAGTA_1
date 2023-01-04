import typing

from qgis.core import (
    Qgis,
    QgsMessageLog,
)



def log_message(message: str, level: typing.Optional[str] = None):
    msg_level = {
        'warning': Qgis.Warning,
        'critical': Qgis.Critical,
    }.get(level, Qgis.Info)
    QgsMessageLog.logMessage(message, 'custom_grid_label', level=msg_level)
