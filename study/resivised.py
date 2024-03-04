import numpy as np
import time


class CSPInstance:

    def __init__(self, variables: list, domain: dict, constraints: list):

        # each variable is just a string
        self.__VARS = variables
        self.__DOMAIN = domain
        self.__CONSTS = constraints

    def __get_unassigned_variables(self, assignments: dict):
        """find unassigned variables and return the one with
        the least domain size.
        this method uses mrv heuristic
        """
        unassigned_vars = [var for var in self.__VARS if var not in assignments]
        return min(unassigned_vars, key=lambda var: len(self.__DOMAIN[var]))

    def __order_d_values(self, var: str):
        """
        Order the values in the domain in some way so that the operation can
        be done efficiently. In this case we just return the domain with no changes.
        """
        return self.__DOMAIN[var]

    def __is_consistent(self, var: str, value: object, assignments: dict):
        """
        check if the assignment of a var with value of value is consistent
        with the rest of the assignments or not.
        """
        assignments[var] = value

        # splitting the constraints to their constraint and incompatible tuples
        for const, inc_tuples in self.__CONSTS:

            if var in const:
                other_var = next(v for v in const if v != var)
                if assignments.get(other_var) is not None:
                    if (value, assignments[other_var]) in inc_tuples:
                        assignments.pop(var)  # incompatible assignment is found
                        return False
        assignments.pop(var)  # no incompatible assignment found.
        return True

    def __undo_d(self, incomplete_assignments: dict, assignments: dict):
        """
        undo all the changes to the domain mainly done with FLA and FC
        """
        # first split the incomplete_assignments to variables and values
        for v, value in incomplete_assignments:
            assignments.pop(v)
            self.__DOMAIN[v].append(value)

    def __arc_consistency(self, assignments: dict):
        """
        remove all the values from domain of variables that can not coexist with
        the other connected variables. This helps us to reduce the size of search space.
        """
        # making a copy of the constraints
        copy_constraints = list(self.__CONSTS)
        inf = {}

        while copy_constraints:
            consts, inc_tuples = copy_constraints.pop(0)

            if all(v in assignments for v in consts):
                other_vars = [v for v in consts if v != var]
                for var in other_vars:
                    inf[var] = []

                    for value in self.__DOMAIN[var]:
                        if not any((value, assignments[v]) in inc_tuples for v in other_vars):
                            inf[var].append(value)
                            self.__DOMAIN[var].remove(value)
                            copy_constraints.extend(
                                (c, incompatible_tuples) for c, incompatible_tuples in self.__CONSTS if
                                var in c and set(other_vars).issubset(set(c)))
        return inf

    def __backTrack_search(self, assignments: dict):
        """
        backtracking
        """
        if len(assignments) == len(self.__VARS):
            return assignments

        var = self.__get_unassigned_variables(assignments)

        for value in self.__order_d_values(var):
            if self.__is_consistent(var, value, assignments):
                assignments[var] = value
                result = self.__backTrack_search(assignments)
                if result is not None:
                    return result
                del assignments[var]

        return None

    def __forward_check(self, var: str, assignments: dict):

        for consts, inc_tuples in self.__CONSTS:
            if var in consts:
                other_var = next(v for v in consts if v != var)
                if assignments.get(other_var) is None:
                    new_domain = [val for val in self.__DOMAIN[other_var] if
                                  (assignments[var], val) not in inc_tuples]
                    if not new_domain:
                        return False
                    self.__DOMAIN[other_var] = new_domain

        return True

    def __forward_checking(self, assignments: dict):
        """
        internal method for forward checking
        """
        if len(assignments) == len(self.__VARS):
            return assignments

        var = self.__get_unassigned_variables(assignments)

        for value in self.__order_d_values(var):
            if self.__is_consistent(var, value, assignments):

                assignments[var] = value

                if self.__forward_check(var, assignments):
                    result = self.__forward_checking(assignments)
                    if result is not None:
                        return result
                del assignments[var]
                self.__undo_d({var: value}, assignments)
        return None

    def __ful_look_ahead(self, assignments: dict):
        if len(assignments) == len(self.__VARS):
            return assignments

        var = self.__get_unassigned_variables(assignments)
        for value in self.__order_d_values(var):
            if self.__is_consistent(var, value, assignments):
                assignments[var] = value
                inferences = self.__arc_consistency(assignments)
                if inferences:
                    result = self.__ful_look_ahead(assignments)
                    if result is not None:
                        return result
                del assignments[var]
                self.__undo_d(inferences, assignments)

        return None

    def full_look_ahead(self):
        assignments = {}
        return self.__ful_look_ahead(assignments)

    def backTracking_search(self):
        assignments = {}
        return self.__backTrack_search(assignments)

    def forward_checking(self):
        assignments = {}
        return self.__forward_checking(assignments)

    def arc_consistency(self):
        assignments = {}
        return self.__arc_consistency(assignments)

    def printCSPInstance(self, domain: list):
        print("CSP instance: ")
        print("variables: ", self.__VARS)
        print("domain", domain)
        print("constraints:")
        for constraint, incompatible_tuples in self.__CONSTS:
            print(f"{constraint}: {incompatible_tuples}")
        return domain,self.__VARS,self.__CONSTS


class RBModel:
    """
    implementing the random binary model for generating random binary CSP models
    the required parameters are provided by user.
    then, an instance of a csp is created by the class CSPInstance
    """

    def __init__(self, varCount: int, tightness: float, alpha: float, rCon: float):
        
        self.__varCount = varCount
        self.__tightness = tightness
        self.__alpha = alpha
        self.__rCon = rCon

        self.domain_size = round(self.__varCount ** self.__alpha)
        self.num_constraints = round(self.__rCon * self.__varCount * np.log(self.__varCount))
        self.num_incompatible_tuples = round(self.__tightness * (self.domain_size ** 2))

        self.__variables = [f'X{i}' for i in range(self.__varCount)]
        self.__domain = list(range(self.domain_size))
        self.constraints=self.__generate_constraints()
        print (self.constraints)
        self.csp_model = CSPInstance(variables=self.__variables,
                                     domain={var: list(self.__domain) for var in self.__variables},
                                     constraints=self.constraints)

    def __generate_constraints(self):
        """
        generate constraints based on RB model acording to the paper
        """
        constraints = []
        p_d_squared = int(round(self.__tightness * self.domain_size ** 2))

        for _ in range(self.num_constraints):

            flag = False

            while True:
                variables = np.random.choice(self.__variables, size=2, replace=False)
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
                t = tuple(np.random.choice(self.__domain, size=2, replace=True))

                while t in incompatible_tuples:
                    t = tuple(np.random.choice(self.__domain, size=2, replace=True))
                incompatible_tuples.append(t)

            constraints.append((variables, incompatible_tuples))
        return constraints

    def getCSPModel(self):
        return self.csp_model

    def getDomain(self):
        return self.__domain


def test(varCount, tightness, alpha, rCon, solve_with, run_arc_consistency):
    rb_model = RBModel(varCount, tightness, alpha, rCon)
    csp_instance: CSPInstance = rb_model.getCSPModel()

    data=csp_instance.printCSPInstance(rb_model.getDomain())
    if run_arc_consistency:
        print("arc consistency results: ", csp_instance.arc_consistency())
    start = time.time()
    if solve_with == "BT":
        sol=csp_instance.backTracking_search()
        end = time.time()
    elif solve_with == "FC":
        sol=csp_instance.forward_checking()
        end = time.time()
    elif solve_with == "FLA":
        sol=csp_instance.full_look_ahead()
        end = time.time()
    else:
        print("invalid searching algorithm")
    print("Possible Solution: ",sol)
    print("time took to run is ", end - start)
    return data,sol


def main():
    varCount = int(input("enter the number of variables: "))
    tightness = float(input("enter the tightness: "))
    alpha = float(input("enter the constant alpha: "))
    rCon = float(input("enter the constant r: "))

    solve_with = input("enter the solving strategy(BT, FC, FLA): ")
    run_arc_consistency: bool = input("do you want to run arc consistency(yes/no): ") == "yes"

    rb_model = RBModel(varCount, tightness, alpha, rCon)
    csp_instance: CSPInstance = rb_model.getCSPModel()

    csp_instance.printCSPInstance(rb_model.getDomain())
    if run_arc_consistency:
        print("arc consistency results: ", csp_instance.arc_consistency())
    start = time.time()
    if solve_with == "BT":
        print("Possible Solution: ", csp_instance.backTracking_search())
        end = time.time()
        print("time took to run is ", end - start)
    elif solve_with == "FC":
        print("Possible Solution: ",csp_instance.forward_checking())
        end = time.time()
        print("time took to run is ", end - start)
    elif solve_with == "FLA":
        print("Possible Solution: ",csp_instance.full_look_ahead())
        end = time.time()
        print("time took to run is ", end - start)
    else:
        print("invalid searching algorithm")


if __name__ == "__main__":
    main()
