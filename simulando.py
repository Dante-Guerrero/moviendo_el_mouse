import numpy as np
import pandas as pd
from datetime import datetime, timedelta


# ========= Config =========
N = 1000
SEMILLA = 42
rng = np.random.default_rng(SEMILLA)

# Rango de fechas
hoy = pd.Timestamp.today().normalize()
limite_nacimiento_ini = pd.Timestamp("1960-01-01")
limite_nacimiento_fin = hoy - pd.DateOffset(years=18)

# ========= Catálogos =========
cargos = [
    "Director(a)",
    "Especialista Legal",
    "Analista Económico",
    "Personal Administrativo",
    "Secretario(a) Administrativo",
]

oficinas = [
    "Oficina de Planeamiento",
    "Oficina de Recursos Humanos",
    "Oficina de Tecnología",
    "Oficina de Asesoría Jurídica",
    "Oficina de Logística",
    "Oficina de Comunicaciones",
    "Oficina de Finanzas",
    "Oficina de Atención al Ciudadano",
]

entidades = [
    "INDECOPI",
    "OEFA",
    "SUNAT",
    "OSCE",
    "SERVIR",
    "MEF",
    "PCM",
    "MINAM",
    "MINEDU",
    "MTC",
]

nombres = [
    "Alejandro","María","Juan","Lucía","Carlos","Valeria","Diego","Daniela","Jorge","Andrea",
    "Luis","Camila","Pedro","Sofía","Fernando","Paula","Hugo","Gabriela","Raúl","Carolina",
    "Sergio","Natalia","Gonzalo","Mónica","Alberto","Patricia","Óscar","Verónica","Iván","Rocío",
    "Martín","Elena","Ricardo","Noelia","Bruno","Fiorella","Pablo","Isabella","Marco","Kiara",
    "Alonso","Ximena","Renato","Claudia","Javier","Brenda","Thiago","Marisol","Miguel","Lourdes",
    "Francisco","Cinthia","Eduardo","Milagros","Rodrigo","Nayeli","Arturo","Liliana","César","Tatiana",
]

apellidos = [
    "García","Rodríguez","Martínez","Chávez","Gonzales","Fernández","López","Pérez","Sánchez","Ramírez",
    "Castro","Rojas","Flores","Díaz","Torres","Vargas","Romero","Gutiérrez","Alvarado","Herrera",
    "Cruz","Mendoza","Paredes","Ruiz","Aguilar","Morales","Vásquez","Silva","Cabrera","Valdez",
    "Ortega","Reyes","Campos","Arroyo","Quispe","Salazar","Peña","Suárez","Chávarry","Núñez",
    "Ibarra","Palacios","Delgado","Chirinos","Carrillo","Muñoz","Matos","Zúñiga","Solano","Ramos",
    "Escobar","León","Puma","Huamán","Rivera","Vega","Montoya","Acosta","Medina","Calderón",
]

assert len(nombres) * len(apellidos) >= N, "Aumenta nombres/apellidos para más combinaciones únicas."

# ========= Generar combinaciones únicas =========
combos = [(n, a) for n in nombres for a in apellidos]
rng.shuffle(combos)
combos = combos[:N]
Nombres, Apellidos = zip(*combos)

# ========= Fechas de nacimiento =========
def fechas_aleatorias(inicio: pd.Timestamp, fin: pd.Timestamp, k: int):
    delta_dias = (fin - inicio).days
    offsets = rng.integers(0, delta_dias + 1, size=k)
    return [inicio + pd.Timedelta(days=int(d)) for d in offsets]

nacimientos = fechas_aleatorias(limite_nacimiento_ini, limite_nacimiento_fin, N)

# ========= Fecha de inicio =========
fechas_inicio = []
for nac in nacimientos:
    mayoria = nac + pd.DateOffset(years=18)
    if mayoria > hoy:
        mayoria = limite_nacimiento_fin
    if mayoria == hoy:
        mayoria = hoy - pd.Timedelta(days=1)
    inicio = fechas_aleatorias(mayoria, hoy, 1)[0]
    fechas_inicio.append(inicio)

# ========= Cese =========
cese_flags = np.array(["NO"] * N, dtype=object)
num_cese = int(round(0.30 * N))
idx_cese = rng.choice(np.arange(N), size=num_cese, replace=False)
cese_flags[idx_cese] = "SÍ"

fechas_cese = [pd.NaT] * N
for i in idx_cese:
    ini = fechas_inicio[i]
    base = ini + pd.Timedelta(days=30)
    if base > hoy:
        base = ini + pd.Timedelta(days=1)
    if base > hoy:
        cese_flags[i] = "NO"
        fechas_cese[i] = pd.NaT
        continue
    fecha_c = fechas_aleatorias(base, hoy, 1)[0]
    fechas_cese[i] = fecha_c

# ========= Otros campos =========
cargos_asignados = rng.choice(cargos, size=N)
oficinas_asignadas = rng.choice(oficinas, size=N)
entidades_asignadas = rng.choice(entidades, size=N)

# ========= DataFrame =========
df = pd.DataFrame({
    "Nombre": Nombres,
    "Apellido": Apellidos,
    "Cargo": cargos_asignados,
    "Oficina": oficinas_asignadas,
    "Entidad": entidades_asignadas,
    "Nacimiento": pd.to_datetime(nacimientos).date,
    "Fecha_inicio": pd.to_datetime(fechas_inicio).date,
    "Cese (SÍ o NO)": cese_flags,
    "Fecha_cese": pd.to_datetime(fechas_cese).date,
})

df = df[
    ["Nombre","Apellido","Cargo","Oficina","Entidad","Nacimiento","Fecha_inicio","Cese (SÍ o NO)","Fecha_cese"]
].reset_index(drop=True)

# ========= Exportar a Excel =========
df.to_excel("data_seguimiento.xlsx", index=False)