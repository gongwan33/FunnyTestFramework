import sys
# append the path of the parent directory
sys.path.append("..")

from FunnyTest.Starter.JSONStarter import JSONStarter

starter = JSONStarter("./TestCases", "./CustomProcedure")
starter.run(True) # True: Headless; False: not headless
res = starter.getSummary()

print("\nTest end.\n")

if res['failedNumber'] > 0:
    exit(-1)
else:
    exit(0)
