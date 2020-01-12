class Token:

    def __init__(self, token_type, token_value):
        self.tokenType = token_type
        self.__value = token_value
        self.__next = None

    def get_type(self):
        return self.tokenType

    def get_value(self):
        return self.__value

    def set_next(self, token):
        self.__next = token

    def get_next(self):
        return self.__next

    def print_debug_token(self):
        print(self.__value + ":" + self.tokenType)
