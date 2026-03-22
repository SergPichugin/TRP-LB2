from tkinter import * 
import math
import numpy as np
from TkToolTip import ToolTip
from PIL import Image, ImageTk, ImageDraw
import random
from tkinter import ttk


root = Tk()
root.title('Калькулятор')
root.geometry('450x400')
root.resizable(False, False)

def create_dark_grid_background(width, height):
    img = Image.new('RGB', (width, height), color='#0A0C12')
    draw = ImageDraw.Draw(img)
    
    for y in range(height):
        ratio = y / height
        r = int(8 + ratio * 5)
        g = int(8 + ratio * 12)
        b = int(18 + ratio * 10)
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    
    for y in range(20, height, 25):
        draw.line([(0, y), (width, y)], fill=(0, 150, 200))
    
    for x in range(20, width, 30):
        draw.line([(x, 0), (x, height)], fill=(0, 120, 180))
    
    for _ in range(100):
        x = random.randint(0, width)
        y = random.randint(0, height)
        brightness = random.randint(100, 220)
        draw.point((x, y), fill=(brightness, brightness, 255))
    
    return img

bg_image_pil = create_dark_grid_background(450, 400)
bg_photo = ImageTk.PhotoImage(bg_image_pil)

canvas = Canvas(root, width=450, height=400, highlightthickness=0)
canvas.pack(fill="both", expand=True)

canvas.create_image(0, 0, image=bg_photo, anchor="nw")
canvas.image = bg_photo

main_frame = Frame(root, bg='#0F1117', bd=2, relief=SOLID)
main_frame.place(x=20, y=20, width=410, height=360)




var_T = DoubleVar(value=10)
var_k = DoubleVar(value=3)
var_t = DoubleVar(value=6)
var_proc = DoubleVar(value=5)
var_E = DoubleVar(value=70)

def calc(T, t, k, Pr, E):
    k = int(k)
    t = int(t)
    n = 10
    Pr = Pr/100
    tn = T/n
    sigma = 0.1
    u = math.exp(sigma * math.sqrt(T/n))
    d = 1/u
    p = (math.exp((Pr*tn))- d)/(u-d)
    q = 1 - p
    
    r = np.zeros((n+1, n+1)) # безрисковая процентная ставка
    r[n][0] = Pr*100

    j = 1
    for i in range(n-1, -1, -1):
        r[i][j] = r[i+1][j-1] * u 
        j = j + 1

    for i in range(n, -1, -1):  
        for j in range(1, n+1):  
            if r[i][j] == 0:  
                r[i][j] = r[i][j-1] * d
    
    # ZCB10
    ZCB10 = np.zeros((n+1, n+1))
    for i in range(0, n+1):
        ZCB10[i][n] = 100

    g = 1
    for j in range(n-1, -1, -1): 
        for i in range(g, n+1):
            ZCB10[i][j] = (p * (ZCB10[i-1][j+1])/100 + q * (ZCB10[i][j+1])/100) / (1 + (r[i][j])/100)
            ZCB10[i][j] = ZCB10[i][j]*100
        if j > 0: 
            g = g + 1
    
    if ZCB10[10][0] < 0:
        lblPrice.config(text=f"Цена ZCB₁₀: {0:.2f}%")
    else:
        lblPrice.config(text=f"Цена ZCB₁₀: {ZCB10[10][0]:.2f}%")
    
    # ZCBt
    ZCBt = np.zeros((t+1, t+1))
    for i in range(0, t+1):
        ZCBt[i][t] = 100
    
    rows = r.shape[0]
    rС = r[rows-(t+1):rows, 0:(t+1)].copy()

    g = 1
    for j in range(t-1, -1, -1): 
        for i in range(g, t+1):
            ZCBt[i][j] = (p * (ZCBt[i-1][j+1])/100 + q * (ZCBt[i][j+1])/100) / (1 + (rС[i][j])/100)
            ZCBt[i][j] = ZCBt[i][j]*100
        if j > 0: 
            g = g + 1
    
    lbl6.config(text=f"Форвард: {(ZCB10[10][0]/ZCBt[t][0])*100:.2f}%")
    
    rows = ZCB10.shape[0]
    ZCB10C = ZCB10[rows-(k+1):rows, 0:(k+1)].copy()
    futV = ZCB10C

    g = 1
    for j in range(k-1, -1, -1): 
        for i in range(g, k+1):
            futV[i][j] = p * (futV[i-1][j+1])/100 + q * (futV[i][j+1])/100
            futV[i][j] = futV[i][j]*100
        if j > 0: 
            g = g + 1
    
    lbl7.config(text=f"Фьючерс: {futV[k][0]:.2f}%")
    
    # option Call
    opCall = np.zeros((k+1, k+1))
    for i in range(0, k+1):
        opCall[i][k] = max(0, futV[i][k] - E)

    g = 1
    for j in range(k-1, -1, -1): 
        for i in range(g, k+1):
            a = p * (opCall[i-1][j+1]/100)
            b = q * (opCall[i][j+1]/100)
            c = math.exp((Pr*T)/k)
            d = futV[i][j]/100 - E/100
            opCall[i][j] = max((a + b)/(c), max(0, d))
            opCall[i][j] = opCall[i][j] * 100
        if j > 0: 
            g = g + 1

    lbl8.config(text=f"Опцион Call: {opCall[k][0]:.2f}%")
    return print("☼")

label_style = {'font': ('Arial', 14), 'bg': '#0F1117', 'fg': '#E4E6F0'}
entry_style = {'font': ('Arial', 12), 'bg': '#1A1E2A', 'fg': '#00FFC6', 
               'readonlybackground': '#1A1E2A', 'highlightthickness': 0, 'bd': 1}

title_label = Label(main_frame, text="Калькулятор", font=('Arial', 18, 'bold'), 
                    bg='#0F1117', fg='#00FFC6')
title_label.pack(pady=(10, 5))

separator = Frame(main_frame, height=2, bg='#2A6F8F')
separator.pack(fill='x', padx=20, pady=(0, 10))

input_frame = Frame(main_frame, bg='#0F1117')
input_frame.pack(pady=5)


def validate_input(P):
    if P == "" or P == "-":
        return True
    try:
        float(P)
        return True
    except ValueError:
        return False

vcmd = (root.register(validate_input), '%P')

row1 = Frame(input_frame, bg='#0F1117')
row1.pack(pady=3)
Label(row1, text="T  =", **label_style).pack(side=LEFT, padx=5)
edtT = Spinbox(row1, from_=0, to=100, increment=1, width=6, textvariable=var_T, 
               state='normal', validate='key', validatecommand=vcmd, **entry_style)
edtT.pack(side=LEFT, padx=5)
Label(row1, text="r (risk-free)  =", **label_style).pack(side=LEFT, padx=5)
edtPr = Spinbox(row1, from_=0, to=100, increment=0.5, width=6, textvariable=var_proc, 
                state='normal', validate='key', validatecommand=vcmd, **entry_style)
edtPr.pack(side=LEFT, padx=5)

row2 = Frame(input_frame, bg='#0F1117')
row2.pack(pady=3)
Label(row2, text="k  =", **label_style).pack(side=LEFT, padx=5)
edtk = Spinbox(row2, from_=0, to=10, increment=1, width=6, textvariable=var_k, 
               state='normal', validate='key', validatecommand=vcmd, **entry_style)
edtk.pack(side=LEFT, padx=5)
Label(row2, text="t  =", **label_style).pack(side=LEFT, padx=5)
edtt = Spinbox(row2, from_=0, to=10, increment=1, width=6, textvariable=var_t, 
               state='normal', validate='key', validatecommand=vcmd, **entry_style)
edtt.pack(side=LEFT, padx=5)

row3 = Frame(input_frame, bg='#0F1117')
row3.pack(pady=3)
Label(row3, text="E  =", **label_style).pack(side=LEFT, padx=5)
edtE = Spinbox(row3, from_=0, to=100, increment=1, width=6, textvariable=var_E, 
               state='normal', validate='key', validatecommand=vcmd, **entry_style)
edtE.pack(side=LEFT, padx=5)

separator2 = Frame(main_frame, height=1, bg='#2A2E45')
separator2.pack(fill='x', padx=20, pady=10)

# результаты
results_frame = Frame(main_frame, bg='#0F1117')
results_frame.pack(pady=5)

result_style = {'font': ('Arial', 14, 'bold'), 'bg': '#0F1117', 'fg': '#E4E6F0'}

lblPrice = Label(results_frame, text="Цена ZCB₁₀: --.-%", **result_style)
lblPrice.pack(anchor='w', pady=3)

lbl6 = Label(results_frame, text="Форвард: --.-%", **result_style)
lbl6.pack(anchor='w', pady=3)

lbl7 = Label(results_frame, text="Фьючерс: --.-%", **result_style)
lbl7.pack(anchor='w', pady=3)

lbl8 = Label(results_frame, text="Опцион Call: --.-%", **result_style)
lbl8.pack(anchor='w', pady=3)


def on_calc():
    calc(float(edtT.get()), float(edtt.get()), 
         float(edtk.get()), float(edtPr.get()), 
         float(edtE.get()))

btn_canvas = Canvas(main_frame, width=180, height=40, bg='#0F1117', highlightthickness=0)
btn_canvas.pack(pady=(10, 15))

def draw_button(state='normal'):
    btn_canvas.delete("button_bg")
    if state == 'pressed':
        color = '#1A5F7F'
    elif state == 'hover':
        color = '#3A8FBF'
    else:
        color = '#2A6F8F'
    
    btn_canvas.create_rounded_rect(5, 5, 175, 35, radius=15, fill=color, outline='', tags="button_bg")
    btn_canvas.create_text(90, 20, text="Рассчитать", font=('Arial', 12, 'bold'), 
                           fill='white', tags="button_text")

def create_rounded_rect(canvas, x1, y1, x2, y2, radius=25, **kwargs):
    points = [x1+radius, y1,
              x2-radius, y1,
              x2, y1,
              x2, y1+radius,
              x2, y2-radius,
              x2, y2,
              x2-radius, y2,
              x1+radius, y2,
              x1, y2,
              x1, y2-radius,
              x1, y1+radius,
              x1, y1]
    return canvas.create_polygon(points, smooth=True, **kwargs)

Canvas.create_rounded_rect = create_rounded_rect

draw_button()

# эффекты кнопки
def on_enter(e):
    draw_button('hover')

def on_leave(e):
    draw_button('normal')

def on_click(e):
    draw_button('pressed')
    on_calc()
    draw_button('normal')

btn_canvas.bind("<Enter>", on_enter)
btn_canvas.bind("<Leave>", on_leave)
btn_canvas.bind("<Button-1>", on_click)

btn_canvas.config(cursor="hand2")

# ToolTips
ToolTip(edtT, text="T — срок модели (лет). Используется для построения 10-периодной биномиальной модели процентной ставки.", delay=0.5)
ToolTip(edtt, text="t — момент исполнения форвардного контракта на бескупонную облигацию ZCB10.", delay=0.5)
ToolTip(edtk, text="k — момент исполнения фьючерсного контракта на облигацию ZCB10.", delay=0.5)
ToolTip(edtPr, text="r₀ — начальная процентная ставка (%). Используется для построения дерева ставок.", delay=0.5)
ToolTip(edtE, text="E — страйк опциона (%). Цена исполнения опциона Call на фьючерс.", delay=0.5)
ToolTip(lblPrice, text="Цена 10-летней бескупонной облигации ZCB10, рассчитанная по биномиальной модели ставок.", delay=0.5)
ToolTip(lbl6, text="Форвардная цена облигации ZCB10 с исполнением в момент времени t.", delay=0.5)
ToolTip(lbl7, text="Цена фьючерса на облигацию ZCB10 с исполнением в момент времени k (без дисконтирования).", delay=0.5)
ToolTip(lbl8, text="Цена американского опциона Call на фьючерс на облигацию ZCB10.", delay=0.5)

root.mainloop()
