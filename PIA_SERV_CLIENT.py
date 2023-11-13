import sqlite3
from sqlite3 import Error
import sys
import csv
import pandas as pd
import datetime
import openpyxl

def servicios_mas_prestados():
    try:
        cantidad_servicios = int(input("Ingrese la cantidad de servicios más prestados a identificar: "))
        fecha_inicial = input("Ingrese la fecha inicial del período a reportar (dd/mm/aaaa): ")
        fecha_final = input("Ingrese la fecha final del período a reportar (dd/mm/aaaa): ")

        with sqlite3.connect("Taller_Mecanico.db") as conn:
            mi_cursor = conn.cursor()

            query = f"""
                SELECT s.nombre, COUNT(ns.s_clave) as cantidad_prestada
                FROM servicios s
                JOIN nota_servicios ns ON s.s_clave = ns.s_clave
                JOIN notas n ON ns.n_clave = n.n_clave
                WHERE n.fecha BETWEEN '{fecha_inicial}' AND '{fecha_final}'
                GROUP BY s.nombre
                ORDER BY cantidad_prestada DESC
                LIMIT {cantidad_servicios};
            """

            result = mi_cursor.execute(query).fetchall()

            if not result:
                print("No hay datos disponibles para el período seleccionado.")
                return

  
            print("\nServicios más prestados:")
            print("Nombre del Servicio | Cantidad Prestada")
            for row in result:
                print(f"{row[0]} | {row[1]}")


    
            export_option = input("\n¿Desea exportar el reporte a CSV o Excel? (Ingrese 'csv' o 'excel', o cualquier otra tecla para omitir): ").lower()
            if export_option in ['csv', 'excel']:
                filename = f"ReporteServiciosMasPrestados_{fecha_inicial}_{fecha_final}.{export_option}"
                df = pd.DataFrame(result, columns=["Nombre del Servicio", "Cantidad Prestada"])
                if export_option == 'csv':
                    df.to_csv(filename, index=False)
                else:
                    df.to_excel(filename, index=False)
                print(f"El reporte ha sido exportado como '{filename}'.")


    except ValueError:
        print("Error: Ingrese un valor válido para la cantidad de servicios.")

def clientes_con_mas_notas():
    try:
        cantidad_clientes = int(input("Ingrese la cantidad de clientes con más notas a identificar: "))
        fecha_inicial = input("Ingrese la fecha inicial del período a reportar (dd/mm/aaaa): ")
        fecha_final = input("Ingrese la fecha final del período a reportar (dd/mm/aaaa): ")

        with sqlite3.connect("Taller_Mecanico.db") as conn:
            mi_cursor = conn.cursor()

            query = f"""
                SELECT c.nombre, COUNT(n.n_clave) as cantidad_notas
                FROM clientes c
                JOIN notas n ON c.c_clave = n.c_clave
                WHERE n.fecha BETWEEN '{fecha_inicial}' AND '{fecha_final}'
                GROUP BY c.nombre
                ORDER BY cantidad_notas DESC
                LIMIT {cantidad_clientes};
            """

            result = mi_cursor.execute(query).fetchall()

            if not result:
                print("No hay datos disponibles para el período seleccionado.")
                return

            print("\nClientes con más notas:")
            print("Nombre del Cliente | Cantidad de Notas")
            for row in result:
                print(f"{row[0]} | {row[1]}")

          
            export_option = input("\n¿Desea exportar el reporte a CSV o Excel? (Ingrese 'csv' o 'excel', o cualquier otra tecla para omitir): ").lower()
            if export_option in ['csv', 'excel']:
                filename = f"ReporteClientesConMasNotas_{fecha_inicial}_{fecha_final}.{export_option}"
                df = pd.DataFrame(result, columns=["Nombre del Cliente", "Cantidad de Notas"])
                if export_option == 'csv':
                    df.to_csv(filename, index=False)
                else:
                    df.to_excel(filename, index=False)
                print(f"El reporte ha sido exportado como '{filename}'.")

    except ValueError:
        print("Error: Ingrese un valor válido para la cantidad de clientes.")


print("MENU")
print("1.- Servivios mas prestados")
print("2.- Clientes con mas notas")

respuesta = int(input("Ingresa un numero: "))

if respuesta == 1:
    servicios_mas_prestados()
elif respuesta == 2:
    clientes_con_mas_notas()
