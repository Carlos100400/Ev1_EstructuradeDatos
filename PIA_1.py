from prettytable import PrettyTable
import sqlite3
from sqlite3 import Error
import sys
from datetime import datetime
import csv
import openpyxl
from openpyxl import Workbook
import re
import pandas as pd

try:
    with sqlite3.connect("Taller_Mecanico.db") as conn:
        mi_cursor = conn.cursor()
        mi_cursor.execute("CREATE TABLE IF NOT EXISTS clientes \
            (c_clave INTEGER PRIMARY KEY, nombre TEXT NOT NULL, rfc TEXT NOT NULL, correo TEXT NOT NULL, estado TEXT NOT NULL);")
        
        mi_cursor.execute("CREATE TABLE IF NOT EXISTS notas \
            (n_clave INTEGER PRIMARY KEY, fecha TIMESTAMP NOT NULL, c_clave INTEGER NOT NULL,\
            monto REAL NOT NULL, estado TEXT NOT NULL, FOREIGN KEY(c_clave) REFERENCES clientes(c_clave));")
        
        mi_cursor.execute("CREATE TABLE IF NOT EXISTS servicios \
            (s_clave INTEGER PRIMARY KEY, nombre TEXT NOT NULL, costo INTEGER NOT NULL, estado TEXT NOT NULL);") 

        mi_cursor.execute("CREATE TABLE IF NOT EXISTS nota_servicios \
            (id_detalle INTEGER PRIMARY KEY, n_clave INTEGER NOT NULL, s_clave INTEGER NOT NULL, \
            FOREIGN KEY(n_clave) REFERENCES notas(n_clave),\
            FOREIGN KEY(s_clave) REFERENCES servicios(s_clave))")
        
        mi_cursor.execute("INSERT INTO clientes (nombre, rfc, correo, estado) VALUES ('Alberto Díaz Ibarra', 'DIIA021114PKO', 'diaz.alberto@gmail.com', 'guardado');")
        mi_cursor.execute("INSERT INTO clientes (nombre, rfc, correo, estado) VALUES ('Debanhi Ochoa Galindo', 'OOGD991005GVH', 'ochoa.debs@gmail.com', 'guardado');")
        mi_cursor.execute("INSERT INTO clientes (nombre, rfc, correo, estado) VALUES ('Carlos Avila Martinez', 'AIMC030609TFV', 'avila.carlos@gmail.com', 'guardado');")
        
        mi_cursor.execute("INSERT INTO servicios (nombre, costo, estado) VALUES ('Llantas', 200, 'guardado');")
        mi_cursor.execute("INSERT INTO servicios (nombre, costo, estado) VALUES ('Ajuste', 500, 'guardado');")
        mi_cursor.execute("INSERT INTO servicios (nombre, costo, estado) VALUES ('Afinación', 300, 'guardado');")
        
        
        print("Tablas creadas exitosamente")
except Error as e:
    print(e)
except Exception:
    print(f"Se produjo el siguiente error: {sys.exc_info()[0]}")

conn = sqlite3.connect("Taller_Mecanico.db")
mi_cursor = conn.cursor()

def obtener_clientes(conn):
    mi_cursor = conn.cursor()
    mi_cursor.execute("SELECT c_clave, nombre FROM clientes WHERE estado= 'guardado';")
    clientes = mi_cursor.fetchall()
    return clientes

def obtener_servicios(conn):
    mi_cursor = conn.cursor()
    mi_cursor.execute("SELECT s_clave, nombre, costo FROM servicios WHERE estado = 'guardado';")
    servicios = mi_cursor.fetchall()
    return servicios

def calcular_monto(servicios_seleccionados):
    return sum(servicio[2] for servicio in servicios_seleccionados)

def mostrar_clientes(clientes):
    if clientes:
        print("\nClientes disponibles:")
        tabla_clientes = PrettyTable()
        tabla_clientes.field_names = ["Clave", "Nombre"]
        tabla_clientes.add_rows(clientes)
        print(tabla_clientes)
    else:
        print("No se encuentran clientes disponibles.")

def mostrar_servicios(servicios):
    if servicios:
        print("\nServicios disponibles:")
        tabla_servicios = PrettyTable() 
        tabla_servicios.field_names = ["Clave", "Nombre", "Costo"]
        tabla_servicios.add_rows(servicios)
        print(tabla_servicios)
    else:
        print("No se encuentran servicios disponibles.")

def registrar_nota(conn):
    try:
        mi_cursor = conn.cursor()

        fecha_act = datetime.now().date()
        while True:
            try:
                fecha_proporcionada = input('Fecha de la nota (dd/mm/aaaa): ')
                fecha_ing = datetime.strptime(fecha_proporcionada, "%d/%m/%Y").date()
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
        mostrar_clientes(clientes)
        
        while True:
            try:
                c_clave = int(input("Ingrese la clave del cliente: "))
                    
                mi_cursor.execute("SELECT * FROM clientes WHERE c_clave = ? AND estado = 'guardado';", (c_clave,))
                cliente_existente = mi_cursor.fetchone()
                if not cliente_existente:
                    print("El cliente no existe. Ingrese una clave existente.")
                else:
                    break
            except ValueError:
                print("Únicamente valores numéricos.")
            except Error as e:
                print(e)
            except Exception as e:
                print(e)

        servicios = obtener_servicios(conn)
        mostrar_servicios(servicios)

        servicios_seleccionados = []
        while True:
            try:
                s_clave = int(input("Ingrese la clave del servicio (0 para finalizar): "))
                if s_clave == 0:
                    break
                mi_cursor.execute("SELECT * FROM servicios WHERE estado = 'guardado' AND s_clave = ?;", (s_clave,))
                servicio_existente = mi_cursor.fetchone()
                if servicio_existente:
                    servicios_seleccionados.append(servicio_existente)
                else:
                    print("El servicio no existe. Ingrese una clave válida.")
            except ValueError:
                print('Ingrese solamente un número entero')
            except Error as e:
                print(e)
            except Exception as e:
                print(e)

        monto_total = calcular_monto(servicios_seleccionados)
        with sqlite3.connect("Taller_Mecanico.db", detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES) as conn:
            mi_cursor = conn.cursor()

            mi_cursor.execute("INSERT INTO notas (fecha, c_clave, monto, estado) VALUES (?, ?, ?, ?)",
                              (fecha_ing, c_clave, monto_total, 'guardado'))
            n_clave = mi_cursor.lastrowid

            for servicio in servicios_seleccionados:
                mi_cursor.execute("INSERT INTO nota_servicios (n_clave, s_clave) VALUES (?, ?)",
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
            break
        elif estado == "2":
            try:
                conn = sqlite3.connect("Taller_Mecanico.db")
                mi_cursor = conn.cursor()
                mi_cursor.execute("UPDATE notas SET estado = 'cancelado' WHERE n_clave = ?", (n_clave,))
                conn.commit()
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
                mostrarClavesC = PrettyTable()
                mostrarClavesC.field_names = ["Clave de notas CANCELADAS"]
                for n_clave in claves:
                    mostrarClavesC.add_row([n_clave[0]])
                print(mostrarClavesC)
            else:
                print("No se encontraron notas canceladas.")
                return False
        except Error as e:
            print(e)
            return False
        except Exception:
            print(f"Se produjo el siguiente error: {sys.exc_info()[0]}")
            return False
        
        while True:
            clave_pedida = input("Ingrese la clave de la nota que desea recuperar (ENTER para no recuperar ninguna nota): ")
            if not clave_pedida.strip():
                print("*** No se recuperó ninguna nota. ***")
                return False
            
            try:
                mi_cursor = conn.cursor()
                valor1 = {"clave": clave_pedida}
                mi_cursor.execute("SELECT * FROM notas WHERE estado = 'cancelado' AND n_clave = :clave;", valor1)
                nota_pos_recup = mi_cursor.fetchall()
                
                if nota_pos_recup:
                    mostrarNotaC = PrettyTable()
                    mostrarNotaC.field_names = ["Clave de la nota", "Fecha", "Clave del cliente", "Monto"]
                    mostrarNotaC.add_row([nota_pos_recup[0][0], nota_pos_recup[0][1], nota_pos_recup[0][2], nota_pos_recup[0][3]])
                    print(mostrarNotaC)
                    break
                else:
                    print("La clave es incorrecta. Inténte de nuevo.")
            except Error as e:
                print(e)
                return False
            except Exception:
                print(f"Se produjo el siguiente error: {sys.exc_info()[0]}")
                return False
        
        while True:
            recup = int(input("¿Desea recuperar la nota? 1. Si, 2. No: "))
            if recup == 1:
                try:
                    mi_cursor = conn.cursor()
                    valor = {"clave": clave_pedida}
                    mi_cursor.execute("UPDATE notas SET estado = 'guardado' WHERE n_clave = :clave;", valor)
                    conn.commit()
                    print(" *** Se recupero la nota *** ")
                    return False
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
                print("*** No se guardo ninguna nota ***")
                return False
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
                mostrarClaves.field_names = ["Clave de notas GUARDADAS"]
                for n_clave in claves:
                    mostrarClaves.add_row([n_clave[0]])
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
        
        while True:
            clave_pedida = input("Ingrese la clave de la nota que desea cancelar (ENTER para no cancelar ninguna nota): ")
            if not clave_pedida.strip():
                print("*** No se recuperó ninguna nota. ***")
                return False
            
            try:
                mi_cursor = conn.cursor()
                valor1 = {"clave": clave_pedida}
                mi_cursor.execute("SELECT * FROM notas WHERE estado = 'guardado' AND n_clave = :clave;", valor1)
                nota_pos_canc = mi_cursor.fetchall()
                
                if nota_pos_canc:
                    mostrarNotaG = PrettyTable()
                    mostrarNotaG.field_names = ["Clave de la nota", "Fecha", "Clave del cliente", "Monto"]
                    mostrarNotaG.add_row([nota_pos_canc[0][0], nota_pos_canc[0][1], nota_pos_canc[0][2], nota_pos_canc[0][3]])
                    print(mostrarNotaG)
                    break
                else:
                    print("La clave es incorrecta. Inténte de nuevo.")
            except Error as e:
                print(e)
                return False
            except Exception:
                print(f"Se produjo el siguiente error: {sys.exc_info()[0]}")
                return False
        
        while True:
            recup = int(input("¿Desea cancelar la nota? 1. Si, 2. No: "))
            if recup == 1:
                try:
                    mi_cursor = conn.cursor()
                    valor = {"clave": clave_pedida}
                    mi_cursor.execute("UPDATE notas SET estado = 'cancelado' WHERE n_clave = :clave;", valor)
                    conn.commit()
                    print(" *** Se canceló la nota *** ")
                    return False
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
                return False
            else:
                print("Opción no válida. Inténte de nuevo.")

def consulta_por_periodo(fecha_inicial, fecha_final):

    if fecha_inicial is None:
        fecha_inicial = datetime.date(2000, 1, 1)
    if fecha_final is None:
        fecha_final = datetime.date.today()

    
    mi_cursor.execute("SELECT n_clave, monto FROM notas WHERE estado = 'guardado' AND fecha BETWEEN ? AND ?", (fecha_inicial, fecha_final))

    notas = mi_cursor.fetchall()

    if notas:
        
        montos = [monto for _, monto in notas]
        monto_promedio = sum(montos) / len(montos)

        
        tabla = PrettyTable()
        tabla.field_names = ["Clave de la nota", "Monto"]
        for n_clave, monto in notas:
            tabla.add_row([n_clave, monto])

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
                writer.writerow(tabla.field_names)  
                writer.writerows(tabla._rows)
            print(f"El informe se ha exportado a {csv_filename}")
            break

        elif formato == "excel":
            excel_filename = f"ReportePorPeriodo_{fecha_inicial_str}_{fecha_final_str}.xlsx"
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Informe"

            ws.append(tabla.field_names)
            
            for row in tabla._rows:
                ws.append(row)
            wb.save(excel_filename)
            print(f"El informe se ha exportado a {excel_filename}")
            break
        else:
            print("Formato no válido. Por favor, seleccione CSV o Excel.")


def consulta_por_folio(folio):
    folio = int(folio)
    mi_cursor.execute("SELECT fecha, c_clave, monto FROM notas WHERE estado = 'guardado' AND n_clave = ?;", (folio,))

    nota = mi_cursor.fetchone()

    if nota:
        fecha, c_clave, monto = nota

        
        mi_cursor.execute('SELECT nombre, rfc, correo FROM clientes WHERE c_clave = ?', (c_clave,))
        cliente = mi_cursor.fetchone()
        nombre, rfc, correo = cliente
       
        mi_cursor.execute('SELECT S.nombre, S.costo \
                            FROM nota_servicios N \
                            INNER JOIN servicios S \
                            ON N.s_clave = S.s_clave \
                            WHERE N.n_clave = ? ', (folio,))
        detalles = mi_cursor.fetchall()

        
        tabla = PrettyTable()
        tabla.field_names = ["Folio", "Fecha", "Cliente", "RFC del cliente", "Correo del cliente", "Monto"]
        tabla.add_row([folio, fecha, nombre, rfc, correo, monto])

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
\nMenú Principal:
1 - Consulta por período
2 - Consulta por folio
3 - Salir
        """)

        opcion = input("Seleccione una opción: ").strip()
        if opcion == "1":
            while True:
                fecha_inicial_str = input("Fecha inicial (DD/MM/AAAA): ")
                fecha_final_str = input("Fecha final (DD/MM/AAAA): ")

                try:
                    fecha_inicial = datetime.strptime(fecha_inicial_str, "%d/%m/%Y").date()
                    fecha_final = datetime.strptime(fecha_final_str, "%d/%m/%Y").date()
                except ValueError:
                    print("Formato de fecha no válido. Utilice DD/MM/AAAA.")
                    continue
                if fecha_inicial<=fecha_final:
                    consulta_por_periodo(fecha_inicial, fecha_final)
                    return False
                else: 
                    print("La fecha final debe ser igual o posterior a la fecha inicial. Inténte de nuevo.")

        elif opcion == "2":
            folio = int(input("Folio de la nota: "))
            consulta_por_folio(folio)
            return False
        elif opcion == "3":
            print("Saliendo del programa.")
            return False
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
                    rfc = input('Ingrese su RFC (Foramto: AAAA123456AAA): ')
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
            
                mi_cursor.execute("INSERT INTO clientes (nombre, rfc, correo, estado) VALUES (?, ?, ?, ?)",
                                (nombre, rfc, correo, 'guardado'))
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

            if opcion == "1":
                query = "SELECT c_clave, nombre, rfc, correo FROM clientes WHERE estado='guardado' ORDER BY c_clave;"
                filename_pattern = "ReporteClientesActivosPorClave_{}"
            elif opcion == "2": 
                query = "SELECT c_clave, nombre, rfc, correo FROM clientes WHERE estado='guardado' ORDER BY nombre;"
                filename_pattern = "ReporteClientesActivosPorNombre_{}"
            else:
                return
            
            mi_cursor.execute(query)
            clientes = mi_cursor.fetchall()
            
            TablaOrdenado = PrettyTable()
            TablaOrdenado.field_names=["Clave", "Nombre", "RFC", "Correo"]
            for c_clave, nombre, rfc, correo in clientes:
                TablaOrdenado.add_row([c_clave, nombre, rfc, correo])

            print(TablaOrdenado)

            export_option = input("¿Desea exportar el reporte a CSV (1), Excel (2) o regresar al menú de reportes (3)? ")
            if export_option in ("1", "2"):
                fecha = datetime.now().strftime("%d_%m_%Y")
                filename = filename_pattern.format(fecha)

                if export_option == "1":
                    with open(f"{filename}.csv", "w", newline="", encoding="utf-8") as csv_file:
                        csv_writer = csv.writer(csv_file)
                        csv_writer.writerow([i for i in TablaOrdenado.field_names])
                        csv_writer.writerows([row for row in TablaOrdenado._rows])
                    print(f"Reporte exportado exitosamente como {filename}.csv")
                    
                elif export_option == "2":
                    df = pd.DataFrame(TablaOrdenado._rows, columns=TablaOrdenado.field_names)
                    df.to_excel(f"{filename}.xlsx", index=False, engine="openpyxl")
                    print(f"Reporte exportado exitosamente como {filename}.xlsx")

            elif export_option == "3":
                return
            else:
                print("Opción no válida.")

    except Error as e:
        print(e)
    except Exception as ex:
        print(f"Se produjo el siguiente error: {ex}")

def menu_clientes():
    while True:
        print("\n Menú Clientes")
        print("1. Agregar un cliente")
        print("2. Consultas y reportes de clientes")
        print("3. Suspender un cliente")
        print("4. Recuperar un cliente")
        print("5. Volver al menú principal")

        opcion = input("Ingrese su opción: ")

        if opcion == "1":
            agregar_cliente()
        elif opcion == "2":
            menu_consultas_reportes_clientes()
        elif opcion == "3":
            suspender_cliente()
        elif opcion == "4":
            recuperar_cliente()
        elif opcion == "5":
            break
        else:
            print("Opción no válida. Inténtelo de nuevo.")

def suspender_cliente():
    try:
        with sqlite3.connect("Taller_Mecanico.db") as conn:
            mi_cursor = conn.cursor()

            clave=None

            mi_cursor.execute("SELECT c_clave, nombre FROM clientes WHERE estado = 'guardado'")
            clientes_activos = mi_cursor.fetchall()
            clave = clientes_activos[0]
            if clientes_activos:
                print("\nClientes activos:")
                tabla_activos=PrettyTable()
                tabla_activos.field_names=["Clave","Nombre"]
                tabla_activos.add_rows(clientes_activos)
                print(tabla_activos)
            else:
                print("No se encuentran clientes activos.")

            clave_suspender = int(input("Ingrese la clave del cliente que desea suspender (0 para volver al menú): "))

            if clave_suspender == 0:
                print("No se suspendió ningún cliente")
                return

            mi_cursor.execute("SELECT * FROM clientes WHERE c_clave = ?", (clave_suspender,))
            cliente_suspender = mi_cursor.fetchone()

            mi_cursor.execute("SELECT * FROM clientes WHERE c_clave = ?", (clave_suspender,))
            cliente_suspender = mi_cursor.fetchone()

            if cliente_suspender:
                print("\nDatos del cliente seleccionado:")
                tabla = PrettyTable()
                tabla.field_names = ["Clave", "Nombre", "RFC", "Correo", "Estado"]
                tabla.add_row(cliente_suspender)
                print(tabla)

                while True:
                    confirmacion = input("¿Desea suspender a este cliente? (S/N): ").upper()

                    if confirmacion == "S":
                        
                        mi_cursor.execute("UPDATE clientes SET estado = 'cancelado' WHERE c_clave = ?", (clave_suspender,))
                        conn.commit()
                        print("Cliente suspendido exitosamente.")
                        break
                    elif confirmacion == "N":
                        print("Operación cancelada.")
                        return False
                    else:
                        print("Opción no válida. Inténte de nuevo.")
            else:
                print("No se encuntra esa clave.")
                return False
    except Error as e:
        print(e)
    except Exception as ex:
        print(f"Se produjo el siguiente error: {ex}")

def recuperar_cliente():
    try:
        with sqlite3.connect("Taller_Mecanico.db") as conn:
            mi_cursor = conn.cursor()

            mi_cursor.execute("SELECT c_clave, nombre FROM clientes WHERE estado = 'cancelado'")
            clientes_suspendidos = mi_cursor.fetchall()

            print("\nClientes suspendidos:")
            tabla_suspendidos=PrettyTable()
            tabla_suspendidos.field_names=["Clave","Nombre"]
            tabla_suspendidos.add_rows(clientes_suspendidos)
            print(tabla_suspendidos)


            clave_recuperar = input("Ingrese la clave del cliente que desea recuperar (0 para volver al menú): ")

            if clave_recuperar == "0":
                return  
            
            mi_cursor.execute("SELECT * FROM clientes WHERE c_clave = ?", (clave_recuperar,))
            cliente_recuperar = mi_cursor.fetchone()

            if cliente_recuperar:
                tabla = PrettyTable()
                tabla.field_names = ["Clave", "Nombre", "RFC", "Correo", "Estado"]
                tabla.add_row(cliente_recuperar)
                print(tabla)
            

                while True:
                    confirmacion = input("¿Desea recuperar a este cliente? (S/N): ").upper()
                    if confirmacion == "S":
                        
                        mi_cursor.execute("UPDATE clientes SET estado = 'guardado' WHERE c_clave = ?", (clave_recuperar,))
                        conn.commit()
                        print("Cliente recuperado exitosamente.")
                        break
                    elif confirmacion == "N":
                        print("Operación cancelada.")
                        return False
                    else:
                        print("Opción no válida. Inténte de nuevo.")
            else:
                print("No se encuntra esa clave.")
                return False
    except Error as e:
        print(e)
    except Exception as ex:
        print(f"Se produjo el siguiente error: {ex}")

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
        print("\n Listado de clientes registrados")
        print("1. Ordenado por clave")
        print("2. Ordenado por nombre")
        print("3. Volver al menú anterior")

        opcion = input("Ingrese su opción: ")

        if opcion in ("1", "2"):
            listado_clientes_ordenado(opcion)
        elif opcion == "3":
            break
        else:
            print("Opción no válida. Inténtelo de nuevo.")

def agregar_servicio(cursor):
    while True:
        nombre_servicio = input("Ingrese el nombre del servicio: ")
        if nombre_servicio.strip() == '':
            print("El nombre del servicio no puede quedar vacío.")
        else: 
            break
    while True:
        try:
            costo_servicio = float(input("Ingrese el costo del servicio: "))
        except ValueError:
            print("Solamente se aceptan valores numéricos. Inténtelo de nuevo.")
        if costo_servicio <= 0:
            print("El costo del servicio debe ser superior a 0.00.")
        else:
            cursor.execute("INSERT INTO servicios (nombre, costo, estado) VALUES (?, ?, ?)", (nombre_servicio, costo_servicio, 'guardado'))
            conn.commit()
            nueva_clave = cursor.lastrowid
            print("Servicio agregado con éxito. Clave del servicio:", nueva_clave)
            break
    
def buscar_por_clave(cursor):
    cursor.execute("SELECT s_clave, nombre FROM servicios WHERE estado='guardado'")
    servicios = cursor.fetchall()

    if not servicios:
        print("No hay servicios registrados.")
        return

    print("Listado de servicios:")
    for servicio in servicios:
        print(f"Clave: {servicio[0]}, Nombre: {servicio[1]}")

    while True:
        try:
            clave_servicio = int(input("Ingrese la clave del servicio que desea buscar: "))
            cursor.execute("SELECT nombre, costo FROM servicios WHERE s_clave = ? AND estado= 'guardado' ", (clave_servicio,))
            servicio_encontrado = cursor.fetchone()
            break
        except ValueError:
            print("Solo se aceptan valores númericos.")
        except Error as e:
            print(e)
        except Exception as e:
            print(e)
    if servicio_encontrado:
        nombre, costo = servicio_encontrado
        print(f"Detalle del servicio - Clave: {clave_servicio}, Nombre: {nombre}, Costo: {costo}")
    else:
        print("No se encontró ningún servicio con la clave proporcionada.")
        
def buscar_por_nombre(cursor):
    nombre_buscar = input("Ingrese el nombre del servicio a buscar: ")

    cursor.execute("SELECT s_clave, nombre, costo FROM servicios WHERE lower(nombre) = lower(?) AND estado = 'guardado'", (nombre_buscar,))
    servicios_encontrados = cursor.fetchall()

    if servicios_encontrados:
        print("Servicios encontrados:")
        for servicio in servicios_encontrados:
            clave, nombre, costo = servicio
            print(f"Clave: {clave}, Nombre: {nombre}, Costo: {costo}")
    else:
        print("No se encontraron servicios con el nombre proporcionado.")

def generar_reporte_por_clave(conn):
    while True:
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
                        break
                    elif export_option == "2":
                        exportar_reporte(servicios, "Excel", "ReporteServiciosPorClave")
                        break
                    elif export_option == "3":
                        return
                    else:
                        print("Opción no válida.")
                else:
                    print("No hay servicios registrados.")
                    break
        except sqlite3.Error as e:
            print("Error al generar el reporte:", e)
            break
        
def suspender_servicio(conn, clave_servicio):
    try:
        with conn:
            mi_cursor = conn.cursor()
            mi_cursor.execute("SELECT * FROM servicios WHERE s_clave = ? AND estado = 'guardado'", (clave_servicio,))
            servicio_encontrado = mi_cursor.fetchone()

            if servicio_encontrado:
                print("Detalle del servicio a suspender:")
                print(f"Clave del servicio: {servicio_encontrado[0]}")
                print(f"Nombre del servicio: {servicio_encontrado[1]}")
                print(f"Costo del servicio: {servicio_encontrado[2]}")

                while True:
                    confirmacion = input("¿Desea suspender este servicio? (Sí/No): ").lower()

                    if confirmacion == "si":
                        mi_cursor.execute("UPDATE servicios SET estado = 'Suspendido' WHERE s_clave = ?", (clave_servicio,))
                        print("Servicio suspendido con éxito.")
                        break
                    elif confirmacion == "no":
                        print("Operación cancelada.")
                        break
                    else:
                        print("Opción no válida. Inténtelo de nuevo.")
            else:
                print("No se encontró ningún servicio con la clave proporcionada o el servicio ya está suspendido.")
    except sqlite3.Error as e:
        print("Error al suspender el servicio:", e)

def recuperar_servicio(conn, clave_servicio):
    try:
        with conn:
            mi_cursor = conn.cursor()
            mi_cursor.execute("SELECT * FROM servicios WHERE s_clave = ? AND estado = 'Suspendido'", (clave_servicio,))
            servicio_encontrado = mi_cursor.fetchone()

            if servicio_encontrado:
                print("Detalle del servicio a recuperar:")
                print(f"Clave del servicio: {servicio_encontrado[0]}")
                print(f"Nombre del servicio: {servicio_encontrado[1]}")
                print(f"Costo del servicio: {servicio_encontrado[2]}")

                while True:
                    confirmacion = input("¿Desea recuperar este servicio? (Sí/No): ").lower()

                    if confirmacion == "si":
                        mi_cursor.execute("UPDATE servicios SET estado = 'guardado' WHERE s_clave = ?", (clave_servicio,))
                        print("Servicio recuperado con éxito.")
                        break
                    elif confirmacion == "no":
                        print("Operación cancelada.")
                        break
                    else:
                        print("Opción no válida. Inténtelo de nuevo.")
            else:
                print("No se encontró ningún servicio con la clave proporcionada o el servicio no está suspendido.")
    except sqlite3.Error as e:
        print("Error al recuperar el servicio:", e)

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
                while True:
                    try:
                        export_option = input("¿Desea exportar el reporte a CSV (1), Excel (2) o regresar al menú de reportes (3)? ")
                    except ValueError:
                        print("Opcion no valida, Ingrese una opcion valida.")
                    if export_option == "1":
                        exportar_reporte(servicios, "CSV", "ReporteServiciosPorNombre")
                        break
                    elif export_option == "2":
                        exportar_reporte(servicios, "Excel", "ReporteServiciosPorNombre")
                        break
                    elif export_option == "3":
                        return
                    else:
                        print("Opción no válida.")
            else:
                print("No hay servicios registrados.")
    except sqlite3.Error as e:
        print("Error al generar el reporte:", e)

def exportar_reporte(servicios, formato, nombre_reporte):
    try:
        fecha_reporte = datetime.now().strftime("%d_%m_%Y")
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
    except Exception as e:
        print(f"Error al exportar el reporte: {e}")

def menu_reportes(cursor):
    while True:
        print("\nOpciones de consulta y reportes:")
        print("1. Búsqueda por clave de servicio")
        print("2. Búsqueda por nombre de servicio")
        print("3. Listado de servicios")
        print("4. Volver al menú de servicios")
        try:
            opcion_reporte = int(input("Seleccione una opción: "))
        except ValueError:
            print("Opcion no valida, Ingrese una opcion valida.")
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
        print("\nOpciones de listado de servicios:")
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

def suspender_servicio_menu(conn,):
    try:
        with conn:
            mi_cursor = conn.cursor()
            mi_cursor.execute("SELECT s_clave, nombre FROM servicios WHERE estado = 'guardado'")
            servicios_activos = mi_cursor.fetchall()

            if not servicios_activos:
                print("No hay servicios activos para suspender.")
                return
            while True:
                print("Servicios activos:")
                print("Clave\tNombre")
                for servicio in servicios_activos:
                    print(f"{servicio[0]}\t{servicio[1]}")

                clave_servicio = input("Ingrese la clave del servicio que desea suspender (0 para regresar): ")

                try:
                    clave_servicio = int(clave_servicio)
                except ValueError:
                    print("Clave no válida. Ingrese un número válido.")
                    continue

                if clave_servicio == 0:
                    print("Volviendo al menú principal.")
                    break
                elif any(servicio[0] == clave_servicio for servicio in servicios_activos):
                    suspender_servicio(conn, clave_servicio)
                    break
                else:
                    print("Clave no válida. Ingrese una clave de servicio activo.")
    except sqlite3.Error as e:
        print("Error al suspender el servicio:", e)

def recuperar_servicio_menu(conn):
    try:
        with conn:
            mi_cursor = conn.cursor()
            mi_cursor.execute("SELECT s_clave, nombre FROM servicios WHERE estado = 'Suspendido'")
            servicios_suspendidos = mi_cursor.fetchall()

            if not servicios_suspendidos:
                print("No hay servicios suspendidos para recuperar.")
                return
            while True:
                print("Servicios suspendidos:")
                print("Clave\tNombre")
                for servicio in servicios_suspendidos:
                    print(f"{servicio[0]}\t{servicio[1]}")
            
                clave_servicio = input("Ingrese la clave del servicio que desea recuperar (0 para regresar): ")

                try:
                    clave_servicio = int(clave_servicio)
                except ValueError:
                    print("Clave no válida. Ingrese un número válido.")
                    break

                if clave_servicio == 0:
                    print("Volviendo al menú principal.")
                    break
                elif any(servicio[0] == clave_servicio for servicio in servicios_suspendidos):
                    recuperar_servicio(conn, clave_servicio)
                    break
                else:
                    print("Clave no válida. Ingrese una clave de servicio suspendido.")
    except sqlite3.Error as e:
        print("Error al recuperar el servicio:", e)

def Servicios():
    try:
        with sqlite3.connect("Taller_Mecanico.db") as conn:
            mi_cursor = conn.cursor()

            while True:
                print("Menú principal:")
                print("1. Agregar un servicio")
                print("2. Suspender un servicio")
                print("3. Recuperar un servicio")
                print("4. Consultas y reportes")
                print("5. Volver al Menu Principal")
                try:    
                    opcion = int(input("Seleccione una opción: "))
                except ValueError:
                    print("Opcion no valida, Ingrese una opcion valida.")
                    continue
                if opcion == 1:
                    agregar_servicio(mi_cursor)
                elif opcion == 2:
                    suspender_servicio_menu(conn)
                elif opcion == 3:
                    recuperar_servicio_menu(conn)
                elif opcion == 4:
                    menu_reportes(mi_cursor)
                elif opcion == 5:
                    print("Volviendo al Menu Principal.")
                    break
                else:
                    print("Opción no válida, Ingrese una opcion valida.")
    except sqlite3.Error as e:
        print("Error de base de datos:", e)
        
def servicios_mas_prestados():
   while True: 
        try:
            cantidad_servicios = int(input("Ingrese la cantidad de servicios más prestados a identificar: "))
            fecha_inicial_str = input("Ingrese la fecha inicial del período a reportar (dd/mm/aaaa): ")
            fecha_inicial = datetime.strptime(fecha_inicial_str, "%d/%m/%Y").date()
            fecha_final_str = input("Ingrese la fecha final del período a reportar (dd/mm/aaaa): ")
            fecha_final = datetime.strptime(fecha_final_str, "%d/%m/%Y").date()

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
                tabla2 = PrettyTable()
                tabla2.field_names = ["Nombre del Servicio", "Cantidad Prestada"]
                for row in result:
                    tabla2.add_row([row[0], row[1]])
                
                print(tabla2)

                
                export_option = input("\n¿Desea exportar el reporte a CSV o Excel? (Ingrese 'csv' o 'excel', o cualquier otra tecla para omitir): ").lower()
                if export_option in ['csv', 'excel']:
                    filename = f"ReporteServiciosMasPrestados_{fecha_inicial.strftime('%d%m%Y')}_{fecha_final.strftime('%d%m%Y')}.{export_option}"
                    df = pd.DataFrame(result, columns=["Nombre del Servicio", "Cantidad Prestada"])
                    if export_option == 'csv':
                        df.to_csv(filename, index=False)
                        print(f"El reporte ha sido exportado como '{filename}'.")
                        break
                    elif export_option== "excel":
                        df.to_excel(f"{filename}.xlsx", index=False, engine="openpyxl")
                        print(f"El reporte ha sido exportado como '{filename}'.")
                        break    

        except ValueError as e:
            print("Error:", e)
        
def clientes_con_mas_notas():
    try:
        cantidad_clientes = int(input("Ingrese la cantidad de clientes con más notas a identificar: "))
        fecha_inicial_str = input("Ingrese la fecha inicial del período a reportar (dd/mm/aaaa): ")
        fecha_inicial = datetime.strptime(fecha_inicial_str, "%d/%m/%Y").date()
        fecha_final_str = input("Ingrese la fecha final del período a reportar (dd/mm/aaaa): ")
        fecha_final = datetime.strptime(fecha_final_str, "%d/%m/%Y")

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
            clientenotas = PrettyTable()
            clientenotas.field_names = ["Nombre del Cliente", 'Cantidad de Notas']
            for row in result:
                clientenotas.add_row([row[0], row[1]])
            print(clientenotas)

            export_option = input("\n¿Desea exportar el reporte a CSV o Excel? (Ingrese 'csv' o 'excel', o cualquier otra tecla para omitir): ").lower()
            if export_option in ['csv', 'excel']:
                filename = f"ClientesConMasNotas_{fecha_inicial.strftime('%d%m%Y')}_{fecha_final.strftime('%d%m%Y')}.{export_option}"
                df = pd.DataFrame(result, columns=["Nombre del Servicio", "Cantidad Prestada"])
                if export_option == 'csv':
                    df.to_csv(filename, index=False)
                elif export_option == 'excel':
                    df.to_excel(f"{filename}.xlsx", index=False, engine="openpyxl")
                print(f"El reporte ha sido exportado como '{filename}'.")

    except ValueError:
        print("Error: Ingrese un valor válido para la cantidad de servicios.")
    
        
def prom_montos(conn):
    while True:
        fecha_inicio_p = input("Ingrese la fecha inicial (DD/MM/YYYY): ")
        fecha_final_p = input("Ingrese la fecha final (DD/MM/YYYY): ")
        try:
            fecha_inicio = datetime.strptime(fecha_inicio_p, '%d/%m/%Y').date()
            fecha_final = datetime.strptime(fecha_final_p, '%d/%m/%Y').date()
            
            if fecha_final <= fecha_inicio:
                print("La fecha final debe ser por lo menos igual a la fecha inicial del período.")
            else:
                break
        except Exception as e:
            print(e)
            
    try:
        conn = sqlite3.connect("Taller_Mecanico.db")
        mi_cursor = conn.cursor()
        valores = (fecha_inicio, fecha_final)
        mi_cursor.execute("SELECT AVG(monto) FROM notas WHERE fecha BETWEEN ? AND ?", valores)
        promedio = mi_cursor.fetchall()
        
        if promedio:
            Tabla_prom = PrettyTable()
            Tabla_prom.field_names = ["Promedio de notas"]
            Tabla_prom.add_row (promedio)
            print(Tabla_prom)
            return False
        else:
            print("No se encontraron notas en ese periodo.")
            return False
    except Error as e:
        print(e)
        return False
    except Exception:
        print(f"Se produjo el siguiente error: {sys.exc_info()[0]}")
        return False
    finally:
        conn.close()
        
        
def estadisticas(conn):
    while True:
        print('''
\n== Estadísticas ==
1. Servicios más prestados
2. Clientes con más notas    
3. Promedio de los montos de las notas 
4. Volver al Menú
    ''')
        op = input("Seleccione la opción que desee: ")
        
        if op == '1':
            servicios_mas_prestados()
        elif op == '2':
            clientes_con_mas_notas()
        elif op == '3':
            prom_montos(conn)
            break
        elif op == '4':
            return False
        else:
            print("Opción no válida.")

def menu_principal():
    conn = sqlite3.connect("Taller_Mecanico.db")
    
    while True:
        print("\n=== Menú Principal ===")
        print("1. Menú Notas")
        print("2. Menú Clientes")
        print("3. Menú Servicios")
        print("4. Estadísticas")
        print("5. Salir")

        opcion = input("Seleccione una opción: ")

        if opcion == '1':
            menu_notas(conn)
        elif opcion == '2':
            menu_clientes()
        elif opcion == '3':
            Servicios()
        elif opcion == '4':
            estadisticas(conn)
        elif opcion == '5':
            confirmacion = input("¿Está seguro que desea salir? (Si/No): ").lower()
            if confirmacion == 'si':
                break
        else:
            print("Opción no válida. Inténtelo de nuevo.")

    conn.close()

menu_principal()