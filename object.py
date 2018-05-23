class Object:
    """
    A simple Object class similar to JavaScript's "Object"
    """

    def __init__(self):
        self.__dict__['data'] = dict()

    def __getattr__(self, attr):
        try:
            return self.data[attr]
        except KeyError:
            return None

    def __setattr__(self, attr, value):
        self.data[attr] = value
