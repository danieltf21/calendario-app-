from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    correo = Column(String, unique=True, nullable=False)
    contrasena = Column(String, nullable=False)
    foto_perfil = Column(String, nullable=True)
    mostrar_actividad = Column(Boolean, default=True)

    eventos = relationship("Evento", back_populates="usuario")


class Evento(Base):
    __tablename__ = "eventos"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    titulo = Column(String, nullable=False)
    hora_inicio = Column(DateTime, nullable=False)
    hora_fin = Column(DateTime, nullable=False)

    usuario = relationship("Usuario", back_populates="eventos")


class Amistad(Base):
    __tablename__ = "amistades"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    amigo_id = Column(Integer, ForeignKey("usuarios.id"))
    estado = Column(String, default="pendiente")