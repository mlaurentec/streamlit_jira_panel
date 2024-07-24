import streamlit as st
import requests
import pandas as pd
from requests.models import HTTPBasicAuth
from os import environ

st.title("Estados para un proyecto")

project = st.text_input("Ingresa el nombre de proyecto:").upper()


# Función para llamar a la API
def call_api(project):
    url = f"https://alignet.atlassian.net/rest/api/3/project/{project}/statuses"
    response = requests.get(
        url=url,
        headers={"Accept": "application/json"},
        auth=HTTPBasicAuth(
            environ.get("JIRA_USER"),
            environ.get("JIRA_TOKEN"),
        ),
    )
    print(url)
    if response.status_code == 200:
        # print(response.json())
        return response.json()
    else:
        st.error("Failed to retrieve data")
        return None


if "data" not in st.session_state:
    st.session_state.data = None

if "issuetype_seleccionado" not in st.session_state:
    st.session_state.issuetype_seleccionado = None

if "status_seleccionado" not in st.session_state:
    st.session_state.status_seleccionado = None

# Botón para realizar la llamada a la API
if st.button("Get Project info"):
    st.session_state.data = call_api(project)
    st.session_state.issuetype_seleccionado = None
    st.session_state.status_seleccionado = None


if st.session_state.data:
    opciones = [d["name"] for d in st.session_state.data]
    issuetype_seleccionado = st.selectbox(
        "Selecciona una opción:",
        opciones,
        index=(
            opciones.index(st.session_state.issuetype_seleccionado)
            if st.session_state.issuetype_seleccionado in opciones
            else 0
        ),
    )
    st.session_state.issuetype_seleccionado = issuetype_seleccionado

    if st.session_state.issuetype_seleccionado:
        for d in st.session_state.data:
            if d["name"] == st.session_state.issuetype_seleccionado:

                opciones_status = [
                    (status["name"], status["id"]) for status in d["statuses"]
                ]

                df = pd.DataFrame(opciones_status, columns=["Nombre", "Id"])
                st.table(df)
