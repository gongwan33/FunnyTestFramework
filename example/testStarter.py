import sys
# append the path of the parent directory
sys.path.append("..")

from FunnyTest.Starter.JSONStarter import JSONStarter

starter = JSONStarter("./TestCases/test2.json", "./CustomProcedure")
starter.run(True) # True: Headless; False: not headless
starter.getSummary()
