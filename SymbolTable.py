class SymbolTable:
    def __init__(self):
        self._kind_dict = {}
        self._type_dict = {}
        self._index_dict = {}

    def __contains__(self, item):
        if item in self._kind_dict:
            return True
    def varCount(self, kind):
        count = 0
        for var in self._kind_dict:
            if self._kind_dict[var] == kind:
                count += 1
        return count

    def define(self, id_name, id_type, id_kind):
        if id_kind == 'var':
            id_kind = 'local'
        if id_kind == 'field':
            id_kind = 'this'
        self._index_dict[id_name] = self.varCount(id_kind)
        self._kind_dict[id_name] = id_kind
        self._type_dict[id_name] = id_type


    def getKind(self, name):
        return self._kind_dict[name]

    def getType(self, name):
        return self._type_dict[name]

    def getIndex(self, name):
        return self._index_dict[name]

    def startSubroutine(self):
        self._kind_dict = {}
        self._type_dict = {}
        self._index_dict = {}
