import CSPInst
import time


def runAlgorithm(func):
    start = time.time()
    result = func()
    end = time.time()
    print("answer: ", result)
    print("take took: {}".format(end - start))


def main():

    varCount = int(input("enter the number of variables: "))
    tightness = float(input("enter the tightness: "))
    alpha = float(input("enter the constant alpha: "))
    rCon = float(input("enter the constant r: "))

    searchingStrategy = input("enter the searching strategy (BT, FC, FLA): ")
    runArcConsistency: bool = input("do you want to run arc consistency(yes/no): ").lower() == "yes"

    # initialing the RB model
    RB_generator = CSPInst.RBModel(
        varCount=varCount,
        tightness=tightness,
        alpha=alpha,
        rCon=rCon
    )

    variables, domain, constraints = RB_generator.getModelDetails()

    CSP_instance = CSPInst.CSPInstance(
        {var: list(domain) for var in variables},
        constraints
    )

    print(variables)
    print(domain)
    for k in constraints:
        print(k, constraints[k])

    if runArcConsistency:
        print("running arc consistency ...")
        CSP_instance.arcConsistency()

    if searchingStrategy == "BT":
        runAlgorithm(CSP_instance.backTrackSearch)
    elif searchingStrategy == "FC":
        runAlgorithm(CSP_instance.forwardChecking)
    elif searchingStrategy == "FLA":
        runAlgorithm(CSP_instance.fullLookAhead)
    else:
        print("invalid searching algorithm.")


if __name__ == "__main__":
    main()

