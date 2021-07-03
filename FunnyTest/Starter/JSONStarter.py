import json
from ..Base.FunnyProcedure import FunnyProcedure

class JSONStarter:
    """
    JSON converter for converting json to Funny Test understanderable procedure function lists
    """

    def __init__(self, testCasePath, customProcedurePath = None):
        self.casePath = testCasePath
        self.customProcedurePath = customProcedurePath

    def loadCases(self):
        """
        Convert json file to recognisable function list
        """
        with open(self.casePath) as jsonFile:
            data = json.load(jsonFile)
            self.funcList = data

    def run(self, isHeadless = False):
        """
        Run the procedure according to loaded json file
        """
        self.loadCases()

        self.funnyProc = FunnyProcedure(isHeadless)

        if self.customProcedurePath is not None:
            self.funnyProc.loadCustomProcedures(self.customProcedurePath)

        self.funnyProc.procedure(self.funcList)

    def getSummary(self):
        """
        Get the summary info of the whole test.

        Return
        ----------
        list
        Summary of successful and failed cases.
        """
        
        return self.funnyProc.summary()