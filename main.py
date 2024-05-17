import urllib.request, urllib.parse, urllib.error
from urllib.request import Request, urlopen
import re
from bs4 import BeautifulSoup
import ssl
from bs4 import BeautifulSoup
import tkinter as tk
from tkinter import *
import pyttsx3
import numpy as np

###TKINTER LOOP###
root = tk.Tk()
root.configure(background="white")
root.geometry("1200x800")
root.title("Prototype")

current_size_base = 14
current_written_size = 16

entry_txt1 = tk.StringVar()
entry_txt2 = tk.StringVar()
bg_col = tk.StringVar()
tb_bg_col = tk.StringVar()
txt_col = tk.StringVar()
text_size_change = tk.StringVar()
label_size_change = tk.StringVar()
web_name = tk.StringVar()
chosen_written_font = tk.StringVar()
chosen_label_font = tk.StringVar()
to_speek_box = tk.StringVar()
speek_input = tk.StringVar()

current_font_label = "Helvetica"
current_font_written = "Comic Sans MS"
current_bg = "white"
current_text_bg = "light cyan"
current_txt_col = "black"
further_question = 0

colours = ["dark red", "red", "orange", "yellow", "green", "blue", "purple", "white", "black", "cyan", "light cyan",
           "magenta","pale turquoise"]
fonts = ["Helvetica", "Comic Sans MS", "Arial", "Times New Roman", "MS Serif", "Calibri", "Rockwell", "Cambria"]

###WEBSITE PROCESSING###

current_link = 0
soup = 0


# Soup creation
def soup_maker():
    if web_name.get() != "":
        global soup
        global current_link
        current_link = 0

        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        page_name = Request(url=web_name.get(), headers={'User-Agent': 'Mozilla/5.0'})

        web_data = urllib.request.urlopen(page_name, context=ctx).read()

        soup = BeautifulSoup(web_data, 'html.parser')

        text_box.insert(END, "page loaded")


def get_next_link():
    if soup != 0:
        global current_link
        sending = soup.find_all('a')[current_link]
        current_link = current_link + 1
        if current_link > len(soup.find_all('a')):
            current_link = 0
        return sending.get('href')
    else:
        return "page not loaded"


def find_section(start, end):
    if soup != 0:
        current_doc = ""
        going = False
        for string in soup.strings:
            if going:
                if string == end:
                    going = False
                else:
                    current_doc = current_doc + " " + string
            elif string == start or start=="":
                going = True
        return current_doc
    else:
        return "page not loaded"


### END WEB PROCESSING ###

### SPEECH COMMAND MAKER ###

def all_possible_versions(command, similar):
    new_commands = [[] for i in range(0, len(command))]

    for i in range(0, len(command)):
        given_arr = splitter(command[i], 0)
        putting_in = []
        if type(given_arr) != type("String"):
            for row in range(0, len(given_arr)):
                if type(given_arr[row][0]) != type("STRING"):
                    for col in range(0, len(given_arr[row])):
                        putting_in.append(given_arr[row][col])
                else:
                    putting_in.append(given_arr[row])
        else:
            putting_in = given_arr

        new_commands[i] = putting_in

    for i in range(0, len(command)):
        new_commands[i] = same_starter(new_commands[i], similar)
    return new_commands


def same_starter(array, similar):
    started = 0
    if type(array) != type("STRING"):
        for i in range(0, len(array)):
            if started == 0:
                current = same(array[i], similar, 0)
                started = 1
            else:
                current = np.concatenate((current, same(array[i], similar, 0)), axis=None)
        return current
    else:
        return same(array, similar, 0)


def same(phrase, similar, pos):
    word_start = pos
    word_end = pos
    for i in range(pos, len(phrase)):
        word_end = i
        if phrase[i] == " " or i == len(phrase) - 1:
            if i == len(phrase) - 1:
                word = phrase[word_start:word_end + 1]
            else:
                word = phrase[word_start:word_end]

            is_in = False
            for e in range(0, len(similar)):

                if word in similar[e]:

                    for j in range(0, len(similar[e])):
                        if similar[e][j] != word:
                            altered_text = phrase[0:word_start] + similar[e][j] + phrase[word_end:len(phrase)]
                            new_pos = i + (len(similar[e][j]) - len(word))
                            return np.concatenate(([same(phrase, similar, i)], [same(altered_text, similar, new_pos)]))

            word_start = i + 1
    return phrase


def splitter(phrase, pos):
    arr = []
    start_pos = 0
    end_pos = 0
    split = 0
    inbetween = ""

    for i in range(pos, len(phrase)):
        if phrase[i] == "{":
            start_pos = i - 1
        if phrase[i] == "}":
            end_pos = i + 1
            split = 1
            break

    if split == 1:
        with_next = phrase.replace("{", "", 1)
        with_next = with_next.replace("}", "", 1)

        removing = phrase[start_pos:end_pos]
        without_next = phrase.replace(removing, "", 1)

        return np.concatenate(
            ([splitter(with_next, end_pos - (2))], [splitter(without_next, end_pos - (end_pos - start_pos))]),
            axis=None)
    else:
        return phrase


def speek_command():
    global further_question
    inp = speek_input.get()
    if further_question != 0:
        if further_question == 3:
            if inp.isnumeric():
                lab_size_change(inp)
            else:
                non_val_inp()
        elif further_question == 4:
            lab_written_change(inp)
        elif further_question == 5:
            lab_size_change(inp)
            lab_written_change(inp)
        elif further_question == 6:
            change_bg_col(inp)
        elif further_question == 7:
            change_lab_col(inp)
        elif further_question == 8:
            change_written_col(inp)
        elif further_question == 9:
            change_text_col(inp)
        elif further_question == 11:
            change_all_font(inp)
        further_question = 0
    else:
        commands = ["show {next} link", "clear {text box}", "show {page} information", "change label size",
                    "change written size", "change text size", "change background {colour}", "change label colour",
                    "change written colour", "change text colour", "load website", "change font"]
        similar = [["show", "get"], ["change", "alter"]]
        ignored = ["the", "a"]
        commands = all_possible_versions(commands, similar)

        found = False
        for i in range(0, len(commands)):
            if inp in commands[i]:
                if i == 0:
                    next_link()
                elif i == 1:
                    clear_text()
                elif i == 2:
                    document_info()
                elif i == 3:
                    further_question = 3
                    ask_for_info("size")
                elif i == 4:
                    further_question = 4
                    ask_for_info("size")
                elif i == 5:
                    further_question = 5
                    ask_for_info("size")
                elif i == 6:
                    further_question = 6
                    ask_for_info("col")
                elif i == 7:
                    further_question = 7
                    ask_for_info("col")
                elif i == 8:
                    further_question = 8
                    ask_for_info("col")
                elif i == 9:
                    further_question = 9
                    ask_for_info("col")
                elif i == 10:
                    print("WIP")
                elif i == 11:
                    further_question = 11
                    ask_for_font()

                found = True
        if not found:
            non_rec_com()


### END COMMAND MAKER ###

### BUTTON FUNCTIONS ####

def clear_text():
    text_box.delete("1.0", END)


def document_info():
    text_box.insert(END, find_section(entry_txt1.get(), entry_txt2.get()) + "\n")


def document_info_base():
    text_box.insert(END, find_section("", "") + "\n")


def next_link():
    text_box.insert(END, get_next_link() + "\n")


def slider_1_changed(event):
    global current_size_base
    current_size_base = slider1.get()
    update_page()


def slider_2_changed(event):
    global current_written_size
    current_written_size = slider2.get()
    update_page()


def manual_text_change():
    global current_written_size
    global current_size_base
    change_lab = label_size_change.get()
    change_txt = text_size_change.get()
    if change_lab != "":
        current_size_base = change_lab
        slider1.set(int(change_lab))
    if change_txt != "":
        current_written_size = change_txt
        slider2.set(int(change_txt))
    update_page()


def lab_size_change(value):
    global current_size_base
    current_size_base = value
    update_page()


def lab_written_change(value):
    global current_written_size
    current_written_size = value
    update_page()


def manual_colour_change():
    global current_bg
    global current_text_bg
    global current_txt_col
    change_lab = bg_col.get()
    change_txt = tb_bg_col.get()
    change_col = txt_col.get()

    if change_lab != "":
        root.configure(background=change_lab)
        showing_frame.configure(background=change_lab)
        canvas.configure(background=change_lab)
        current_bg = change_lab
    if change_txt != "":
        current_text_bg = change_txt
    if change_col != "":
        current_txt_col = change_col
    update_page()


def change_bg_col(col):
    global current_bg
    root.configure(background=col)
    showing_frame.configure(background=col)
    canvas.configure(background=col)
    current_bg = col
    update_page()


def change_text_col(col):
    change_lab_col(col)
    change_written_col(col)
    update_page()


def change_lab_col(col):
    global current_txt_col
    current_txt_col = col
    update_page()


def change_written_col(col):
    global current_txt_col
    current_txt_col = col
    update_page()


def non_rec_com():
    text_box.insert(END, "Command not recognised\n")

def non_val_inp():
    text_box.insert(END, "Input not valid\n")

def ask_for_info(regards):
    if regards == "col":
        text_box.insert(END, "What colour do you want?\n")
    else:
        text_box.insert(END, "What size?\n")


def ask_for_font():
    text_box.insert(END, "Enter number font you want: \n")
    for i in range(0, len(fonts)):
        text_box.insert(END, (str(i + 1) + ": " + fonts[i] + "\n"))


def change_all_font(num):
    global current_font_label
    global current_font_written
    num = int(num) - 1
    changing_to = fonts[num]
    current_font_written = changing_to
    current_font_label = changing_to
    update_page()

def change_fonts():
    global current_font_label
    global current_font_written
    label = chosen_written_font.get()
    txt = chosen_label_font.get()
    if label != "":
        current_font_written = label
    if txt != "":
        current_font_label = txt
    update_page()


def speak_entry():
    engine = pyttsx3.init()
    engine.say(to_speek_box.get())
    engine.runAndWait()


def pre_update():
    manual_text_change()
    manual_colour_change()
    change_fonts()


def update_page():
    label_font = (current_font_label, current_size_base)
    entry_font = (current_font_written, current_written_size)

    label.config(font=(current_font_label, int(current_size_base) * 2), bg=current_bg, fg=current_txt_col)

    text_box.config(font=entry_font, bg=current_text_bg, fg=current_txt_col)
    b1.config(font=label_font, bg=current_bg, fg=current_txt_col)
    b2.config(font=label_font, bg=current_bg, fg=current_txt_col)
    labelE1.config(font=label_font, bg=current_bg, fg=current_txt_col)
    entry1.config(font=entry_font, bg=current_text_bg, fg=current_txt_col)
    labelE2.config(font=label_font, bg=current_bg, fg=current_txt_col)
    entry2.config(font=entry_font, bg=current_text_bg, fg=current_txt_col)
    b3.config(font=label_font, bg=current_bg, fg=current_txt_col)
    b4.config(font=label_font, bg=current_bg, fg=current_txt_col)
    labelS1.config(font=label_font, bg=current_bg, fg=current_txt_col)
    labelS2.config(font=label_font, bg=current_bg, fg=current_txt_col)
    labelFS1.config(font=label_font, bg=current_bg, fg=current_txt_col)
    entry3.config(font=entry_font, bg=current_text_bg, fg=current_txt_col)
    b5.config(font=label_font, bg=current_bg, fg=current_txt_col)
    labelFS2.config(font=label_font, bg=current_bg, fg=current_txt_col)
    entry4.config(font=entry_font, bg=current_text_bg, fg=current_txt_col)
    labelBG1.config(font=label_font, bg=current_bg, fg=current_txt_col)
    back_ground_select.config(font=label_font, bg=current_bg, fg=current_txt_col)
    labelBG2.config(font=label_font, bg=current_bg, fg=current_txt_col)
    entry_box_colour_select.config(font=label_font, bg=current_bg, fg=current_txt_col)
    b5.config(font=label_font, bg=current_bg, fg=current_txt_col)
    labelBG3.config(font=label_font, bg=current_bg, fg=current_txt_col)
    entry_text_colour_select.config(font=label_font, bg=current_bg, fg=current_txt_col)
    b6.config(font=label_font, bg=current_bg, fg=current_txt_col)
    LabelF1.config(font=label_font, bg=current_bg, fg=current_txt_col)
    entry_label_font.config(font=label_font, bg=current_bg, fg=current_txt_col)
    b7.config(font=label_font, bg=current_bg, fg=current_txt_col)
    LabelF2.config(font=label_font, bg=current_bg, fg=current_txt_col)
    entry_written_font.config(font=label_font, bg=current_bg, fg=current_txt_col)
    b8.config(font=label_font, bg=current_bg, fg=current_txt_col)
    LabelPL1.config(font=label_font, bg=current_bg, fg=current_txt_col)
    entry5.config(font=entry_font, bg=current_text_bg, fg=current_txt_col)
    b9.config(font=label_font, bg=current_bg, fg=current_txt_col)
    LabelSP.config(font=label_font, bg=current_bg, fg=current_txt_col)
    entry6.config(font=entry_font, bg=current_text_bg, fg=current_txt_col)
    b10.config(font=label_font, bg=current_bg, fg=current_txt_col)
    lbspeak.config(font=label_font, bg=current_bg, fg=current_txt_col)
    entry7.config(font=entry_font, bg=current_text_bg, fg=current_txt_col)
    b11.config(font=label_font, bg=current_bg, fg=current_txt_col)

### END BUTTON FUNCTIONS ###

##Canvas and frame set up for scroll
# main frame
main_frame = Frame(root)
main_frame.pack(fill=BOTH, expand=1)

# create canvus within frame
canvas = Canvas(main_frame)
canvas.pack(side=LEFT, fill=BOTH, expand=1)

# create scrollbar
scroll_bar = Scrollbar(main_frame, orient=VERTICAL, command=canvas.yview)
scroll_bar.pack(side=RIGHT, fill=Y)

# config canvaas
canvas.configure(yscrollcommand=scroll_bar.set)
canvas.bind(
    '<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)

# Frame 2 electric boogaloo
showing_frame = Frame(canvas, width=1000, height=100)

# canvas again...
canvas.create_window((0, 0), window=showing_frame, anchor="nw")


##page making

label = tk.Label(showing_frame, text="Welcome to the prototype")

text_box = tk.Text(showing_frame, bd=1, bg="light cyan", height=32, width=52, wrap=tk.WORD)

scrollT = Scrollbar(showing_frame, orient='vertical', command=text_box.yview)
text_box['yscrollcommand'] = scrollT.set

b1 = tk.Button(showing_frame, text="clear", command=lambda: clear_text())

b2 = tk.Button(showing_frame, text="next link", command=lambda: next_link())

labelE1 = Label(showing_frame, text="Start:")

entry1 = tk.Entry(showing_frame, textvariable=entry_txt1, bg="light cyan")

labelE2 = Label(showing_frame, text="End:")

entry2 = tk.Entry(showing_frame, textvariable=entry_txt2, bg="light cyan")

b3 = tk.Button(showing_frame, text="All Text", command=lambda: document_info_base())

b4 = tk.Button(showing_frame, text="Text information specified", command=lambda: document_info())

labelS1 = tk.Label(showing_frame, text="Label size:")

slider1 = Scale(showing_frame, from_=0, to=50, tickinterval=10, length=200, orient=HORIZONTAL, command=slider_1_changed)
slider1.set(14)

labelS2 = tk.Label(showing_frame, text="Written text size:")

slider2 = Scale(showing_frame, from_=0, to=50, tickinterval=10, length=200, orient=HORIZONTAL, command=slider_2_changed)
slider2.set(16)

labelFS1 = tk.Label(showing_frame, text="Enter label font size:")

entry3 = tk.Entry(showing_frame, textvariable=label_size_change, bg="light cyan")

b5 = tk.Button(showing_frame, text="Change font size", height=5, command=lambda: manual_text_change())

labelFS2 = tk.Label(showing_frame, text="Enter text font size:")

entry4 = tk.Entry(showing_frame, textvariable=text_size_change, bg="light cyan")

labelBG1 = tk.Label(showing_frame, text="Choose window background colour:")

back_ground_select = tk.OptionMenu(showing_frame, bg_col, *colours)

labelBG2 = tk.Label(showing_frame, text="Choose entry box background colour:")

entry_box_colour_select = tk.OptionMenu(showing_frame, tb_bg_col, *colours)

labelBG3 = tk.Label(showing_frame, text="Choose text colour:")

entry_text_colour_select = tk.OptionMenu(showing_frame, txt_col, *colours)

b6 = tk.Button(showing_frame, text="Set colours", height=5, command=lambda: manual_colour_change())

LabelF1 = tk.Label(showing_frame, text="Choose label font:")

entry_label_font = tk.OptionMenu(showing_frame, chosen_label_font, *fonts)

LabelF2 = tk.Label(showing_frame, text="Choose written font:")

entry_written_font = tk.OptionMenu(showing_frame, chosen_written_font, *fonts)

b7 = tk.Button(showing_frame, text="Change fonts", height=3, command=lambda: change_fonts())

b8 = tk.Button(showing_frame, text="Update all word formats", command=lambda: pre_update())

LabelPL1 = tk.Label(showing_frame, text="Enter Website name:")

entry5 = tk.Entry(showing_frame, textvariable=web_name, bg="light cyan")

b9 = tk.Button(showing_frame, text="Load Page", command=lambda: soup_maker())

LabelSP = tk.Label(showing_frame, text="Enter what to be spoken:")

entry6 = tk.Entry(showing_frame, textvariable=to_speek_box, bg="light cyan")

b10 = tk.Button(showing_frame, text="Speak!", command=lambda: speak_entry())

lbspeak = tk.Label(showing_frame, text="Speech command input")
entry7 = tk.Entry(showing_frame, textvariable=speek_input, bg="light cyan")
b11 = tk.Button(showing_frame, text="do", command=lambda: speek_command())

#Layout

label.grid(column=0, row=0, columnspan=5, sticky=tk.NS)
text_box.grid(column=0, row=1, rowspan=20, sticky=tk.W)
scrollT.grid(column=1, row=1, rowspan=20, sticky='ns')
b1.grid(column=3, row=1, sticky=tk.W)
b2.grid(column=4, row=1, sticky=tk.E)
labelE1.grid(column=3, row=2, sticky=tk.W)
entry1.grid(column=4, row=2, sticky=tk.E)
labelE2.grid(column=3, row=3, sticky=tk.W)
entry2.grid(column=4, row=3, sticky=tk.E)
b3.grid(column=3, row=4, sticky=tk.W)
b4.grid(column=4, row=4, sticky=tk.E)
labelS1.grid(column=3, row=5, sticky=tk.W)
slider1.grid(column=4, row=5, columnspan=2, sticky=tk.N)
labelS2.grid(column=3, row=6, sticky=tk.W)
slider2.grid(column=4, row=6, columnspan=2, sticky=tk.N)
labelFS1.grid(column=3, row=7, sticky=tk.W)
entry3.grid(column=4, row=7, sticky=tk.NS)
b5.grid(column=5, row=7, rowspan=2, sticky=tk.E)
labelFS2.grid(column=3, row=8, sticky=tk.W)
entry4.grid(column=4, row=8, sticky=tk.NS)
labelBG1.grid(column=3, row=9, sticky=tk.W)
back_ground_select.grid(column=4, row=9, sticky=tk.N)
b6.grid(column=5, row=9, rowspan=3, sticky=tk.E)
labelBG2.grid(column=3, row=10, sticky=tk.W)
entry_box_colour_select.grid(column=4, row=10, sticky=tk.N)
labelBG3.grid(column=3, row=11, sticky=tk.W)
entry_text_colour_select.grid(column=4, row=11, sticky=tk.N)
LabelF1.grid(column=3, row=12, sticky=tk.W)
entry_label_font.grid(column=4, row=12, sticky=tk.NS)
b7.grid(column=5, row=12, rowspan=2, sticky=tk.E)
LabelF2.grid(column=3, row=13, sticky=tk.W)
entry_written_font.grid(column=4, row=13, sticky=tk.NS)
b8.grid(column=3, row=14, sticky=tk.NS, columnspan=2)
LabelPL1.grid(column=3, row=15, sticky=W)
entry5.grid(column=4, row=15, sticky=N)
b9.grid(column=5, row=15, sticky=E)
LabelSP.grid(column=3, row=16, stick=W)
entry6.grid(column=4, row=16, sticky=NS)
b10.grid(column=5, row=16, sticky=E)
lbspeak.grid(column=3, row=17, sticky=W)
entry7.grid(column=4, row=17, sticky=NS)
b11.grid(column=5, row=17, sticky=E)

root.mainloop()
