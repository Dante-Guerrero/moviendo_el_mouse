import argparse
import pandas as pd
from pathlib import Path

# Columnas esperadas
COLS = [
    "Nombre","Apellido","Cargo","Oficina","Entidad",
    "Nacimiento","Fecha_inicio","Cese (SÍ o NO)","Fecha_cese"
]

def normaliza_cese(x: str) -> str:
    if pd.isna(x):
        return "NO"
    s = str(x).strip().upper().replace("Í","I")
    if s in {"SI","SÍ","YES","Y"}:
        return "SÍ"
    return "NO"

def leer_excel(path_in: Path, hoja: str | None):
    df = pd.read_excel(
        path_in,
        sheet_name=hoja if hoja else 0,
        dtype={
            "Nombre":"string","Apellido":"string","Cargo":"string",
            "Oficina":"string","Entidad":"string","Cese (SÍ o NO)":"string"
        }
    )
    # Asegura columnas y fechas
    faltantes = [c for c in COLS if c not in df.columns]
    if faltantes:
        raise ValueError(f"Faltan columnas en el Excel: {faltantes}")
    for c in ["Nacimiento","Fecha_inicio","Fecha_cese"]:
        df[c] = pd.to_datetime(df[c], errors="coerce")
    # Normaliza cese
    df["Cese (SÍ o NO)"] = df["Cese (SÍ o NO)"].map(normaliza_cese)
    return df

def aplica_filtros(df: pd.DataFrame, args: argparse.Namespace) -> pd.DataFrame:
    m = pd.Series(True, index=df.index)

    def ci_contains(series: pd.Series, term: str) -> pd.Series:
        term = term.strip()
        return series.fillna("").str.casefold().str.contains(term.casefold(), na=False)

    # Texto: permite múltiples valores, OR interno por campo
    if args.nombre:
        m &= pd.concat([ci_contains(df["Nombre"], t) for t in args.nombre], axis=1).any(axis=1)
    if args.apellido:
        m &= pd.concat([ci_contains(df["Apellido"], t) for t in args.apellido], axis=1).any(axis=1)
    if args.cargo:
        m &= df["Cargo"].fillna("").str.casefold().isin([c.casefold() for c in args.cargo])
    if args.oficina:
        m &= df["Oficina"].fillna("").str.casefold().isin([o.casefold() for o in args.oficina])
    if args.entidad:
        m &= df["Entidad"].fillna("").str.casefold().isin([e.casefold() for e in args.entidad])

    # Cese
    if args.cese is not None:
        m &= df["Cese (SÍ o NO)"].eq("SÍ" if args.cese else "NO")

    # Rangos de fecha
    def rango_fecha(col, dmin, dmax):
        s = df[col]
        mm = pd.Series(True, index=df.index)
        if dmin:
            mm &= s.ge(pd.to_datetime(dmin, errors="coerce"))
        if dmax:
            mm &= s.le(pd.to_datetime(dmax, errors="coerce"))
        return mm

    if args.nac_desde or args.nac_hasta:
        m &= rango_fecha("Nacimiento", args.nac_desde, args.nac_hasta)
    if args.ini_desde or args.ini_hasta:
        m &= rango_fecha("Fecha_inicio", args.ini_desde, args.ini_hasta)
    if args.cese_desde or args.cese_hasta:
        # Solo aplica a quienes tienen fecha de cese
        con_cese = df["Fecha_cese"].notna()
        m &= con_cese & rango_fecha("Fecha_cese", args.cese_desde, args.cese_hasta)

    out = df.loc[m].copy()

    # Orden y límite
    if args.ordenar:
        # ejemplo: --ordenar "Entidad,-Fecha_inicio,Apellido"
        claves = []
        ascending = []
        for token in [t.strip() for t in args.ordenar.split(",")]:
            if token.startswith("-"):
                claves.append(token[1:])
                ascending.append(False)
            else:
                claves.append(token)
                ascending.append(True)
        # ignora columnas inexistentes en silencio
        claves_validas = [c for c in claves if c in out.columns]
        if claves_validas:
            asc = [ascending[i] for i, c in enumerate(claves) if c in out.columns]
            out = out.sort_values(by=claves_validas, ascending=asc)

    if args.limite:
        out = out.head(args.limite)

    return out

def exporta_excel(df: pd.DataFrame, path_out: Path, hoja: str):
    # Asegura formato de fechas legible en Excel
    df = df.copy()
    with pd.ExcelWriter(path_out, engine="openpyxl", datetime_format="yyyy-mm-dd") as xw:
        df.to_excel(xw, sheet_name=hoja, index=False)

def build_parser():
    p = argparse.ArgumentParser(
        description="Filtra data_seguimiento.xlsx y exporta los resultados a Excel."
    )
    p.add_argument("--input", default="data_seguimiento.xlsx", help="Ruta del Excel de entrada.")
    p.add_argument("--hoja", default=None, help="Nombre de hoja de entrada (opcional).")

    # Filtros de texto (múltiples)
    p.add_argument("--nombre", nargs="*", help="Filtro contiene para Nombre (acepta varios).")
    p.add_argument("--apellido", nargs="*", help="Filtro contiene para Apellido (acepta varios).")
    p.add_argument("--cargo", nargs="*", help="Coincidencia exacta insensible a mayúsculas.")
    p.add_argument("--oficina", nargs="*", help="Coincidencia exacta insensible a mayúsculas.")
    p.add_argument("--entidad", nargs="*", help="Coincidencia exacta insensible a mayúsculas.")

    # Cese: --cese si quieres SÍ; --no-cese si quieres NO
    g = p.add_mutually_exclusive_group()
    g.add_argument("--cese", action="store_true", help="Filtra Cese = SÍ.")
    g.add_argument("--no-cese", dest="cese", action="store_false", help="Filtra Cese = NO.")

    # Rangos de fechas (YYYY-MM-DD)
    p.add_argument("--nac-desde", help="Fecha mínima de Nacimiento.")
    p.add_argument("--nac-hasta", help="Fecha máxima de Nacimiento.")
    p.add_argument("--ini-desde", help="Fecha mínima de Inicio.")
    p.add_argument("--ini-hasta", help="Fecha máxima de Inicio.")
    p.add_argument("--cese-desde", help="Fecha mínima de Cese.")
    p.add_argument("--cese-hasta", help="Fecha máxima de Cese.")

    # Orden y límite
    p.add_argument("--ordenar", help="Ej: 'Entidad,-Fecha_inicio,Apellido'. El '-' invierte el orden.")
    p.add_argument("--limite", type=int, help="Número máximo de filas en el resultado.")

    # Salida
    p.add_argument("--output", default="data_filtrado.xlsx", help="Ruta de Excel de salida.")
    p.add_argument("--hoja-salida", default="Filtrado", help="Nombre de la hoja de salida.")

    return p

def main():
    parser = build_parser()
    args = parser.parse_args()

    path_in = Path(args.input)
    if not path_in.exists():
        raise FileNotFoundError(f"No encuentro el Excel de entrada: {path_in.resolve()}")

    df = leer_excel(path_in, args.hoja)
    filtrado = aplica_filtros(df, args)
    exporta_excel(filtrado, Path(args.output), args.hoja_salida)

if __name__ == "__main__":
    main()