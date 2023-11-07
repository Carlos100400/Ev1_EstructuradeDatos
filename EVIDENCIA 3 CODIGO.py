from prettytable import PrettyTable
import sqlite3
from sqlite3 import Error
import sys
import datetime
import csv
import openpyxl
from openpyxl import Workbook
import re
import pandas as pd

conn = sqlite3.connect("Taller_Mecanico.db")
mi_cursor = conn.cursor()

def obtener_clientes(conn):
    mi_cursor = conn.cursor()
    mi_cursor.execute("SELECT c_clave, nombre FROM clientes")
    clientes = mi_cursor.fetchall()
    return clientes

def obtener_servicios(conn):
    mi_cursor = conn.cursor()
    mi_cursor.execute("SELECT s_clave, nombre, costo FROM servicios")
    servicios = mi_cursor.fetchall()
    return servicios

def calcular_monto(servicios_seleccionados):
    return sum(servicio[2] for servicio in servicios_seleccionados)

def registrar_nota(conn):
    try:
        mi_cursor = conn.cursor()
        
        fecha_act = datetime.date.today()
        while True:
            try:
                fecha_proporcionada = input('Fecha de la nota (dd/mm/aaaa): ')
                fecha_ing = datetime.datetime.strptime(fecha_proporcionada, "%d/%m/%Y").date()
                if fecha_ing >= fecha_act:
                    print('La fecha no puede ser posterior a la actual del sistema. Intente de nuevo.\n')
                    break
                else:
                    break
            except ValueError:
                print('Tipo de formato no válido. Inténtelo de nuevo\n')
            except Exception as error:
                print(f'Ocurrió un problema: {error}\n')

        clientes = obtener_clientes(conn)
        print("Clientes disponibles:")
        for cliente in clientes:
            print(f"Clave: {cliente[0]}, Nombre: {cliente[1]}")
        

        c_clave = int(input("Ingrese la clave del cliente: "))

        mi_cursor.execute("SELECT * FROM clientes WHERE c_clave = ?", (c_clave,))
        cliente_existente = mi_cursor.fetchone()
        if not cliente_existente:
            print("El cliente no existe. Registre al cliente primero.")
            return

        servicios = obtener_servicios(conn)
        print("Servicios disponibles:")
        for servicio in servicios:
            print(f"Clave: {servicio[0]}, Nombre: {servicio[1]}, Costo: {servicio[2]}")


        servicios_seleccionados = []
        while True:
            s_clave = int(input("Ingrese la clave del servicio (0 para finalizar): "))
            if s_clave == 0:
                break
            mi_cursor.execute("SELECT * FROM servicios WHERE s_clave = ?", (s_clave,))
            servicio_existente = mi_cursor.fetchone()
            if not servicio_existente:
                print("El servicio no existe. Ingrese una clave válida.")
                continue
            servicios_seleccionados.append(servicio_existente)

        monto_total = calcular_monto(servicios_seleccionados)

        mi_cursor.execute("INSERT INTO notas (fecha, c_clave, monto, estado) VALUES (?, ?, ?, ?)",
                          (fecha_ing, c_clave, monto_total, 'guardado'))
        n_clave = mi_cursor.lastrowid()

        for servicio in servicios_seleccionados:
            mi_cursor.execute("INSERT INTO detalle_nota (n_clave, s_clave) VALUES (?, ?)",
                              (n_clave, servicio[0]))

        conn.commit()
        print(f"Nota registrada exitosamente con folio {n_clave}")

    except Error as e:
        print(e)
        conn.rollback()

    except Exception as ex:
        print(f"Se produjo el siguiente error: {ex}")
        conn.rollback()

    while True:
        estado = input("¿Desea guardar la nota? 1. Sí, 2. No :  ")

        if estado == "1":
            print("*** Se guardó la nota ***")
        elif estado == "2":
            try:
                conn = sqlite3.connect("Taller_Mecanico.db")
                mi_cursor = conn.cursor()
                mi_cursor.execute("UPDATE notas SET estado = 'cancelado' WHERE n_clave = (?)", n_clave)
                print(" *** Se canceló la nota *** ")
                break
            except Error as e:
                print(e)
                return False
            except Exception:
                print(f"Se produjo el siguiente error: {sys.exc_info()[0]}")
                return False
            finally:
                conn.close()
        else:
            print("Opción NO válida. Inténtelo de nuevo.")

def RecuperarNota(mi_cursor):
    conn = sqlite3.connect("Taller_Mecanico.db")
    while True:
        try:
            mi_cursor = conn.cursor()
            mi_cursor.execute("SELECT n_clave FROM notas WHERE estado = 'cancelado';")
            claves = mi_cursor.fetchall()
            
            if claves:
                mostrarClaves = PrettyTable()
                mostrarClaves.field_names("Clave de notas CANCELADAS")
                for c_clave in claves:
                    mostrarClaves.add_row(c_clave)
                print(mostrarClaves)
            else:
                print("No se encontraron notas canceladas.")
                return False
        except Error as e:
            print(e)
            return False
        except Exception:
            print(f"Se produjo el siguiente error: {sys.exc_info()[0]}")
            return False
        finally:
            conn.close()
        
        while True:
            clave_pedida = input("Ingrese la clave de la nota que desea recuperar (ENTER para no recuperar ninguna nota): ")
            if not clave_pedida.strip():
                print("*** No se recuperó ninguna nota. ***")
                break
            
            try:
                mi_cursor = conn.cursor()
                valor1 = {"clave": clave_pedida}
                mi_cursor.execute("SELECT * FROM notas WHERE estado = 'cancelado', n_clave = :clave;", valor1)
                nota_pos_recup = mi_cursor.fetchall()
                
                if nota_pos_recup:
                    mostrarNotaC = PrettyTable()
                    mostrarNotaC.field_names("Clave de la nota", "Fecha", "Clave del cliente", "Monto")
                    mostrarNotaC.add_colum = (nota_pos_recup[0], nota_pos_recup[1], nota_pos_recup[2], nota_pos_recup[3])
                    break
                else:
                    print("La clave es incorrecta. Inténte de nuevo.")
            except Error as e:
                print(e)
                return False
            except Exception:
                print(f"Se produjo el siguiente error: {sys.exc_info()[0]}")
                return False
            finally:
                conn.close()
        
        while True:
            recup = input("¿Desea cancelar la nota? 1. Si, 2. No: ")
            if recup == 1:
                try:
                    mi_cursor = conn.cursor()
                    valor = {"clave": clave_pedida}
                    mi_cursor.execute("UDAPTE notas SET estado = 'cancelado' WHERE clave = :clave;", valor)
                    print(" *** Se canceló la nota *** ")
                    break
                except Error as e:
                    print(e)
                    return False
                except:
                    print(f"Se produjo el siguiente error: {sys.exc_info()[0]}")
                    return False
                finally:
                    if (conn):
                        conn.close()
            elif recup == 2:
                print("*** No se canceló ninguna nota ***")
                break
            else:
                print("Opción no válida. Inténte de nuevo.")
        
        
def CancelarNota(mi_cursor):
    conn = sqlite3.connect("Taller_Mecanico.db")
    while True:
        try:
            mi_cursor = conn.cursor()
            mi_cursor.execute("SELECT n_clave FROM notas WHERE estado = 'guardado';")
            claves = mi_cursor.fetchall()
            
            if claves:
                mostrarClaves = PrettyTable()
                mostrarClaves.field_names("Clave de notas GUARDADAS")
                for c_clave in claves:
                    mostrarClaves.add_row(c_clave)
                print(mostrarClaves)
            else:
                print("No se encontraron notas guardadas.")
                return False
        except Error as e:
            print(e)
            return False
        except Exception:
            print(f"Se produjo el siguiente error: {sys.exc_info()[0]}")
            return False
        finally:
            conn.close()
        
        while True:
            clave_pedida = input("Ingrese la clave de la nota que desea cancelar (ENTER para no recuperar ninguna nota): ")
            if not clave_pedida.strip():
                print("*** No se recuperó ninguna nota. ***")
                break
            
            try:
                mi_cursor = conn.cursor()
                valor1 = {"clave": clave_pedida}
                mi_cursor.execute("SELECT * FROM notas WHERE estado = 'guardado', n_clave = :clave;", valor1)
                nota_pos_canc = mi_cursor.fetchall()
                
                if nota_pos_canc:
                    mostrarNotaG = PrettyTable()
                    mostrarNotaG.field_names("Clave de la nota", "Fecha", "Clave del cliente", "Monto")
                    mostrarNotaG.add_colum = (nota_pos_canc[0], nota_pos_canc[1], nota_pos_canc[2], nota_pos_canc[3])
                    break
                else:
                    print("La clave es incorrecta. Inténte de nuevo.")
            except Error as e:
                print(e)
                return False
            except Exception:
                print(f"Se produjo el siguiente error: {sys.exc_info()[0]}")
                return False
            finally:
                conn.close()
        
        while True:
            recup = input("¿Desea cancelar la nota? 1. Si, 2. No: ")
            if recup == 1:
                try:
                    mi_cursor = conn.cursor()
                    valor = {"clave": clave_pedida}
                    mi_cursor.execute("UDAPTE notas SET estado = 'cancelado' WHERE clave = :clave;", valor)
                    print(" *** Se canceló la nota *** ")
                    break
                except Error as e:
                    print(e)
                    return False
                except:
                    print(f"Se produjo el siguiente error: {sys.exc_info()[0]}")
                    return False
                finally:
                    if (conn):
                        conn.close()
            elif recup == 2:
                print("*** No se canceló ninguna nota ***")
                break
            else:
                print("Opción no válida. Inténte de nuevo.")

def consulta_por_periodo(fecha_inicial, fecha_final):
    conn = sqlite3.connect('mi_base_de_datos.db')
    mi_cursor = conn.cursor()

    mi_cursor.execute("CREATE TABLE IF NOT EXISTS notas \
            (n_clave INTEGER PRIMARY KEY, fecha TIMESTAMP NOT NULL, c_clave INTEGER NOT NULL,\
            monto REAL NOT NULL, estado TEXT NOT NULL, FOREIGN KEY(c_clave) REFERENCES clientes(c_clave));")
    conn.commit()

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
    conn = sqlite3.connect('mi_base_de_datos.db')
    mi_cursor = conn.cursor()
    mi_cursor.execute("CREATE TABLE IF NOT EXISTS notas \
            (n_clave INTEGER PRIMARY KEY, fecha TIMESTAMP NOT NULL, c_clave INTEGER NOT NULL,\
            monto REAL NOT NULL, estado TEXT NOT NULL, FOREIGN KEY(c_clave) REFERENCES clientes(c_clave));")
    conn.commit()

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

def Consultas_Notas():
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

def menu_notas(conn):
    while True:
        print("\n=== Menú Notas ===")
        print("1. Registrar una nota")
        print("2. Cancelar una nota")
        print("3. Recuperar una nota")
        print("4. Consultas y reportes de notas")
        print("5. Volver al menú principal")

        opcion = input("Seleccione una opción: ")

        if opcion == '1':
            registrar_nota(conn)
        elif opcion == '2':
            CancelarNota(conn)
        elif opcion == '3':
            RecuperarNota(conn)
        elif opcion == '4':
            Consultas_Notas()
        elif opcion == '5':
            break
        else:
            print("Opción no válida. Inténtelo de nuevo.")


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
            
            TablaOrdenado = PrettyTable()
            TablaOrdenado.field_names("Clave", "Nombre", "RFC", "Correo")
            for c_clave, nombre, rfc, correo in clientes:
                TablaOrdenado.add_row(c_clave, nombre, rfc, correo)
            

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

def Servicios():
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

def menu_principal():
    conn = sqlite3.connect("Taller_Mecanico.db")
    
    while True:
        print("\n=== Menú Principal ===")
        print("1. Menú Notas")
        print("2. Menú Clientes")
        print("3. Menú Servicios")
        print("4. Salir")

        opcion = input("Seleccione una opción: ")

        if opcion == '1':
            menu_notas(conn)
        elif opcion == '2':
            menu_clientes()
        elif opcion == '3':
            Servicios()
        elif opcion == '4':
            confirmacion = input("¿Está seguro que desea salir? (Sí/No): ").lower()
            if confirmacion == 'si':
                break
        else:
            print("Opción no válida. Inténtelo de nuevo.")

    conn.close()

menu_principal()