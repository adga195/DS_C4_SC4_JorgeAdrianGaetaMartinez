# Jorge Adrián Gaeta Martínez
# Reto C4SC4: Conociendo el desempeño del Área de Marketing de Socialize your knowledge

# Librerías necesarias
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Configuración de la página
st.set_page_config(
    page_title="Análisis de desempeño - Adrián Gaeta",
    layout="wide"
)

pageLogo, pageHeader = st.columns([1,3])
with pageHeader:
    st.title("Dashboard de Análisis de desempeño")
    st.text("Reto C4SC4: Conociendo el desempeño del Área de Marketing de Socialize your knowledge." \
    "\nDashboard interactivo para visualizar y analizar los datos de desempeño de los colaboradores.")
with pageLogo:
    st.image("./logo-c4sc4.png", width=512)

# Función para cargar datos
df = pd.read_csv("employee_data.csv")

st.divider()

# Configuración de la barra lateral y filtros
with st.sidebar:
    st.header("Controles")

    # Filtro para género
    gender_options = ["All"] + sorted([g for g in df['gender'].dropna().unique().tolist()])
    gender_select = st.selectbox("Selecciona el género:", gender_options, index=0)

    # Filtro para puntaje de desempeño en forma de rango
    min_ps = int(np.nanmin(df['performance_score'])) if not df['performance_score'].dropna().empty else 1
    max_ps = int(np.nanmax(df['performance_score'])) if not df['performance_score'].dropna().empty else 5
    ps_range = st.slider("Rango del puntaje de desempeño:", min_value=1, max_value=5, value=(min(1, min_ps), max(5, max_ps)), step=1)

    # Filtro para estado civil
    marital_opts = ["All"] + sorted([m for m in df['marital_status'].dropna().unique().tolist()])
    sel_marital = st.selectbox("Selecciona el estado civil:", marital_opts, index=0)

# Aplicación de filtros al DataFrame
filtered_data = pd.Series(True, index=df.index)
if gender_select != "All":
    filtered_data &= df['gender'] == gender_select
filtered_data &= df['performance_score'].between(ps_range[0], ps_range[1])
if sel_marital != "All":
    filtered_data &= df['marital_status'] == sel_marital

# Tabla de datos filtrados
st.subheader("Datos de colaboradores filtrados")
filtered_data_frame = df[filtered_data].copy()
st.dataframe(filtered_data_frame)
st.markdown(
    f"<div style='text-align: center; color: gray; font-size: 0.9em;'>Mostrando {len(filtered_data_frame)} de {len(df)} colaboradores tras aplicar filtros.</div>",
    unsafe_allow_html=True
)
st.divider()

# Histograma con la distribución de los puntajes de desempeño
st.subheader("Distribución de los puntajes de desempeño")
if filtered_data_frame.empty:
    st.markdown(
        "<div style='text-align: center; color: gray; font-size: 0.9em;'>No hay puntajes de desempeño disponibles para los filtros seleccionados.</div>",
        unsafe_allow_html=True
    )
elif 'performance_score' in filtered_data_frame.columns:
    fig = px.histogram(
        filtered_data_frame,
        x="performance_score",
        labels={"performance_score": "Puntaje de desempeño"},
        nbins=4
    )
    fig.update_xaxes(dtick=1)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("La columna 'performance_score' no está disponible.")

st.divider()

# Gráfico de pastel con el promedio de horas trabajadas por género
st.subheader("Promedio de horas trabajadas por género")
if {'average_work_hours','gender'}.issubset(filtered_data_frame.columns):
    by_gender = filtered_data_frame.groupby('gender', dropna=True)['average_work_hours'].mean().reset_index()
    fig = px.pie(
        by_gender,
        names="gender",
        values="average_work_hours",
        hole=0.4
    )
    fig.update_traces(textinfo='percent+label', pull=[0.05]*len(by_gender))
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Las columnas 'average_work_hours' y 'gender' no están disponibles.")

st.divider()

# Gráfico de dispersión entre edad y salario, coloreado por género y con tamaño según puntaje de desempeño
st.subheader("Edad de los empleados vs. Salario")
if {'age','salary'}.issubset(filtered_data_frame.columns):
    fig = px.scatter(
        filtered_data_frame.dropna(subset=['age','salary']),
        x="age",
        y="salary",
        # Mostrar los datos asociados al punto y etiquetas en el hover
        hover_data=["name_employee","position","performance_score"],
        labels={"age": "Edad", "salary": "Salario", "performance_score": "Puntaje de desempeño", "position": "Puesto", "name_employee": "Nombre"},
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Las columnas 'age' y 'salary' no están disponibles.")

st.divider()

# Gráfico de dispersión entre horas promedio trabajadas y puntaje de desempeño
st.subheader("Relación: Horas promedio trabajadas vs. Puntaje de desempeño")
if {'average_work_hours','performance_score'}.issubset(filtered_data_frame.columns):
    fig = px.scatter(
        filtered_data_frame.dropna(subset=['average_work_hours','performance_score']),
        x="average_work_hours",
        y="performance_score",
        hover_data=["name_employee","average_work_hours","performance_score"],
        labels={"average_work_hours": "Horas promedio trabajadas", "performance_score": "Puntaje de desempeño", "name_employee": "Nombre", "gender": "Género"}
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Las columnas 'average_work_hours' y 'performance_score' no están disponibles.")

st.divider()

# Conclusiones automáticas basadas en los datos filtrados y análisis estadísticos básicos
st.subheader("Conclusiones")
conclusions = []

if 'satisfaction_level' in filtered_data_frame.columns and not filtered_data_frame['satisfaction_level'].dropna().empty:
    satisfaction_mean = filtered_data_frame['satisfaction_level'].mean()
    conclusions.append(f"- Nivel de satisfacción promedio en el conjunto filtrado: **{satisfaction_mean:.2f}**.")
    conclusions.append("  - El valor máximo es 5, una satisfacción promedio por encima de 3.5 se consideraría buena.")

if {'age','salary'}.issubset(filtered_data_frame.columns) and filtered_data_frame[['age','salary']].dropna().shape[0] > 2:
    correlation_age_salary = filtered_data_frame[['age','salary']].dropna().corr().iloc[0,1]
    conclusions.append(f"- Correlación **edad–salario**: **{correlation_age_salary:.2f}**")
    conclusions.append("  - Una correlación cercana a +1 indica que a mayor edad, mayor salario.")
    conclusions.append("  - Una correlación cercana a -1 indica que a mayor edad, menor salario.")
    conclusions.append("  - Una correlación cercana a 0 indica que no hay relación entre edad y salario.")

if {'average_work_hours','performance_score'}.issubset(filtered_data_frame.columns) and filtered_data_frame[['average_work_hours','performance_score']].dropna().shape[0] > 2:
    correlation_hours_performance = filtered_data_frame[['average_work_hours','performance_score']].dropna().corr().iloc[0,1]
    conclusions.append(f"- Correlación **horas–desempeño**: **{correlation_hours_performance:.2f}**.")
    conclusions.append("  - Una correlación cercana a +1 indica que a más horas trabajadas, mejor desempeño.")
    conclusions.append("  - Una correlación cercana a -1 indica que a más horas trabajadas, peor desempeño.")
    conclusions.append("  - Una correlación cercana a 0 indica que no hay relación entre horas trabajadas y desempeño.")

if 'absences' in filtered_data_frame.columns and not filtered_data_frame['absences'].dropna().empty:
    absences_mean = filtered_data_frame['absences'].mean()
    absences_std = filtered_data_frame['absences'].std()
    absences_max = filtered_data_frame['absences'].max()
    absences_min = filtered_data_frame['absences'].min()
    conclusions.append(f"- Promedio de **ausencias** en el conjunto filtrado: **{absences_mean:.2f}**.")
    conclusions.append(f"  - Desviación estándar de **ausencias**: **{absences_std:.2f}**.")
    conclusions.append(f"  - Rango de ausencias esperado para la mayoría de empleados (promedio ± 2 desviaciones estándar): **{max(absences_mean - 2 * absences_std, 0):.2f}** a **{max(0, absences_mean + 2 * absences_std):.2f}**.")
    conclusions.append(f"  - Máximo de **ausencias** del conjunto filtrado: **{absences_max:.1f}**.")
    conclusions.append(f"  - Mínimo de **ausencias** del conjunto filtrado: **{absences_min:.1f}**.")

if not conclusions:
    st.write("No hay datos para generar conclusiones automáticas con los filtros aplicados.")
else:
    st.markdown("\n".join(conclusions))