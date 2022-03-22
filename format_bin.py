import codecs
import os
from typing import final
import format_dat
from hacktools import common, nds

binrange = [(0x88f54, 0x92c00)]


def extract(data):
    binfile = data + "extract/arm9.bin"
    binout = data + "bin_output.txt"
    fontout = data + "font_output.txt"

    nds.extractBIN(binrange, encoding="shift_jis", binin=binfile, binfile=binout, readfunc=format_dat.readShiftJISBIN)
    common.logMessage("Extracting FONT to", fontout, "...")
    with codecs.open(fontout, "w", "utf-8") as out:
        with common.Stream(binfile, "rb") as f:
            f.seek(0x8b068)
            while f.tell() < 0x8c048:
                charcode = f.read(2)[::-1]
                f.seek(-2, 1)
                charcodehex = f.readUShort()
                index = f.readUShort()
                common.logDebug(common.toHex(f.tell()), common.toHex(charcodehex), common.toHex(index))
                out.write(charcode.decode("shift_jis") + "=" + str(index) + "\n")
    common.logMessage("Done!")


class ARMSection:
    def __init__(self):
        self.start = 0
        self.size = 0
        self.bsssize = 0
        self.datastart = 0


def repack(data):
    binin = data + "extract/arm9.bin"
    header = data + "extract/header.bin"
    binout = data + "repack/arm9.bin"
    common.copyFile(binin, binout)
    with codecs.open(data + "fontconfig.txt", "r", "utf-8") as f:
        section = common.getSection(f, "")
    with common.Stream(data + "fontdata.bin", "wb") as f:
        for c in section:
            f.write(c.replace("～", "〜").encode("shift_jis"))
            f.writeUShort(int(section[c][0]))
    common.armipsPatch(common.bundledFile("bin_patch.asm"))
