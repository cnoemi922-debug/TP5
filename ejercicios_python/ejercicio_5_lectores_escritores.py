"""
UNJu - Facultad de Ingeniería
Teoría de Sistemas Operativos (TSO) - Ciclo Lectivo 2026
Cátedra: Ing. María Fernanda Vázquez - JTP: Ing. Fabio D. Argañaraz

Ejercicio Práctico N° 5:
Lectores - Escritores
"""

import sys
import threading
import time
import random

# Configuración UTF-8 para Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


# ============================================================
# VARIABLES COMPARTIDAS Y SEMÁFOROS
# ============================================================

# Protege el contador de lectores
mutex = threading.Semaphore(1)

# Controla el acceso exclusivo de escritores
sem_write = threading.Semaphore(1)

# Cantidad de lectores activos
readcounter = 0


# Base de datos simulada
base_de_datos = {
    "version": 1,
    "contenido": "Datos iniciales consistentes del sistema operativo."
}


# Lock solamente para imprimir ordenadamente
print_lock = threading.Lock()


def log(msg):
    with print_lock:
        print(f"[{time.strftime('%H:%M:%S')}] {msg}")


# ============================================================
# PROCESO LECTOR
# ============================================================

def lector(id_lector, iteraciones=2):
    global readcounter

    for _ in range(iteraciones):

        time.sleep(random.uniform(0.1, 0.4))

        # ----------------------------------------------------
        # ENTRADA DEL LECTOR
        # ----------------------------------------------------

        mutex.acquire()

        readcounter += 1

        # El primer lector bloquea a los escritores
        if readcounter == 1:
            sem_write.acquire()

        mutex.release()


        # ----------------------------------------------------
        # SECCIÓN DE LECTURA
        # Varios lectores pueden leer simultáneamente
        # ----------------------------------------------------

        log(
            f"📖 Lector {id_lector} LEYENDO datos "
            f"(v{base_de_datos['version']}) | "
            f"Lectores activos: {readcounter}"
        )

        time.sleep(random.uniform(0.2, 0.5))

        log(f"✨ Lector {id_lector} terminó de leer.")


        # ----------------------------------------------------
        # SALIDA DEL LECTOR
        # ----------------------------------------------------

        mutex.acquire()

        readcounter -= 1

        # El último lector permite nuevamente escritores
        if readcounter == 0:
            sem_write.release()

        mutex.release()


# ============================================================
# PROCESO ESCRITOR
# ============================================================

def escritor(id_escritor, iteraciones=2):
    global base_de_datos

    for _ in range(iteraciones):

        time.sleep(random.uniform(0.3, 0.7))

        log(
            f"⏳ Escritor {id_escritor} "
            f"solicitando permiso para escribir..."
        )

        # Acceso exclusivo
        sem_write.acquire()

        try:
            # -----------------------------------------------
            # SECCIÓN CRÍTICA DE ESCRITURA
            # -----------------------------------------------

            nueva_version = base_de_datos["version"] + 1

            log(
                f"✍️ [EXCLUSIÓN MUTUA] Escritor "
                f"{id_escritor} MODIFICANDO la BD "
                f"a versión {nueva_version}..."
            )

            time.sleep(random.uniform(0.3, 0.6))

            base_de_datos["version"] = nueva_version

            base_de_datos["contenido"] = (
                f"Registro actualizado por escritor "
                f"{id_escritor} a las "
                f"{time.strftime('%H:%M:%S')}"
            )

            log(
                f"✅ Escritor {id_escritor} finalizó "
                f"escritura de versión {nueva_version}."
            )

        finally:
            # Liberar la BD
            sem_write.release()


# ============================================================
# PROGRAMA PRINCIPAL
# ============================================================

if __name__ == "__main__":

    print("=" * 70)
    print("EJERCICIO 5: Lectores y Escritores")
    print("=" * 70)

    hilos = []

    # Crear 5 lectores
    for i in range(1, 6):
        t = threading.Thread(
            target=lector,
            args=(i,)
        )
        hilos.append(t)

    # Crear 2 escritores
    for j in range(1, 3):
        t = threading.Thread(
            target=escritor,
            args=(j,)
        )
        hilos.append(t)

    # Mezclar el orden de inicio
    random.shuffle(hilos)

    # Iniciar todos los hilos
    for t in hilos:
        t.start()

    # Esperar que todos terminen
    for t in hilos:
        t.join()

    print()
    print("=" * 70)
    print("Simulación finalizada.")
    print("Estado final de la BD:")
    print(base_de_datos)
    print("=" * 70)