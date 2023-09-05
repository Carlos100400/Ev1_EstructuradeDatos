from prettytable import PrettyTable
import datetime

folios = {}
not_guardada = {}
not_cancel = {}

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
        print("caso2")
    case 3:
        print("caso3")
    case 4:
        print("caso4")
    case 5:
        print("Gracias por su preferencia. Vuelva pronto.")