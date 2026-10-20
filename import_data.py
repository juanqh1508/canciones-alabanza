import pandas as pd
import requests
from io import StringIO
from database import db, Salmista, Canto

# Sheet URL for ADRIANA (gid=1981750432)
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRwfHp4SilrLfMn7kgEqGUGfKOXuGsxs6ybsGaqct5LuGBqYxetOI1GtX2kN6Ck8JMJh22CDSO8oOUI/pub?gid=1981750432&single=true&output=csv"

SINGER_COLORS = {
    'Adriana Guerra': '#0ea5e9',
    'Walkisley Concepción': '#10b981',
    'Maickel Morales': '#6366f1',
    'Laura González': '#8b5cf6',
    'Rossana de Gantes': '#ec4899',
    'Daniel Pérez': '#f43f5e',
    'Aura Ostía': '#f59e0b',
    'Nilka Núñez': '#14b8a6',
    'Anya Guerra': '#06b6d4',
    'Congregacional / General': '#64748b'
}

def clean_val(val):
    if pd.isna(val):
        return ""
    s = str(val).strip()
    return "" if s.lower() == "nan" else s

def is_test_entry(title):
    t = title.lower().strip()
    if t in ['zzzzzz', 'sdasd'] or 'fkfjfjfjfj' in t:
        return True
    if len(t) < 3:
        return True
    return False

def sync_data(app=None):
    """
    Downloads from Google Sheets published CSV (ADRIANA tab)
    and updates/inserts into SQLite database.
    """
    print(f"Descargando datos desde Google Sheets (ADRIANA)...")
    try:
        response = requests.get(CSV_URL, timeout=15)
        response.encoding = 'utf-8'
    except Exception as e:
        return False, f"Error de conexión con Google Sheets: {e}"

    if response.status_code != 200:
        return False, f"Error HTTP {response.status_code} al descargar datos de Google Sheets."

    try:
        df = pd.read_csv(StringIO(response.text))
        df.columns = [c.strip() for c in df.columns]
    except Exception as e:
        return False, f"Error al procesar el archivo CSV: {e}"

    imported_count = 0
    updated_count = 0

    def run_sync():
        nonlocal imported_count, updated_count
        # Ensure map of salmistas
        salmistas_map = {}
        for s in Salmista.query.all():
            if s.nombre in SINGER_COLORS:
                s.color = SINGER_COLORS[s.nombre]
            salmistas_map[s.nombre] = s

        for index, row in df.iterrows():
            titulo = clean_val(row.get('CANTOS'))
            if not titulo or is_test_entry(titulo):
                continue

            salmista_nombre = clean_val(row.get('SALMISTA'))
            if not salmista_nombre:
                salmista_nombre = 'Congregacional / General'

            if salmista_nombre not in salmistas_map:
                color = SINGER_COLORS.get(salmista_nombre, '#8b5cf6')
                nuevo_s = Salmista(nombre=salmista_nombre, color=color)
                db.session.add(nuevo_s)
                db.session.flush()
                salmistas_map[salmista_nombre] = nuevo_s

            salmista = salmistas_map[salmista_nombre]

            id_canto = clean_val(row.get('IDCANTO'))
            tipo = clean_val(row.get('TIPO'))
            tema = clean_val(row.get('TEMA'))
            biblia = clean_val(row.get('BIBLIA'))
            tono = clean_val(row.get('TONO'))
            acompanante = clean_val(row.get('ACOMPANANTE'))
            tipotono = clean_val(row.get('TIPOTONO'))
            archivo = clean_val(row.get('ARCHIVO'))
            observaciones = clean_val(row.get('OBSERVACIONES'))
            fecha = clean_val(row.get('FECHA'))

            canto = None
            if id_canto:
                canto = Canto.query.filter_by(id_canto=id_canto).first()

            if canto:
                canto.titulo = titulo
                canto.tipo = tipo
                canto.tema = tema
                canto.biblia = biblia
                canto.tono = tono
                canto.acompanante = acompanante
                canto.tipotono = tipotono
                canto.archivo = archivo
                canto.observaciones = observaciones
                canto.fecha = fecha
                canto.autor = salmista
                updated_count += 1
            else:
                nuevo_canto = Canto(
                    id_canto=id_canto or None,
                    titulo=titulo,
                    tipo=tipo,
                    tema=tema,
                    biblia=biblia,
                    tono=tono,
                    acompanante=acompanante,
                    tipotono=tipotono,
                    archivo=archivo,
                    observaciones=observaciones,
                    fecha=fecha,
                    autor=salmista
                )
                db.session.add(nuevo_canto)
                imported_count += 1

        db.session.commit()
        return True, f"Sincronización exitosa: {imported_count} agregados, {updated_count} actualizados."

    if app:
        with app.app_context():
            return run_sync()
    else:
        from app import app as flask_app
        with flask_app.app_context():
            return run_sync()

if __name__ == "__main__":
    from app import app
    ok, msg = sync_data(app)
    print(msg)
