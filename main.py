from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from models import Base, Usuario, Evento, Amistad
from schemas import UsuarioCrear, UsuarioRespuesta, EventoCrear, EventoRespuesta, AmistadCrear, AmistadRespuesta
from seguridad import encriptar_contrasena, verificar_contrasena

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = create_engine("sqlite:///./calendario.db")
SessionLocal = sessionmaker(bind=engine)
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def read_root():
    return {"mensaje": "¡Hola, mi app de calendario está funcionando!"}


@app.post("/usuarios", response_model=UsuarioRespuesta)
def crear_usuario(usuario: UsuarioCrear, db: Session = Depends(get_db)):
    nuevo_usuario = Usuario(
        nombre=usuario.nombre,
        correo=usuario.correo,
        contrasena=encriptar_contrasena(usuario.contrasena)
    )
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    return nuevo_usuario


@app.get("/usuarios/{usuario_id}", response_model=UsuarioRespuesta)
def obtener_usuario(usuario_id: int, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario


@app.get("/usuarios/buscar/{correo}", response_model=UsuarioRespuesta)
def buscar_usuario_por_correo(correo: str, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.correo == correo).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario


@app.post("/eventos", response_model=EventoRespuesta)
def crear_evento(evento: EventoCrear, db: Session = Depends(get_db)):
    nuevo_evento = Evento(
        usuario_id=evento.usuario_id,
        titulo=evento.titulo,
        hora_inicio=evento.hora_inicio,
        hora_fin=evento.hora_fin
    )
    db.add(nuevo_evento)
    db.commit()
    db.refresh(nuevo_evento)
    return nuevo_evento


@app.get("/usuarios/{usuario_id}/estado")
def obtener_estado(usuario_id: int, db: Session = Depends(get_db)):
    ahora = datetime.now()

    evento_activo = db.query(Evento).filter(
        Evento.usuario_id == usuario_id,
        Evento.hora_inicio <= ahora,
        Evento.hora_fin >= ahora
    ).first()

    if evento_activo:
        return {
            "usuario_id": usuario_id,
            "estado": "ocupado",
            "actividad": evento_activo.titulo,
            "hasta": evento_activo.hora_fin
        }
    else:
        return {
            "usuario_id": usuario_id,
            "estado": "libre"
        }


@app.post("/amistades", response_model=AmistadRespuesta)
def enviar_solicitud(amistad: AmistadCrear, db: Session = Depends(get_db)):
    nueva_amistad = Amistad(
        usuario_id=amistad.usuario_id,
        amigo_id=amistad.amigo_id,
        estado="pendiente"
    )
    db.add(nueva_amistad)
    db.commit()
    db.refresh(nueva_amistad)
    return nueva_amistad


@app.put("/amistades/{amistad_id}/aceptar", response_model=AmistadRespuesta)
def aceptar_solicitud(amistad_id: int, db: Session = Depends(get_db)):
    amistad = db.query(Amistad).filter(Amistad.id == amistad_id).first()
    if not amistad:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    amistad.estado = "aceptado"
    db.commit()
    db.refresh(amistad)
    return amistad


@app.get("/usuarios/{usuario_id}/solicitudes")
def listar_solicitudes_pendientes(usuario_id: int, db: Session = Depends(get_db)):
    solicitudes = db.query(Amistad).filter(
        Amistad.amigo_id == usuario_id,
        Amistad.estado == "pendiente"
    ).all()

    resultado = []
    for s in solicitudes:
        remitente = db.query(Usuario).filter(Usuario.id == s.usuario_id).first()
        resultado.append({
            "solicitud_id": s.id,
            "de_usuario_id": remitente.id,
            "de_nombre": remitente.nombre
        })
    return resultado


@app.get("/usuarios/{usuario_id}/amigos")
def listar_amigos(usuario_id: int, db: Session = Depends(get_db)):
    amistades = db.query(Amistad).filter(
        Amistad.usuario_id == usuario_id,
        Amistad.estado == "aceptado"
    ).all()

    ahora = datetime.now()
    resultado = []

    for a in amistades:
        amigo = db.query(Usuario).filter(Usuario.id == a.amigo_id).first()

        evento_activo = db.query(Evento).filter(
            Evento.usuario_id == amigo.id,
            Evento.hora_inicio <= ahora,
            Evento.hora_fin >= ahora
        ).first()

        if evento_activo:
            estado = "ocupado"
            actividad = evento_activo.titulo
        else:
            estado = "libre"
            actividad = None

        resultado.append({
            "amigo_id": amigo.id,
            "nombre": amigo.nombre,
            "estado": estado,
            "actividad": actividad
        })

    return resultado


@app.post("/login")
def login(correo: str, contrasena: str, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.correo == correo).first()
    if not usuario or not verificar_contrasena(contrasena, usuario.contrasena):
        raise HTTPException(status_code=401, detail="Correo o contraseña incorrectos")
    return {"mensaje": "Login exitoso", "usuario_id": usuario.id, "nombre": usuario.nombre}
@app.get("/usuarios/{usuario_id}/eventos")
def listar_eventos(usuario_id: int, db: Session = Depends(get_db)):
    eventos = db.query(Evento).filter(
        Evento.usuario_id == usuario_id
    ).order_by(Evento.hora_inicio).all()

    return [
        {
            "id": e.id,
            "titulo": e.titulo,
            "hora_inicio": e.hora_inicio,
            "hora_fin": e.hora_fin
        }
        for e in eventos
    ]