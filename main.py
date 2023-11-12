import os
from kivy.app import App
from kivy.lang import Builder
from telas import *
from botoes import *
import requests
import certifi
from bannervenda import BannerVenda
from functools import partial
from myfirebase import MyFirebase
from bannervendedor import BannerVendedor
from datetime import datetime
GUI = Builder.load_file('main.kv')

os.environ["SSL_CERT_FILE"] = certifi.where()
class MainApp(App):
    cliente = None
    produto = None
    unidade = None

    def build(self):
        self.firebase = MyFirebase()
        return GUI

    def on_start(self):
        # carregar as informações do usuário
        arquivos = os.listdir("icones/fotos_perfil")

        pagina_foto_perfil = self.root.ids["fotoperfilpage"]
        lista_fotos = pagina_foto_perfil.ids["lista_fotos_perfil"]
        for foto in arquivos:
            imagem = ImageButton(source=f"icones/fotos_perfil/{foto}", on_release=partial(self.mudar_foto_perfil, foto))
            lista_fotos.add_widget(imagem)

        # carregar informações do cliente
        arquivos = os.listdir("icones/fotos_clientes")

        pagina_foto_cliente = self.root.ids["adicionarvendaspage"]
        lista_clientes = pagina_foto_cliente.ids["lista_clientes"]
        for foto in arquivos:
            imagem = ImageButton(source=f"icones/fotos_clientes/{foto}",on_release=partial(self.selecionar_cliente, foto))
            label = LabelButton(text=foto.replace('png', '').capitalize(), on_release=partial(self.selecionar_cliente, foto))
            lista_clientes.add_widget(imagem)
            lista_clientes.add_widget(label)
        # carregar informações do produto
        arquivos = os.listdir("icones/fotos_produtos")

        pagina_foto_produto = self.root.ids["adicionarvendaspage"]
        lista_produtos = pagina_foto_cliente.ids["lista_produtos"]
        for foto in arquivos:
            imagem = ImageButton(source=f"icones/fotos_produtos/{foto}",
                                 on_release=partial(self.selecionar_produto, foto))
            label = LabelButton(text=foto.replace('png', '').capitalize(),
                                on_release=partial(self.selecionar_produto, foto))
            lista_produtos.add_widget(imagem)
            lista_produtos.add_widget(label)

        # carrega as informações do usuario
        self.carregar_info_usuario()

    def carregar_info_usuario(self):
        try:
            with open("refreshtoken.txt", 'r') as arquivo:
                refresh_token = arquivo.read()
            local_id, id_token = self.firebase.trocar_token(refresh_token)
            self.localid = local_id
            self.id_token = id_token

            # pegar informações do usuário
            r = requests.get(f"https://appvendas-7f3af-default-rtdb.firebaseio.com/{self.localid}/.json?auth={self.id_token}")
            dicionario_vendedor = r.json()

            # alterar foto de perfil do usuário
            foto_perfil = self.root.ids['foto_perfil']
            foto_perfil.source = f"icones/fotos_perfil/{dicionario_vendedor['avatar']}"
            self.avatar = dicionario_vendedor['avatar']

            # preencher o id_unci
            id_vendedor = dicionario_vendedor['id_vendededor']
            self.id_vendedor = id_vendedor
            pagina_ajuste = self.root.ids['ajustespage']
            pagina_ajuste.ids['id_vendedor'].text = f"Seu ID Único: {id_vendedor}"

            # preencher as vendsas do usuario
            total_vendas = dicionario_vendedor['total_vendas']
            self.total_vendas = total_vendas
            homepage = self.root.ids['homepage']
            homepage.ids['label_total_vendas'].text = f"[color=#000000]Total de Vendas:[/color] [b]R${total_vendas}[/b]"

            # preencher equipe
            self.equipe = dicionario_vendedor['equipe']
            # preecnher a lista de vendas
            try:
                vendas = dicionario_vendedor['vendas']
                self.vendas = vendas
                pagina_homepage = self.root.ids['homepage']
                lista_vendas = pagina_homepage.ids['lista_vendas']
                for cod_venda in vendas:
                    venda = vendas[cod_venda]
                    banner = BannerVenda(cliente=venda["cliente"],
                                         foto_cliente=venda["foto_ciente"],
                                         produto=venda['produto'],
                                         foto_produto=venda["foto_produto"],
                                         data=venda["data"],
                                         preco=venda["preco"],
                                         unidade=venda["unidade"],
                                         quantidade=venda["quantidade"]
                                         )
                    lista_vendas.add_widget(banner)

            except Exception as error:
                print(error)


            # preecnher equipe vendas
            equipe = dicionario_vendedor['equipe']
            lista_equipe = equipe.split(',')

            pagina_listavendedores = self.root.ids['listarvendedorespage']
            lista_vendedores = pagina_listavendedores.ids['lista_vendedores']

            for id_vendedor_equipe in lista_equipe:
                if id_vendedor_equipe != '':
                    banner_vendedor = BannerVendedor(id_vendededor=id_vendedor_equipe)
                    lista_vendedores.add_widget(banner_vendedor)

            self.mudar_tela("homepage")

        except:
            pass
    def mudar_tela(self, id_tela):
        gerenciador_tela = self.root.ids['screen_manager']
        gerenciador_tela.current = id_tela

    def mudar_foto_perfil(self, foto, *args):
        foto_perfil = self.root.ids['foto_perfil']
        foto_perfil.source = f"icones/fotos_perfil/{foto}"

        info = f'{{"avatar": "{foto}"}}'
        r = requests.patch(f"https://appvendas-7f3af-default-rtdb.firebaseio.com/{self.localid}/.json?auth={self.id_token}", data=str(info))
        self.mudar_tela("ajustespage")

    def adicionar_vendedor(self, id_vendedor_adicionado):
        link = f'https://appvendas-7f3af-default-rtdb.firebaseio.com/.json?orderBy="id_vendededor"&equalTo="{id_vendedor_adicionado}"'
        r = requests.get(link)
        r_dic = r.json()

        pagina_adicionarvendedor = self.root.ids['adicionarvendedorespage']
        mensagem_texto = pagina_adicionarvendedor.ids['mensagem_outrovendedor']

        if r_dic == {}:
            mensagem_texto.text = 'Usuário não encontrado'
        else:
            equipe = self.equipe.split(',')
            if id_vendedor_adicionado in equipe:
                mensagem_texto.text = 'Vendedor já faz parte da equipe'
            else:
                self.equipe = self.equipe + f",{id_vendedor_adicionado}"
                info = f'{{"equipe": "{self.equipe}"}}'
                requests.patch(f"https://appvendas-7f3af-default-rtdb.firebaseio.com/{self.localid}/.json?auth={self.id_token}", data=info)
                mensagem_texto.text = 'Vendedor adicionado com sucesso'
                # adicionar o banner do usuario adicionado
                pagina_listavendedores = self.root.ids['listarvendedorespage']
                lista_vendedores = pagina_listavendedores.ids['lista_vendedores']
                banner_vendedor = BannerVendedor(id_vendededor=id_vendedor_adicionado)
                lista_vendedores.add_widget(banner_vendedor)

    def selecionar_cliente(self, foto, *args):
        # pintar as outras letras de branco
        self.cliente = foto.replace("png", ",")
        pagina_adicionarvendas = self.root.ids["adicionarvendaspage"]
        lista_clientes = pagina_adicionarvendas.ids["lista_clientes"]

        for item in list(lista_clientes.children):
            item.color = (1, 1, 1, 1)
            # pintar de azul a letra do item que selecionamos
            # foto -> carrefour.png / Label -> Carrefour -> carrefour -> carrefour.png
            try:
                texto = item.text
                texto = texto.lower() + "png"
                if foto == texto:
                    item.color = (0, 207 / 255, 219 / 255, 1)
            except:
                pass
    def selecionar_produto(self, foto, *args):
        # pintar as outras letras de branco
        self.produto = foto.replace("png", ",")
        pagina_adicionarvendas = self.root.ids["adicionarvendaspage"]
        lista_produtos = pagina_adicionarvendas.ids["lista_produtos"]

        for item in list(lista_produtos.children):
            item.color = (1, 1, 1, 1)
            # pintar de azul a letra do item que selecionamos
            try:
                texto = item.text
                texto = texto.lower() + "png"
                if foto == texto:
                    item.color = (0, 207 / 255, 219 / 255, 1)
            except:
                pass

    def selecionar_unidade(self, id_label, *args):
        pagina_adicionarvendas = self.root.ids["adicionarvendaspage"]
        self.unidade = id_label.replace("unidades_", "")
        pagina_adicionarvendas.ids["unidades_kg"].color = (1, 1, 1, 1)
        pagina_adicionarvendas.ids["unidades_unidades"].color = (1, 1, 1, 1)
        pagina_adicionarvendas.ids["unidades_litros"].color = (1, 1, 1, 1)

        # pintar o cara selecionado de azul
        pagina_adicionarvendas.ids[id_label].color = (0, 207/255, 219/255, 1)

    def adicionar_venda(self):
        cliente = self.cliente
        produto = self.produto
        unidade = self.unidade


        pagina_adicionar_venda = self.root.ids["adicionarvendaspage"]
        data = pagina_adicionar_venda.ids["label_data"].text.replace("Data: ", "")
        preco = pagina_adicionar_venda.ids["preco_total"].text
        quantidade =pagina_adicionar_venda.ids["quantidade"].text

        if not cliente:
            pagina_adicionar_venda.ids["label_selecione_cliente"].color = (1,0,0,1)
        if not produto:
            pagina_adicionar_venda.ids["label_selecione_produto"].color = (1,0,0,1)
        if not unidade:
            pagina_adicionar_venda.ids["unidades_kg"].color = (1, 0, 0, 1)
            pagina_adicionar_venda.ids["unidades_unidades"].color = (1, 0, 0, 1)
            pagina_adicionar_venda.ids["unidades_litros"].color = (1, 0, 0, 1)
        if not preco:
            pagina_adicionar_venda.ids["label_preco"].color = (1, 0, 0, 1)
        else:
            try:
                preco = float(preco)
            except:
                pagina_adicionar_venda.ids["label_preco"].color = (1, 0, 0, 1)
        if not quantidade:
            pagina_adicionar_venda.ids["label_quantidade"].color = (1, 0, 0, 1)
        else:
            try:
                quantidade = float(quantidade)
            except:
                pagina_adicionar_venda.ids["label_quantidade"].color = (1, 0, 0, 1)
        # dado que ele preencheu todos os campos temos que adicionnar a venda no banco de dados e adicionar o banner de venda
        if cliente and produto and unidade and preco and quantidade and (type(preco)  == float) and (type(quantidade)  == float):
            produto = produto.replace(',','')
            cliente = cliente.replace(',', '')
            foto_produto = produto + "png"
            foto_cliente = cliente + "png"
            info = f'{{"cliente": "{cliente}", "produto": "{produto}", "foto_ciente": "{foto_cliente}", "foto_produto": "{foto_produto}", "data": "{data}", "unidade": "{unidade}", "preco": "{preco}", "quantidade": "{quantidade}" }}'

            requests.post(f"https://appvendas-7f3af-default-rtdb.firebaseio.com/{self.localid}/vendas.json?auth={self.id_token}", data=info)

            banner = BannerVenda(cliente=cliente,
                                 foto_cliente= foto_cliente,
                                 produto= produto,
                                 foto_produto= foto_produto,
                                 data= data,
                                 preco= preco,
                                 unidade= unidade,
                                 quantidade= quantidade,
                                 )
            pagina_homepage = self.root.ids['homepage']
            lista_vendas = pagina_homepage.ids['lista_vendas']
            lista_vendas.add_widget(banner)


            requisicao = requests.get(f"https://appvendas-7f3af-default-rtdb.firebaseio.com/{self.localid}/total_vendas.json?auth={self.id_token}")
            print(self.localid)
            print(requisicao.json())
            total_vendas = requisicao.json()
            total_vendas = float(total_vendas)
            total_vendas += preco
            info = f'{{"total_vendas": "{total_vendas}"}}'
            requests.patch(f"https://appvendas-7f3af-default-rtdb.firebaseio.com/{self.localid}.json?auth={self.id_token}", data=info)
            homepage = self.root.ids['homepage']
            homepage.ids['label_total_vendas'].text = f"[color=#000000]Total de Vendas:[/color] [b]R${total_vendas}[/b]"
            self.mudar_tela("homepage")


        self.cliente = None
        self.produto = None
        self.unidade = None

    def carregar_todas_vendas(self):
        pagina_todasvendas = self.root.ids["todasvendaspage"]
        lista_vendas =pagina_todasvendas.ids["lista_vendas"]

        for item in list(lista_vendas.children):
            lista_vendas.remove_widget(item)
        # preencher a pagina todasvendaspage

        # pegar informações do usuário
        r = requests.get(f'https://appvendas-7f3af-default-rtdb.firebaseio.com/.json?orderBy="id_vendededor"')
        dicionario_vendedor = r.json()
        print(dicionario_vendedor)

        # alterar foto de perfil do usuário
        foto_perfil = self.root.ids['foto_perfil']
        foto_perfil.source = f"icones/fotos_perfil/hash.png"

        total_vendas = 0
        for local_id_usuario in dicionario_vendedor:
            try:
                vendas = dicionario_vendedor[local_id_usuario]["vendas"]
                for id_vendas in vendas:
                   venda =  vendas[id_vendas]
                   total_vendas += float(venda["preco"])
                   banner = BannerVenda(cliente=venda["cliente"],
                                        foto_cliente=venda["foto_ciente"],
                                        produto=venda["produto"],
                                        foto_produto=venda["foto_produto"],
                                        data=venda["data"],
                                        preco=venda["preco"],
                                        unidade=venda["unidade"],
                                        quantidade=venda["quantidade"],
                                        )
                   lista_vendas.add_widget(banner)
            except:
                pass
        pagina_todasvendas.ids['label_total_vendas'].text = f"[color=#000000]Total de Vendas:[/color] [b]R${total_vendas}[/b]"



        # redirecionar para pagina todasvendas
        self.mudar_tela("todasvendaspage")

    def sair_todas_vendas(self, id_tela):
        foto_perfil = self.root.ids['foto_perfil']
        foto_perfil.source = f"icones/fotos_perfil/{self.avatar}"

        self.mudar_tela(id_tela)

    def carregar_veendas_vendedor(self, dic_info_vendededor, *args):
        pagina_vendasoutrovendedorpage = self.root.ids["vendasoutrovendedorpage"]
        lista_vendas =pagina_vendasoutrovendedorpage.ids["lista_vendas"]
        total_vendas = dic_info_vendededor["total_vendas"]
        pagina_vendasoutrovendedorpage.ids['label_total_vendas'].text = f"[color=#000000]Total de Vendas:[/color] [b]R${total_vendas}[/b]"

        try:
            vendas = dic_info_vendededor["vendas"]

            for item in list(lista_vendas.children):
                lista_vendas.remove_widget(item)

            for id_vendas in vendas:
               venda =  vendas[id_vendas]
               banner = BannerVenda(cliente=venda["cliente"],
                                    foto_cliente=venda["foto_ciente"],
                                    produto=venda["produto"],
                                    foto_produto=venda["foto_produto"],
                                    data=venda["data"],
                                    preco=venda["preco"],
                                    unidade=venda["unidade"],
                                    quantidade=venda["quantidade"],
                                    )
               lista_vendas.add_widget(banner)
        except:
            pass

        foto_perfil = self.root.ids['foto_perfil']
        foto_perfil.source = f"icones/fotos_perfil/{dic_info_vendededor['avatar']}"

        self.mudar_tela("vendasoutrovendedorpage")

    def ajustar_data(self):
        data = datetime.now()
        data = data.strftime("%d/%m/%Y")
        pagina_adicionarvendedorespage = self.root.ids["adicionarvendaspage"]
        label_data = pagina_adicionarvendedorespage.ids["label_data"]
        label_data.text = f"Data: {data}"

    def adicionar_venda_data(self):
        self.ajustar_data()
        self.mudar_tela("adicionarvendaspage")


MainApp().run()
