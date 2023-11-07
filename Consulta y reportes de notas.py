import sqlite3
import datetime
import csv
import openpyxl
from prettytable import PrettyTable


conn = sqlite3.connect('mi_base_de_datos.db')
mi_cursor = conn.cursor()



mi_cursor.execute("CREATE TABLE IF NOT EXISTS notas \
            (n_clave INTEGER PRIMARY KEY, fecha TIMESTAMP NOT NULL, c_clave INTEGER NOT NULL,\
            monto REAL NOT NULL, estado TEXT NOT NULL, FOREIGN KEY(c_clave) REFERENCES clientes(c_clave));")
conn.commit()


def consulta_por_periodo(fecha_inicial, fecha_final):
    
    if fecha_inicial is None:
        fecha_inicial = datetime.date(2000, 1, 1)
    if fecha_final is None:
        fecha_final = datetime.date.today()

    
    mi_cursor.execute('''
        SELECT fecha, monto
        FROM notas
        WHERE fecha BETWEEN ? AND ?
    ''', (fecha_inicial, fecha_final))

    notas = mi_cursor.fetchall()

    if notas:
        
        montos = [monto for _, monto in notas]
        monto_promedio = sum(montos) / len(montos)

        
        tabla = PrettyTable()
        tabla.field_names = ["Fecha", "Monto"]
        for fecha, monto in notas:
            tabla.add_row([fecha, monto])

        print("Informe de notas por período:")
        print(tabla)
        print(f"Monto promedio: ${monto_promedio:.2f}")

        
        exportar_informe(fecha_inicial, fecha_final, tabla)

    else:
        print("No hay notas emitidas para el período especificado.")


def exportar_informe(fecha_inicial, fecha_final, tabla):
    fecha_inicial_str = fecha_inicial.strftime("%m_%d_%Y")
    fecha_final_str = fecha_final.strftime("%m_%d_%Y")

    while True:
        formato = input("Seleccione el formato de exportación (CSV o Excel): ").strip().lower()

        if formato == "csv":
            csv_filename = f"ReportePorPeriodo_{fecha_inicial_str}_{fecha_final_str}.csv"
            with open(csv_filename, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerows(tabla)
            print(f"El informe se ha exportado a {csv_filename}")
            break

        elif formato == "excel":
            excel_filename = f"ReportePorPeriodo_{fecha_inicial_str}_{fecha_final_str}.xlsx"
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Informe"
            for row in tabla:
                ws.append(row)
            wb.save(excel_filename)
            print(f"El informe se ha exportado a {excel_filename}")
            break

        else:
            print("Formato no válido. Por favor, seleccione CSV o Excel.")


def consulta_por_folio(folio):
    
    mi_cursor.execute('''
        SELECT fecha, c_clave, monto, estado
        FROM notas
        WHERE n_clave = ? AND estado <> 'cancelada'
    ''', (folio,))

    nota = mi_cursor.fetchone()

    if nota:
        fecha, c_clave, monto, estado = nota

        
        mi_cursor.execute('SELECT nombre FROM clientes WHERE c_clave = ?', (c_clave,))
        cliente_nombre = mi_cursor.fetchone()[0]

       
        mi_cursor.execute('SELECT servicio, costo FROM detalles WHERE n_clave = ?', (folio,))
        detalles = mi_cursor.fetchall()

        
        tabla = PrettyTable()
        tabla.field_names = ["Folio", "Fecha", "Cliente", "Monto", "Estado"]
        tabla.add_row([folio, fecha, cliente_nombre, monto, estado])

        print("Informe de la nota por folio:")
        print(tabla)

        print("Detalles de la nota:")
        detalles_tabla = PrettyTable()
        detalles_tabla.field_names = ["Servicio", "Costo"]
        detalles_tabla.add_rows(detalles)
        print(detalles_tabla)

    else:
        print("La nota no se encuentra en el sistema o está cancelada.")


while True:
    print("""
    Menú Principal:
    1 - Consulta por período
    2 - Consulta por folio
    3 - Salir
    """)

    opcion = input("Seleccione una opción: ").strip()

    if opcion == "1":
        fecha_inicial_str = input("Fecha inicial (DD/MM/AAAA): ")
        fecha_final_str = input("Fecha final (DD/MM/AAAA): ")

        try:
            fecha_inicial = datetime.datetime.strptime(fecha_inicial_str, "%d/%m/%Y").date()
            fecha_final = datetime.datetime.strptime(fecha_final_str, "%d/%m/%Y").date()
        except ValueError:
            print("Formato de fecha no válido. Utilice DD/MM/AAAA.")
            continue

        consulta_por_periodo(fecha_inicial, fecha_final)

    elif opcion == "2":
        folio = int(input("Folio de la nota: "))
        consulta_por_folio(folio)

    elif opcion == "3":
        print("Saliendo del programa.")
        break

    else:
        print("Opción no válida. Por favor, seleccione una opción válida.")

