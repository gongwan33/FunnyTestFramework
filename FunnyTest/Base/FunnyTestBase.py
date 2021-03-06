from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver import ActionChains

from ..Log.TestLog import TestLog

class FunnyTestBase:
    """
    The basic function class based on selenium
    Only support chromedriver at the moment
    Author: Richard Wong
    """

    def __init__(self, isHeadless = False, windowSize = "1920,1080"):
        """
        Constructor 

        Parameters
        ----------
        isHeadless : bool
            set the browser to headless mode
        windowSize : string
            set the window size for headless mode
        """

        self.chrome_options = webdriver.ChromeOptions()
        self.chrome_options.add_argument("--window-size=%s" % windowSize)

        if isHeadless:
            self.chrome_options.add_argument("--headless")
            self.chrome_options.add_argument("--no-sandbox")

        self.driver = webdriver.Chrome(options = self.chrome_options)
        self.logUtil = TestLog()

    def __del__(self):
        """
        Destructor 
        """

        if self.driver is not None:
            self.close()

    def getDriver(self):
        """
        Get current driver

        Return
        ----------
        object
        Current driver
        """

        return self.driver

    def visit(self, url, waitCSS = None, timeOut = 40, waitFunc = "visibility_of_element_located", appendCredential = None):
        """
        Visit a specific url and wait for a specific element 

        Parameters
        ----------
        url : string
            The target url
        waitCSS : string
            The css for locating the target element to wait util return a result. If set None, no element will be waited
        timeOut : int
            The seconds to wait
        waitFunc : string
            The EC function used for detecting target element. 
            For example: visibility_of_element_located, invisibility_of_element_located, 
            presence_of_element_located, element_to_be_clickable
        appendCredential : string
            The credentials for browser verification. (Format: "username:password")

        Return
        ----------
        bool
        If found the target element (waitCSS is not None) or load finished without error, return True
        Otherwise, return False
        """

        try:
            if appendCredential is not None:
                url = url.replace('https://', 'https://' + appendCredential + '@')
                url = url.replace('http://', 'https://' + appendCredential + '@')
            
            self.driver.get(url)

            if waitCSS is not None:
                WebDriverWait(self.driver, timeOut).until(
                    getattr(EC, waitFunc)((By.CSS_SELECTOR, waitCSS))
                )
        except Exception as e:
            self.logUtil.log(e)
            self.close()
            return False

        return True

    def close(self):
        """
        Close driver
        """

        if self.driver is not None:
            self.driver.close()
            self.driver = None

    def closeCurrentWindow(self):
        """
        Close current window
        """

        try:
            if self.driver is not None:
                self.driver.close()
        except Exception as e:
            self.logUtil.log(e)
            return False

        return True


    def waitFor(self, waitCSS, timeOut = 40, waitFunc = "visibility_of_element_located"):
        """
        Wait for a specific element 

        Parameters
        ----------
        waitCSS : string
            The css for locating the target element to wait.
        timeOut: int
            The seconds to wait
        waitFunc: string
            The EC function used for detecting target element. 
            For example: visibility_of_element_located, invisibility_of_element_located, 
            presence_of_element_located, element_to_be_clickable

        Return
        ----------
        bool
        If target element matched, return True.
        Otherwise, return False.
        """

        try:
            WebDriverWait(self.driver, timeOut).until(
                getattr(EC, waitFunc)((By.CSS_SELECTOR, waitCSS))
            )

        except Exception as e:
            self.logUtil.log('Not found.', 'warning')
            self.logUtil.log(e)
            return False

        return True

    def click(self, css):
        """
        Click a specific element 

        Parameters
        ----------
        css : string
            The css for locating the target clickable element.
        """

        try:
            target = self.driver.find_element(By.CSS_SELECTOR, css)

            if target is not None:

                target.click()
                return True
        except Exception as e:
            self.logUtil.log(e)
            self.close()

            return False

        return False

    def selectOption(self, css, value):
        """
        Select a specific option in a select list 

        Parameters
        ----------
        css : string
            The css for locating the target select element.
        value: string
            The value of the target option

        Return
        ----------
        bool
        Return True if successfully selected.
        Otherwise return False.
        """

        try:
            target = self.driver.find_element(By.CSS_SELECTOR, css)

            if target is not None:
                options = target.find_element(By.CSS_SELECTOR, "option")
                
                for option in options:
                    optValue = options.get_attribute('value')

                    if optValue == value:
                        option.click()
                        return True
                
                self.logUtil.log("Option not found.")

        except Exception as e:
            self.logUtil.log(e)
            self.close()
            return False

        return False

    def input(self, css, value):
        """
        Type in a text box.

        Parameters
        ----------
        css : string
            The css for locating the target input element.
        value: string
            The value for input

        Return
        ----------
        bool
        Return True if successfully input.
        Otherwise return False.
        """

        try:
            target = self.driver.find_element(By.CSS_SELECTOR, css)

            if target is not None:
                target.send_keys(value)

                return True

        except Exception as e:
            self.logUtil.log(e)
            self.close()
            return False

        return False

    def getAttribute(self, css, attr):
        """
        Count the attribute from a element.

        Parameters
        ----------
        css : string
            The css for locating the target.
        
        attr : string
            The attribute name.
        
        Return
        ----------
        string
        The corresponding attribute. If not found, return None
        """

        try:
            targetEle = self.driver.find_element(By.CSS_SELECTOR, css)
            
            if targetEle is not None:
                return targetEle.get_attribute(attr)

        except Exception as e:
            self.logUtil.log(e)
            self.close()
            return None

        return None

    def getAttributes(self, css, attr):
        """
        Count the attributes from elements.

        Parameters
        ----------
        css : string
            The css for locating the target.
        
        attr : string
            The attribute name.
        
        Return
        ----------
        string
        The corresponding attribute. If not found, return None
        """

        try:
            targetEles = self.driver.find_elements(By.CSS_SELECTOR, css)
            attributes = None

            if targetEles is not None and len(targetEles) > 0:

                attributes = []

                for targetEle in targetEles:
                    attribute = targetEle.get_attribute(attr)

                    if attribute is not None:
                        attributes.append(attribute)

            return attributes

        except Exception as e:
            self.logUtil.log(e)
            self.close()
            return None

        return None

    def countElements(self, css):
        """
        Count the target elements.

        Parameters
        ----------
        css : string
            The css for locating the target to count.
        
        Return
        ----------
        int
        The number target elements
        """

        try:
            targets = self.driver.find_elements(By.CSS_SELECTOR, css)

            if targets is not None:
                return len(targets)

        except Exception as e:
            self.logUtil.log(e)
            self.close()
            return 0
        
        return 0

    def switchToFrame(self, css):
        """
        Switch to an iframe

        Parameters
        ----------
        css : string
            The css for locating the target iframe.
            If set to 'default', switch to default main frame
        
        Return
        ----------
        bool
        Return True if successfully switched.
        Otherwise return False.
        """

        try:
            if css == 'default':
                # switch to default main frame
                self.driver.switch_to.default_content()
            else:

                frame = self.driver.find_element(By.CSS_SELECTOR, css)

                if frame is not None:
                    self.driver.switch_to.frame(frame)
                    return True

        except Exception as e:
            self.logUtil.log(e)
            self.close()
            return False

        return False

    def getWindowHandler(self, index = None):
        """
        Get the window handle

        Parameters
        ----------
        index : string
            The index for the window. 
            If set to None, return current window handle
        
        Return
        ----------
        object
        The window handle
        """

        if index is None:
            return self.driver.current_window_handle
        else:
            return self.driver.window_handles[index]

    def switchToWindow(self, windowHandle = -1):
        """
        Switch to a window

        Parameters
        ----------
        windowHandle : object
            The handle for the target window. 
            If set to -1, switch to the last opened window.
        
        Return
        ----------
        bool
        Return True if successfully switched.
        Otherwise return False.
        """
        try:

            targetHandle = windowHandle
            if windowHandle == -1:
                targetHandle = self.driver.window_handles[-1]

            self.driver.switch_to.window(targetHandle)

            return True

        except Exception as e:
            self.logUtil.log(e)
            self.close()
            return False

    def scrollTo(self, css):
        """
        Scroll to a specific element.
        
        Parameters
        ----------
        css : string
            The css of the target element.
        
        Return
        ----------
        bool
        Return True if successfully scrolled.
        Otherwise return False.
        """

        try:
            element = self.driver.find_element(By.CSS_SELECTOR, css)
            self.driver.execute_script("arguments[0].scrollIntoView();", element)

        except Exception as e:
            self.logUtil.log(e)
            self.close()
            return False

        return True

    def output(self, content):
        """
        Output content to screen
        
        Parameters
        ----------
        content : any
            The content to be output. It should be stringifiable.
        
        Return
        ----------
        bool
        Return True if successfully ouput.
        Otherwise return False.
        """

        try:
            self.logUtil.log(str(content))
        except Exception as e:
            self.logUtil.log(e)
            return False
        
        return True
