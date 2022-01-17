class ListCreator(list):
    def __init__(self, *args):
        super(ListCreator, self).__init__(args)

    def __sub__(self, other):
        return self.__class__(*[item for item in self if item not in other])