notas_canceladas = {
    1: "Detalle de la nota 1",
    2: "Detalle de la nota 2",
    3: "Detalle de la nota 3",
}

# Mostrar un listado tabular de las notas canceladas
print("Listado de notas canceladas:")
print("Folio\tDetalle")
for folio, _ in notas_canceladas.items():
    print(f"{folio}\tNota cancelada")

# Pedir al usuario que indique el folio de la nota que desea recuperar
folio_deseado = int(input("Indique el folio de la nota que desea recuperar (0 para no recuperar ninguna): "))

# Verificar si el usuario desea recuperar una nota
if folio_deseado == 0:
    print("No se ha recuperado ninguna nota.")
else:
    # Verificar si el folio indicado existe en el diccionario de notas canceladas
    if folio_deseado in notas_canceladas:
        # Mostrar el detalle de la nota y pedir confirmación
        detalle_nota = notas_canceladas[folio_deseado]
        print(f"Detalle de la nota {folio_deseado}: {detalle_nota}")
        confirmacion = input("¿Desea recuperar esta nota? (Sí/No): ").lower()

        # Verificar la confirmación del usuario
        if confirmacion == "si":
            print("La nota ha sido recuperada con éxito.")
        else:
            print("La nota no ha sido recuperada.")
    else:
        print("El folio indicado no corresponde a ninguna nota cancelada.")