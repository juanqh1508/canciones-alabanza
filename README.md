# Ministerio de Alabanza - Dashboard Web

Plataforma interactiva para la gestión, búsqueda y consulta del repertorio musical del ministerio de alabanza. Conectada en tiempo real con la hoja **ADRIANA** de Google Sheets.

## 🚀 Características
- **Buscador en tiempo real:** Búsqueda reactiva por título, letras, salmista, tono musical, temas y citas bíblicas.
- **Desglose de Medleys / Popurrís:** Reconoce más de 990 canciones individuales integradas en los repertorios.
- **Filtros por Salmista:** Filtrado instantáneo por cada cantante con sus colores identificativos.
- **Filtros por Género y Tono:** Adoración, Pentecostal, Guerra y Júbilo, Pop/Rock, Himnos y selección rápida de tonalidad musical.
- **Vista Dual:** Alterna entre vista en Tarjetas y vista en Tabla.
- **Modal de Detalle & Copiar Repertorio:** Muestra las canciones desglosadas con botón para copiar directo a WhatsApp.
- **Listo para Vercel y Netlify:** Incluye versión estática independiente en `/public` que no requiere servidores y lee directamente desde Google Sheets.

## 🛠️ Ejecución Local

### Opción 1: Con archivo .bat (Windows)
Haz doble clic en:
```
INICIAR_DASHBOARD.bat
```

### Opción 2: Con Python
```bash
pip install -r requirements.txt
python app.py
```
Abre en tu navegador `http://localhost:5000` (o el puerto asignado automáticamente).

## 🌐 Despliegue en la Nube

### Netlify Drop
1. Entra a [app.netlify.com/drop](https://app.netlify.com/drop).
2. Arrastra la carpeta `public` y tu sitio estará en línea en segundos.

### Vercel
Conecta este repositorio directamente en [vercel.com](https://vercel.com) y se desplegará de forma automática usando la configuración de `vercel.json`.
