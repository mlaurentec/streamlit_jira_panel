import streamlit as st
import requests
import pandas as pd
from requests.auth import HTTPBasicAuth
import streamlit_shadcn_ui as ui
from os import environ
from dotenv import load_dotenv
import os

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

st.title("Projects")

SEARCH_ISSUE_FROM_JQL_MESSAGE_SUCCESS = "issue encontrado correctamente"

jql = st.text_input("Ingresa tu Jql")

if "issue_from_jql" not in st.session_state:
    st.session_state.issue_from_jql = None

if "total_finalizadas" not in st.session_state:
    st.session_state.total_finalizadas = 0

if "total_issues" not in st.session_state:
    st.session_state.total_issues = 0


def search_issue_from_jql(jql):
    try:
        url = "https://alignet.atlassian.net/rest/api/3/search"
        params = {"jql": jql}
        response = requests.get(
            url=url,
            params=params,
            headers={"Accept": "application/json"},
            auth=HTTPBasicAuth(
                os.getenv("JIRA_USER"),
                os.getenv("JIRA_TOKEN"),
            ),
        )
        if response.status_code != 200:
            print("fallo")

        response_json = response.json()

        issues_finded = response_json["total"]
        response_issues = response_json["issues"]
        if issues_finded != 0:
            list_issues_finded = [
                {
                    "key": issue["key"],
                    "Resumen": issue["fields"]["summary"],
                    "Persona asignada": issue["fields"]["assignee"]["displayName"],
                    "Estado": issue["fields"]["status"]["name"],
                }
                for issue in response_issues
            ]
            return list_issues_finded

        return []

    except Exception as error:
        print(error)
        return []


# Botón para realizar la llamada a la API
if st.button("Get Issues"):
    st.session_state.issue_from_jql = search_issue_from_jql(jql)
    st.session_state.total_issues = len(st.session_state.issue_from_jql)

    st.session_state.total_finalizadas = len(
        list(
            filter(
                lambda d: d["Estado"] == "Finalizada", st.session_state.issue_from_jql
            )
        )
    )

# Mostrar las tarjetas métricas después de actualizar los valores
cols = st.columns(2)
with cols[0]:
    ui.metric_card(
        title="Total Issues",
        content=st.session_state.total_issues,
        description="",
        key="card1",
    )
with cols[1]:
    ui.metric_card(
        title="Total Finalizadas",
        content=st.session_state.total_finalizadas,
        description="",
        key="card2",
    )


# Mostrar los resultados de la búsqueda
if st.session_state.issue_from_jql:
    # st.write(st.session_state.issue_from_jql)
    if len(st.session_state.issue_from_jql) == 0:
        st.warning("No se encontro issues", icon="⚠️")
    df = pd.DataFrame(
        st.session_state.issue_from_jql,
        columns=["key", "Resumen", "Persona asignada", "Estado"],
    )
    st.table(df)
