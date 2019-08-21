class a(object):
    def __init__(self, x, y):
        self.__x = x
        self.__y = y

class b(a):
    def __init__(self, x, y, z):
        super().__init__(x, y)
        self.__z = z

    def pront(self):
        print (self.__z, self.__y, self.__x)

bew = b(1, 2, 3)
bew.pront()