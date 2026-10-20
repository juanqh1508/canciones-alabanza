from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from database import db, Salmista, Canto
import os
from collections import Counter

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///alabanza.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'dev_key_alabanza_2026'

db.init_app(app)

with app.app_context():
    db.create_all()

@app.context_processor
def inject_global_data():
    salmistas = Salmista.query.all()
    salmistas = sorted(salmistas, key=lambda s: len(s.cantos), reverse=True)
    return {'salmistas_nav': salmistas}

@app.route('/')
def index():
    salmistas = Salmista.query.all()
    # Sort salmistas by song count descending
    salmistas = sorted(salmistas, key=lambda s: len(s.cantos), reverse=True)
    
    cantos = Canto.query.order_by(Canto.id.desc()).all()
    
    # Calculate stats
    total_cantos = len(cantos)
    total_songs_parsed = sum(len(c.titulos_lista) for c in cantos)
    total_salmistas = len([s for s in salmistas if len(s.cantos) > 0])
    
    # Collect unique filters
    tipos_counter = Counter([c.tipo for c in cantos if c.tipo])
    tonos_counter = Counter([c.tono for c in cantos if c.tono and c.tono != 'N/A'])
    temas_set = sorted(list(set([c.tema.strip() for c in cantos if c.tema and c.tema.strip()])))
    
    # Clean top genres
    top_genres = tipos_counter.most_common(5)
    top_tonos = tonos_counter.most_common(8)

    # Convert all cantos to dict for instant client-side search & filtering
    cantos_json = [c.to_dict() for c in cantos]
    
    return render_template(
        'index.html',
        salmistas=salmistas,
        cantos=cantos,
        cantos_json=cantos_json,
        total_cantos=total_cantos,
        total_songs_parsed=total_songs_parsed,
        total_salmistas=total_salmistas,
        top_genres=top_genres,
        top_tonos=top_tonos,
        tipos_list=sorted(list(tipos_counter.keys())),
        tonos_list=sorted(list(tonos_counter.keys())),
        temas_list=temas_set
    )

@app.route('/cantante/<int:id>')
def view_singer(id):
    salmista = Salmista.query.get_or_404(id)
    all_salmistas = Salmista.query.all()
    cantos = salmista.cantos
    
    # Stats for this singer
    total_cantos = len(cantos)
    total_songs_parsed = sum(len(c.titulos_lista) for c in cantos)
    
    tipos_counter = Counter([c.tipo for c in cantos if c.tipo])
    tonos_counter = Counter([c.tono for c in cantos if c.tono and c.tono != 'N/A'])
    
    cantos_json = [c.to_dict() for c in cantos]
    
    return render_template(
        'singer.html',
        salmista=salmista,
        all_salmistas=all_salmistas,
        cantos=cantos,
        cantos_json=cantos_json,
        total_cantos=total_cantos,
        total_songs_parsed=total_songs_parsed,
        top_genres=tipos_counter.most_common(4),
        top_tonos=tonos_counter.most_common(5),
        tipos_list=sorted(list(tipos_counter.keys())),
        tonos_list=sorted(list(tonos_counter.keys()))
    )

@app.route('/api/cantos')
def api_cantos():
    q = request.args.get('q', '').lower().strip()
    salmista_id = request.args.get('salmista_id', type=int)
    tipo = request.args.get('tipo', '').strip()
    tono = request.args.get('tono', '').strip()
    tema = request.args.get('tema', '').strip()

    query = Canto.query

    if salmista_id:
        query = query.filter_by(salmista_id=salmista_id)
    if tipo:
        query = query.filter(Canto.tipo.ilike(f'%{tipo}%'))
    if tono:
        query = query.filter(Canto.tono == tono)
    if tema:
        query = query.filter(Canto.tema.ilike(f'%{tema}%'))

    cantos = query.all()

    if q:
        filtered = []
        for c in cantos:
            text_corpus = f"{c.titulo} {c.autor.nombre if c.autor else ''} {c.tipo or ''} {c.tono or ''} {c.tema or ''} {c.biblia or ''} {c.observaciones or ''} {c.acompanante or ''}".lower()
            if q in text_corpus:
                filtered.append(c)
        cantos = filtered

    return jsonify([c.to_dict() for c in cantos])

@app.route('/api/sync', methods=['POST', 'GET'])
def api_sync():
    from import_data import sync_data
    success, message = sync_data(app)
    return jsonify({
        'success': success,
        'message': message
    })

@app.route('/añadir', methods=['GET', 'POST'])
def add_song():
    if request.method == 'POST':
        titulo = request.form.get('titulo')
        salmista_id = request.form.get('salmista')
        tipo = request.form.get('tipo')
        tema = request.form.get('tema')
        biblia = request.form.get('biblia')
        tono = request.form.get('tono')
        tipotono = request.form.get('tipotono')
        acompanante = request.form.get('acompanante')
        archivo = request.form.get('archivo')
        observaciones = request.form.get('observaciones')
        fecha = request.form.get('fecha')

        if salmista_id == 'NEW':
            nombre_nuevo = request.form.get('new_salmista', '').strip()
            if not nombre_nuevo:
                flash('El nombre del cantante no puede estar vacío.', 'danger')
                return redirect(url_for('add_song'))
                
            salmista = Salmista.query.filter_by(nombre=nombre_nuevo).first()
            if not salmista:
                import random
                vibrant_colors = ['#ff007a', '#0ea5e9', '#10b981', '#f59e0b', '#6366f1', '#8b5cf6', '#ec4899', '#f43f5e']
                salmista = Salmista(
                    nombre=nombre_nuevo,
                    color=random.choice(vibrant_colors)
                )
                db.session.add(salmista)
                db.session.commit()
        else:
            salmista = Salmista.query.get(int(salmista_id))

        if not salmista:
            flash('Error al identificar al cantante.', 'danger')
            return redirect(url_for('add_song'))

        import uuid
        nuevo_canto = Canto(
            id_canto=str(uuid.uuid4())[:8],
            titulo=titulo,
            tipo=tipo,
            tema=tema,
            biblia=biblia,
            tono=tono,
            tipotono=tipotono,
            acompanante=acompanante,
            archivo=archivo,
            observaciones=observaciones,
            fecha=fecha,
            autor=salmista
        )
        db.session.add(nuevo_canto)
        db.session.commit()

        flash('¡Canto añadido correctamente!', 'success')
        return redirect(url_for('index'))

    salmistas = Salmista.query.all()
    return render_template('add_song.html', salmistas=salmistas)

if __name__ == '__main__':
    import socket
    import threading
    import webbrowser
    import sys

    def get_free_port(preferred=5000):
        for p in [preferred, 5050, 5001, 8080, 5055]:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                s.bind(('127.0.0.1', p))
                s.listen(1)
                s.close()
                return p
            except OSError:
                continue
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('127.0.0.1', 0))
        p = s.getsockname()[1]
        s.close()
        return p

    port = get_free_port(5000)
    url = f"http://localhost:{port}"

    print("\n" + "=" * 65)
    print("   MINISTERIO DE ALABANZA - DASHBOARD WEB")
    print(f"   -> Servidor web iniciado en: {url}")
    print("   -> Abriendo tu navegador automaticamente...")
    print("   -> Deja esta ventana abierta mientras uses la pagina.")
    print("   -> Para detener el servidor: presiona Ctrl + C")
    print("=" * 65 + "\n")

    # Open browser automatically after 1 second
    threading.Timer(1.2, lambda: webbrowser.open(url)).start()

    try:
        app.run(host='127.0.0.1', port=port, debug=False)
    except KeyboardInterrupt:
        print("\nServidor detenido por el usuario.")
    except Exception as e:
        print(f"\n[ERROR INESPERADO] {e}")
        input("\nPresiona Enter para cerrar esta ventana...")

