import pandas as pd

df = pd.read_excel("data_seguimiento.xlsx")

entidad = "MEF"

df_filtrado = df[df["Entidad"].str.lower() == entidad.lower()]

df_filtrado.to_excel("data_seguimiento.xlsx", index=False)