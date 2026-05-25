# Código completo corrigido — CAMISAS EDITOR PRO
# =========================================================
# CAMISAS EDITOR PRO
# VERSÃO COMPLETA PROFISSIONAL
# =========================================================

import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import requests
from io import BytesIO
import re
import os
import shutil
import threading

# =========================================================
# CONFIG
# =========================================================

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

APP_COLOR = "#7c3aed"
BG_COLOR = "#070B14"
CARD_COLOR = "#111827"

# =========================================================
# APP
# =========================================================

class CamisasEditor(ctk.CTk):

    def __init__(self):

        super().__init__()

        self.title("CAMISAS EDITOR PRO")

        self.geometry("1600x900")

        self.configure(
            fg_color=BG_COLOR
        )

        self.products = []

        self.js_path = None

        self.original_content = ""

        self.image_cache = {}

        self.grid_columnconfigure(
            1,
            weight=1
        )

        self.grid_rowconfigure(
            0,
            weight=1
        )

        self.create_sidebar()

        self.create_main()

    # =====================================================
    # SIDEBAR
    # =====================================================

    def create_sidebar(self):

        self.sidebar = ctk.CTkFrame(
            self,
            width=250,
            fg_color="#050810",
            corner_radius=0
        )

        self.sidebar.grid(
            row=0,
            column=0,
            sticky="ns"
        )

        self.sidebar.grid_propagate(False)

        logo = ctk.CTkLabel(
            self.sidebar,
            text="⚽ CAMISAS\nEDITOR",
            font=("Arial", 28, "bold"),
            justify="left",
            text_color="white"
        )

        logo.pack(
            anchor="w",
            padx=25,
            pady=(30,20)
        )

        self.import_btn = ctk.CTkButton(
            self.sidebar,
            text="Selecionar products.js",
            height=45,
            corner_radius=12,
            fg_color=APP_COLOR,
            hover_color="#6d28d9",
            command=self.load_js
        )

        self.import_btn.pack(
            fill="x",
            padx=20,
            pady=10
        )

        self.new_btn = ctk.CTkButton(
            self.sidebar,
            text="+ Adicionar Camisa",
            height=45,
            corner_radius=12,
            fg_color="#2563eb",
            hover_color="#1d4ed8",
            command=self.add_product
        )

        self.new_btn.pack(
            fill="x",
            padx=20,
            pady=10
        )

        self.info_label = ctk.CTkLabel(
            self.sidebar,
            text="Nenhum arquivo carregado",
            text_color="gray",
            wraplength=200,
            justify="left"
        )

        self.info_label.pack(
            anchor="w",
            padx=20,
            pady=20
        )

        self.save_btn = ctk.CTkButton(
            self.sidebar,
            text="Salvar Alterações",
            height=50,
            corner_radius=12,
            fg_color="#16a34a",
            hover_color="#15803d",
            command=self.save_js
        )

        self.save_btn.pack(
            side="bottom",
            fill="x",
            padx=20,
            pady=20
        )

    # =====================================================
    # MAIN
    # =====================================================

    def create_main(self):

        self.main = ctk.CTkFrame(
            self,
            fg_color=BG_COLOR
        )

        self.main.grid(
            row=0,
            column=1,
            sticky="nsew"
        )

        self.main.grid_rowconfigure(
            1,
            weight=1
        )

        self.main.grid_columnconfigure(
            0,
            weight=1
        )

        top = ctk.CTkFrame(
            self.main,
            fg_color=BG_COLOR
        )

        top.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=20,
            pady=20
        )

        title = ctk.CTkLabel(
            top,
            text="Todas as Camisas",
            font=("Arial", 32, "bold")
        )

        title.pack(side="left")

        self.search = ctk.CTkEntry(
            top,
            width=350,
            height=45,
            placeholder_text="Buscar camisas..."
        )

        self.search.pack(
            side="right",
            padx=10
        )

        self.search.bind(
            "<KeyRelease>",
            self.filter_products
        )

        self.scroll = ctk.CTkScrollableFrame(
            self.main,
            fg_color=BG_COLOR
        )

        self.scroll.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=15
        )

    # =====================================================
    # FILTRO
    # =====================================================

    def filter_products(self, event=None):

        term = self.search.get().lower()

        filtered = []

        for p in self.products:

            if term in p["name"].lower():

                filtered.append(p)

        self.render_products(filtered)

    # =====================================================
    # DRIVE IMAGE
    # =====================================================

    def convert_drive_link(self, link):

        patterns = [
            r"/d/([a-zA-Z0-9_-]+)",
            r"id=([a-zA-Z0-9_-]+)"
        ]

        for pattern in patterns:

            match = re.search(pattern, link)

            if match:

                file_id = match.group(1)

                return f"https://drive.google.com/thumbnail?id={file_id}&sz=w1200"

        return link

    # =====================================================
    # DRIVE VIDEO
    # =====================================================

    def convert_video_link(self, link):

        patterns = [
            r"/d/([a-zA-Z0-9_-]+)",
            r"id=([a-zA-Z0-9_-]+)"
        ]

        for pattern in patterns:

            match = re.search(pattern, link)

            if match:

                file_id = match.group(1)

                return f"https://drive.google.com/file/d/{file_id}/preview"

        return link

    # =====================================================
    # LOAD JS
    # =====================================================

    def load_js(self):

        path = filedialog.askopenfilename(
            filetypes=[("JavaScript", "*.js")]
        )

        if not path:
            return

        self.js_path = path

        with open(path, "r", encoding="utf-8") as f:

            self.original_content = f.read()

        self.products = self.parse_products(
            self.original_content
        )

        self.info_label.configure(
            text=f"{len(self.products)} camisas carregadas\n\n{os.path.basename(path)}"
        )

        self.render_products()

    # =====================================================
    # PARSER
    # =====================================================

    def parse_products(self, content):

        products = []

        matches = re.finditer(
            r'\{[\s\S]*?\n\}',
            content
        )

        for match in matches:

            block = match.group(0)

            if 'name:' not in block:
                continue

            try:

                name = self.extract(
                    block,
                    'name:"'
                )

                price = self.extract(
                    block,
                    'price:"'
                )

                old_price = self.extract(
                    block,
                    'oldPrice:"'
                )

                promotion = (
                    "promotion:true"
                    in block
                )

                ready = (
                    "ready:true"
                    in block
                )

                category_match = re.search(
                    r'category:(.*?),\n',
                    block,
                    re.S
                )

                category = "brasil"

                if category_match:

                    category_raw = category_match.group(1).strip()

                    if category_raw.startswith("["):

                        category = re.findall(
                            r'"(.*?)"',
                            category_raw
                        )

                    else:

                        category = category_raw.replace(
                            '"',
                            ""
                        )

                sizes_match = re.search(
                    r'sizes:\s*\[(.*?)\]',
                    block,
                    re.S
                )

                sizes = []

                if sizes_match:

                    sizes = re.findall(
                        r'"(.*?)"',
                        sizes_match.group(1)
                    )

                images_block = re.search(
                    r'images:\s*\[(.*?)\]',
                    block,
                    re.S
                )

                images = []

                if images_block:

                    images = re.findall(
                        r'"(.*?)"',
                        images_block.group(1)
                    )

                video = ""

                video_match = re.search(
                    r'video:"(.*?)"',
                    block
                )

                if video_match:

                    video = video_match.group(1)

                products.append({

                    "raw": block,
                    "name": name,
                    "price": price,
                    "old_price": old_price,
                    "promotion": promotion,
                    "ready": ready,
                    "category": category,
                    "sizes": sizes,
                    "images": images,
                    "image": images[0] if images else "",
                    "video": video

                })

            except:
                pass

        return products

    # =====================================================
    # EXTRACT
    # =====================================================

    def extract(self, text, start):

        try:

            part = text.split(start)[1]

            return part.split('"')[0]

        except:

            return ""

    # =====================================================
    # RENDER
    # =====================================================

    def render_products(self, products=None):

        if products is None:
            products = self.products

        for w in self.scroll.winfo_children():
            w.destroy()

        row = 0
        col = 0

        for product in products:

            card = self.create_card(
                self.scroll,
                product
            )

            card.grid(
                row=row,
                column=col,
                padx=12,
                pady=12,
                sticky="n"
            )

            col += 1

            if col >= 4:

                col = 0

                row += 1

    # =====================================================
    # CARD
    # =====================================================

    def create_card(self, parent, product):

        card = ctk.CTkFrame(
            parent,
            width=280,
            height=500,
            fg_color=CARD_COLOR,
            corner_radius=18
        )

        card.grid_propagate(False)

        img_label = ctk.CTkLabel(
            card,
            text=""
        )

        img_label.pack(pady=15)

        def load_image():

            try:

                if product["image"] in self.image_cache:

                    photo = self.image_cache[
                        product["image"]
                    ]

                else:

                    response = requests.get(
                        product["image"],
                        timeout=3
                    )

                    image = Image.open(
                        BytesIO(response.content)
                    )

                    image = image.resize((220,220))

                    photo = ImageTk.PhotoImage(image)

                    self.image_cache[
                        product["image"]
                    ] = photo

                img_label.configure(image=photo)

                img_label.image = photo

            except:
                pass

        threading.Thread(
            target=load_image,
            daemon=True
        ).start()

        name = ctk.CTkLabel(
            card,
            text=product["name"],
            font=("Arial", 20, "bold")
        )

        name.pack(
            anchor="w",
            padx=20
        )

        prices = ctk.CTkFrame(
            card,
            fg_color="transparent"
        )

        prices.pack(
            fill="x",
            padx=20,
            pady=10
        )

        normal = ctk.CTkLabel(
            prices,
            text=product["old_price"],
            text_color="gray"
        )

        normal.pack(anchor="w")

        promo = ctk.CTkLabel(
            prices,
            text=product["price"],
            text_color="#ef4444",
            font=("Arial", 24, "bold")
        )

        promo.pack(anchor="w")

        sizes_text = ", ".join(product["sizes"])

        size_label = ctk.CTkLabel(
            card,
            text=f"Tamanhos: {sizes_text}",
            text_color="#9ca3af"
        )

        size_label.pack(
            anchor="w",
            padx=20,
            pady=(0,10)
        )

        status = (
            "🔥 PROMOÇÃO"
            if product["promotion"]
            else "NORMAL"
        )

        st = ctk.CTkLabel(
            card,
            text=status,
            text_color=APP_COLOR
        )

        st.pack(
            anchor="w",
            padx=20
        )

        promo_switch = ctk.CTkSwitch(
            card,
            text="Promoção",
            progress_color=APP_COLOR
        )

        promo_switch.pack(
            anchor="w",
            padx=20
        )

        if product["promotion"]:
            promo_switch.select()

        def toggle_promo():

            product["promotion"] = (
                promo_switch.get() == 1
            )

            st.configure(
                text="🔥 PROMOÇÃO"
                if product["promotion"]
                else "NORMAL"
            )

        promo_switch.configure(
            command=toggle_promo
        )

        actions = ctk.CTkFrame(
            card,
            fg_color="transparent"
        )

        actions.pack(
            side="bottom",
            fill="x",
            padx=15,
            pady=15
        )

        edit_btn = ctk.CTkButton(
            actions,
            text="Editar",
            width=110,
            fg_color=APP_COLOR,
            command=lambda p=product:
            self.edit_product(p)
        )

        edit_btn.pack(
            side="left",
            padx=5
        )

        delete_btn = ctk.CTkButton(
            actions,
            text="Excluir",
            width=110,
            fg_color="#dc2626",
            hover_color="#991b1b",
            command=lambda p=product:
            self.delete_product(p)
        )

        delete_btn.pack(
            side="right",
            padx=5
        )

        return card

    # =====================================================
    # DELETE
    # =====================================================

    def delete_product(self, product):

        confirm = messagebox.askyesno(
            "Excluir",
            f'Deseja excluir "{product["name"]}" ?'
        )

        if not confirm:
            return

        self.products.remove(product)

        self.render_products()

    # =====================================================
    # ADD PRODUCT
    # =====================================================

    def add_product(self):

        new_product = {

            "raw": "",
            "name": "NOVA CAMISA",
            "price": "R$120",
            "old_price": "R$150",
            "promotion": True,
            "ready": False,
            "category": "brasil",
            "sizes": ["P"],
            "images": [],
            "image": "",
            "video": ""
        }

        self.products.append(
            new_product
        )

        self.render_products()

        self.edit_product(new_product)

    # =====================================================
    # EDIT CORRIGIDO
    # =====================================================

    def edit_product(self, product):

        win = ctk.CTkToplevel(self)

        win.geometry("820x720")

        win.title("Editar Camisa")

        win.configure(
            fg_color=BG_COLOR
        )

        win.grid_rowconfigure(0, weight=1)
        win.grid_columnconfigure(0, weight=1)

        scroll = ctk.CTkScrollableFrame(
            win,
            fg_color=BG_COLOR
        )

        scroll.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=10,
            pady=10
        )

        ctk.CTkLabel(
            scroll,
            text="Nome"
        ).pack(
            anchor="w",
            padx=20,
            pady=(15,0)
        )

        name = ctk.CTkEntry(
            scroll,
            height=45
        )

        name.pack(
            fill="x",
            padx=20,
            pady=5
        )

        name.insert(0, product["name"])

        ctk.CTkLabel(
            scroll,
            text="Preço"
        ).pack(anchor="w", padx=20)

        price = ctk.CTkEntry(scroll, height=45)

        price.pack(fill="x", padx=20, pady=5)

        price.insert(0, product["price"])

        ctk.CTkLabel(
            scroll,
            text="Preço Antigo"
        ).pack(anchor="w", padx=20)

        old = ctk.CTkEntry(scroll, height=45)

        old.pack(fill="x", padx=20, pady=5)

        old.insert(0, product["old_price"])

        ctk.CTkLabel(
            scroll,
            text="Categorias"
        ).pack(anchor="w", padx=20, pady=(10,0))

        category_entry = ctk.CTkEntry(
            scroll,
            height=45,
            placeholder_text="Ex: brasil,retro"
        )

        category_entry.pack(fill="x", padx=20, pady=5)

        current_category = product["category"]

        if isinstance(current_category, list):
            current_category = ",".join(current_category)

        category_entry.insert(0, current_category)

        ctk.CTkLabel(
            scroll,
            text="Tamanhos"
        ).pack(anchor="w", padx=20, pady=(10,0))

        sizes_entry = ctk.CTkEntry(
            scroll,
            height=45,
            placeholder_text="Ex: P,M,G,GG"
        )

        sizes_entry.pack(fill="x", padx=20, pady=5)

        sizes_entry.insert(0, ",".join(product["sizes"]))

        ctk.CTkLabel(
            scroll,
            text="Vídeo Google Drive"
        ).pack(anchor="w", padx=20, pady=(10,0))

        video_entry = ctk.CTkEntry(scroll, height=45)

        video_entry.pack(fill="x", padx=20, pady=5)

        video_entry.insert(0, product["video"])

        promo = ctk.CTkSwitch(
            scroll,
            text="Promoção"
        )

        promo.pack(anchor="w", padx=20, pady=15)

        if product["promotion"]:
            promo.select()

        ctk.CTkLabel(
            scroll,
            text="Links das imagens"
        ).pack(anchor="w", padx=20)

        images_box = ctk.CTkTextbox(
            scroll,
            height=280
        )

        images_box.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=10
        )

        for img in product["images"]:
            images_box.insert("end", img + "\n")

        def save():

            product["name"] = name.get()
            product["price"] = price.get()
            product["old_price"] = old.get()
            product["promotion"] = promo.get() == 1

            categories = category_entry.get().strip()

            if "," in categories:

                final_categories = []

                for cat in categories.split(","):

                    cat = cat.strip()

                    if cat:
                        final_categories.append(cat)

                product["category"] = final_categories

            else:

                product["category"] = categories

            sizes = sizes_entry.get().strip()

            final_sizes = []

            for size in sizes.split(","):

                size = size.strip()

                if size:
                    final_sizes.append(size)

            product["sizes"] = final_sizes

            video = video_entry.get().strip()

            if video:
                video = self.convert_video_link(video)

            product["video"] = video

            images = images_box.get(
                "1.0",
                "end"
            ).splitlines()

            final_images = []

            for img in images:

                img = img.strip()

                if img:

                    img = self.convert_drive_link(img)

                    final_images.append(img)

            product["images"] = final_images

            if final_images:
                product["image"] = final_images[0]

            self.render_products()

            win.destroy()

        buttons = ctk.CTkFrame(
            scroll,
            fg_color="transparent"
        )

        buttons.pack(
            fill="x",
            padx=20,
            pady=20
        )

        btn_save = ctk.CTkButton(
            buttons,
            text="Salvar Alterações",
            height=50,
            fg_color="#16a34a",
            hover_color="#15803d",
            command=save
        )

        btn_save.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(0,10)
        )

        btn_cancel = ctk.CTkButton(
            buttons,
            text="Cancelar",
            height=50,
            fg_color="#374151",
            hover_color="#1f2937",
            command=win.destroy
        )

        btn_cancel.pack(
            side="right",
            fill="x",
            expand=True
        )

    # =====================================================
    # SAVE JS
    # =====================================================

    def save_js(self):

        if not self.js_path:
            return

        backup = self.js_path.replace(
            ".js",
            "_backup.js"
        )

        shutil.copy(
            self.js_path,
            backup
        )

        content = "/* PRODUTOS */\n\nconst products=[\n"

        for p in self.products:

            content += "{\n"

            content += f'name:"{p["name"]}",\n'

            content += f'price:"{p["price"]}",\n'

            content += f'oldPrice:"{p["old_price"]}",\n'

            content += (
                f'promotion:{"true" if p["promotion"] else "false"},\n'
            )

            if isinstance(p["category"], list):

                cats = ",".join([
                    f'"{c}"'
                    for c in p["category"]
                ])

                content += f'category:[{cats}],\n'

            else:

                content += f'category:"{p["category"]}",\n'

            content += 'ready:false,\n'

            sizes = ",".join([
                f'"{s}"'
                for s in p["sizes"]
            ])

            content += f'sizes:[{sizes}],\n'

            content += 'desc:"Descrição",\n\n'

            content += 'images:[\n\n'

            for img in p["images"]:

                img = self.convert_drive_link(img)

                content += f'"{img}",\n'

            content += '\n]'

            if p["video"]:

                video = self.convert_video_link(
                    p["video"]
                )

                content += f',\nvideo:"{video}"'

            content += "\n},\n"

        content += "];\n\nwindow.products = products;"

        with open(
            self.js_path,
            "w",
            encoding="utf-8"
        ) as f:

            f.write(content)

        messagebox.showinfo(
            "Sucesso",
            "Arquivo salvo com sucesso!\nBackup criado."
        )

# =========================================================
# START
# =========================================================

app = CamisasEditor()

app.mainloop()
