import sqlite3
from sqlite3 import Error
import sys

try:
    with sqlite3.connect("Taller_Mecanico.db") as conn:
        mi_cursor = conn.cursor()
        mi_cursor.execute("CREATE TABLE IF NOT EXISTS clientes \
            (c_clave INTEGER PRIMARY KEY, nombre TEXT NOT NULL, rfc TEXT NOT NULL, correo TEXT NOT NULL);")
        
        mi_cursor.execute("CREATE TABLE IF NOT EXISTS notas \
            (n_clave INTEGER PRIMARY KEY, fecha TIMESTAMP NOT NULL, c_clave INTEGER NOT NULL,\
            monto REAL NOT NULL, estado TEXT NOT NULL, FOREIGN KEY(c_clave) REFERENCES clientes(c_clave));")
        
        mi_cursor.execute("CREATE TABLE IF NOT EXISTS servicios \
            (s_clave INTEGER PRIMARY KEY, nombre TEXT NOT NULL, costo INTEGER NOT NULL);")
        
        mi_cursor.execute("CREATE TABLE IF NOT EXISTS detalle_nota \
            (id_detalle INTEGER PRIMARY KEY, n_clave INTEGER NOT NULL, s_clave INTEGER NOT NULL, \
            FOREIGN KEY(n_clave) REFERENCES notas(n_clave),\
            FOREIGN KEY(s_clave) REFERENCES servicios(s_clave))")
        
        print("Tablas creadas exitosamente")
except Error as e:
    print(e)
except Exception:
    print(f"Se produjo el siguiente error: {sys.exc_info()[0]}")