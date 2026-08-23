# PerfilEgreso 360

Sistema de seguimiento y aseguramiento del logro del Perfil de Egreso, inspirado
en las fichas de rendimiento deportivo (radar de competencias, "ficha de jugador")
aplicadas a evidencia académica.

> Transforma calificaciones y evaluaciones dispersas en un perfil visual,
> longitudinal y accionable del logro del Perfil de Egreso — a nivel individual,
> de cohorte y de carrera — con detección de brechas, recomendaciones de mejora
> y análisis asistido por IA.

## Ejecutar localmente

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Abre el módulo **Captura** y presiona **"Cargar datos de demostración"** para
explorar la app sin necesidad de un archivo real.

## Acceso restringido con cuenta Google

La app no muestra ningún dato sin una sesión iniciada. El flujo es:

1. **Autenticación** — Google verifica la identidad (OIDC nativo de Streamlit:
   `st.login()` / `st.user` / `st.logout()`, requiere Streamlit ≥ 1.42).
2. **Autorización** — el correo debe estar en la lista blanca de
   `.streamlit/secrets.toml`: por dominio institucional o por correo puntual.
3. **Sincronización de sesión** — al entrar, la sesión queda asociada a ese
   correo; si en el mismo navegador entra otra cuenta, los datos cargados por
   la anterior se descartan automáticamente.

### Configurar Google

1. En [Google Cloud Console](https://console.cloud.google.com/) → *APIs y
   servicios* → *Pantalla de consentimiento OAuth*: tipo **Interno** si el
   dominio institucional está en Workspace (así solo entran cuentas del
   dominio), o **Externo** si necesitas correos fuera del dominio.
2. *Credenciales* → **Crear credenciales** → *ID de cliente de OAuth* →
   **Aplicación web**.
3. En **URIs de redireccionamiento autorizados** agrega:
   - `http://localhost:8501/oauth2callback` (desarrollo)
   - `https://TU-APP.streamlit.app/oauth2callback` (producción)
4. Copia `client_id` y `client_secret` a `.streamlit/secrets.toml`
   (parte de `.streamlit/secrets.toml.example`).
5. Genera el `cookie_secret`:
   `python -c "import secrets; print(secrets.token_urlsafe(48))"`

En Streamlit Community Cloud el archivo no se sube: el mismo contenido se pega
en *Manage app → Settings → Secrets*, y `redirect_uri` debe apuntar a la URL
pública de la app.

Para desarrollo local sin credenciales OAuth, `permitir_sin_login = true` en
`[acceso]` deja pasar sin login. **Debe quedar en `false` al desplegar.**

## Estructura del proyecto

```
PerfilEgreso360/
├── app.py                 # App Streamlit — navegación por los 5 módulos
├── .streamlit/
│   ├── config.toml          # Tema base claro de Streamlit
│   └── secrets.toml.example # Plantilla de credenciales Google + lista blanca
├── src/
│   ├── auth.py              # Login con Google, lista blanca y sesión por usuario
│   ├── config.py           # Meta institucional, líneas formativas, umbrales
│   ├── data_io.py           # Datos demo + lectura de Excel (plantilla propia y acta USEK)
│   ├── engine.py            # Cálculo de logro, brechas, niveles y recomendaciones
│   ├── charts.py            # Radar de competencias y gráficos de evolución/brechas
│   ├── ai.py                 # Interpretación con IA (OpenAI opcional + fallback local)
│   └── reports.py            # Exportación de reportes a Excel
├── data/demo/                # (reservado para archivos de ejemplo)
├── requirements.txt
└── README.md
```

## Flujo conceptual

```
Evaluación → Resultado de Aprendizaje → Línea formativa → Perfil de Egreso
     ↓
Motor de tributación (engine.py) → Logro por línea/estudiante
     ↓
Brechas = Meta institucional − Logro observado
     ↓
Recomendaciones (reglas) + Diagnóstico ejecutivo (IA opcional)
     ↓
Reportes exportables (Excel)
```

## Los 5 módulos

1. **Captura** — carga datos de demostración, la plantilla propia (6 hojas) o
   un acta institucional real (USEK). Principio de diseño: *la app se adapta
   al archivo institucional, no al revés*.
2. **Configuración** — el "cerebro académico": meta institucional, líneas
   formativas, Resultados de Aprendizaje y ponderaciones por tipo de evidencia,
   editables por carrera.
3. **Análisis y diagnóstico** — vista Individual (ficha tipo jugador con
   radar), Cohorte y Carrera; brechas por línea, alertas tempranas y
   evolución por corte.
4. **Recomendaciones** — motor de reglas que prioriza acciones según el
   tamaño de la brecha, más un diagnóstico ejecutivo (IA opcional vía OpenAI,
   con fallback local si no hay API key).
5. **Reportes** — Alerta temprana, Competencias, Líneas formativas, Total
   líneas y Total competencias, todos agrupados bajo un mismo módulo y
   exportables a Excel.

## Pendientes conocidos

Estos quedaron identificados como trabajo abierto y conviene abordarlos antes
de un uso institucional real:

- [ ] Definir el modelo académico definitivo (competencias vs. líneas vs. RA)
- [ ] Construir la matriz de tributación real (qué asignatura/RA alimenta
      cada línea y con qué peso)
- [ ] Validar académicamente los umbrales de clasificación (70/80/90) y la
      meta de 85%
- [ ] Robustecer `leer_acta_usek()` para distintos formatos de acta y carreras
- [ ] Incorporar evidencias externas (pruebas nacionales, interciclo,
      estandarizadas) sin distorsionar el resultado
- [ ] Persistencia en base de datos (cohortes, cortes e históricos —
      Streamlit hoy solo procesa en memoria/sesión)
- [x] Acceso restringido con cuenta Google (`src/auth.py`)
- [ ] Permisos diferenciados por rol: hoy el rol solo se muestra en la barra
      lateral; falta restringir módulos según Administrador / Calidad /
      Director de Carrera / Docente
- [ ] Exportación a PDF ejecutivo (hoy solo Excel)
- [ ] Seguimiento de acciones de mejora (responsable, plazo, indicador,
      estado, resultado en el siguiente corte)
- [ ] Diseño UI definitivo tipo dossier/ejecutivo (ver mockup HTML del
      proyecto — ficha individual + panel ejecutivo). El tema base ya pasó de
      fondo negro a fondo papel por legibilidad; falta recuperar la ficha
      individual como pieza destacada.

## Despliegue

Pensado para desplegarse en **Streamlit Community Cloud** conectando este
repositorio de GitHub directamente. Antes de publicar:

- Cargar los secretos en *Settings → Secrets* (nunca en el repositorio).
- Ajustar `redirect_uri` a la URL pública y registrarla en Google Cloud.
- Verificar que `permitir_sin_login` esté en `false`.
