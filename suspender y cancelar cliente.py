def suspender_cliente():
    try:
        with sqlite3.connect("Taller_Mecanico.db") as conn:
            mi_cursor = conn.cursor()

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
