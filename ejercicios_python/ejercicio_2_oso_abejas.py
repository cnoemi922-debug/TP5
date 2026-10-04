import sys
import threading
import time
import random

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

M = 10
NUM_ABEJAS = 5
tarro_miel = 0
simulacion_activa = True

# Mecanismos de sincronización
mutex = threading.Lock()
sem_oso = threading.Semaphore(0)
sem_tarro_disponible = threading.Semaphore(1)


def abeja(id_abeja):
    global tarro_miel, simulacion_activa

    while simulacion_activa:
        time.sleep(random.uniform(0.05, 0.2))

        # Esperar hasta que el tarro esté disponible
        sem_tarro_disponible.acquire()

        if not simulacion_activa:
            sem_tarro_disponible.release()
            break

        with mutex:
            tarro_miel += 1
            print(f"Abeja {id_abeja} agrega miel: {tarro_miel}/{M}")

            if tarro_miel == M:
                print("Tarro lleno -> despertando al oso")
                sem_oso.release()
                # No liberar sem_tarro_disponible:
                # el oso debe vaciar el tarro primero
            else:
                sem_tarro_disponible.release()


def oso(max_tarros=2):
    global tarro_miel, simulacion_activa

    tarros_comidos = 0

    while tarros_comidos < max_tarros and simulacion_activa:

        # Dormir hasta que el tarro esté lleno
        sem_oso.acquire()

        with mutex:
            print(f"Oso despierta y come {tarro_miel} porciones de miel")
            tarro_miel = 0
            tarros_comidos += 1

        # El tarro vuelve a estar disponible
        sem_tarro_disponible.release()
        time.sleep(0.05)

    simulacion_activa = False

    # Desbloquear posibles abejas esperando
    sem_tarro_disponible.release()


if __name__ == "__main__":
    print("=" * 60)
    print("Iniciando Simulación: El Oso y las Abejas")
    print("=" * 60)

    hilo_oso = threading.Thread(target=oso, args=(2,))
    hilos_abejas = [
        threading.Thread(target=abeja, args=(i,), daemon=True)
        for i in range(1, NUM_ABEJAS + 1)
    ]

    hilo_oso.start()

    for hilo in hilos_abejas:
        hilo.start()

    hilo_oso.join()

    print("Simulación terminada correctamente.")