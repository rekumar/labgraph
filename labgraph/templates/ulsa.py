from templates import BaseTemplate


class HeatingAction(BaseTemplate):
    def __init__(self, name: str, temperature: float, duration: int, **kwargs):
        super().__init__(name, type="HeatingAction")
        self.parameters = {
            "temperature": temperature,
            "duration": duration,
        }
        if any(key in kwargs for key in self.parameters):
            raise ValueError("Got multiple arguments for same parameter!")
        self.parameters.update(kwargs)


class MixingAction(BaseTemplate):
    def __init__(self, name: str, duration: int, **kwargs):
        super().__init__(name, type="MixingAction")
        self.duration = duration
