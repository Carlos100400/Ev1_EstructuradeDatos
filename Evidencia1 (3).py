from prettytable import PrettyTable
import datetime

folios = {}
not_guardada = {}
not_cancel = {}
respuesta2 = "SI"
notas = {}
nueva_clave = {}

while respuesta2.upper()=="SI" :
      print('''
      Menú Principal
      1 - Registro de nota
      2 - Consultas y reportes
      3 - Cancelar una nota
      4 - Recuperar una nota
      5 - Salir del menú
      ''')
      while True:
            try:
                  opcion=int(input("Seleccione la opción que desee (Unicamente números): "))
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
            servicios = input('Servicios a realizar: ')
            num_serv = servicios.split(',')
            
            while True:
                  try:
                        monto = 0
                        for servicio in servicios.split():
                              monto += float(input('¿Cuál es el precio del servicio?: '))
                  except ValueError:
                        print('Solamente acepta valores numéricos. Inténte de nuevo.')
                  else:
                        if monto > 0:
                              break
                        else:
                              print('El precio del servicio tiene que ser mayor a 0.')
                              
            cliente = input('Nombre del cliente: ')
            
            fecha_act = str (datetime.date.today())
            
            datos_guardados = (fecha_act, cliente, servicios, monto)
            
            tabla = PrettyTable()
            
            tabla.field_names = ['Descripción', 'Datos']
            tabla.add_row(['Folio', f'{folio}'])
            tabla.add_row(['Fecha', f'{fecha_act}'])
            tabla.add_row(['Cliente', f'{cliente}'])
            tabla.add_row(['Monto a pagar', f'{monto}'])
            
            print(tabla)
            
            while True:
                  respuesta = input(' Seleccione la opción que desee (1 - Guardar o 2 - Cancelar): ')
                  if respuesta == "1":
                        print('Nota guardada')
                        not_guardada[folio] = datos_guardados
                        break
                  elif respuesta == "2":
                        print('Nota cancelada')
                        not_cancel[folio] = datos_guardados
                        break
                  else:
                        print('No se encuentra esa opción. Inténte de nuevo.')
                        
      case 2:
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

                    
                match opcion2:
                    case 1:
                        fecha_inicial = input("Ingrese una fecha inicial (YYYY-MM-DD): ")
                        fecha_final = input("Ingrese una fecha final (YYYY-MM-DD): ")
                        fecha_inicial = datetime.datetime.strptime(fecha_inicial, '%Y-%m-%d').date()
                        fecha_final = datetime.datetime.strptime(fecha_final, '%Y-%m-%d').date()

                        if ((fecha_inicial) == (nota_periodo[1]) and (fecha_final) == (nota_periodo[1])):
                            print(f'Notas del {fecha_inicial} al {fecha_final}')
                            

                            nueva_clave = max(not_guardada.keys(), default = 0)
                            not_guardada[nueva_clave] = (folio, fecha_act, cliente, servicios, monto)
                            
                            tabla2 = PrettyTable()
                            tabla2.field_names = ["Clave", "Folio", "Fecha", "Cliente", "Servicio", "Monto"]

                            for clave, (folio, fecha_act, cliente, servicios, monto) in not_guardada.items():
                                tabla2.add_row([clave, folio, fecha_act, cliente, servicios, monto])
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

                    case 3:
                        break
      case 3:
            consulta_folio = int(input("Ingrese el numero de folio de la nota que desea cancelar: "))
            if consulta_folio in not_guardada:
                 datos_guardados = not_guardada[consulta_folio]
                 print("Datos de la nota:")
                 print(f"Folio: {datos_guardados[0]}")
                 print(f"Fecha: {datos_guardados[1]}")
                 print(f"Cliente: {datos_guardados[2]}")
                 print(f"Servicio: {datos_guardados[3]}")
                 print(f"Monto: {datos_guardados[4]}")     
                 while True:
                      confirmacion = input("¿Está seguro de que desea cancelar esta nota? (Si/N0): ")
                      if confirmacion.lower() == "si":
                           del not_guardada[consulta_folio]
                           not_cancel[consulta_folio] = not_guardada
                           print("Nota cancelada exitosamente.")
                           break
                      elif confirmacion.lower() == "no":
                           print("Cancelación de nota cancelada.")
                           break
                      else:
                           print("Opción inválida solo acepta No o Si. Inténtalo nuevamente.")
                           continue
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
                tabla_detalle_recuperada.add_row(["Servicios", datos_guardados[3]])
                tabla_detalle_recuperada.add_row(["Monto", datos_guardados[4]])

                print("Detalle de la nota a recuperar:")
                print(tabla_detalle_recuperada)

                confirmacion = input("¿Está seguro de que desea recuperar esta nota? (Si/No): ")
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
      case _:
            print ("Seleccione una opcion del menú")
  respuesta2 = input("¿Desea regresar al menú principal? SI/NO: ")

