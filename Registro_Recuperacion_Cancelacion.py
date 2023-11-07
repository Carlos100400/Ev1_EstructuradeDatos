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