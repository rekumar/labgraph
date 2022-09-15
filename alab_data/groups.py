class Sample:
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"Sample({self.name}, {self.group})"
