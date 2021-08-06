import json, os
from ..Base.FunnyProcedure import FunnyProcedure
from ..Log.TestLog import TestLog

class JSONStarter:
    """
    JSON converter for converting json to Funny Test understanderable procedure function lists
    """

    def __init__(self, testCasePath, customProcedurePath = None):
        self.casePath = testCasePath
        self.customProcedurePath = customProcedurePath
        self.logUtil = TestLog()

    def loadCases(self):
        """
        Convert json file to recognisable function list
        """

        data = {}
        for jsonFileName in os.listdir(self.casePath):
            if jsonFileName.endswith(".json"):
                with open(self.casePath + '/' + jsonFileName, 'r') as jsonFile:
                    runName = os.path.splitext(jsonFileName)[0]

                    if runName not in data:
                        data[runName] = json.load(jsonFile)
                        self.funcList = data
                    else:
                        self.logUtil.log("The test run - " + runName + " already exists.", "warning")
                        continue

    def run(self, isHeadless = False, windowSize = "1920,1080"):
        """
        Run the procedure according to loaded json file

        Return
        ----------
        bool
        Success or not
        """

        try:
            self.loadCases()

            for runName in self.funcList:
                self.funnyProc = FunnyProcedure(isHeadless, windowSize)

                if self.customProcedurePath is not None:
                    self.funnyProc.loadCustomProcedures(self.customProcedurePath)

                funcs = self.funcList[runName]
                self.logUtil.log("Test Run: " + runName)
                self.logUtil.log("++++++++++++++++++++++++++++++\n")

                if not self.funnyProc.procedure(funcs, runName):
                    return False
                
            return True
        except Exception as e:
            self.logUtil.log(e)
            return False

    def getSummary(self):
        """
        Get the summary info of the whole test.

        Return
        ----------
        list
        Summary of successful and failed cases.
        """
        
        return self.funnyProc.summary()
