import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re

def extraer_fecha_del_nombre_archivo(nombre_archivo):
    coincidencia = re.search(r'\d{4}\.\d{2}\.\d{2}', nombre_archivo)
    if coincidencia:
        año, mes, día = coincidencia.group(0).split('.')
        return int(año), int(mes), int(día)
    return None, None, None

def obtener_rango_columnas(rango):
    columnas = []
    partes = rango.split(':')
    if len(partes) == 2:
        start, end = partes
        for col in range(ord(start.upper()), ord(end.upper()) + 1):
            columnas.append(chr(col))
    return columnas

def convertir_columnas_a_indices(df, columnas):
    max_columna = len(df.columns)
    indices_columnas = []
    for columna in columnas:
        indice = ord(columna) - ord('A')
        if indice < max_columna:
            indices_columnas.append(indice)
    return indices_columnas

def cargar_datos(archivo):
    """Carga datos desde el archivo y realiza validaciones iniciales."""
    df = pd.read_excel(archivo)
    df.columns = df.columns.str.strip()  # Eliminar espacios en los nombres de las columnas
    st.write("Columnas disponibles en el archivo:", df.columns.tolist())
    return df

def limpiar_datos(df):
    """Limpia y valida los datos en el DataFrame."""
    columnas_requeridas = ['Fecha', 'Representante', 'CódigoProducto', 'Unidades']
    
    columnas_presentes = df.columns.tolist()
    columnas_faltantes = [col for col in columnas_requeridas if col not in columnas_presentes]
    
    if columnas_faltantes:
        st.error(f"Las siguientes columnas están faltando en el archivo: {', '.join(columnas_faltantes)}")
        return df  # Salir de la función si faltan columnas
    
    df = df.dropna(subset=columnas_requeridas)
    df['Unidades'] = pd.to_numeric(df['Unidades'], errors='coerce')
    df = df.dropna(subset=['Unidades'])
    df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce')
    df = df.dropna(subset=['Fecha'])
    
    return df

def transformar_datos(df):
    """Transforma los datos para análisis."""
    df['Mes'] = df['Fecha'].dt.to_period('M')
    return df

def calcular_estadisticas(df):
    """Calcula estadísticas básicas y ventas por categorías."""
    ventas_representante = df.groupby('Representante')['Unidades'].sum()
    ventas_producto = df.groupby('CódigoProducto')['Unidades'].sum()
    ventas_diarias = df.groupby('Fecha')['Unidades'].sum()
    ventas_mensuales = df.groupby('Mes')['Unidades'].sum()
    
    return ventas_representante, ventas_producto, ventas_diarias, ventas_mensuales

def generar_graficos(ventas_representante, ventas_producto, ventas_diarias, ventas_mensuales):
    """Genera gráficos para las estadísticas calculadas con mejoras visuales."""
    try:
        # Gráfico de Ventas Diarias
        st.write("### Ventas Diarias")
        st.write("Este gráfico muestra la cantidad total de unidades vendidas cada día. Puedes observar las tendencias de ventas a lo largo del tiempo y detectar días con ventas inusuales o picos en la demanda.")
        plt.figure(figsize=(12, 6))
        sns.lineplot(x=ventas_diarias.index, y=ventas_diarias.values, marker='o', color='b')
        plt.title('Ventas Diarias')
        plt.xlabel('Fecha')
        plt.ylabel('Unidades Vendidas')
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(plt.gcf())
        plt.clf()

        # Gráfico de Ventas por Representante
        st.write("### Ventas por Representante")
        st.write("Este gráfico muestra el total de unidades vendidas por cada representante de ventas. Puedes ver quiénes son los principales vendedores y cómo se comparan entre sí.")
        plt.figure(figsize=(12, 6))
        sns.barplot(x=ventas_representante.index, y=ventas_representante.values, palette='viridis')
        plt.title('Total de Ventas por Representante')
        plt.xlabel('Representante')
        plt.ylabel('Unidades Vendidas')
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(plt.gcf())
        plt.clf()

        # Gráfico de Ventas por Producto
        st.write("### Ventas por Producto")
        st.write("Este gráfico muestra el total de unidades vendidas para cada código de producto. Permite identificar los productos más vendidos y aquellos con menor demanda.")
        plt.figure(figsize=(12, 6))
        sns.barplot(x=ventas_producto.index, y=ventas_producto.values, palette='magma')
        plt.title('Total de Ventas por Producto')
        plt.xlabel('Código de Producto')
        plt.ylabel('Unidades Vendidas')
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(plt.gcf())
        plt.clf()

        # Gráfico de Ventas Mensuales
        st.write("### Ventas Mensuales")
        st.write("Este gráfico muestra el total de unidades vendidas cada mes. Ayuda a identificar patrones estacionales y tendencias de ventas a lo largo de los meses.")
        plt.figure(figsize=(12, 6))
        sns.lineplot(x=ventas_mensuales.index.to_timestamp(), y=ventas_mensuales.values, marker='o', color='g')
        plt.title('Ventas Mensuales')
        plt.xlabel('Mes')
        plt.ylabel('Unidades Vendidas')
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(plt.gcf())
        plt.clf()

    except Exception as e:
        st.error(f"Error al generar los gráficos: {e}")

def analisis_adicional(df):
    """Realiza un análisis adicional sobre los datos."""
    try:
        st.header("Análisis Adicional")
        
        # Correlación entre unidades vendidas y el tiempo
        st.write("#### Correlación entre Unidades Vendidas y Fecha")
        df['Fecha_ordinal'] = df['Fecha'].apply(lambda x: x.toordinal())
        correlation = df[['Fecha_ordinal', 'Unidades']].corr().iloc[0, 1]
        st.write(f"Correlación: {correlation:.2f}")
        
        # Visualización de la tendencia de ventas
        if len(df['Fecha'].dt.to_period('M').unique()) > 3:
            st.write("#### Tendencia de Ventas")
            df.set_index('Fecha', inplace=True)
            df_monthly = df.resample('M').sum()
            plt.figure(figsize=(12, 6))
            sns.lineplot(data=df_monthly, x=df_monthly.index, y='Unidades', marker='o', color='b')
            plt.title('Tendencia de Ventas Mensuales')
            plt.xlabel('Fecha')
            plt.ylabel('Unidades Vendidas')
            plt.grid(True)
            plt.xticks(rotation=45)
            plt.tight_layout()
            st.pyplot(plt.gcf())
            plt.clf()
        else:
            st.write("No hay suficientes datos para realizar una tendencia de ventas.")
            
    except Exception as e:
        st.error(f"Error en el análisis adicional: {e}")

def seleccion_periodo(df):
    """Permite al usuario seleccionar un periodo para análisis."""
    st.write("### Seleccionar Periodo")
    periodos = df['Mes'].unique()
    periodo_seleccionado = st.selectbox("Seleccionar Periodo", periodos)
    df_filtrado = df[df['Mes'] == periodo_seleccionado]
    return df_filtrado

def main():
    st.title("Análisis de Ventas de Teléfonos")

    st.header("Carga de Datos")
    archivo = st.file_uploader("Selecciona un archivo Excel", type=["xls", "xlsx"])

    if archivo:
        df = cargar_datos(archivo)
        if not df.empty:
            df = limpiar_datos(df)
            df = transformar_datos(df)
            ventas_representante, ventas_producto, ventas_diarias, ventas_mensuales = calcular_estadisticas(df)
            
            if ventas_representante is not None:
                st.header("Estadísticas de Ventas")
                st.write("Total de Ventas por Representante:")
                st.write(ventas_representante)
                
                st.write("Total de Ventas por Producto:")
                st.write(ventas_producto)
                
                st.write("Total de Ventas Diarias:")
                st.write(ventas_diarias)
                
                st.write("Total de Ventas Mensuales:")
                st.write(ventas_mensuales)
                
                st.header("Visualización de Datos")
                generar_graficos(ventas_representante, ventas_producto, ventas_diarias, ventas_mensuales)
                
                st.header("Análisis Adicional")
                analisis_adicional(df)

                st.header("Análisis por Periodo")
                df_filtrado = seleccion_periodo(df)
                ventas_representante, ventas_producto, ventas_diarias, ventas_mensuales = calcular_estadisticas(df_filtrado)
                generar_graficos(ventas_representante, ventas_producto, ventas_diarias, ventas_mensuales)
        else:
            st.warning("No se encontraron datos válidos en el archivo.")

if __name__ == "__main__":
    main()
