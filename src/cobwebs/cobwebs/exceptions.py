class NotImplementedException(BaseException):
    message_format = "This function is not implemented."
    code = 500
    title = 'Not implemented'


class UnknownCommandError(BaseException):
    message_format = "This command is not authorized."
    code = 500
    title = 'Unknown Command'


class ConfigFileException(BaseException):
    message_format = "Cannot find a usable configuration file."
    code = 500
    title = 'Config File Error'


class AuthException(BaseException):
    message_format = "There is an error with the username or the password supplied..."
    code = 401
    title = 'Authentication Error'
