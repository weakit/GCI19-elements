#!/usr/bin/env python3
import json
import time
import random
import requests
import tkinter as tk
from io import BytesIO
from bs4 import BeautifulSoup
from PIL import Image, ImageTk
from tkinter import messagebox


CUI = False

URL = "https://rawcdn.githack.com/Bowserinator/Periodic-Table-JSON/" \
      "1871a04b65c5c6774fe8d1c64abe35b0f577c3b5/PeriodicTableJSON.json"

Table = json.loads(requests.get(URL).text)['elements']  # The Periodic Table

T = {x['number']: x for x in Table}
T.update({x['symbol']: x for x in Table})
T.update({x['symbol'].lower(): x for x in Table})
T.update({x['name'].lower(): x for x in Table})


def hint_a(element):
    if element not in Table:
        element = T[element]
    if element['appearance'] is not None:
        return 'The element has a "%s" appearance.' % element['appearance']


def hint_b(element):
    if element not in Table:
        element = T[element]
    if element['discovered_by'] is not None:
        return 'The element was discovered by ' + element['discovered_by']


def hint_c(element):
    """Get element image from wikipedia, if present."""
    if element not in Table:
        element = T[element]
    url = element['source']
    soup = BeautifulSoup(requests.get(url).text, 'html.parser')
    a = soup.find('table', class_='infobox').find('tbody').find('tr').find('a', class_='image')
    if a:
        f = a['href'][6:]
        js = json.loads(requests.get(
            "https://en.wikipedia.org/w/api.php?action=query&titles=%s"
            "&prop=imageinfo&iiprop=url&iiurlwidth=1000&format=json" % f).text)
        pages = js["query"]["pages"]
        return pages[next(iter(pages))]["imageinfo"][0]["thumburl"]


def hint_default(element, guess):
    guess = T[guess.lower()]
    if guess['period'] == element['period']:
        if guess['number'] > element['number']:
            return 'The correct element is to the left of %s.' % guess['name']
        else:
            return 'The correct element is to the right of %s.' % guess['name']
    else:
        if guess['period'] > element['period']:
            return 'The correct element is above %s.' % guess['name']
        else:
            return 'The correct element is below %s.' % guess['name']


def correct(s, e):
    return s.lower() == e['name'].lower() or s.lower() == e['symbol'].lower()


def show_image(img):
    res = requests.get(img)
    img = Image.open(BytesIO(res.content))
    img.show("Image Hint")


def console():
    e = random.choice(Table)
    print("The atomic number is:", e['number'])
    hints = [hint_a, hint_b, hint_c]
    sel = input("Enter name/symbol of element: ")
    turns = 1
    while not correct(sel, e):
        if hints:
            hint = random.choice(hints)
            hints.remove(hint)
            if hint(e) is None:
                continue
            if hint == hint_c:
                hint = "Image"
                show_image(hint_c(e))
            else:
                hint = hint(e)
        elif sel in T:
            hint = hint_default(e, sel)
        else:
            hint = hint_default(e, random.choice(Table)['name'])
        print("\nIncorrect Choice.")
        print("\nHint:", hint)
        turns += 1
        if turns == 5:
            break
        sel = input("\nEnter name/symbol of element: ")
    if turns == 5:
        print("The correct element was %s [%s].\nBetter luck next time." % (e['name'], e['symbol']))
    else:
        print("\nCongrats, you won.")
    print('\n' + e['summary'])


def _reset(root):
    root.destroy()
    gui()


def gui():
    def show_hint(hint):
        messagebox.showerror('Incorrect Answer', 'Hint:\n' + hint)

    def show_image_hint(img):
        res = requests.get(img)
        img = Image.open(BytesIO(res.content))
        img.thumbnail((600, 600), Image.LANCZOS)
        img_root = tk.Tk()
        img_root.title("Image Hint")
        image = ImageTk.PhotoImage(img, master=img_root)
        label = tk.Label(img_root, image=image)
        label.image = image
        label.pack()
        img_root.mainloop()

    def win():
        messagebox.showinfo('You won.', e['summary'])
        reset()

    def lose():
        messagebox.showinfo('You lost.', 'The correct element was %s.\n\n%s' % (e['name'], e['summary']))
        reset()

    def check():
        nonlocal turns
        text = inp.get()
        if not text:
            atomic.config(activebackground='gray60')
            entry.focus_set()
            atomic.flash()
            atomic.config(activebackground='gray50')
            return
        if correct(text, e):
            return win()
        inp.set('')
        turns += 1
        if turns == 5:
            lose()
        if hints:
            while hints:
                hint = random.choice(hints)
                hints.remove(hint)
                if hint(e) is None:
                    break
                if hint == hint_c:
                    return show_image_hint(hint_c(e))
                else:
                    hint = hint(e)
                    return show_hint(hint)
        if text in T:
            hint = hint_default(e, text)
            return show_hint(hint)
        else:
            hint = hint_default(e, random.choice(Table)['name'])
            return  show_hint(hint)

    def reset():
        return _reset(root)

    def delete():
        try:
            root.destroy()
        except tk.TclError:
            pass
        finally:
            exit()

    random.seed(random.random() * time.time())
    e = random.choice(Table)
    hints = [hint_a, hint_b, hint_c]
    turns = 0

    root = tk.Tk()

    menu = tk.Menu(root)
    menu.add_command(label="New Element", command=reset)

    root.config(menu=menu)
    root.title("Elements")
    root.geometry("300x220")
    root.resizable(False, False)
    root.protocol("WM_DELETE_WINDOW", delete)

    inp = tk.StringVar()

    lb1 = tk.Label(root, text='guess the element with the \natomic number')
    lb2 = tk.Label(root, text='element name or symbol')
    atomic = tk.Button(root, text=e['number'], font=('', 32), relief=tk.SUNKEN,
                       fg='white', bg='gray50', activeforeground='white', activebackground='gray50')
    entry = tk.Entry(root, justify='center', textvariable=inp,)
    button = tk.Button(root, text='check', command=check, justify='center', padx=5)

    lb1.place(relx=0.5, y=25, anchor='center')
    atomic.place(relx=0.5, y=79, anchor='center')
    entry.place(relwidth=0.6, relx=0.5, y=135, anchor=tk.CENTER)
    lb2.place(relx=0.5, y=155, anchor=tk.CENTER)
    button.place(relx=0.5, y=185, anchor='center')

    root.mainloop()


if __name__ == '__main__':
    if CUI:
        console()
    else:
        gui()
