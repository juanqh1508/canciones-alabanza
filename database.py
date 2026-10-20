from flask_sqlalchemy import SQLAlchemy
import re

db = SQLAlchemy()

def parse_song_titles(raw_title):
    if not raw_title:
        return []
    text = str(raw_title).replace('\r', '')
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    results = []
    for line in lines:
        parts = [p.strip().rstrip('.') for p in line.split(',') if p.strip()]
        for p in parts:
            if p and p.lower() != 'nan':
                results.append(p)
    return results

class Salmista(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False)
    color = db.Column(db.String(20), default="#764ba2") # Hex color
    cantos = db.relationship('Canto', backref='autor', lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'color': self.color,
            'cantos_count': len(self.cantos)
        }

class Canto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_canto = db.Column(db.String(50), unique=True, nullable=True)
    titulo = db.Column(db.Text, nullable=False)
    tipo = db.Column(db.String(100)) # Género
    tema = db.Column(db.String(150))
    biblia = db.Column(db.String(200))
    tono = db.Column(db.String(50))
    acompanante = db.Column(db.String(100))
    tipotono = db.Column(db.String(50))
    archivo = db.Column(db.String(500)) # Link or path
    observaciones = db.Column(db.Text)
    fecha = db.Column(db.String(50))
    salmista_id = db.Column(db.Integer, db.ForeignKey('salmista.id'), nullable=False)

    @property
    def titulos_lista(self):
        return parse_song_titles(self.titulo)

    def to_dict(self):
        return {
            'id': self.id,
            'id_canto': self.id_canto or '',
            'titulo': self.titulo,
            'titulos_lista': self.titulos_lista,
            'tipo': self.tipo or 'Otros',
            'tema': self.tema or '',
            'biblia': self.biblia or '',
            'tono': self.tono or 'N/A',
            'acompanante': self.acompanante or '',
            'tipotono': self.tipotono or '',
            'archivo': self.archivo or '',
            'observaciones': self.observaciones or '',
            'fecha': self.fecha or '',
            'salmista_id': self.salmista_id,
            'salmista_nombre': self.autor.nombre if self.autor else 'Sin asignar',
            'salmista_color': self.autor.color if self.autor else '#764ba2'
        }
