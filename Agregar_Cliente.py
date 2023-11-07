import sqlite3
from sqlite3 import Error
import sys
import csv
import datetime
import pandas as pd
import re


def agregar_cliente():
    while True:
        try:
            with sqlite3.connect("Taller_Mecanico.db") as conn:
                mi_cursor = conn.cursor()
                nombre = input("Ingrese el nombre completo del cliente, (DEJE VACIO PARA TERMINAR): " )

                if not nombre.strip():
                    print("Se dejó de generar clientes")
                    break
               
                while True:
                    rfc = input('Ingrese su RFC: ')
                    if rfc == "":
                        print("El RFC no puede omitirse, inténtelo de nuevo.")
                        continue

                    if not re.match('^[A-Z]{4}\d{6}[A-Z0-9]{3}$', rfc):
                        print("RFC no válido. Inténtelo de nuevo.")
                        continue
                    break

                while True:
                    correo = input("Ingrese su correo electrónico: ")
                    if correo == "":
                        print("El Correo no puede omitirse, inténtelo de nuevo.")
                        continue

                    if not re.match('^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', correo):
                        print("Correo electrónico no válido.")
                        continue
                    break
            
                mi_cursor.execute("INSERT INTO clientes (nombre, rfc, correo) VALUES (?, ?, ?)",
                                (nombre, rfc, correo))
                conn.commit()
                print("Cliente agregado exitosamente")

        except Error as e:
            print(e)
        except Exception:
            print(f"Se produjo el siguiente error: {sys.exc_info()[0]}")



def listado_clientes_ordenado(opcion):
    try:
        with sqlite3.connect("Taller_Mecanico.db") as conn:
            mi_cursor = conn.cursor()

            if opcion == 1:
                query = "SELECT * FROM clientes ORDER BY c_clave;"
                filename_pattern = "ReporteClientesActivosPorClave_{}"
            elif opcion == 2: 
                query = "SELECT * FROM clientes ORDER BY nombre;"
                filename_pattern = "ReporteClientesActivosPorNombre_{}"
            else:
                return

            mi_cursor.execute(query)
            clientes = mi_cursor.fetchall()

            print("Listado de clientes:")
            for cliente in clientes:
                print(cliente)

            export_option = input("¿Desea exportar el reporte a CSV (1), Excel (2) o regresar al menú de reportes (3)? ")
            if export_option in ("1", "2"):
                fecha = datetime.datetime.now().strftime("%m_%d_%Y")
                filename = filename_pattern.format(fecha)

                if export_option == "1":
                    with open(f"{filename}.csv", "w", newline="", encoding="utf-8") as csv_file:
                        csv_writer = csv.writer(csv_file)
                        csv_writer.writerow([i[0] for i in mi_cursor.description])
                        csv_writer.writerows(clientes)
                    print(f"Reporte exportado exitosamente como {filename}.csv")
                    
                elif export_option == "2": 
                    df = pd.DataFrame(clientes, columns=[i[0] for i in mi_cursor.description])
                    df.to_excel(f"{filename}.xlsx", index=False, engine="openpyxl")
                    print(f"Reporte exportado exitosamente como {filename}.xlsx")

            elif export_option == "3":
                return
            else:
                print("Opción no válida. Volviendo al menú principal.")

    except Error as e:
        print(e)
    except Exception:
        print(f"Se produjo el siguiente error: {sys.exc_info()[0]}")

def menu_clientes():
    while True:
        print("\n2.2. Menú Clientes")
        print("1. Agregar un cliente")
        print("2. Consultas y reportes de clientes")
        print("3. Volver al menú principal")

        opcion = input("Ingrese su opción: ")

        if opcion == "1":
            agregar_cliente()
        elif opcion == "2":
            menu_consultas_reportes_clientes()
        elif opcion == "3":
            break
        else:
            print("Opción no válida. Inténtelo de nuevo.")

def menu_consultas_reportes_clientes():
    while True:
        print("\nConsultas y reportes de clientes")
        print("1. Listado de clientes registrados")
        print("2. Volver al menú anterior")

        opcion = input("Ingrese su opción: ")

        if opcion == "1":
            sub_menu_listado_clientes()
        elif opcion == "2":
            break
        else:
            print("Opción no válida. Inténtelo de nuevo.")

def sub_menu_listado_clientes():
    while True:
        print("\n2.2.2.1. Listado de clientes registrados")
        print("1. Ordenado por clave")
        print("2. Ordenado por nombre")
        print("3. Volver al menú anterior")

        opcion = input("Ingrese su opción: ")

        if opcion in ("1", "2"):
            listado_clientes_ordenado(int(opcion))
        elif opcion == "3":
            break
        else:
            print("Opción no válida. Inténtelo de nuevo.")


menu_clientes()