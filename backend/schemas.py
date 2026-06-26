import re
from typing import Annotated
from pydantic import BaseModel, Field, AfterValidator

def validate_username(v: str) -> str:
    if re.search(r"\s", v):
        raise ValueError("用户名不能包含空格或换行符")
        
    if not re.match(r"^[a-zA-Z0-9_\u4e00-\u9fa5]+$", v):
        raise ValueError("用户名只能包含中文、字母、数字和下划线")
    
    return v

UsernameStr = Annotated[
    str,
    Field(min_length=2, max_length=15),
    AfterValidator(validate_username)
]

class UserCreate(BaseModel):
    username: UsernameStr
    password: str

class ChangePassword(BaseModel):
    old_password: str
    new_password: str

class ChangeUsername(BaseModel):
    new_username: UsernameStr

class Password(BaseModel):
    password: str