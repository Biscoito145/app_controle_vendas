from botoes import ImageButton, LabelButton
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Color, Rectangle
import requests
from kivy.app import App
from functools import partial


class BannerVendedor(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__()

        with self.canvas:
            Color(rgb=(0, 0, 0, 1))
            self.rec = Rectangle(size=self.size, pos=self.pos)
        self.bind(pos=self.atualizar_rec, size=self.atualizar_rec)

        id_vendededor = kwargs['id_vendededor']

        link = f'https://appvendas-7f3af-default-rtdb.firebaseio.com/.json?orderBy="id_vendededor"&equalTo="{id_vendededor}"'
        r = requests.get(link)
        r_dic = r.json()
        valor = list(r_dic.values())[0]
        avatar = valor['avatar']
        total_vendas = valor['total_vendas']

        meu_aplicativo = App.get_running_app()
        imagem = ImageButton(source=f"icones/fotos_perfil/{avatar}", size_hint=(0.3, 0.8), pos_hint={"right": 0.4, "top": 0.9}, on_release=partial(meu_aplicativo.carregar_veendas_vendedor, valor))
        label_id = LabelButton(text=f'ID Vendedor: {id_vendededor}', size_hint=(0.5, 0.5), pos_hint={"right": 0.9, "top": 0.9}, on_release=partial(meu_aplicativo.carregar_veendas_vendedor, valor))
        label_total_vendas = LabelButton(text=f'Total de Vendas: R${float(total_vendas):.2f}', size_hint=(0.5, 0.5), pos_hint={"right": 0.9, "top": 0.6}, on_release=partial(meu_aplicativo.carregar_veendas_vendedor, valor))

        self.add_widget(imagem)
        self.add_widget(label_id)
        self.add_widget(label_total_vendas)


    def atualizar_rec(self, *args):
        self.rec.pos = self.pos
        self.rec.size = self.size
