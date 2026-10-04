"""
UNJu - Facultad de Ingeniería
Teoría de Sistemas Operativos (TSO) - Ciclo Lectivo 2026
Cátedra: Ing. María Fernanda Vázquez - JTP: Ing. Fabio D. Argañaraz

Ejercicio Práctico N° 4: Monitores y Variables de Condición
El Barbero Dormilón
"""

import sys
import threading
import time
import random

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')


class BarberiaMonitor:

    def __init__(self, num_sillas_espera=3):
        self.num_sillas = num_sillas_espera
        self.clientes_esperando = 0

        # Cerrojo del monitor
        self.lock = threading.Lock()

        # Variables de condición
        self.cond_barbero = threading.Condition(self.lock)
        self.cond_sala_espera = threading.Condition(self.lock)
        self.cond_corte = threading.Condition(self.lock)

        # Estado de la barbería
        self.silla_barbero_ocupada = False
        self.cliente_listo_en_sillon = False
        self.corte_terminado = False
        self.barberia_abierta = True


    def entrar_cliente(self, cliente_id):

        with self.lock:

            print(
                f"👤 Cliente {cliente_id} llega a la barbería. "
                f"(Sillas ocupadas: {self.clientes_esperando}/{self.num_sillas})"
            )

            # Si la sala está llena, el cliente se va
            if self.clientes_esperando >= self.num_sillas:

                print(
                    f"🚪 [SALA LLENA] Cliente {cliente_id} "
                    f"se va sin cortarse el pelo."
                )

                return False

            # Cliente entra en sala de espera
            self.clientes_esperando += 1

            # Despertar al barbero
            self.cond_barbero.notify()

            # Esperar hasta que el sillón quede libre
            while self.silla_barbero_ocupada:
                self.cond_sala_espera.wait()

            # Cliente pasa al sillón
            self.clientes_esperando -= 1

            self.silla_barbero_ocupada = True
            self.cliente_listo_en_sillon = True
            self.corte_terminado = False

            print(f"💺 Cliente {cliente_id} se sienta en el sillón.")

            # Avisar al barbero
            self.cond_barbero.notify()

            # Esperar a que termine el corte
            while not self.corte_terminado:
                self.cond_corte.wait()

            print(f"✅ Cliente {cliente_id} terminó su corte.")

            # Cliente abandona el sillón
            self.silla_barbero_ocupada = False
            self.cliente_listo_en_sillon = False
            self.corte_terminado = False

            # Avisar al barbero que el sillón quedó libre
            self.cond_barbero.notify()

            # Avisar al siguiente cliente
            self.cond_sala_espera.notify()

            return True


    def atender_siguiente_cliente(self):

        with self.lock:

            # Esperar mientras no haya cliente listo
            while (
                not self.cliente_listo_en_sillon
                and self.barberia_abierta
            ):

                # Si hay clientes esperando,
                # permitir que uno pase al sillón
                if self.clientes_esperando > 0:
                    self.cond_sala_espera.notify()

                # Barbero duerme
                self.cond_barbero.wait()

            # Si la barbería cerró y no hay cliente
            if (
                not self.barberia_abierta
                and not self.cliente_listo_en_sillon
            ):
                return False

            return True


    # Alias pedagógico
    esperar_cliente_para_corte = atender_siguiente_cliente


    def finalizar_corte(self):

        with self.lock:

            # Indicar que terminó el corte
            self.corte_terminado = True

            # Despertar al cliente
            self.cond_corte.notify()

            # Esperar hasta que el cliente
            # abandone el sillón
            while self.silla_barbero_ocupada:
                self.cond_barbero.wait()


    def cerrar_barberia(self):

        with self.lock:

            self.barberia_abierta = False

            # Despertar cualquier hilo bloqueado
            self.cond_barbero.notify_all()
            self.cond_sala_espera.notify_all()
            self.cond_corte.notify_all()


def hilo_barbero(barberia):

    while True:

        hay_cliente = barberia.atender_siguiente_cliente()

        if not hay_cliente:
            break

        print("✂️ [Barbero] Cortando el cabello...")

        time.sleep(random.uniform(0.1, 0.25))

        barberia.finalizar_corte()


def hilo_cliente(barberia, cliente_id):

    time.sleep(random.uniform(0.05, 0.3))

    barberia.entrar_cliente(cliente_id)


if __name__ == "__main__":

    print("=" * 60)
    print(" Barbería con Monitores y Variables de Condición (UNJu FI)")
    print("=" * 60)

    barberia = BarberiaMonitor(num_sillas_espera=3)

    t_barbero = threading.Thread(
        target=hilo_barbero,
        args=(barberia,),
        name="Barbero"
    )

    t_barbero.start()

    # Llegan 8 clientes concurrentemente
    clientes = []

    for i in range(1, 9):

        t_cli = threading.Thread(
            target=hilo_cliente,
            args=(barberia, i),
            name=f"Cliente-{i}"
        )

        clientes.append(t_cli)

        t_cli.start()

    for t_cli in clientes:
        t_cli.join()

    time.sleep(0.5)

    barberia.cerrar_barberia()

    t_barbero.join()

    print("=" * 60)
    print(" Simulación de Barbería finalizada.")
    print("=" * 60)