from dataclasses import dataclass,field
from datetime import datetime

@dataclass
class User:
    _id:str
    email:str
    password:str
    timetables:list[str] = field(default_factory=list)


@dataclass
class Timetable:
    _id:str
    name:str
    duration:float=0
    subjects:list[str] = field(default_factory=list)

@dataclass
class Subject:
    _id:str
    name:str
    duration:float
