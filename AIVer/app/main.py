from fastapi import FastAPI, logger
from app.Cobol2Java import RunAPI

app = FastAPI()
app.include_router(RunAPI.router)

@app.get("/pdfDeleteSign")
def sign_delete(pageno : int = -1):
    input_pdf = "C:\\tmp\\test5.pdf"
    output_pdf = "C:\\tmp\\test5_out.pdf"
    target_page_index = pageno
    doc = fitz.open(input_pdf)
    page = doc[target_page_index]
    image_list = page.get_images(full=True)

    for img in image_list:
        xref = img[0]  # 画像の参照番号
        #スタンプ画像の場合、削除対象とする。
        pix = fitz.Pixmap(doc, xref)
        if pix.width == 93 and pix.height == 92:
           page.delete_image(xref)

    doc.save(output_pdf, garbage=4, deflate=True)
    doc.close()
    print("画像削除完了")

    #画像削除後のPDFファイルファイルで元ファイルを上書きすること。
    try:
        shutil.copy2(output_pdf, input_pdf)
        print(f"処理成功")
    except Exception as e:
        print(f"エラー発生：{e}")

    #画像削除後のPDFファイルを削除すること。
    try:
        os.remove(output_pdf)
    except FileNotFoundError:
        print("ファイルが見つかりません")
    except PermissionError:
        print("権限がありません")
    except Exception as e:
        print(f"エラー発生: {e}")

    return {"success": "スタンプ削除済でした。"}


@app.get("/pdfAddSign1")
def sign_add(pageno : int = -1):
    global canvas_tk,page_height,page_width,image_path,circles,input_pdf,output_pdf,target_page_index,root,tk,context_menu
    target_page_index = pageno
    input_pdf = "C:\\tmp\\test5.pdf"
    output_pdf = "C:\\tmp\\test5.pdf"
    image_path = "C:\\tmp\\square.png"
    current_circle = None
    latest_x = None
    latest_y = None 
    circles = []
    # ==================================
    # ① PDFを画像として表示
    # ==================================
    doc = fitz.open(input_pdf)
    page = doc[target_page_index]

    pix = page.get_pixmap()
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

    root = tk.Tk()
    tk_img = ImageTk.PhotoImage(img)

    canvas_tk = tk.Canvas(root, width=img.width, height=img.height, cursor="hand2")
    canvas_tk.pack()
    canvas_tk.create_image(0, 0, anchor="nw", image=tk_img)

    page_width = page.rect.width
    page_height = page.rect.height 

    # コンテキストメニュー作成
    # ------------------------
    context_menu = tk.Menu(root, tearoff=0)
    context_menu.add_command(label="仮押印", command=on_dbl_right_press)
    context_menu.add_command(label="予備１", command=lambda: print("編集クリック"))
    context_menu.add_separator()
    context_menu.add_command(label="予備２", command=lambda: print("削除クリック"))

    #canvas_tk.bind("<ButtonRelease-1>", on_click)
    canvas_tk.bind("<Button-1>", on_press)
    canvas_tk.bind("<B1-Motion>", on_drag)
    canvas_tk.bind("<ButtonRelease-1>", on_release)
    canvas_tk.bind("<Button-3>", on_right_press)
    #canvas_tk.bind("<Double-Button-3>", on_dbl_right_press)

    root.mainloop()

    return {"success": "押印画面を正常に起動しました。"}

# ------------------------
# メニュー表示関数
# ------------------------
def show_context_menu(event):
    context_menu.post(event.x_root, event.y_root)

def on_press(event):
    global latest_x, latest_y
    latest_x = event.x
    latest_y = event.y

def on_drag(event):
    global latest_x, latest_y,current_circle

    latest_x = event.x
    latest_y = event.y

    # 前の円を削除
    if current_circle:
        canvas_tk.delete(current_circle)

    diameter = 3 / 2.54 * 72
    radius = diameter / 2

    current_circle = canvas_tk.create_oval(
        latest_x - radius,
        latest_y - radius,
        latest_x + radius,
        latest_y + radius,
        outline="red",
        width=2
    )

def on_release(event):
    global latest_x, latest_y,canvas_tk,page_height,page_width
    latest_x = event.x
    latest_y = event.y
    print("画面座標:", event.x, event.y)
    
    pdf_x = latest_x
    pdf_y = page_height - latest_y
    # 前の円を削除
    if current_circle:
        canvas_tk.delete(current_circle)

    #print(f"page_height = {page_height}")
    #add_image_original_size(pdf_x, (840 - pdf_y))
    #logger.info("APIが呼び出されました")
    add_image_original_size(pdf_x, (page_height - pdf_y))

# ==================================
# ② クリック時処理
# ==================================
def on_click(event):
    click_x = event.x
    click_y = event.y

    print("画面座標:", click_x, click_y)

    # PDF座標へ変換（Y軸反転）
    pdf_x = click_x
    pdf_y = page_height - click_y

    print("PDF座標:", pdf_x, pdf_y)

    #add_image_to_pdf(pdf_x, pdf_y)
    #add_image_original_size(pdf_x, (840 - pdf_y))

# =========================
# オリジナルサイズで貼る
# =========================
def add_image_original_size(x, y):

    global canvas_tk
    # 画像の実サイズ取得
    img = Image.open(image_path)
    img_width_px, img_height_px = img.size

    # DPI取得（なければ72と仮定）
    dpi = img.info.get("dpi", (72, 72))[0]

    # px → pt 変換
    width_pt = img_width_px * 72 / dpi
    height_pt = img_height_px * 72 / dpi

    print("画像ptサイズ:", width_pt, height_pt)

    # 3cm → pt（≒px）
    diameter = 3 / 2.54 * 72   # 約85
    radius = diameter / 2
    
    print("円描画座標:", x, y)
    # 円を描画（赤枠）
    circle_id = canvas_tk.create_oval(
        x - radius,
        y - radius,
        x + radius,
        y + radius,
        outline="red",
        width=2
    )
    circles.append((circle_id, x, y))
 
def on_right_press(event):

    global latest_x, latest_y, circles

    if current_circle is None:
        return

    diameter = 3 / 2.54 * 72
    radius = diameter / 2

    for circle_id, cx, cy in circles:
        dx = event.x - cx
        dy = event.y - cy

        if dx * dx + dy * dy <= radius * radius:
            canvas_tk.delete(circle_id)
            circles = [c for c in circles if c[0] != circle_id]
            print("削除成功")
            return
    show_context_menu(event)

    print("円の外です")

def on_dbl_right_press():

    # 画像の実サイズ取得
    img = Image.open(image_path)
    img_width_px, img_height_px = img.size

    # DPI取得（なければ72と仮定）
    dpi = img.info.get("dpi", (72, 72))[0]

    # px → pt 変換
    width_pt = img_width_px * 72 / dpi
    height_pt = img_height_px * 72 / dpi

    print("on_dbl_right_press:画像ptサイズ:", width_pt, height_pt)

    # 3cm → pt（≒px）
    diameter = 3 / 2.54 * 72   # 約85
    radius = diameter / 2
    
    packet = io.BytesIO()

    img = Image.open(image_path)
    img_width_px, img_height_px = img.size
    dpi = img.info.get("dpi", (72, 72))[0]

    width_pt = img_width_px * 72 / dpi
    height_pt = img_height_px * 72 / dpi

    packet = io.BytesIO()
    c = pdf_canvas.Canvas(packet, pagesize=(page_width, page_height))

    print(len(circles))
    if circles is None or len(circles) == 0:
        print("処理対象なし")
    else:
        print("押印ー処理開始")
        for circle_id, x, y in circles:
            c.drawImage(image_path, x - radius, page_height - y - 30,
                    width=width_pt,
                    height=height_pt,
                    mask='auto')
        c.save()
    
        packet.seek(0)
        overlay_pdf = PdfReader(packet)
    
        reader = PdfReader(input_pdf)
        writer = PdfWriter()
    
        for i in range(len(reader.pages)):
            page_obj = reader.pages[i]
            #★改修箇所（一ページに押印しても全頁の同一箇所に押印されていました。）★
            if i == target_page_index:
                page_obj.merge_page(overlay_pdf.pages[0])

            writer.add_page(page_obj)
    
        with open(output_pdf, "wb") as f:
            writer.write(f)

        # ★ 画面を閉じる処理
        try:
            root.after(0, root.destroy)
            #root.quit()
            #root.destroy()   # ウィンドウを閉じる
        except Exception as e:
            print(f"画面クローズエラー: {e}")

        print("保存完了（原寸）")

#canvas_tk.bind("<Button-1>", on_press)
#canvas_tk.bind("<B1-Motion>", on_drag)
#canvas_tk.bind("<ButtonRelease-1>", on_release)
#canvas_tk.bind("<Button-3>", on_right_press)
#canvas_tk.bind("<Double-Button-3>", on_dbl_right_press)

#root.mainloop()