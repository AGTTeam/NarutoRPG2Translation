import codecs
import os
from typing import final
import format_dat
from hacktools import common, nds

binrange = [(0x88f54, 0x9118c), (0x91194, 0x91978), (0x91998, 0x92c00)]
freeranges = [(0x92fc0+0x700, 0x92fc0+0x1000, True)]


def extract(data):
    binfile = data + "extract/arm9.bin"
    binout = data + "bin_output.txt"
    fontout = data + "font_output.txt"

    nds.extractBIN(binrange, encoding="shift_jis", binin=binfile, binfile=binout, readfunc=format_dat.readShiftJISBIN, writepos=True)
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


def repack(data):
    binin = data + "extract/arm9.bin"
    headerin = data + "extract/header.bin"
    headerout = data + "repack/header.bin"
    binfile = data + "bin_input.txt"
    binout = data + "repack/arm9.bin"
    nds.expandBIN(binin, binout, headerin, headerout, 0x1000, 0x1ff9000)
    for post in ["", "small"]:
        with codecs.open(data + "fontconfig" + post + ".txt", "r", "utf-8") as f:
            section = common.getSection(f, "", inorder=True)
            with common.Stream(data + "fontdata" + post + ".bin", "wb") as f:
                for c in section:
                    f.write(c["name"].replace("～", "〜").encode("shift_jis"))
                    f.writeUShort(int(c["value"]))
                f.writeUShort(0)
                f.writeUShort(8)
    nds.repackBIN(binrange, freeranges, format_dat.readShiftJISBIN, format_dat.writeShiftJISBIN, "shift_jis", "#", binin, binout, binfile, injectstart=0x1ff9000 - 0x92fc0, nocopy=True)
    common.armipsPatch(common.bundledFile("bin_patch.asm"))
