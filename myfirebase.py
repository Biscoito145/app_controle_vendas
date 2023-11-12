import requests
from kivy.app import App


class MyFirebase:
    API_KEY = "AIzaSyAePtyENwZvHeR-mJrLlEGw0inNpoXzGl0"

    def criar_conta(self, email, senha):
        link = f'https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={self.API_KEY}'

        info = {"email": email,
                "password": senha,
                "returnSecureToken": True}
        r = requests.post(link, data=info)
        r_dic = r.json()
        print(r_dic)

        if r.ok:
            print("Usuario criado")
            refresh_token = r_dic['refreshToken']  # autenticação
            local_id = r_dic['localId']  # man´tem o usuário logado
            id_token = r_dic['idToken']  # id_usuario
            meu_aplicativo = App.get_running_app()
            meu_aplicativo.localid = local_id
            meu_aplicativo.id_token = id_token

            with open("refreshtoken.txt", "w") as arquivo:
                arquivo.write(refresh_token)

            requisicao = requests.get(f"https://appvendas-7f3af-default-rtdb.firebaseio.com/id_prox_vendedeor.json?auth={id_token}")
            id_vendededor = requisicao.json()

            link = f"https://appvendas-7f3af-default-rtdb.firebaseio.com/{local_id}.json?auth={id_token}"
            info_usuario = (f'{{"avatar": "foto1.png", "equipe": "", "total_vendas": 0, "vendas": "", '
                            f'"id_vendededor": "{id_vendededor}"}}')
            requests.patch(link, data=info_usuario)

            # atualizar o proximoo id_vendedeor
            link = (f"https://appvendas-7f3af-default-rtdb.firebaseio.com/.json?auth={id_token}")
            id_prox_vendedeor = int(id_vendededor) + 1
            proximo_id = f'{{"id_prox_vendedeor": "{id_prox_vendedeor}"}}'
            requests.patch(link, data=proximo_id)

            meu_aplicativo.carregar_info_usuario()
            meu_aplicativo.mudar_tela("homepage")

        else:
            mensagem_erro = r_dic["error"]["message"]
            meu_aplicativo = App.get_running_app()
            pagina_login = meu_aplicativo.root.ids["loginpage"]
            pagina_login.ids['mensagem_login'].text = mensagem_erro
            pagina_login.ids['mensagem_login'].color = (1, 0, 0, 1)

    def fazer_login(self, email, senha):
        link = f'https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={self.API_KEY}'

        info = {"email": email,
                "password": senha,
                "returnSecureToken": True}
        r = requests.post(link, data=info)
        r_dic = r.json()
        print(r_dic)

        if r.ok:
            refresh_token = r_dic['refreshToken']  # autenticação
            local_id = r_dic['localId']  # man´tem o usuário logado
            id_token = r_dic['idToken']  # id_usuario
            meu_aplicativo = App.get_running_app()
            meu_aplicativo.localid = local_id
            meu_aplicativo.id_token = id_token

            with open("refreshtoken.txt", "w") as arquivo:
                arquivo.write(refresh_token)

            meu_aplicativo.carregar_info_usuario()
            meu_aplicativo.mudar_tela("homepage")

        else:
            mensagem_erro = r_dic["error"]["message"]
            meu_aplicativo = App.get_running_app()
            pagina_login = meu_aplicativo.root.ids["loginpage"]
            pagina_login.ids['mensagem_login'].text = mensagem_erro
            pagina_login.ids['mensagem_login'].color = (1, 0, 0, 1)

    def trocar_token(self, refresh_token):
        link = f"https://securetoken.googleapis.com/v1/token?key={self.API_KEY}"
        info = {"grant_type": "refresh_token",
                "refresh_token": refresh_token
                }

        r = requests.post(link, data=info)
        r_dic = r.json()
        local_id = r_dic['user_id']
        id_token = r_dic['id_token']
        return local_id, id_token
