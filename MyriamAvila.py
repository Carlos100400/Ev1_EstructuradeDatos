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
                
def prom_montos(conn):
    while True:
        fecha_inicio_p = input("Ingrese la fecha inicial (DD/MM/YYYY): ")
        fecha_final_p = input("Ingrese la fecha final (DD/MM/YYYY): ")
        try:
            fecha_inicio = datetime.datetime.strptime(fecha_inicio_p, '%d/%m/%Y').date()
            fecha_final = datetime.datetime.strptime(fecha_final_p, '%d/%m/%Y').date()
            
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
