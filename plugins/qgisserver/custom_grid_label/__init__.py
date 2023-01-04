# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    from .customgridlabel.main import CustomGridLabel
    return CustomGridLabel(iface)


# noinspection PyPep8Naming
def serverClassFactory(serverIface):
    from .customgridlabel.servermain import CustomGridLabelServer
    return CustomGridLabelServer(serverIface)
