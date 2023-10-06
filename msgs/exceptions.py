class MSGSUnknownProvider(Exception):
    pass


class MSGSProviderIsDisabled(Exception):
    pass


class MSGSTemplateDoesNotExist(Exception):
    pass


class MSGSSignalNotFound(Exception):
    pass


class MSGSConfigurationError(Exception):
    pass


class MSGSCannotBeSent(Exception):
    def __init__(self):
        self.message = (
            "Message instance cannot be sent twice. "
            "Duplicate it instead of multiple sending "
            "or set the `auto_duplicate` option."
        )
        super().__init__(self.message)
