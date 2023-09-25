#case 3
            tabla_folios_guardados = PrettyTable()
            tabla_folios_guardados.field_names = ["Folio"]
            for folio_guardado in not_guardada.keys():
                tabla_folios_guardados.add_row([folio_guardado])

            print(tabla_folios_guardados)

            consulta_folio = int(input("Ingrese el número de folio de la nota que desea cancelar: "))
            if consulta_folio in not_guardada:
                datos_guardados = not_guardada[consulta_folio]
                print("Datos de la nota:")
                print(f"Folio: {datos_guardados[0]}")
                print(f"Fecha: {datos_guardados[1]}")
                print(f"Cliente: {datos_guardados[2]}")
                print(f"RFC: {datos_guardados[3]}")
                print(f"Correo: {datos_guardados[4]}")
                print(f"Servicio: {', '.join([f'{servicio}: ${costo:.2f}' for servicio, costo in datos_guardados[5]])}")
                print(f"Monto: ${datos_guardados[6]:.2f}")
                confirmacion = input("¿Está seguro de que desea cancelar esta nota? (SI/NO): ")
                if confirmacion.lower() == "si":
                    del not_guardada[consulta_folio]
                    not_cancel[consulta_folio] = datos_guardados
                    print("Nota cancelada exitosamente.")
                else:
                    print("Cancelación de nota cancelada.")
            else:
                print("\nLa nota no se encuentra en el sistema.")
                break
#pass