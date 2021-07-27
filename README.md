# Funny Test Framework

-----------

The Funny Test Framework is base on selenium. It consumes the test vectors (precedures) from JSON files and translates them to selenium modules. It is designed for web functional test. 

### Requirements

#### Run with docker

You don't need to install any dependencies if you use the container starter provided under the `docker` folder. It works together with other docker images environment created by gongwan33 perfectly. However, the docker environment doesn't support non headless mode at the moment. 

#### Run with out docker

The following dependencies are need:

- Python3

- Selenium for Python. (`pip3 install selenium`)

- Chrome web driver. Please download the correct version according to your Chrome browser. 

### Folder Structure 

There are three folders in the FunnyTest directory which is the core part of the whole framework. `Base` folder includes the basic pre-written selenium functions and framework logics. `Log` folder contains the logging functions. And `Starter` includes the test vector parser. Currently only JSON starter is avaliable.

### Quick Start

To start a test, please refer to the `example` folder. The `testStarter.py` is the entry script. Run command `python3 testStarter.py` will start the test process. 

In `testStarter.py`, there are mainly three lines of code (as shown below) and they can be used in most of the senarios. 

The first line creates a new JSON starter with the test vector json files' directory path and the custom procedures' folder (see next chapter `Extendability`). The test vector json file's name will be used as the `Test Run` name which will contain the procedures.

The second line starts the test. If its parameter is set to True, the headless mode will be activated. Otherwise, the chrome browser will show up. 

```python
starter = JSONStarter("./TestCases", "./CustomProcedure")
starter.run(True) # True: Headless; False: not headless
starter.getSummary()
```

### Extendability

Apart from the pre written standard procedure functions, you can add your customized procedure functions. The customzied functions will take in the driver instance from selenium and other parameters defined by yourself. They should be saved in a folder and the corresponding path should be specified when creating the starter.

### Standard procedures

A standard procedure block looks like the following:

```json
{
    "type": "stdProcedure",
    "id": "CSLoginTest",
    "command": "click",
    "condition": "%result[ProcedureA]%",
    "params": ["#sign"],
    "expect": true,
    "expectTime": 100
}
```

`type`, `id`, `command`, `params` are compulsory. `expect` and `expectTime` are optional.

- `type`: should either be `stdProcedure` or `customProcedure`.

- `id`: the name of the current procedure. Every procedure should have a unique `id`.

- `command`: the command you are going to run for test. See `Standard Commands`.

- `condition`: reference to the result of `ProcedureA` as condition to execute this procedure block. 

- `params`: the params taken by the `command`. See `Standard Commands`.

- `expect`: expected return for this test. If the actual return is the same as expected, the procedure will be considered as pass.

- `expectTime`: expected time consumption by this test. If the actual time consumption is less than or equal to the expected time consumption, the procedure will be considered as pass.

### Referencing the Result of Another Procedure

In `condition` and `params`, `%result[ProcedureId]%` can be used to fetch other procedure's result. In `params`, this can even used inside a string to accomplish more complex tasks. For example, `https://%result[GetURLFromItem]%/login` is able to generate a url based on the result of `GetURLFromItem`.

### Standard Commands

#### visit

Visit a page and wait for a certian element.

Parameters:

- url: the url for the target page.

- waitCSS: the css selector for the element to wait.

- timeOut: the maximum time for waiting.

- waitFun: the waiting mode. For details, please refer to https://selenium-python.readthedocs.io/waits.html. The supported functions are:

* presence_of_element_located

* visibility_of_element_located

* visibility_of

* presence_of_all_elements_located

* invisibility_of_element_located

* element_to_be_clickable

* element_to_be_selected

* element_located_to_be_selected

- appendCredential: the credentials for browser verification. (Format: "username:password")

Return: bool

#### waitFor

Wait for a specific element on the page.

- waitCSS: the css selector for the element to wait.

- timeOut: the maximum time for waiting.

- waitFun: The waiting mode. Similar to `visit` command.

#### click

Click a certain element.

Parameters:

- css: the css selector for the element to be clicked.

Return: bool

#### selectOption

Select a specific option in a select list.

Parameters:

- css: The css for locating the target select element.

- value: The value of the target option.

Return: bool

#### input

Type in a text box.

Parameters:
        
- css: The css for locating the target input element.

- value: The value for input

Return: bool

#### countElements

Count the target elements.

Parameters:

css: The css for locating the target to count.

Return: the number of the elements.

#### switchToFrame

Switch to an iframe.

Parameters:
        
css: The css for locating the target iframe. If set to 'default', switch to the default main frame.

Return: bool

#### getWindowHandler

Get the window handle.

Parameters:
        
index: The index for the window. If set to None, return current window handle.

Return: the required window handle.

#### switchToWindow

Switch to a window

Parameters:

windowHandle: The handle for the target window. If set to -1, switch to the last opened window.

Return: bool
        
#### closeCurrentWindow

Close current window

Return: bool

#### getAttribute

Get the attribute from a element.

Parameters:

css: the css for locating the target.
        
attr: the attribute name.
        
Return: string

#### scrollTo

Scroll to a specific element.

Parameters:

css: the css of the target element.
        
Return: bool


