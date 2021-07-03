import os
import sys
import time
import importlib
from .FunnyTestBase import FunnyTestBase
from ..Log.TestLog import TestLog

class FunnyProcedure:
    """
    The class containing functions for different test procedures
    """

    def __init__(self, isHeadLess = False):
        self.returnList = {}
        self.funnyTestBase = FunnyTestBase(isHeadLess)
        self.customFuncMods = []
        self.failedCases = []
        self.successfulCases = []
        self.logUtil = TestLog()

    def loadCustomProcedures(self, path):
        """
        Import custom procedure functions from a directory

        Parameters
        ----------
        path : string
            The path to the direcotry containing the customized procedures
        """

        sys.path.append(path)
        
        for module in os.listdir(path):
            
            if module == '__init__.py' or module[-3:] != '.py':
                continue
            
            mod = importlib.import_module(module[:-3])
            self.customFuncMods.append(mod)
            
    def getFunc(self, funcName):
        """
        Find custom procedure functions from the module list

        Parameters
        ----------
        funcName : string
            The function name
        """

        for mod in self.customFuncMods:
            if hasattr(mod, funcName):
                return getattr(mod, funcName)

        return None

    def saveResult(self, validationResult, procedureDict):
        """
        Save result to the sucessful/failed cases list

        Parameters
        ----------
        validationResult : dict
            Did the case run successfully or not

        procedureDict: dictionary
            The corresponding dict of the procedure
        
        timeConsumption: number
            The time consumption of this case
        """
        
        procedureDict['testResult'] = validationResult

        if not (validationResult['expectedValueTestResult'] and validationResult['expectedTimeTestResult']):
            self.failedCases.append(procedureDict)
            #break
        else:
            self.successfulCases.append(procedureDict)

    def procedure(self, procedureList):
        """
        The function to deal with procedures 

        Parameters
        ----------
        funcList : array
            The array of function dict
            For example:
            [
                {
                    "type": "stdProcedure",
                    "id": "exampleP1S1",
                    "command": "visit",
                    "params": ["https://google.com", "img", 20],
                    "expect": True,
                },
                {
                    "type": "customProcedure",
                    "id": "exampleP1S2",
                    "command": customFunc1,
                    "params": ["%exampleP1S1", param1, param2, ...],
                    "expect": True,
                },
                ...
            ]
            If a param starts with %, it means it's referring a return value from previous procedure.

        Return
        ----------
        bool
        Return True if no error.
        Otherwise False
        """

        try:
            for procedureDict in procedureList:
                procedureType = procedureDict['type']
                command = procedureDict['command']
                params = procedureDict['params']
                id = procedureDict['id']

                expectValue = None
                if 'expect' in procedureDict:
                    expectValue = procedureDict['expect']
                
                expectTime = None
                if 'expectTime' in procedureDict:
                    expectTime = procedureDict['expectTime']

                self.logUtil.log("Processing: " + id)
                self.logUtil.log("------------------------------------")
                self.logUtil.log("type: " + procedureType)
                self.logUtil.log("command: " + command)
                self.logUtil.log("params: " + ','.join(map(lambda x: str(x), params)))
                self.logUtil.log("expect: " + str(expectValue))
                self.logUtil.log("====================================")

                timeStampStart = time.time()
                if procedureType == 'stdProcedure':

                    if not self.checkReturnIdExist(id):
                        self.returnList[id] = getattr(self.funnyTestBase, command)(*params)

                        timeConsumption = round((time.time() - timeStampStart) * 1000)
                        validationResult = self.validateExpectValue(expectValue, self.returnList[id], expectTime, timeConsumption)
                        self.logUtil.log("Time consumption (ms): " + str(validationResult['actualTime']))

                        self.saveResult(validationResult, procedureDict)
                        
                    else:
                        break

                elif procedureType == 'customProcedure':
                    driver = self.funnyTestBase.getDriver()
                    params.insert(0, driver)

                    if not self.checkReturnIdExist(id):
                        
                        customProcedure = self.getFunc(command)

                        if customProcedure is not None:
                            self.returnList[id] = customProcedure(*params)

                            timeConsumption = round((time.time() - timeStampStart) * 1000)
                            validationResult = self.validateExpectValue(expectValue, self.returnList[id], expectTime, timeConsumption)
                            self.logUtil.log("Time consumption (ms): " + str(validationResult['actualTime']))

                            self.saveResult(validationResult, procedureDict)
                            
                        else:
                            self.logUtil.log('Error: ' + command + 'does not exist.')
                    
                    else:
                        break

                self.logUtil.log("====================================\n\n")

            self.funnyTestBase.close()

        except Exception as e:
            self.logUtil.log(e)
            self.funnyTestBase.close()

            return False

        return True

    def checkReturnIdExist(self, returnId):
        """
        Check if the id already exists in the return list.

        Parameters
        ----------
        returnId : string
            The id of returned value.

        Return
        ----------
        bool
        If existed, return true.
        Otherwise, return false.
        """

        if returnId in self.returnList:
            self.logUtil.log("Warning: this return id: " + returnId + " already exists.")
            return True
        else:
            return False

    def validateExpectValue(self, expectValue, actual, expectTime, timeConsumption):
        """
        Check expect value and actual value

        Parameters
        ----------
        expectValue : any
            Expected value

        actual : any
            Actual returned value

        expectTime : number
            Expected time consumption

        timeConsumption : number
            The actual time consumption of the case

        Return
        ----------
        bool
        If actual returned value equals expected value, return true.
        Otherwise, return false.
        """

        outputTextValue = None
        outputTextTime = None

        expectedValueTestResult = True
        if expectValue != 'any' and expectValue is not None:
            
            if actual == expectValue:
                outputTextValue = ("Success: expect matches.", 'success')
                expectedValueTestResult = True
            else:
                outputTextValue = ("Error: expect is " + str(expectValue) + " | actual is" + str(actual), 'warning')
                expectedValueTestResult = False
            
            self.logUtil.log(*outputTextValue)

        expectedTimeTestResult = True
        if expectTime != 'any' and expectTime is not None:
            
            if expectTime >= timeConsumption:
                expectedTimeTestResult = True
            else:
                outputTextTime = ("Error: expect time consumption is " + str(expectTime) + " ms | actual time consumption is " + str(timeConsumption) + ' ms', 'warning')
                expectedTimeTestResult = False

            if outputTextTime is not None:
                self.logUtil.log(*outputTextTime)

        return {
            'expectedValueTestResult': expectedValueTestResult,
            'expectedValueOutputInfo': outputTextValue,
            'expectedTimeTestResult': expectedTimeTestResult,
            'expectedTimeOutputInfo': outputTextTime,
            'actualTime': timeConsumption,
            'actualReturn': actual,
            'expectedTime': expectTime,
            'expectedReturn': expectValue, 
        }

    def summary(self):
        """
        Print the summary info of the whole test.

        Return
        ----------
        list
        Summary of successful and failed cases.
        """

        self.logUtil.log("++++++++++++++++++++++++++++++")
        self.logUtil.log("Successful cases (" + str(len(self.successfulCases)) + '):', 'success')

        for case in self.successfulCases:
            self.logUtil.log('+ ' + case['id'] + ' (' + str(case['testResult']['actualTime']) + ' ms)')

        self.logUtil.log("")
        self.logUtil.log("Failed cases (" + str(len(self.failedCases)) + '):', "warning")

        for case in self.failedCases:
            testResult = case['testResult']
            self.logUtil.log('+ ' + case['id'] + ' (' + str(testResult['actualTime']) + ' ms)')

            self.logUtil.log("-----------------------------")
            self.logUtil.log("Reason: ")

            if not testResult['expectedValueTestResult'] and not (testResult['expectedReturn'] is None or testResult['expectedReturn'] == 'any'):
                self.logUtil.log("Value dosn't match: (expect - " + str(testResult['expectedReturn']) + " | actual - " + str(testResult['actualReturn']) + ')', 'warning')

            if not testResult['expectedTimeTestResult'] and not (testResult['expectedTime'] is None or testResult['expectedTime'] == 'any'):
                self.logUtil.log("Unexpected time consumption (ms): (expect - " + str(testResult['expectedTime']) + " | actual - " + str(testResult['actualTime']) + ')', 'warning')

            self.logUtil.log("-----------------------------")

        self.logUtil.log("\nTest end.\n")

        return {
            'success': self.successfulCases,
            'fail': self.failedCases,
        }
