import socket

HOST        = '127.0.0.1'
PORT        = 9999
BUFFER_SIZE = 1024


class Stare:
    def __init__(self):
        self.clienti = set()
        self.mesaje = {}
        self.urmator_id = 1

    def este_conectat(self, adresa):
        return adresa in self.clienti

    def conecteaza(self, adresa):
        if adresa in self.clienti:
            return False
        self.clienti.add(adresa)
        return True

    def deconecteaza(self, adresa):
        if adresa not in self.clienti:
            return False
        self.clienti.discard(adresa)
        return True

    def numar_clienti(self):
        return len(self.clienti)

    def publica_mesaj(self, autor, text):
        id_mesaj = self.urmator_id
        self.mesaje[id_mesaj] = (autor, text)
        self.urmator_id += 1
        return id_mesaj

    def sterge_mesaj(self, id_mesaj, autor):
        if id_mesaj not in self.mesaje:
            return 'INEXISTENT'
        if self.mesaje[id_mesaj][0] != autor:
            return 'NEAUTORIZAT'
        del self.mesaje[id_mesaj]
        return 'OK'

    def listeaza_mesaje(self):
        return list(self.mesaje.items())


stare = Stare()

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((HOST, PORT))

print("=" * 50)
print(f"  SERVER UDP pornit pe {HOST}:{PORT}")
print("  Asteptam mesaje de la clienti...")
print("=" * 50)

while True:
    try:
        date_brute, adresa_client = server_socket.recvfrom(BUFFER_SIZE)
        mesaj_primit = date_brute.decode('utf-8').strip()

        parti = mesaj_primit.split(' ', 1)
        comanda = parti[0].upper()
        argumente = parti[1] if len(parti) > 1 else ''

        print(f"\n[PRIMIT] De la {adresa_client}: '{mesaj_primit}'")

        if comanda == 'CONNECT':
            if stare.conecteaza(adresa_client):
                raspuns = f"OK: Conectat cu succes. Clienti activi: {stare.numar_clienti()}"
                print(f"[SERVER] Client nou conectat: {adresa_client}")
            else:
                raspuns = "EROARE: Esti deja conectat la server."

        elif comanda == 'DISCONNECT':
            if stare.deconecteaza(adresa_client):
                raspuns = "OK: Deconectat cu succes. La revedere!"
                print(f"[SERVER] Client deconectat: {adresa_client}")
            else:
                raspuns = "EROARE: Nu esti conectat la server."

        elif comanda in ('PUBLISH', 'DELETE', 'LIST'):
            if not stare.este_conectat(adresa_client):
                raspuns = "EROARE: Trebuie sa fii conectat pentru a folosi aceasta comanda."

            elif comanda == 'PUBLISH':
                if not argumente:
                    raspuns = "EROARE: Mesajul nu poate fi gol."
                else:
                    id_mesaj = stare.publica_mesaj(adresa_client, argumente)
                    raspuns = f"OK: Mesaj publicat cu ID={id_mesaj}"

            elif comanda == 'DELETE':
                try:
                    id_mesaj = int(argumente)
                except ValueError:
                    raspuns = "EROARE: ID-ul trebuie sa fie un numar intreg."
                else:
                    rezultat = stare.sterge_mesaj(id_mesaj, adresa_client)
                    if rezultat == 'INEXISTENT':
                        raspuns = f"EROARE: Nu exista mesaj cu ID={id_mesaj}."
                    elif rezultat == 'NEAUTORIZAT':
                        raspuns = "EROARE: Doar autorul poate sterge propriul mesaj."
                    else:
                        raspuns = f"OK: Mesajul cu ID={id_mesaj} a fost sters."

            else:
                mesaje = stare.listeaza_mesaje()
                if not mesaje:
                    raspuns = "OK: Nu exista mesaje publicate."
                else:
                    linii = [f"ID={id_m}: {text}" for id_m, (_, text) in mesaje]
                    raspuns = "OK:\n" + "\n".join(linii)

        else:
            raspuns = f"EROARE: Comanda '{comanda}' este necunoscuta. Comenzi valide: CONNECT, DISCONNECT, PUBLISH, DELETE, LIST"

        server_socket.sendto(raspuns.encode('utf-8'), adresa_client)
        print(f"[TRIMIS]  Catre {adresa_client}: '{raspuns}'")

    except KeyboardInterrupt:
        print("\n[SERVER] Oprire server...")
        break
    except Exception as e:
        print(f"[EROARE] {e}")

server_socket.close()
print("[SERVER] Socket inchis.")
