from mcdreforged.utils.serializer import Serializable


class RemoteCommandResult(Serializable):
    success: bool = True

    def __init__(self, success: bool = True, **kwargs):
        super().__init__(**kwargs)
        self.success = success
