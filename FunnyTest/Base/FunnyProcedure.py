import os
import sys
import time
import re
import importlib
import builtins
import copy
from .FunnyTestBase import FunnyTestBase
from ..Log.TestLog import TestLog

class FunnyProcedure:
    """
    The class containing functions for different test procedures
    """

    def __init__(self, isHeadLess = False, windowSize = "1920,1080"):
        self.returnList = {}
        self.funnyTestBase = FunnyTestBase(isHeadLess, windowSize)
        self.customFuncMods = []
        self.summaries = {}
        self.logUtil = TestLog()
        self.subprocedureList = {}

    def parseShortCode(self, param, runName, procedureDict):
        """
        Parse short codes

        Parameters
        ----------
        param : string
            The original param string

        runName : string
            The run name

        procedureDict : dict
            The procedure definition where the param is from

        Return
        ----------
        any
        The result params
        """

        if isinstance(param, str) and len(param) > 2:

            # Check for %loopParam%
            # Check for %result[procedureID]%
            match = re.search(r'(.*)%loopParam%(.*)', param)

            if match != None and len(match.groups()) >= 1:

                if 'loopParam' in procedureDict:

                    if not isinstance(procedureDict['loopParam'], str):
                        return procedureDict['loopParam']

                    prefix = match.group(1)
                    resVal = prefix + procedureDict['loopParam']

                    if len(match.groups()) > 1:
                        surfix = match.group(2)
                        resVal = resVal + surfix

                    return resVal

            else:

                # Check for %result[procedureID]%
                match = re.search(r'(.*)%result\[\"?\'?(\w+)\'?\"?\]%(.*)', param)

                if match != None and len(match.groups()) >= 2:
                    resKey = match.group(2)
                    prefix = match.group(1)

                    if (runName in self.returnList) and (resKey in self.returnList[runName]):

                        savedRes = self.returnList[runName][resKey]

                        if not isinstance(savedRes, str):
                            return savedRes

                        resVal = prefix + savedRes

                        if len(match.groups()) > 2:
                            surfix = match.group(3)

                            if len(surfix) > 0 and type(resVal) == str:
                                resVal = prefix + resVal + surfix

                        return resVal

        return param

    def generateParams(self, params, runName, procedureDict):
        """
        Filter params and replace the elements according to the Funny Test Magic Param rules

        Parameters
        ----------
        params : list
            The original params

        runName : string
            The run name

        procedureDict : dict
            The procedure definition where the params are from

        Return
        ----------
        list
        The result params
        """
        
        resParams = []
        for param in params:
            resParams.append(self.parseShortCode(param, runName, procedureDict))
        
        return resParams

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

    def saveResult(self, validationResult, procedureDict, runName):
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

        if runName not in self.summaries:
            self.summaries[runName] = {
                'successfulCases': [],
                'failedCases': [],
            }

        if not (validationResult['expectedValueTestResult'] and validationResult['expectedTimeTestResult']):
            
            self.summaries[runName]['failedCases'].append(procedureDict)
            #break
        else:

            self.summaries[runName]['successfulCases'].append(procedureDict)

    def procedure(self, procedureList, runName, specialProcedure = None):
        """
        The function to deal with procedures 

        Parameters
        ----------
        procedureList : array
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
        
        rumName : string
            Run name for the procedures
        
        specialProcedure : dict
            {
                'type': loop/subprocedure,
                'parentName': name
            }

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
                id = procedureDict['id']

                if specialProcedure is not None:
                    id = specialProcedure['parentName'] + '.' + id
                    procedureDict['id'] = id

                params = None
                if 'params' in procedureDict:
                    params = procedureDict['params']

                expectValue = None
                if 'expect' in procedureDict:
                    expectValue = procedureDict['expect']
                
                expectTime = None
                if 'expectTime' in procedureDict:
                    expectTime = procedureDict['expectTime']

                condition = None
                if 'condition' in procedureDict:
                    condition = procedureDict['condition']
                
                subprocedure = None
                if 'subprocedure' in procedureDict and specialProcedure is None:
                    subprocedure = procedureDict['subprocedure']

                    if subprocedure not in self.subprocedureList:
                        self.subprocedureList[subprocedure] = []

                    del procedureDict['subprocedure']

                    self.subprocedureList[subprocedure].append(procedureDict)

                    self.logUtil.log("Subprocedure: " + subprocedure + " [" + id + "] added.\n")

                    continue

                if params != None:
                    params = self.generateParams(params, runName, procedureDict)
                
                self.logUtil.log("Processing: " + id)
                self.logUtil.log("------------------------------------")
                self.logUtil.log("type: " + procedureType)
                self.logUtil.log("command: " + command)

                if params != None:
                    self.logUtil.log("params (" + str(len(params)) + "): " \
                        + ','.join(map(lambda x: (str(x) if len(str(x)) < 500 else str(x)[0:500] + '...') if hasattr(x, '__str__') else '<Unprintable variable>', params)))

                if condition != None:
                    self.logUtil.log("condition: " + str(condition))

                if expectValue != None:
                    self.logUtil.log("expect: " + str(expectValue))

                if expectTime != None:
                    self.logUtil.log("expect time: " + str(expectTime))
                self.logUtil.log("====================================")

                if condition != None and not self.parseShortCode(condition, runName, procedureDict):
                    self.logUtil.log("Condition value is: " + str(condition))
                    continue
                
                timeStampStart = time.time()

                # Call standard procedures
                if procedureType == 'stdProcedure':
                    
                    if not self.checkReturnIdExist(id, runName):
                        self.returnList[runName][id] = getattr(self.funnyTestBase, command)(*params)
                        
                        timeConsumption = round((time.time() - timeStampStart) * 1000)
                        validationResult = self.validateExpectValue(expectValue, self.returnList[runName][id], expectTime, timeConsumption)
                        self.logUtil.log("Time consumption (ms): " + str(validationResult['actualTime']))

                        self.saveResult(validationResult, procedureDict, runName)
                        
                    else:
                        self.logUtil.log("Duplicated procedure id.", 'warning')
                        break

                # Call custom procedures from injected outside definition file
                elif procedureType == 'customProcedure':
                    driver = self.funnyTestBase.getDriver()
                    params.insert(0, driver)

                    if not self.checkReturnIdExist(id, runName):
                        
                        customProcedure = self.getFunc(command)

                        if customProcedure is not None:
                            self.returnList[runName][id] = customProcedure(*params)

                            timeConsumption = round((time.time() - timeStampStart) * 1000)
                            validationResult = self.validateExpectValue(expectValue, self.returnList[runName][id], expectTime, timeConsumption)
                            self.logUtil.log("Time consumption (ms): " + str(validationResult['actualTime']))

                            self.saveResult(validationResult, procedureDict, runName)
                            
                        else:
                            self.logUtil.log('Error: ' + command + 'does not exist.', 'warning')
                    
                    else:
                        self.logUtil.log("Error: Duplicated procedure id.", 'warning')
                        break

                # Start loop
                # command => Subprocedure name
                # params => The list to loop through
                elif procedureType == 'loop':

                    self.logUtil.log("\nLoop procedure start\n")

                    if params is None or len(params) <= 0:
                        self.logUtil.log("Error: illegal loop params.", 'warning')
                        break

                    loopParams = params[0]
                    if command in self.subprocedureList and isinstance(loopParams, list):
                        for (idx, param) in enumerate(loopParams):

                            self.logUtil.log("Loop param: " + param + " subprocedure: " + command)

                            currentSubprocedures = copy.deepcopy(self.subprocedureList[command])

                            # add the loop parameter to subprocedureDict
                            for subpro in currentSubprocedures:
                                subpro['loopParam'] = param

                            self.procedure(currentSubprocedures, runName, {'type': 'subprocedure', 'parentName': id + '.' + str(idx) + '.' + command})

                    else:
                        self.logUtil.log("Target subprodure for loop does not exist.", 'warning')
                        break

                # Call subprocedures
                # command => Subprocedure name
                elif procedureType == 'callSubprocedure':

                    self.logUtil.log("\nCalling subprocedure - " + command + "\n")

                    if command in self.subprocedureList:
                        subList = copy.deepcopy(self.subprocedureList[command])
                        self.procedure(subList, runName, {'type': 'subprocedure', 'parentName': command})
                    else:
                        self.logUtil.log("Target subprodure does not exist.", 'warning')
                        break

                self.logUtil.log("====================================\n\n")

            if specialProcedure is None:
                self.funnyTestBase.close()

        except Exception as e:
            self.logUtil.log(e)
            self.funnyTestBase.close()

            return False

        return True

    def checkReturnIdExist(self, returnId, runName):
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
        
        if runName not in self.returnList:
            self.returnList[runName] = {}
            return False
        
        if returnId in self.returnList[runName]:
            self.logUtil.log("Warning: this return id: " + returnId + " already exists.", "warning")
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
            
            outputTextValue = ("Success: expect matches.", 'success')

            if not isinstance(expectValue, list) and actual == expectValue:
                expectedValueTestResult = True
            elif isinstance(expectValue, list) and len(expectValue) == 2:
                operator = expectValue[0].strip()

                if isinstance(expectValue[1], str):
                    expected = expectValue[1].strip()
                else:
                    expected = expectValue[1]

                if eval(str(actual) + operator + str(expected)):
                    expectedValueTestResult = True
                else:
                    expectedValueTestResult = False

            elif isinstance(expectValue, list) and len(expectValue) == 3:
                cmd = expectValue[0].strip()
                operator = expectValue[1].strip()

                if isinstance(expectValue[2], str):
                    expected = expectValue[2].strip()
                else:
                    expected = expectValue[2]

                cmdParts = cmd.split(':')

                if len(cmdParts) == 2:
                    cmdType = cmdParts[0].strip()
                    cmdContent = cmdParts[1].strip()

                    if cmdType == 'pythonFunc' and eval(str(getattr(builtins, cmdContent)(actual)) + operator + str(expected)):
                        expectedValueTestResult = True
                    else:
                        expectedValueTestResult = False

                else:
                    expectedValueTestResult = False

            else:
                expectedValueTestResult = False

            if not expectedValueTestResult:
                outputTextValue = ("Error: expect is " + str(expectValue) + " | actual is" + str(actual), 'warning')
            
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

        failedNumber = 0
        successfulNumber = 0

        self.logUtil.log("Test Summary")

        for runName in self.summaries:

            successfulCases = self.summaries[runName]['successfulCases']
            failedCases = self.summaries[runName]['failedCases']

            successfulNumber += len(successfulCases)
            failedNumber += len(failedCases)

            self.logUtil.log("++++++++++++++++++++++++++++++")
            self.logUtil.log("Test Run:" + runName)
            self.logUtil.log("++++++++++++++++++++++++++++++")

            self.logUtil.log("Successful cases (" + str(len(successfulCases)) + '):', 'success')

            for case in successfulCases:
                self.logUtil.log('+ ' + case['id'] + ' (' + str(case['testResult']['actualTime']) + ' ms)')

            self.logUtil.log("")
            self.logUtil.log("Failed cases (" + str(len(failedCases)) + '):', "warning")

            for case in failedCases:
                testResult = case['testResult']
                self.logUtil.log('+ ' + case['id'] + ' (' + str(testResult['actualTime']) + ' ms)')

                self.logUtil.log("-----------------------------")
                self.logUtil.log("Reason: ")

                if not testResult['expectedValueTestResult'] and not (testResult['expectedReturn'] is None or testResult['expectedReturn'] == 'any'):
                    self.logUtil.log("Value dosn't match: (expect - " + str(testResult['expectedReturn']) + " | actual - " + str(testResult['actualReturn']) + ')', 'warning')

                if not testResult['expectedTimeTestResult'] and not (testResult['expectedTime'] is None or testResult['expectedTime'] == 'any'):
                    self.logUtil.log("Unexpected time consumption (ms): (expect - " + str(testResult['expectedTime']) + " | actual - " + str(testResult['actualTime']) + ')', 'warning')

                self.logUtil.log("-----------------------------")

        return {
            'successNumber': successfulNumber,
            'failedNumber': failedNumber,
        }
