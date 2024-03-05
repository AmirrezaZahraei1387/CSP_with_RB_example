import math


class RBModel:
    """
    the RB model is used to generate CSP instances under
    the control of difficulty to solve the CSP model.
    """

    def __init__(self, varCount: int, tightness: float, alpha: float, rCon: float):

        self.__varCount = varCount
        self.__tightness = tightness
        self.__alpha = alpha
        self.__rCon = rCon

        self.__domainSize = round(self.__varCount ** alpha)
        self.__constraintCount = round(self.__rCon * self.__varCount * math.log(self.__varCount))
        self.__incTupleCount = round(self.__tightness * (self.__domainSize ** 2))

    def generateConstraints(self):
        pass

    def getModelState(self):
        return self.__domainSize, self.__constraintCount, self.__incTupleCount
