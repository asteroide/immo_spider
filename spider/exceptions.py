

class AuthException(BaseException):
    message_format = "There is an error with the username or the password supplied..."
    code = 401
    title = 'Authentication Error'
