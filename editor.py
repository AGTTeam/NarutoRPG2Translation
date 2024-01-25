import codecs
import customtkinter
import os
import tkinter
from PIL import Image
from hacktools import common
import format_dat


class CustomTextBox(customtkinter.CTkTextbox):
    def insert(self, index, text, tags=None):
        if not hasattr(self, "oldtext"):
            self.oldtext = text.strip()
            self.callback(self.lbl, self.speaker, self.oldtext)
        return super().insert(index, text, tags)

    def _check_if_scrollbars_needed(self, event=None, continue_loop: bool = False):
        super()._check_if_scrollbars_needed(event, continue_loop)
        if not hasattr(self, "oldtext") or not hasattr(self, "lbl"):
            return
        currenttext = self._textbox.get(1.0, tkinter.END).strip()
        if currenttext != self.oldtext:
            self.oldtext = currenttext
            self.callback(self.lbl, self.speaker, currenttext)
        


class EditorFrame(customtkinter.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.items = []
        self.idtochar = {}
        self.chartolen = {}
        self.chartosjis = {}
        self.font = {}
        
        originalfontpath = "NarutoRPG2Data/out_FONT/sys_bg_a_00"
        workfontpath = "NarutoRPG2Data/work_FONT/sys_bg_a_00"
        fontoutput = "NarutoRPG2Data/font_input.txt"
        fontconfig = "NarutoRPG2Data/fontconfig.txt"

        self.bg1 = Image.open("editor1.png")
        self.bg1 = self.bg1.convert("RGBA")
        self.bg2 = Image.open("editor2.png")
        self.bg2 = self.bg2.convert("RGBA")

        with codecs.open(fontoutput, "r", "utf-8") as input:
            section = common.getSection(input, "", inorder=True)
            for fontid in section:
                if fontid["value"] == "":
                    continue
                self.idtochar[int(fontid["value"])] = fontid["name"]
        with codecs.open(fontconfig, "r", "utf-8") as input:
            section = common.getSection(input, "", inorder=True)
            currentchar = 32
            for fontlen in section:
                self.chartolen[fontlen["name"]] = int(fontlen["value"])
                self.chartosjis[chr(currentchar)] = fontlen["name"]
                currentchar += 1
        self.glyphs = format_dat.readFontGlyphs(fontconfig)

        j = 0
        for i in range(1, 3):
            for file in common.getFiles(originalfontpath + str(i) + "/"):
                if os.path.isfile(workfontpath + str(i) + "/" + file):
                    img = Image.open(workfontpath + str(i) + "/" + file)
                else:
                    img = Image.open(originalfontpath + str(i) + "/" + file)
                img = img.convert("RGBA")
                self.font[self.idtochar[j]] = img
                j += 1
                if j not in self.idtochar:
                    break
    

    def generateImage(self, lbl, speaker, text):
        if speaker == "narrator":
            img = self.bg1.copy()
            startx = 15
            starty = 16
            wordwrap = format_dat.wordwrap
        else:
            img = self.bg2.copy()
            startx = 48
            starty = 16
            wordwrap = format_dat.wordwrap2
        currentx = startx
        currenty = starty
        wordwrapped = common.wordwrap(text, self.glyphs, wordwrap, format_dat.detectTextCode, strip=False)
        if wordwrapped.count("|") > 1:
            old_img = img
            img = Image.new("RGBA", (old_img.width, old_img.height * 2))
            img.paste(old_img, (0, 0))
            img.paste(old_img, (0, old_img.height))
        i = 0
        while i < len(wordwrapped):
            c = wordwrapped[i]
            if c == "#":
                break
            if c == "<":
                textcode = wordwrapped[i:].split(">", 1)[0]
                # TODO handle colors
                i += len(textcode) + 1
                continue
            if c == "|":
                currentx = startx
                if currenty == starty + 16:
                    currenty = self.bg2.height + starty
                else:
                    currenty += 16
                i += 1
                continue
            if c == '\'':
                c = "^"
            if c in self.chartosjis:
                # ASCII character, use VWF
                c = self.chartosjis[c]
                charwidth = self.chartolen[c]
            else:
                charwidth = 8
            if c not in self.font:
                common.logMessage("Char not found", c)
                currentx += 8
                i += 1
                continue
            charglyph = self.font[c]
            img.paste(charglyph, (currentx, currenty), charglyph)
            currentx += charwidth
            i += 1
        ctkimg = customtkinter.CTkImage(dark_image=img, size=(img.width, img.height))
        lbl.configure(image=ctkimg)
        lbl.image = ctkimg


    def extractSpeaker(self, line):
        for speaker in format_dat.speakercodesrev:
            if ("<" + speaker + ">" in line):
                self.currentspeaker = speaker
                return speaker
        return self.currentspeaker


    def openFile(self, filepath):
        for child in self.winfo_children():
            child.destroy()
        self.alltexts = []
        row = 0
        self.currentspeaker = "narrator"
        self.filepath = filepath
        with codecs.open(filepath, "r", "utf-8") as input:
            section = common.getSection(input, "", comment="#ignore#comments", inorder=True)
        for line in section:
            lbl = customtkinter.CTkLabel(self, text="")
            lbl.grid(row=row, column=0, padx=10, pady=5)
            text = CustomTextBox(self, width=400, height=65)
            text.lbl = lbl
            text.callback = self.generateImage
            text.speaker = self.extractSpeaker(line["name"])
            text.insert(tkinter.END, line["value"])
            text.grid(row=row, column=1, padx=10, pady=5)
            text2 = customtkinter.CTkTextbox(self, width=400, height=65)
            text2.insert(tkinter.END, line["name"])
            text2.grid(row=row, column=2, padx=10, pady=5)
            self.alltexts.append((text, text2))
            row += 1


class EditorApp(customtkinter.CTk):
    def __init__(self, version):
        super().__init__()
        self.title("NarutoRPGTranslation v" + version + " Editor")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.topframe = customtkinter.CTkFrame(self, height=35, corner_radius=0)
        self.topframe.grid(row=0, column=0, padx=10, pady=0, sticky="nw")
        self.topframe.grid_columnconfigure(0, weight=1)
        self.openbutton = customtkinter.CTkButton(self.topframe, border_width=2, width=70, text="Open", command=self.open)
        self.openbutton.grid(row=0, column=0, padx=10, pady=2)
        self.savebutton = customtkinter.CTkButton(self.topframe, border_width=2, width=70, text="Save", command=self.save)
        self.savebutton.grid(row=0, column=1, padx=10, pady=2)
        self.editorframe = EditorFrame(master=self, width=256+400+400+50, height=800, corner_radius=0, fg_color="transparent")
        self.editorframe.grid(row=1, column=0, sticky="nsew")
        self.editorframe.openFile("NarutoRPG2Data/dat_input/msgmap/msg_map_dj_02ao.dat")

    def open(self):
        file = tkinter.filedialog.askopenfilename(initialdir="NarutoRPG2Data/dat_input/msgmap", filetypes=[('DAT files', '*.dat')])
        if file is not None:
            self.editorframe.openFile(file)

    def save(self):
        with codecs.open(self.editorframe.filepath, "w", "utf-8") as output:
            for alltext in self.editorframe.alltexts:
                output.write(alltext[1]._textbox.get(1.0, tkinter.END).strip())
                output.write("=")
                output.write(alltext[0]._textbox.get(1.0, tkinter.END).strip())
                output.write("\n")
