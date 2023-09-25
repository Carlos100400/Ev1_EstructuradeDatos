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

case 5:
            confirmacion = input("¿Está seguro de que desea salir del menú principal? (SI/NO): ")
            if confirmacion.lower() == "si":
                with open("estado_app.csv", "w", newline="") as csv_file:
                    csv_writer = csv.writer(csv_file)
                    for folio, datos in not_guardada.items():
                        csv_writer.writerow([folio, *datos])
                    for folio, datos in not_cancel.items():
                        csv_writer.writerow([folio, *datos])
                print("Estado de la aplicación guardado en 'estado_app.csv'.")
                print("Gracias por su preferencia. Vuelva pronto.")
                break
            else:
                print("Salida del menú principal cancelada.")
        case _:
            print("Seleccione una opción del menú")
    respuesta2 = ""
            
