import sys
import threading
import time

# Configuración UTF-8 para consola Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# ============================================================================
# PARTE 1: Exclusión Mutua y Ordenamiento sobre Variable Compartida
# ============================================================================

X = 199

# B comienza bloqueado y debe esperar a que A termine
sem_orden_AB = threading.Semaphore(0)


def proceso_A():
    global X
    X = X + 1
    print(f"[Parte 1] Proceso A: X = {X}")

    # Habilita a B
    sem_orden_AB.release()


def proceso_B():
    global X

    # Espera hasta que A haya terminado
    sem_orden_AB.acquire()

    X = X // 10
    print(f"[Parte 1] Proceso B: X = {X}")


# ============================================================================
# PARTE 2: Sincronización de Trazas Estrictas (Secuencia ABCABC)
# ============================================================================

# A comienza habilitado.
# B y C comienzan bloqueados.
sem_sig_A = threading.Semaphore(1)
sem_sig_B = threading.Semaphore(0)
sem_sig_C = threading.Semaphore(0)


def proceso_emisor_A(rondas=3):
    for i in range(rondas):
        sem_sig_A.acquire()

        print(f"[Parte 2] Ronda {i+1} -> 🅰️ Proceso A ejecutando")
        time.sleep(0.1)

        sem_sig_B.release()


def proceso_receptor_B(rondas=3):
    for i in range(rondas):
        sem_sig_B.acquire()

        print(f"[Parte 2] Ronda {i+1} -> 🅱️ Proceso B ejecutando")
        time.sleep(0.1)

        sem_sig_C.release()


def proceso_receptor_C(rondas=3):
    for i in range(rondas):
        sem_sig_C.acquire()

        print(f"[Parte 2] Ronda {i+1} -> 🅲 Proceso C ejecutando")
        time.sleep(0.1)

        sem_sig_A.release()


if __name__ == "__main__":
    print("=" * 60)
    print("EJERCICIO 1 - PARTE 1: Variable Compartida")
    print("=" * 60)

    hA = threading.Thread(target=proceso_A)
    hB = threading.Thread(target=proceso_B)

    hA.start()
    hB.start()

    hA.join()
    hB.join()

    print(f"Valor final de X = {X}")

    print("\n" + "=" * 60)
    print("EJERCICIO 1 - PARTE 2: Secuencia Estricta ABCABC")
    print("=" * 60)

    tA = threading.Thread(target=proceso_emisor_A)
    tB = threading.Thread(target=proceso_receptor_B)
    tC = threading.Thread(target=proceso_receptor_C)

    tA.start()
    tB.start()
    tC.start()

    tA.join()
    tB.join()
    tC.join()