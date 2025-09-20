import pandas as pd

ruta_excel = "data_filtrado.xlsx"
df = pd.read_excel(ruta_excel)

print("-" * 40)

for _, fila in df.iterrows():
    print(f"Nombre: {fila['Nombre']} {fila['Apellido']}")
    print(f"Cargo: {fila['Cargo']}")
    print(f"Oficina: {fila['Oficina']}")
    print("-" * 40)