from prettytable import PrettyTable
import datetime
import re
folios = {}
nota_cancelada = {}
not_guardada = {}
not_cancel = {}
nota_periodo = {}
respuesta2 = ""
regreso = ""
notas = {}
nueva_clave = {}
detalle_nota = {}
servicios = []
costo1 = []
costo = 0
total_costo = 0

while respuesta2=='':
    print('''
      *** Menú Principal ***
      1 - Registro de nota
      2 - Consultas y reportes
      3 - Cancelar una nota
      4 - Recuperar una nota
      5 - Salir del menú
      ''')

    while True:
        try:
            opcion=int(input("\nSeleccione la opción que desee (Unicamente números): "))
        except ValueError:
            print("Solamente se aceptan valores numéricos. Inténte de nuevo")
        except Exception:
            print("Opción no válida. Inténte de nuevo.")
        else:
            if opcion<6:
                break
            else:
                print("Solamente se aceptan valores del 1 al 5. Inténte de nuevo.")

    match opcion:
        case 1:
            folio = max(folios, default=100) + 1
            folios[folio] = ''
            
            while True:
                cliente = input('Nombre del cliente: ')
                if cliente.strip():
                    break
                else:
                    print("Intente de nuevo.")

            while True:
                rfc = input('Ingrese su RFC: ')
    
                if rfc == "":
                    print("El RFC no puede omitirse, inténtalo de nuevo.")
                    continue
    
                if not re.match('^[A-Z]{4}\d{6}[A-Z0-9]{3}$', rfc):
                    print("RFC no válido. Inténtalo de nuevo.")
                    continue
    
                break

            while True:
                correo = input("Ingrese su correo electrónico: ")

                if correo == "":
                    print("El Correo no puede omitirse, inténtalo de nuevo.")
                    continue

                if not re.match('^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', correo):  
                    print("Correo electrónico no válido")
                    continue

                break
            
            while True:
                servicio = input("Ingrese un servicio (o deje un espacio en blanco para terminar): ")
                if servicio.strip() == "":
                    break
                while True:
                    try:
                        costo = float(input("Ingrese el costo del servicio: "))
                    except ValueError:
                        print('Solamente acepta valores numéricos. Inténte de nuevo.')
                    except Exception:
                        print("Dato no válido. Inténte de nuevo.")
                    else:
                        if costo > 0:
                            break
                        else:
                            print('El precio del servicio tiene que ser mayor a 0.')
                servicios.append((servicio,costo)) 

            print("\nLista de servicios y costos:")
            for servicio, costo in servicios:
                print(f"Servicio: {servicio}",f"Costo: ${costo}")
            
            mostrar_costo = [costo[1] for costo in servicios]
            entero=[int(cadena) for cadena in mostrar_costo]
            total_costo=sum(entero)

            fecha_act = datetime.date.today()
            while True:
                try:
                    while True:
                        fecha_proporcionada = input('Fecha de la nota (dd/mm/aaaa): ')
                        fecha_ing = datetime.datetime.strptime(fecha_proporcionada,"%d/%m/%Y").date()
                        fecha_cliente =  fecha_ing.strftime ("%d/%m/%Y")
                        if fecha_ing <= fecha_act:
                                break
                        else:
                            print('La fecha no puede ser posterior a la actual del sistema\n')
                except ValueError:
                    print('Tipo de formato no válido. Intente de nuevo\n')
                except Exception as error:
                    print(f'Ocurrió un problema: {error}\n')
                else:
                    break
            
            mostrar_servicios= [servicio[0] for servicio in servicios]
            datos_guardados = [folio, fecha_cliente, cliente, total_costo]
            datos_guardados.insert(3,mostrar_servicios)

            tabla = PrettyTable()
            tabla.field_names =['Folio', 'Nombre', 'RFC', 'Correo','Fecha', 'Servicio', 'Total a Pagar']
            tabla.add_row([f'{folio}', f'{cliente}', f'{rfc}', f'{correo}', f'{fecha_cliente}',f'{mostrar_servicios}',f'{total_costo}'])
            print(tabla)

            while True:
                respuesta = int(input(' Seleccione la opción que desee (1 - Guardar o 2 - Cancelar): '))
                if respuesta == 1:
                    print('*** Nota guardada ***')

                    not_guardada[folio] = datos_guardados
                    
                    nota_periodo = [folio, fecha_cliente, cliente, [mostrar_servicios], total_costo]
                    
                    break
                elif respuesta == 2:
                    print('*** Nota cancelada ***')
                    not_cancel[folio] = datos_guardados
                    break
                else:
                    print('No se encuentra esa opción. Inténte de nuevo.')
                
        case 2:
            while regreso == "":
                print("Consultas y reportes")
                print("1 - Consular una nota por periodo")
                print("2 - Consultar una nota por folio")
                print("3 - Regresar al menu principal")
                

                while True:
                    try:
                        opcion2=int(input("Seleccione la opción que desee (Unicamente números): "))
                    except ValueError:
                        print("Solamente se aceptan valores numéricos. Inténte de nuevo")
                    except Exception:
                        print("Opción no válida. Inténte de nuevo.")
                    else:
                        if opcion2<=0 or opcion2>3:
                            print("Solamente se aceptan valores del 1 al 3. Inténte de nuevo")
                    break
                if opcion2 == 3:
                    break
    
                while True:
                    match opcion2:
                        case 1:
                            fecha_inicial = input("Ingrese una fecha inicial (DD/MM/YYYY): ")
                            fecha_inicial = datetime.datetime.strptime(fecha_inicial, '%d/%m/%Y').date()
                            fecha_final = input("Ingrese una fecha final (DD/MM/YYYY): ")
                            fecha_final = datetime.datetime.strptime(fecha_final, '%d/%m/%Y').date()
                            
                            fecha_periodo = datetime.datetime.strptime((nota_periodo[1]), '%d/%m/%Y').date()

                            if ((fecha_inicial) <= (fecha_periodo) and (fecha_final) >= (fecha_periodo)):
                                print(f'Notas del {fecha_inicial} al {fecha_final}')
                                

                                nueva_clave = max(not_guardada.keys(), default = 0)
                                not_guardada[nueva_clave] = (folio, fecha_act, cliente, servicios, total_costo)
                                
                                tabla2 = PrettyTable()
                                tabla2.field_names = ["Clave", "Folio", "Fecha", "Cliente", "Servicio", "Costo"]

                                for clave, (folio, fecha_act, cliente, servicios, total_costo) in not_guardada.items():
                                    tabla2.add_row([clave, folio, fecha_act, cliente, servicios, total_costo])
                                    clave=clave+1

                                print(tabla2)
                                break
                                      
                            else:
                                print("No hay notas emitidas para el período especificado.")
                                break

                    
                        case 2:
                            consulta_folio = int(input("Ingrese el folio de la nota que desea consultar: "))
                            if consulta_folio in not_guardada:
                                datos_guardados = not_guardada[consulta_folio]
                                print("Datos de la nota:")
                                print(f"Folio: {datos_guardados[0]}")
                                print(f"Fecha: {datos_guardados[1]}")
                                print(f"Cliente: {datos_guardados[2]}")
                                print(f"Servicio: {datos_guardados[3]}")
                                print(f"Monto: {datos_guardados[4]}")
                            elif consulta_folio in not_cancel:
                                print("Esta nota ha sido cancelada.")
                            else:
                                print("Este folio no se encuentra en el sistema.")
                            break
                regreso = input("Presione ENTER para volver al menú de Subconsultas.")

        case 3:
            tabla_folios_guardados = PrettyTable()
            tabla_folios_guardados.field_names = ["Folio"]
            for folio_guardado in not_guardada.keys():
                tabla_folios_guardados.add_row([folio_guardado])

            print(tabla_folios_guardados)
            
            consulta_folio = int(input("Ingrese el numero de folio de la nota que desea cancelar: "))
            if consulta_folio in not_guardada:
                datos_guardados = not_guardada[consulta_folio]
                print("Datos de la nota:")
                print(f"Folio: {datos_guardados[0]}")
                print(f"Fecha: {datos_guardados[1]}")
                print(f"Cliente: {datos_guardados[2]}")
                print(f"Servicio: {datos_guardados[3]}") #aparece la lista
                print(f"Monto: {datos_guardados[4]}")
                confirmacion = input("¿Está seguro de que desea cancelar esta nota? (SI/N0): ")
                if confirmacion.lower() == "si":
                    del not_guardada[consulta_folio]
                    not_cancel[consulta_folio] = datos_guardados
                    print("Nota cancelada exitosamente.")
                else:
                    print("Cancelación de nota cancelada.")
            else:
                print("\nLa nota no se encuentra en el sistema.")
                break


        case 4:
            print("Recuperar una nota:")
            print("Folios de notas canceladas:")


            tabla_folios_cancelados = PrettyTable()
            tabla_folios_cancelados.field_names = ["Folio"]
            for folio_cancelada in not_cancel.keys():
                tabla_folios_cancelados.add_row([folio_cancelada])

            print(tabla_folios_cancelados)

            consulta_folio = int(input("Ingrese el folio de la nota que desea recuperar (0 para cancelar): "))

            if consulta_folio == 0:
                print("No se recuperó ninguna nota.")
            elif consulta_folio in not_cancel:
                datos_guardados = not_cancel[consulta_folio]

                tabla_detalle_recuperada = PrettyTable()
                tabla_detalle_recuperada.field_names = ["Referencia", "Datos"]
                tabla_detalle_recuperada.add_row(["Folio", datos_guardados[0]])
                tabla_detalle_recuperada.add_row(["Fecha", datos_guardados[1]])
                tabla_detalle_recuperada.add_row(["Cliente", datos_guardados[2]])
                tabla_detalle_recuperada.add_row(["Servicios", datos_guardados[3]]) #aparece la lista
                tabla_detalle_recuperada.add_row(["Monto", datos_guardados[4]])

                print("Detalle de la nota a recuperar:")
                print(tabla_detalle_recuperada)

                confirmacion = input("¿Está seguro de que desea recuperar esta nota? (SI/NO): ")
                if confirmacion.lower() == "si":
                    not_guardada[consulta_folio] = datos_guardados
                    del not_cancel[consulta_folio]
                    print("Nota recuperada exitosamente.")
                else:
                    print("Cancelación de recuperación de nota.")
            else:
                print("El folio ingresado no corresponde a una nota cancelada.")

        case 5:
            print("Gracias por su preferencia. Vuelva pronto.")
            break
        case _:
            print ("Seleccione una opcion del menú")
    respuesta2=""