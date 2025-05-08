import argparse
from server import Server, RemoteServer
from client import Client

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--server', help='Chemin du fichier JSON du serveur local')
    parser.add_argument('--url', help='URL du serveur distant')
    args = parser.parse_args()

    # Vous pouvez indiquer que la variable `server` peut être
    # soit un `RemoteServer` soit un `Server`
    server: RemoteServer | Server
    if args.server:
        print(f"Chargement du serveur local : {args.server}")
        server = Server(args.server)
    elif args.url:
        print(f"Connexion au serveur distant : {args.url}")
        server = RemoteServer(args.url)
    else:
        raise ValueError("Vous devez spécifier un fichier JSON local (--server) ou une URL distante (--url).")

    app = Client(server)
    app.main_menu()
