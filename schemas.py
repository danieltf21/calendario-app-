from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional

class UsuarioCrear(BaseModel):
    nombre: str
    correo: str
    contrasena: str

class UsuarioRespuesta(BaseModel):
    id: int
    nombre: str
    correo: str
    foto_perfil: Optional[str] = None
    mostrar_actividad: bool = True

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


class EventoRecurrente(BaseModel):
    usuario_id: int
    titulo: str
    dia_semana: int  # 0=Lunes ... 6=Domingo
    hora_inicio: str  # "10:00"
    hora_fin: str      # "12:00"
    fecha_inicio: date
    fecha_fin: date


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


class ActualizarFoto(BaseModel):
    foto_base64: str

class ActualizarPrivacidad(BaseModel):
    mostrar_actividad: bool