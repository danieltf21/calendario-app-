from pydantic import BaseModel
from datetime import datetime

class UsuarioCrear(BaseModel):
    nombre: str
    correo: str
    contrasena: str

class UsuarioRespuesta(BaseModel):
    id: int
    nombre: str
    correo: str

    class Config:
        orm_mode = True


class EventoCrear(BaseModel):
    usuario_id: int
    titulo: str
    hora_inicio: datetime
    hora_fin: datetime

class EventoRespuesta(BaseModel):
    id: int
    titulo: str
    hora_inicio: datetime
    hora_fin: datetime

    class Config:
        orm_mode = True


class AmistadCrear(BaseModel):
    usuario_id: int
    amigo_id: int

class AmistadRespuesta(BaseModel):
    id: int
    usuario_id: int
    amigo_id: int
    estado: str

    class Config:
        orm_mode = True