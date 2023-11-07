import sqlite3
import csv
from openpyxl import Workbook
from datetime import datetime

def agregar_servicio(cursor):
    while True:
        nombre_servicio = input("Ingrese el nombre del servicio: ")
        if nombre_servicio.strip() == '':
            print("El nombre del servicio no puede quedar vacío.")
            continue
        try:
            costo_servicio = float(input("Ingrese el costo del servicio: "))
        except ValueError:
            print("Solamente se aceptan valores numéricos. Inténtelo de nuevo.")
            continue
        if costo_servicio <= 0:
            print("El costo del servicio debe ser superior a 0.00.")
            continue
        else:
            cursor.execute("INSERT INTO servicios (nombre, costo) VALUES (?, ?)", (nombre_servicio, costo_servicio))
            conn.commit()
            nueva_clave = cursor.lastrowid
            print("Servicio agregado con éxito. Clave del servicio:", nueva_clave)
        break

def buscar_por_clave(cursor):
    cursor.execute("SELECT s_clave, nombre FROM servicios")
    servicios = cursor.fetchall()

    if not servicios:
        print("No hay servicios registrados.")
        return

    print("Listado de servicios:")
    for servicio in servicios:
        print(f"Clave: {servicio[0]}, Nombre: {servicio[1]}")

    clave_servicio = int(input("Ingrese la clave del servicio que desea buscar: "))

    cursor.execute("SELECT nombre, costo FROM servicios WHERE s_clave = ?", (clave_servicio,))
    servicio_encontrado = cursor.fetchone()

    if servicio_encontrado:
        nombre, costo = servicio_encontrado
        print(f"Detalle del servicio - Clave: {clave_servicio}, Nombre: {nombre}, Costo: {costo}")
    else:
        print("No se encontró ningún servicio con la clave proporcionada.")

def buscar_por_nombre(cursor):
    nombre_buscar = input("Ingrese el nombre del servicio a buscar: ")

    cursor.execute("SELECT s_clave, nombre, costo FROM servicios WHERE lower(nombre) = lower(?)", (nombre_buscar,))
    servicios_encontrados = cursor.fetchall()

    if servicios_encontrados:
        print("Servicios encontrados:")
        for servicio in servicios_encontrados:
            clave, nombre, costo = servicio
            print(f"Clave: {clave}, Nombre: {nombre}, Costo: {costo}")
    else:
        print("No se encontraron servicios con el nombre proporcionado.")


def generar_reporte_por_clave(conn):
    try:
        with conn:
            mi_cursor = conn.cursor()
            mi_cursor.execute("SELECT * FROM servicios ORDER BY s_clave")
            servicios = mi_cursor.fetchall()

            if servicios:
                print("Reporte de servicios ordenados por clave:")
                for servicio in servicios:
                    print(f"Clave del servicio: {servicio[0]}")
                    print(f"Nombre del servicio: {servicio[1]}")
                    print(f"Costo del servicio: {servicio[2]}")
                try:
                    export_option = input("¿Desea exportar el reporte a CSV (1), Excel (2) o regresar al menú de reportes (3)? ")
                except ValueError:
                    print("Opcion no valida, Ingrese una opcion valida.")
                if export_option == "1":
                    exportar_reporte(servicios, "CSV", "ReporteServiciosPorClave")
                elif export_option == "2":
                    exportar_reporte(servicios, "Excel", "ReporteServiciosPorClave")
                elif export_option == "3":
                    return
                else:
                    print("Opción no válida.")
            else:
                print("No hay servicios registrados.")

    except sqlite3.Error as e:
        print("Error al generar el reporte:", e)

def generar_reporte_por_nombre(conn):
    try:
        with conn:
            mi_cursor = conn.cursor()
            mi_cursor.execute("SELECT * FROM servicios ORDER BY nombre")
            servicios = mi_cursor.fetchall()

            if servicios:
                print("Reporte de servicios ordenados por nombre:")
                for servicio in servicios:
                    print(f"Clave del servicio: {servicio[0]}")
                    print(f"Nombre del servicio: {servicio[1]}")
                    print(f"Costo del servicio: {servicio[2]}")
                try:
                    export_option = input("¿Desea exportar el reporte a CSV (1), Excel (2) o regresar al menú de reportes (3)? ")
                except ValueError:
                    print("Opcion no valida, Ingrese una opcion valida.")
                if export_option == "1":
                    exportar_reporte(servicios, "CSV", "ReporteServiciosPorNombre")
                elif export_option == "2":
                    exportar_reporte(servicios, "Excel", "ReporteServiciosPorNombre")
                elif export_option == "3":
                    return
                else:
                    print("Opción no válida.")
            else:
                print("No hay servicios registrados.")

    except sqlite3.Error as e:
        print("Error al generar el reporte:", e)

def exportar_reporte(servicios, formato, nombre_reporte):
    fecha_reporte = datetime.now().strftime("%m_%d_%Y")
    nombre_archivo = f"{nombre_reporte}_{fecha_reporte}"

    if formato == "CSV":
        with open(f"{nombre_archivo}.csv", 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Clave del servicio", "Nombre del servicio", "Costo del servicio"])
            for servicio in servicios:
                writer.writerow([servicio[0], servicio[1], servicio[2]])
        print(f"Reporte exportado a {nombre_archivo}.csv")
    elif formato == "Excel":
        wb = Workbook()
        ws = wb.active
        ws.append(["Clave del servicio", "Nombre del servicio", "Costo del servicio"])
        for servicio in servicios:
            ws.append([servicio[0], servicio[1], servicio[2]])
        wb.save(f"{nombre_archivo}.xlsx")
        print(f"Reporte exportado a {nombre_archivo}.xlsx")
    else:
        print("Formato de exportación no válido.")

def menu_reportes(cursor):
    while True:
        print("Opciones de consulta y reportes:")
        print("1. Búsqueda por clave de servicio")
        print("2. Búsqueda por nombre de servicio")
        print("3. Listado de servicios")
        print("4. Volver al menú de servicios")
        try:
            opcion_reporte = int(input("Seleccione una opción: "))
        except ValueError:
                print("Opcion no valida, Ingrese una opcion valida.")
                continue
        if opcion_reporte == 1:
            buscar_por_clave(cursor)
        elif opcion_reporte == 2:
            buscar_por_nombre(cursor)
        elif opcion_reporte == 3:
            menu_listado_servicios(cursor)
        elif opcion_reporte == 4:
            print("Volviendo al menú de servicios.")
            break
        else:
            print("Opción no válida, Ingrese una opcion valida.")

def menu_listado_servicios(cursor):
    while True:
        print("Opciones de listado de servicios:")
        print("1. Listar servicios ordenados por clave")
        print("2. Listar servicios ordenados por nombre de servicio")
        print("3. Volver al menú anterior")
        try:
            opcion_listado = int(input("Seleccione una opción: "))
        except ValueError:
            print("Opción no válida. Ingrese una opción válida.")
            continue
        if opcion_listado == 1:
            generar_reporte_por_clave(conn)
        elif opcion_listado == 2:
            generar_reporte_por_nombre(conn)
        elif opcion_listado == 3:
            print("Volviendo al menú anterior.")
            break
        else:
            print("Opción no válida. Ingrese una opción válida.")


try:
    with sqlite3.connect("Taller_Mecanico.db") as conn:
        mi_cursor = conn.cursor()

        mi_cursor.execute("CREATE TABLE IF NOT EXISTS servicios (s_clave INTEGER PRIMARY KEY, nombre TEXT NOT NULL, costo REAL NOT NULL);")

        while True:
            print("Menú principal:")
            print("1. Agregar un servicio")
            print("2. Consultas y reportes")
            print("3. Volver al Menu Principal")
            try:    
                opcion = int(input("Seleccione una opción: "))
            except ValueError:
                print("Opcion no valida, Ingrese una opcion valida.")
                continue
            if opcion == 1:
                agregar_servicio(mi_cursor)
            elif opcion == 2:
                menu_reportes(mi_cursor)
            elif opcion == 3:
                print("Volviendo al Menu Principal.")
                break
            else:
                print("Opción no válida, Ingrese una opcion valida.")


except sqlite3.Error as e:
    print("Error de base de datos:", e)