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
