"""
a variable used to hold values
"""
from smartimage.smartimageXmlObject import SmartimageXmlObject


class Variable(SmartimageXmlObject):
    """
    a variable used to hold values
    """

    def __init__(self,parent:SmartimageXmlObject,xml:str):
        SmartimageXmlObject.__init__(self,parent,xml)
        self._value=None

    @property
    def name(self)->str:
        """
        name of the variable
        """
        return self._getProperty('name')

    @property
    def description(self)->str:
        """
        optional description of this variable
        """
        return self._getProperty('description','')

    @property
    def uitype(self)->str:
        """
        an html input type like:
            (checkbox color date datetime datetime-local email file hidden
            image month number password radio range search tel text time url week )
        """
        return self._getProperty('type','text')
    @property
    def type(self)->str:
        """
        the ui type of this variable
        """
        return self.uitype

    @property
    def default(self):
        """
        default value for this variable
        """
        return self._getProperty('default','')

    @property
    def value(self):
        """
        the current value of this variable
        """
        if self._value is None:
            return self.default
        return self._value
    @value.setter
    def value(self,value):
        self._value=value

    def __int__(self)->int:
        """
        convert to int
        """
        return int(self.value)

    def __float__(self)->float:
        """
        convert to float
        """
        return float(self.value)

    def __repr__(self)->str:
        """
        convert to string
        """
        return str(self.value)

    def __bool__(self)->bool:
        """
        convert to bool
        """
        # this doesn't seem to work right with python.
        # must call toBool directly!
        return self.toBool()
    def toBool(self)->bool:
        """
        convert to bool
        """
        s=self.__repr__()
        return s and s[0].lower() in ('y','t','1')
