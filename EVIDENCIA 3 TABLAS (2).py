import sqlite3
from sqlite3 import Error
import sys

try:
    with sqlite3.connect("Taller_Mecanico.db") as conn:
        mi_cursor = conn.cursor()
        mi_cursor.execute("CREATE TABLE IF NOT EXISTS clientes \
            (c_clave INTEGER PRIMARY KEY, nombre TEXT NOT NULL, rfc TEXT NOT NULL, correo TEXT NOT NULL, estado TEXT NOT NULL);")
        
        mi_cursor.execute("CREATE TABLE IF NOT EXISTS notas \
            (n_clave INTEGER PRIMARY KEY, fecha TIMESTAMP NOT NULL, c_clave INTEGER NOT NULL,\
            monto REAL NOT NULL, estado TEXT NOT NULL, FOREIGN KEY(c_clave) REFERENCES clientes(c_clave));")
        
        mi_cursor.execute("CREATE TABLE IF NOT EXISTS servicios \
            (s_clave INTEGER PRIMARY KEY, nombre TEXT NOT NULL, costo INTEGER NOT NULL, estado TEXT NOT NULL);") 

        mi_cursor.execute("CREATE TABLE IF NOT EXISTS nota_servicios \
            (id_detalle INTEGER PRIMARY KEY, n_clave INTEGER NOT NULL, s_clave INTEGER NOT NULL, \
            FOREIGN KEY(n_clave) REFERENCES notas(n_clave),\
            FOREIGN KEY(s_clave) REFERENCES servicios(s_clave))")
        
        mi_cursor.execute("INSERT INTO clientes (nombre, rfc, correo, estado) VALUES ('Alberto Díaz Ibarra', 'DIIA021114PKO', 'diaz.alberto@gmail.com', 'guardado');")
        mi_cursor.execute("INSERT INTO clientes (nombre, rfc, correo, estado) VALUES ('Debanhi Ochoa Galindo', 'OOGD991005GVH', 'ochoa.debs@gmail.com', 'guardado');")
        mi_cursor.execute("INSERT INTO clientes (nombre, rfc, correo, estado) VALUES ('Carlos Avila Martinez', 'AIMC030609TFV', 'avila.carlos@gmail.com', 'guardado');")
        
        mi_cursor.execute("INSERT INTO servicios (nombre, costo, estado) VALUES ('Llantas', 200, 'guardado');")
        mi_cursor.execute("INSERT INTO servicios (nombre, costo, estado) VALUES ('Ajuste', 500, 'guardado');")
        mi_cursor.execute("INSERT INTO servicios (nombre, costo, estado) VALUES ('Afinación', 300, 'guardado');")

        
        print("Tablas creadas exitosamente")
except Error as e:
    print(e)
except Exception:
    print(f"Se produjo el siguiente error: {sys.exc_info()[0]}")
    