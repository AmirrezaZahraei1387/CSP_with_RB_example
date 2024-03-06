import math
import random


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

        self.__variables = [f'X{i}' for i in range(self.__varCount)]
        self.__domain = list(range(self.__domainSize))
        self.__constraints = self.__generateConstraints()

    def __generateConstraints(self):
        """
        generate constraints based on RB model according to the paper
        """
        constraints = []
        p_d_squared = int(round(self.__tightness * self.__domainSize ** 2))

        for _ in range(self.__constraintCount):

            flag = False

            while True:
                variables = random.sample(self.__variables, 2)

                for v, _ in constraints:
                    if ((variables[0] == v[0] and variables[1] == v[1]) or (variables[0] == v[1] and
                                                                            variables[1] == v[0])):
                        flag = True
                        break
                if flag:
                    flag = False
                    continue
                break

            incompatible_tuples = []
            for _ in range(p_d_squared):
                t = tuple(random.choices(self.__domain, k=2))

                while t in incompatible_tuples:
                    t = tuple(random.choices(self.__domain, k=2))
                incompatible_tuples.append(t)

            constraints.append((variables, incompatible_tuples))
        return constraints

    def getModelDetails(self):
        return self.__variables, self.__domain, self.__constraints

    def getModelState(self):
        return self.__domainSize, self.__constraintCount, self.__incTupleCount
