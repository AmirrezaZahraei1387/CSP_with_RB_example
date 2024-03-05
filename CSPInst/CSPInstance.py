
class CSPInstance:
    """
    creating binary CSP instances by a given set of variables, domain and constraints.
    three different search algorithms are provided to search for one single solution of
    in the CSP model. These include Full-Look-ahead, backtracking and forward-checking.

    assignments are used in all the 3 algorithms. If you see a word assignment you can assume
    it is a dict object of the form {variable: value}.Similarly, the partial assignment put emphasis
    on the fact that the assignment is incomplete.

    A simple arc-consistency is implemented using revision method. You can run it after the
    creation of the model.
    """
    def __init__(self, varsD: dict, constraints: dict):
        """
        :param varsD: is a dict object of the form {Var: ["domain of the variable", value1, value2, ...]}
        :param constraints: is a dict object of the form {(Var1, Var2): [(value1, value2), ... ]}
        """
        self.__varsD = varsD
        self.__constraints = constraints

    def __getDomain(self, var: object):
        return self.__varsD[var]

    def __isConsistent(self, var: object, value: object, assignments: dict):
        """
        Checks if the assignment of the variable var with value does not violate any
        of the defined constraints or not. If yes return True otherwise it will return
        False.
        """
        assignments[var] = value

        for constraint in self.__constraints:
            if var in constraint:

                other_var = next(x for x in constraint if x != var)

                if other_var in assignments.keys():
                    assin = list(constraint)
                    assin[assin.index(var)] = value
                    assin[assin.index(other_var)] = assignments.get(other_var)

                    if tuple(assin) in self.__constraints[constraint]:
                        assignments.pop(var)
                        return False
        assignments.pop(var)
        return True

    def __getUnassignedVars(self, assignments: dict):
        """
        find the unassigned variables and then return the one with the least
        domain for efficiency.
        """
        unassigned_vars = [var for var in self.__varsD if var not in assignments]
        return min(unassigned_vars, key=lambda var: len(self.__getDomain(var)))

    def __ac3Revision(self, constraint: tuple):
        """
        get a binary constraint and remove the variables that
        violate from their domains. Mainly used for arc_consistency(ac3)
        """
        revised = False
        for value1 in self.__varsD[constraint[0]]:

            if all((value1, value2) in self.__constraints[constraint] for value2 in self.__varsD[constraint[1]]):
                self.__varsD[constraint[0]].remove(value1)
                revised = True
        return revised

    def __arc_consistency(self):
        queue = list(self.__constraints.keys())

        while queue:
            constraint = queue.pop(0)
            if self.__ac3Revision(constraint):
                for u in self.__constraints:
                    if queue.count(u) == 0:
                        queue.append(u)

    def __backTrackSearch(self, assignments):
        """
        the internal method for backtracking.
        Simply traversing the tree completely to find the solution.
        """
        if len(assignments) == len(self.__varsD):
            return assignments

        var = self.__getUnassignedVars(assignments)

        for value in self.__getDomain(var):
            if self.__isConsistent(var, value, assignments):
                assignments[var] = value
                result = self.__backTrackSearch(assignments)
                if result is not None:
                    return result
                del assignments[var]
        return None

    def backTrackSearch(self):
        assignments = dict()
        return self.__backTrackSearch(assignments)

    def arcConsistency(self):
        self.__arc_consistency()
        print(self.__varsD)




