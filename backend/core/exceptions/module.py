from fastapi.exceptions import HTTPException


class ModuleException(HTTPException):
    def __init__(self, status_code: int, enum=None, code: str = None, message: str = None):
        if not enum and (code and message):
            raise ModuleException(status_code=500, code='ENUM_ERROR', message='Enum not found')
        if enum:
            code = enum.name
            message = enum.value + message if message else ''
        super().__init__(status_code=status_code, detail={
            'code': code,
            'msg': message
        })
