import csv
import io
import json
from datetime import datetime

import joblib
import numpy as np
import streamlit as st


st.set_page_config(
    page_title="Asesor de Rendimiento del Aguacate",
    page_icon="🥑",
    layout="wide",
)


@st.cache_resource
def cargar_recursos():
    modelo = joblib.load("yield_model.joblib")
    with open("model_metadata.json", "r", encoding="utf-8") as archivo:
        metadatos = json.load(archivo)
    return modelo, metadatos


modelo, meta = cargar_recursos()
caracteristicas = list(meta["features"])


NOMBRES_ES = {
    "N": "Nitrógeno",
    "P": "Fósforo",
    "K": "Potasio",
    "Ca": "Calcio",
    "Mg": "Magnesio",
    "Zn": "Zinc",
    "Mn": "Manganeso",
    "Fe": "Hierro",
    "Cu": "Cobre",
    "B": "Boro",
    "Cl": "Cloruro",
    "S": "Azufre",
}


def simbolo_nutriente(nombre):
    texto = str(nombre).strip()
    base = texto.split("(")[0].strip()

    for simbolo in ["Ca", "Mg", "Zn", "Mn", "Fe", "Cu", "Cl", "N", "P", "K", "B", "S"]:
        if base == simbolo or texto.startswith(f"{simbolo}("):
            return simbolo

    texto_min = texto.lower()
    equivalencias = {
        "nitrogen": "N",
        "phosphorus": "P",
        "potassium": "K",
        "calcium": "Ca",
        "magnesium": "Mg",
        "zinc": "Zn",
        "manganese": "Mn",
        "iron": "Fe",
        "copper": "Cu",
        "boron": "B",
        "chloride": "Cl",
        "chlorine": "Cl",
        "sulfur": "S",
        "sulphur": "S",
    }

    for palabra, simbolo in equivalencias.items():
        if palabra in texto_min:
            return simbolo

    return base


def unidad_nutriente(nombre):
    texto = str(nombre).lower()
    simbolo = simbolo_nutriente(nombre)

    if "ppm" in texto:
        return "ppm"
    if "%" in texto or "percent" in texto or "pct" in texto:
        return "%"
    if simbolo in {"N", "P", "K", "Ca", "Mg", "Cl", "S"}:
        return "%"
    return "ppm"


def etiqueta_es(nombre):
    simbolo = simbolo_nutriente(nombre)
    nombre_es = NOMBRES_ES.get(simbolo, str(nombre))
    return f"{nombre_es} ({simbolo})"


def obtener_valor_meta(seccion, caracteristica, predeterminado=np.nan):
    datos = meta.get(seccion, {})
    try:
        return float(datos.get(caracteristica, predeterminado))
    except (TypeError, ValueError):
        return float(predeterminado)


@st.cache_resource
def calcular_referencia_nutricional_ideal():
    """
    Predicción del modelo para el perfil nutricional ideal/default guardado
    en los metadatos. Esta predicción se usa como referencia de 100%.
    """
    defaults = meta.get("defaults", {})
    valores_ideales = []

    for caracteristica in caracteristicas:
        valor = defaults.get(caracteristica, np.nan)
        try:
            valor = float(valor)
        except (TypeError, ValueError):
            valor = np.nan
        valores_ideales.append(valor)

    x_ideal = np.array([valores_ideales], dtype=float)
    return max(0.0, float(modelo.predict(x_ideal)[0]))


REFERENCIA_NUTRICIONAL_IDEAL = calcular_referencia_nutricional_ideal()


def predecir(valores):
    x = np.array([valores], dtype=float)
    rendimiento = max(0.0, float(modelo.predict(x)[0]))
    referencia = REFERENCIA_NUTRICIONAL_IDEAL
    potencial = min(100.0, 100.0 * rendimiento / referencia) if referencia > 0 else 0.0
    return rendimiento, potencial, referencia


def interpretar_potencial(potencial):
    if potencial >= 80:
        return (
            "Potencial alto",
            "Este perfil nutricional se aproxima al rendimiento asociado con un perfil nutricional ideal en el modelo.",
        )
    if potencial >= 55:
        return (
            "Potencial moderado",
            "Este perfil nutricional muestra un potencial intermedio y puede haber oportunidades para mejorar el equilibrio entre nutrientes.",
        )
    return (
        "Potencial bajo",
        "Este perfil nutricional se encuentra considerablemente por debajo del rendimiento asociado con un perfil nutricional ideal en el modelo.",
    )


def evaluar_nutriente(caracteristica, valor):
    p10 = obtener_valor_meta("p10", caracteristica)
    p90 = obtener_valor_meta("p90", caracteristica)
    unidad = unidad_nutriente(caracteristica)

    if np.isnan(valor):
        return {
            "estado": "Dato no disponible",
            "direccion": "faltante",
            "severidad": 0.0,
            "detalle": "El modelo utilizará el tratamiento de valores faltantes aprendido durante el entrenamiento.",
        }

    if np.isnan(p10) or np.isnan(p90) or p90 <= p10:
        return {
            "estado": "Sin rango histórico",
            "direccion": "desconocido",
            "severidad": 0.0,
            "detalle": "No hay límites históricos suficientes para clasificar este valor.",
        }

    amplitud = max(p90 - p10, 1e-9)

    if valor < p10:
        diferencia = p10 - valor
        severidad = diferencia / amplitud
        estado = "Fuertemente limitante" if severidad >= 0.50 else "Limitante"
        return {
            "estado": estado,
            "direccion": "bajo",
            "severidad": severidad,
            "detalle": f"{diferencia:.3g} {unidad} por debajo del percentil 10 histórico ({p10:.3g} {unidad}).",
        }

    if valor > p90:
        diferencia = valor - p90
        severidad = diferencia / amplitud
        estado = "Exceso marcado" if severidad >= 0.50 else "Exceso"
        return {
            "estado": estado,
            "direccion": "alto",
            "severidad": severidad,
            "detalle": f"{diferencia:.3g} {unidad} por encima del percentil 90 histórico ({p90:.3g} {unidad}).",
        }

    return {
        "estado": "Dentro del rango central",
        "direccion": "central",
        "severidad": 0.0,
        "detalle": f"Dentro del rango histórico central ({p10:.3g}–{p90:.3g} {unidad}).",
    }


def generar_csv(identificacion, valores, rendimiento, potencial, referencia, evaluaciones):
    salida = io.StringIO()
    escritor = csv.writer(salida)

    escritor.writerow(["Informe del Asesor de Rendimiento del Aguacate"])
    escritor.writerow(["Fecha", datetime.now().strftime("%Y-%m-%d %H:%M")])
    escritor.writerow(["Huerto o productor", identificacion["huerto"]])
    escritor.writerow(["Bloque o parcela", identificacion["bloque"]])
    escritor.writerow(["Número de muestra", identificacion["muestra"]])
    escritor.writerow([])
    escritor.writerow(["Resultado", "Valor"])
    escritor.writerow(["Rendimiento estimado (kg)", f"{rendimiento:.2f}"])
    escritor.writerow(["Potencial del perfil nutricional (%)", f"{potencial:.1f}"])
    escritor.writerow(["Rendimiento de referencia con nutrición ideal (kg)", f"{referencia:.2f}"])
    escritor.writerow([])
    escritor.writerow(["Elemento", "Valor", "Unidad", "Estado", "Interpretación"])

    for i, caracteristica in enumerate(caracteristicas):
        valor = valores[i]
        evaluacion = evaluaciones[i]
        escritor.writerow(
            [
                etiqueta_es(caracteristica),
                "" if np.isnan(valor) else f"{valor:.4g}",
                unidad_nutriente(caracteristica),
                evaluacion["estado"],
                evaluacion["detalle"],
            ]
        )

    escritor.writerow([])
    escritor.writerow(
        [
            "Nota",
            "Esta herramienta apoya la toma de decisiones. Las asociaciones del modelo no constituyen por sí solas una recomendación de fertilización.",
        ]
    )

    return salida.getvalue().encode("utf-8-sig")


st.markdown(
    """
    <style>
    .block-container {
        max-width: 1180px;
        padding-top: 1.4rem;
        padding-bottom: 3rem;
    }

    .hero {
        background: linear-gradient(135deg, #173f2a, #3f7d44);
        color: white;
        padding: 30px 34px;
        border-radius: 22px;
        margin-bottom: 18px;
        box-shadow: 0 10px 28px rgba(23, 63, 42, 0.16);
    }

    .hero h1 {
        margin: 0;
        font-size: 2.35rem;
        line-height: 1.1;
    }

    .hero p {
        opacity: 0.94;
        margin: 0.55rem 0 0;
        font-size: 1.02rem;
        max-width: 800px;
    }

    .result-card {
        background: linear-gradient(180deg, #f4faef, #ffffff);
        border: 1px solid #bdd7ac;
        padding: 20px 22px;
        border-radius: 18px;
        margin-top: 10px;
    }

    .priority-item {
        background: #fafbf8;
        border: 1px solid #e1e8dc;
        border-left: 5px solid #708d62;
        padding: 12px 14px;
        border-radius: 12px;
        margin-bottom: 9px;
    }

    .priority-item strong {
        color: #244b31;
    }

    .fine-print {
        color: #526257;
        font-size: 0.88rem;
        line-height: 1.5;
    }

    div[data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid #dfe9da;
        padding: 14px 16px;
        border-radius: 15px;
    }

    div[data-baseweb="input"] input {
        font-size: 1.18rem !important;
        font-weight: 600 !important;
    }

    div.stButton > button:first-child,
    div[data-testid="stDownloadButton"] > button {
        border-radius: 12px;
        font-weight: 700;
    }

    @media (max-width: 700px) {
        .hero {
            padding: 24px 22px;
        }

        .hero h1 {
            font-size: 1.9rem;
        }

        div[data-baseweb="input"] input {
            font-size: 1.12rem !important;
        }
    }
    </style>

    <div class="hero">
        <h1>🥑 Asesor de Rendimiento del Aguacate</h1>
        <p>
            Herramienta de apoyo a la decisión que utiliza las interacciones
            entre nutrientes foliares para estimar el rendimiento y el
            potencial del perfil nutricional.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.info(
    "Esta herramienta describe asociaciones observadas en los datos históricos. "
    "No garantiza una respuesta a la fertilización ni sustituye la evaluación de un asesor agronómico."
)


with st.expander("Identificación de la muestra (opcional)"):
    id1, id2, id3 = st.columns(3)
    with id1:
        huerto = st.text_input("Huerto o productor")
    with id2:
        bloque = st.text_input("Bloque o parcela")
    with id3:
        muestra = st.text_input("Número de muestra")


st.subheader("Resultados del análisis foliar")
st.caption(
    "Ingrese los resultados del laboratorio usando las unidades indicadas para cada nutriente."
)

valores = []
faltantes = []
columnas = st.columns(3)

for i, caracteristica in enumerate(caracteristicas):
    predeterminado = obtener_valor_meta("defaults", caracteristica, 0.0)
    unidad = unidad_nutriente(caracteristica)
    etiqueta = etiqueta_es(caracteristica)

    with columnas[i % 3]:
        st.markdown(f"**{etiqueta}** · {unidad}")
        sin_dato = st.checkbox(
            "Dato no disponible",
            value=False,
            key=f"sin_dato_{i}",
        )

        if sin_dato:
            st.number_input(
                f"Valor de {etiqueta}",
                value=float(predeterminado),
                disabled=True,
                key=f"valor_inactivo_{i}",
                label_visibility="collapsed",
            )
            valores.append(np.nan)
            faltantes.append(True)
        else:
            formato = "%.4f" if unidad == "%" else "%.2f"
            paso = max(abs(predeterminado) * 0.02, 0.001 if unidad == "%" else 0.1)
            valor = st.number_input(
                f"Valor de {etiqueta}",
                min_value=0.0,
                value=float(predeterminado),
                step=float(paso),
                format=formato,
                key=f"valor_{i}",
                label_visibility="collapsed",
            )
            valores.append(float(valor))
            faltantes.append(False)


if st.button(
    "Analizar el potencial de rendimiento",
    type="primary",
    use_container_width=True,
):
    st.session_state["mostrar_resultados_es"] = True


if st.session_state.get("mostrar_resultados_es", False):
    rendimiento, potencial, referencia = predecir(valores)
    categoria, interpretacion = interpretar_potencial(potencial)
    evaluaciones = [
        evaluar_nutriente(caracteristica, valores[i])
        for i, caracteristica in enumerate(caracteristicas)
    ]

    st.markdown('<div class="result-card">', unsafe_allow_html=True)
    st.subheader("Resultados")

    m1, m2, m3 = st.columns(3)
    m1.metric("Potencial del perfil nutricional", f"{potencial:.0f}%")
    m2.metric("Rendimiento estimado", f"{rendimiento:,.1f} kg")
    m3.metric("Referencia con nutrición ideal", f"{referencia:,.1f} kg")

    st.progress(int(round(max(0.0, min(100.0, potencial)))))
    st.markdown(f"### {categoria}")
    st.write(interpretacion)

    disponibles = len(caracteristicas) - sum(faltantes)
    st.caption(
        f"Cobertura de la muestra: {disponibles} de {len(caracteristicas)} nutrientes ingresados."
    )
    st.markdown("</div>", unsafe_allow_html=True)

    prioridades = [
        (i, evaluacion)
        for i, evaluacion in enumerate(evaluaciones)
        if evaluacion["direccion"] in {"bajo", "alto", "faltante"}
    ]
    prioridades.sort(key=lambda item: item[1]["severidad"], reverse=True)

    st.subheader("Qué revisar primero")

    if prioridades:
        for i, evaluacion in prioridades:
            caracteristica = caracteristicas[i]
            st.markdown(
                f"""
                <div class="priority-item">
                    <strong>{etiqueta_es(caracteristica)}: {evaluacion["estado"]}</strong><br>
                    <span class="fine-print">{evaluacion["detalle"]}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.success(
            "Todos los valores ingresados se encuentran dentro del rango histórico central del conjunto de datos."
        )

    st.caption(
        "Un valor fuera del rango histórico es una señal para revisar, no una recomendación automática de fertilización."
    )

    with st.expander("Estado de todos los nutrientes"):
        for i, caracteristica in enumerate(caracteristicas):
            evaluacion = evaluaciones[i]
            st.markdown(
                f"**{etiqueta_es(caracteristica)} — {evaluacion['estado']}**  \n"
                f"{evaluacion['detalle']}"
            )

    with st.expander("Prueba de escenario: modificar un nutriente"):
        st.write(
            "Cambie un nutriente para observar cómo varía la predicción. "
            "Esta comparación matemática no es una recomendación de fertilización."
        )

        seleccion = st.selectbox(
            "Nutriente que desea probar",
            options=range(len(caracteristicas)),
            format_func=lambda indice: etiqueta_es(caracteristicas[indice]),
        )

        caracteristica_prueba = caracteristicas[seleccion]
        valor_actual = valores[seleccion]

        if np.isnan(valor_actual):
            valor_actual = obtener_valor_meta("defaults", caracteristica_prueba, 0.0)

        unidad_prueba = unidad_nutriente(caracteristica_prueba)
        nuevo_valor = st.number_input(
            f"Nuevo valor de {etiqueta_es(caracteristica_prueba)} ({unidad_prueba})",
            min_value=0.0,
            value=float(valor_actual),
            step=max(abs(float(valor_actual)) * 0.02, 0.001 if unidad_prueba == "%" else 0.1),
            format="%.4f" if unidad_prueba == "%" else "%.2f",
            key="nuevo_valor_escenario_es",
        )

        valores_escenario = list(valores)
        valores_escenario[seleccion] = float(nuevo_valor)
        rendimiento_escenario, potencial_escenario, _ = predecir(valores_escenario)

        e1, e2 = st.columns(2)
        e1.metric(
            "Rendimiento estimado del escenario",
            f"{rendimiento_escenario:,.1f} kg",
            delta=f"{rendimiento_escenario - rendimiento:+.1f} kg",
        )
        e2.metric(
            "Potencial del escenario",
            f"{potencial_escenario:.0f}%",
            delta=f"{potencial_escenario - potencial:+.1f} puntos",
        )

    identificacion = {
        "huerto": huerto,
        "bloque": bloque,
        "muestra": muestra,
    }

    informe_csv = generar_csv(
        identificacion,
        valores,
        rendimiento,
        potencial,
        referencia,
        evaluaciones,
    )

    st.download_button(
        "Descargar informe en CSV",
        data=informe_csv,
        file_name="informe_rendimiento_aguacate.csv",
        mime="text/csv",
        use_container_width=True,
    )


with st.expander("Información del modelo"):
    st.markdown(
        """
        El modelo se basa en datos de cosecha de **3,254 observaciones de árboles individuales**
        obtenidas a través de un transecto de la industria del aguacate del sur de California.
        Los datos combinan los conjuntos de **Crowley y Lovatt**, y la investigación contó
        con el apoyo de la **California Avocado Commission**.

        El rendimiento real también depende del riego, clima, salinidad, carga de fruta,
        plagas, enfermedades, portainjerto, cultivar y edad del árbol.
        """
    )

    st.caption(
        f"Modelo seleccionado: {meta.get('model_name', 'modelo guardado')} · "
        f"Registros de entrenamiento: {meta.get('training_records', 'no indicado')}"
    )
