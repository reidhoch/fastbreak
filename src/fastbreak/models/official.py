from pydantic import BaseModel


class Official(BaseModel):
    personId: int
    name: str
    nameI: str
    firstName: str
    familyName: str
    jerseyNum: str
    assignment: str
