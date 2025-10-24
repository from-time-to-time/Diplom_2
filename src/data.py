class Messages:
    UNAUTHORISED = "You should be authorised"
    INCORRECT = "email or password are incorrect"
    EXISTING = "User already exists"
    REQUIRED = "Email, password and name are required fields"

class HTTPStatus:
    OK = 200
    UNAUTHORIZED = 401
    BAD_REQUEST = 400
    INTERNAL_SERVER_ERROR = 500
    EXIST = 403
