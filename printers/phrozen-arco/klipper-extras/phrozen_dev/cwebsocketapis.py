####################################
# Phrozen ChromaKit (MMU) - Websocket API Registration
# Developer: Lan Caigang
# Created: 2023-08-30
####################################


from .cmds import *

####################################
# Websocket API layer
# Inherits from Commands, adds websocket endpoints
####################################
class Apis(Commands):
    # Constructor
    def __init__(self, config):
        super(Apis, self).__init__(config)
        self.G_WebsocketWebhooks = self.G_PhrozenPrinter.lookup_object("webhooks")

    # Register custom websocket API endpoints
    def WebsocketAPIs_RegisterAPIs(self):
        self.G_PhrozenFluiddRespondInfo("[(dev.python)WebsocketAPIs_RegisterAPIs] Register phrozen custom websocket API")
        self.G_WebsocketWebhooks.register_endpoint("phrozen/soft_ver", self.WebsocketAPIs_SoftVersion)

    # Handle software version query via websocket
    def WebsocketAPIs_SoftVersion(self, web_request):
        self.G_PhrozenFluiddRespondInfo("[(dev.python)WebsocketAPIs_SoftVersion]")
        # Send version response via websocket
        web_request.send({"soft_version": FW_VERSION})
