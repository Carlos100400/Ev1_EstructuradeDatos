from prettytable import PrettyTable
import datetime
import re
import csv
import openpyxl

def exportar_a_excel(cliente, notas):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = f"Notas_{cliente}_{datetime.date.today()}"

    ws.append(["Folio", "Fecha", "Cliente", "RFC", "Correo", "Servicio", "Total a Pagar"])

    for folio, fecha, _, rfc, correo, servicios, total_costo in notas:
        ws.append([folio, fecha, cliente, rfc, correo, "\n".join([f"{servicio}: ${costo:.2f}" for servicio, costo in servicios]), f"${total_costo:.2f}"])

    excel_filename = f"{cliente}_{datetime.date.today()}.xlsx"
    wb.save(excel_filename)
    print(f"La información se ha exportado a {excel_filename}")

folios = {}
not_guardada = {}
not_cancel = {}
respuesta2 = ""
regreso = ""

while respuesta2 == '':
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
            opcion = int(input("\nSeleccione la opción que desee (Unicamente números): "))
        except ValueError:
            print("Solamente se aceptan valores numéricos. Inténtelo de nuevo.")
        except Exception:
            print("Opción no válida. Inténtelo de nuevo.")
        else:
            if opcion < 6:
                break
            else:
                print("Solamente se aceptan valores del 1 al 5. Inténtelo de nuevo.")

    match opcion:
        case 1:
            folio = max(folios, default=100) + 1
            folios[folio] = ''

            while True:
                cliente = input('Nombre del cliente: ')
                if cliente.strip():
                    break
                else:
                    print("Inténtelo de nuevo.")

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

            servicios = []
            total_costo = 0.0

            while True:
                servicio = input("Ingrese un servicio (o deje un espacio en blanco para terminar): ")
                if servicio.strip() == "":
                    break
                while True:
                    try:
                        costo = float(input("Ingrese el costo del servicio: "))
                    except ValueError:
                        print('Solamente acepta valores numéricos. Inténtelo de nuevo.')
                    except Exception:
                        print("Dato no válido. Inténtelo de nuevo.")
                    else:
                        if costo > 0:
                            servicios.append((servicio, costo))
                            total_costo += costo
                            break
                        else:
                            print('El precio del servicio tiene que ser mayor a 0.')

            fecha_act = datetime.date.today()
            while True:
                try:
                    while True:
                        fecha_proporcionada = input('Fecha de la nota (dd/mm/aaaa): ')
                        fecha_ing = datetime.datetime.strptime(fecha_proporcionada, "%d/%m/%Y").date()
                        fecha_cliente = fecha_ing.strftime("%d/%m/%Y")
                        if fecha_ing <= fecha_act:
                            break
                        else:
                            print('La fecha no puede ser posterior a la actual del sistema\n')
                except ValueError:
                    print('Tipo de formato no válido. Inténtelo de nuevo\n')
                except Exception as error:
                    print(f'Ocurrió un problema: {error}\n')
                else:
                    break

            datos_guardados = [folio, fecha_cliente, cliente, rfc, correo, servicios, total_costo]

            tabla = PrettyTable()
            tabla.field_names = ['Folio', 'Nombre', 'RFC', 'Correo', 'Fecha', 'Servicio', 'Total a Pagar']
            tabla.add_row([f'{folio}', f'{cliente}', f'{rfc}', f'{correo}', f'{fecha_cliente}',
                           '\n'.join([f"{servicio}: ${costo:.2f}" for servicio, costo in servicios]),
                           f'${total_costo:.2f}'])
            print(tabla)

            while True:
                respuesta = int(input(' Seleccione la opción que desee (1 - Guardar o 2 - Cancelar): '))
                if respuesta == 1:
                    print('*** Nota guardada ***')

                    not_guardada[folio] = datos_guardados

                    break
                elif respuesta == 2:
                    print('*** Nota cancelada ***')
                    not_cancel[folio] = datos_guardados
                    break
                else:
                    print('No se encuentra esa opción. Inténtelo de nuevo.')
        case 2:
            pass
        case 3:
            pass

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
                tabla_detalle_recuperada.add_row(["RFC", datos_guardados[3]])
                tabla_detalle_recuperada.add_row(["Correo", datos_guardados[4]])
                tabla_detalle_recuperada.add_row(["Servicios", ', '.join([f'{servicio}: ${costo:.2f}' for servicio, costo in datos_guardados[5]])])
                tabla_detalle_recuperada.add_row(["Monto", f"${datos_guardados[6]:.2f}"])
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
            pass
        case _:
            print("Seleccione una opción del menú")
    respuesta2 = ""
