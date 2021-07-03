class TestLog:
    """
    The class for logging function
    """

    OKGREEN = '\033[92m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

    preFixMap = {
        'warning': FAIL,
        'success': OKGREEN,
    }

    def log(self, text, type = "info", target = "screen"):
        """
        Print text to the target

        Parameters
        ----------
        text : string
            The text to pring

        type : string
            The type of the text. info | warning | success

        target : string
            The target for print. Default to screeen.
        """

        textToPrint = ''
        if type in self.preFixMap:
            textToPrint = self.preFixMap[type] + text + self.ENDC
        else:
            textToPrint = text

        if target == 'screen':
            print(textToPrint)