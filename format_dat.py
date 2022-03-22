import codecs
import os
from hacktools import common

wordwrap = 190


def extract(data):
    datfolder = data + "extract/data/rom/text/msg/"
    outfolder = data + "dat_output/"
    common.logMessage("Extracting DAT to", outfolder, "...")
    common.makeFolder(outfolder)
    for file in common.showProgress(common.getFiles(datfolder)):
        common.logDebug("Processing", file)
        filesize = os.path.getsize(datfolder + file)
        common.makeFolders(outfolder + os.path.dirname(file))
        with codecs.open(outfolder + file, "w", "utf-8") as out:
            with common.Stream(datfolder + file, "rb") as f:
                fixedsize = fixedLength(file)
                if fixedsize > 0:
                    i = 0
                    foundstr = []
                    while True:
                        f.seek(i * fixedsize)
                        if f.tell() >= filesize:
                            break
                        sjis = readShiftJIS(f)
                        if sjis not in foundstr:
                            foundstr.append(sjis)
                            if sjis != "":
                                out.write(sjis + "=\n")
                        if "msg_f_iteminst" in file:
                            f.seek(i * fixedsize + 0x6a)
                            sjis = readShiftJIS(f)
                            if sjis not in foundstr:
                                foundstr.append(sjis)
                                if sjis != "":
                                    out.write(sjis + "=\n")
                        i += 1
                else:
                    ptrnum = f.readUInt()
                    for i in range(ptrnum):
                        f.seek(4 + i * 2)
                        ptr = f.readUShort()
                        f.seek(ptr)
                        sjis = readShiftJIS(f)
                        common.logDebug(sjis)
                        if sjis.endswith("$$"):
                            sjis = sjis[:-2]
                        if sjis.endswith("|"):
                            sjis = sjis[:-1]
                        common.logDebug(sjis)
                        common.logDebug("Reading ptr", i, "at", common.toHex(ptr), sjis)
                        sjissplit = sjis.split("$$$")
                        for subsjis in sjissplit:
                            if subsjis.endswith("|"):
                                subsjis = subsjis[:-1]
                            if subsjis != "":
                                out.write(subsjis + "=\n")
    common.logMessage("Done!")


def repack(data):
    datin = data + "extract/data/rom/text/msg/"
    datout = data + "repack/data/rom/text/msg/"
    fontconfig = data + "fontconfig.txt"
    infolder = data + "dat_input/"
    chartot = transtot = 0

    if not os.path.isdir(infolder):
        common.logError("Input folder", infolder, "not found")
        return

    sections = {}
    common.logMessage("Repacking DAT from", infolder, "...")
    glyphs = readFontGlyphs(fontconfig)
    for file in common.getFiles(infolder):
        if os.path.isfile(file.replace("/", "/[COMPLETE]")) or os.path.isfile(file.replace("/", "/[TEST]")):
            continue
        filename = file.replace("[COMPLETE]", "").replace("[TEST]", "")
        with codecs.open(infolder + file, "r", "utf-8") as input:
            section = common.getSection(input, "")
            chartot, transtot = common.getSectionPercentage(section, chartot, transtot)
            sections[filename] = section
    common.makeFolder(datout)
    for file in common.showProgress(common.getFiles(datin)):
        common.logDebug("Processing", file)
        filesize = os.path.getsize(datin + file)
        common.makeFolders(datout + os.path.dirname(file))
        common.copyFile(datin + file, datout + file)
        with common.Stream(datin + file, "rb") as fin:
            with common.Stream(datout + file, "rb+") as f:
                fixedsize = fixedLength(file)
                if fixedsize > 0:
                    i = 0
                    while True:
                        fin.seek(i * fixedsize)
                        f.seek(fin.tell())
                        if fin.tell() >= filesize:
                            break
                        if sjis != "":
                            sjis = getTranslation(sections, file, readShiftJIS(fin))
                        if "msg_f_iteminst" in file:
                            writeShiftJIS(f, sjis, 0x6a - 2)
                            fin.seek(i * fixedsize + 0x6a)
                            f.seek(fin.tell())
                            if sjis != "":
                                sjis = getTranslation(sections, file, readShiftJIS(fin))
                            writeShiftJIS(f, sjis, 0x36 - 2)
                        else:
                            writeShiftJIS(f, sjis, fixedsize - 2)
                        i += 1
                else:
                    ptrnum = fin.readUInt()
                    f.seek(0x404)
                    for i in range(ptrnum):
                        fin.seek(4 + i * 2)
                        ptr = fin.readUShort()
                        fin.seek(ptr)
                        sjis = readShiftJIS(fin)
                        add1 = add2 = False
                        if sjis.endswith("$$"):
                            sjis = sjis[:-2]
                            add1 = True
                        if sjis.endswith("|"):
                            sjis = sjis[:-1]
                            add2 = True
                        sjissplit = sjis.split("$$$")
                        for j in range(len(sjissplit)):
                            add3 = False
                            if sjissplit[j].endswith("|"):
                                sjissplit[j] = sjissplit[j][:-1]
                                add3 = True
                            if sjissplit[j] != "":
                                sjissplit[j] = getTranslation(sections, file, sjissplit[j])
                                prewrap = sjissplit[j]
                                sjissplit[j] = common.wordwrap(sjissplit[j], glyphs, wordwrap, detectTextCode)
                                common.logMessage(prewrap, sjissplit[j])
                            if add3:
                                sjissplit[j] += "|"
                        sjis = "$$$".join(sjissplit)
                        if add2:
                            sjis += "|"
                        if add1:
                            sjis += "$$"
                        f.writeUShortAt(4 + i * 2, f.tell())
                        writeShiftJIS(f, sjis)
    common.logMessage("Done!")


def getTranslation(sections, file, sjis):
    if sjis in sections[file] and sections[file][sjis][0] != "":
        return sections[file][sjis][0]
    for sectionfile in sections:
        if sjis in sections[sectionfile] and sections[sectionfile][sjis][0] != "":
            return sections[sectionfile][sjis][0]
    return sjis


def detectTextCode(s, i=0):
    if s[i] == "<":
        return len(s[i:].split(">", 1)[0]) + 1
    return 0


def readFontGlyphs(file):
    glyphs = {}
    with codecs.open(file, "r", "utf-8") as f:
        fontconfig = common.getSection(f, "")
        asciicount = 0x20
        for c in fontconfig:
            charlen = int(fontconfig[c][0])
            glyph = common.FontGlyph(0, charlen, charlen)
            glyphs[c] = glyph
            if asciicount < 0x7f:
                glyphs[chr(asciicount)] = glyph
                asciicount += 1
    return glyphs


def fixedLength(file):
    size = 0
    if "msginst" in file or "msgmenu" in file or "msgchrname" in file:
        size = 0x6a
        if "msgchrname" in file:
            size = 0xc
        elif "msg_menufield." in file:
            size = 0x16
        elif "msg_menujinkei" in file:
            size = 0x36
        elif "msg_f_iteminst" in file or "msg_f_jyutuinst" in file:
            size = 0xa0
    return size


speakercodes = {
    0x00: "naruto",
    0x01: "sasuke",
    0x02: "sakura",
    0x03: "shikamaru",
    0x04: "choji",
    0x05: "kiba",
    0x06: "neji",
    0x07: "lee",
    0x08: "gaara",
    0x09: "temari",
    0x0a: "kankuro",
    0x0b: "jiraiya",
    0x0c: "tsunade",
    0x0d: "orochimaru",
    0x0e: "kakashi",
    0x0f: "ino",
    0x10: "shino",
    0x11: "hinata",
    0x12: "tenten",
    0x13: "itachi",
    0x14: "kisame",
    0x15: "kabuto",
    0x16: "jirobo",
    0x17: "kidomaru",
    0x18: "takuya",
    0x19: "sakon",
    0x1a: "kimimaro",
    0x1b: "guy",
    0x1c: "asuma",
    0x1d: "kurenai",
    0x1e: "shizune",
    0x1f: "akamaru",
    0x20: "akamaru2",
    0x21: "ibiki",
    0x22: "anko",
    0x23: "iruka",
    0x24: "konohamaru",
    0x25: "ebisu",
    0x26: "teuchi",
    0x27: "mizuki",
    0x28: "tazuna",
    0x29: "inari",
    0x2a: "homura",
    0x2b: "koharu",
    0x2c: "tonton",
    0x2d: "pakkun",
    0x2e: "gamakichi",
    0x2f: "gamatatsu",
    0x30: "katsuyu",
    0x31: "girlnaruto",
    0x32: "sasuke2",
    0x33: "naruto2",
    0x34: "sasuke3",
    0x35: "sasuke4",
    0x36: "sakura2",
    0x37: "ino2",
    0x38: "kakashi2",
    0x39: "itachi2",
    0x3a: "sasuke5",
    0x3b: "sasuke6",
    0x3c: "bunta",
    0x3d: "manda",
    0x3e: "???",
    0x3f: "naruto3",
    0xff: "narrator",
}
speakercodesrev = {v: k for k, v in speakercodes.items()}

colorcodes = {
    0x30: "black",
    0x31: "gray",
    0x32: "blue",
    0x33: "red",
    0x34: "black2",
    0x35: "gray2",
    0x36: "blue2",
    0x37: "red2",
}
colorcodesrev = {v: k for k, v in colorcodes.items()}


def readShiftJISBIN(f, encoding="shift_jis"):
    return readShiftJIS(f, encoding, False)


def readShiftJIS(f, encoding="shift_jis", allowunk=True):
    sjis = ""
    i = 0
    while True:
        b1 = f.readByte()
        if b1 == 0x00:
            break
        elif b1 == 0x0a:
            sjis += "|"
            i += 1
        elif b1 == 0x0b:
            sjis += "<0B>"
            i += 1
        else:
            b2 = f.readByte()
            if b1 == 0x7:
                if b2 in colorcodes:
                    colorcode = colorcodes[b2]
                else:
                    colorcode = "c" + common.toHex(b2)
                sjis += "<" + colorcode + ">"
            elif b1 == 0x5:
                sjis += "<w" + str(b2) + ">"
            elif b1 == 0x6:
                sjis += "<sound" + common.toHex(b2) + ">"
            elif b1 == 0x9:
                if b2 == 0x01:
                    sjis += "<instant>"
                else:
                    sjis += "<09" + common.toHex(b2) + ">"
            elif b1 == 0xe:
                sjis += "<symbol" + common.toHex(b2) + ">"
            elif b1 == 0xf or b1 == 0x10:
                if b2 in speakercodes:
                    speakercode = speakercodes[b2]
                else:
                    speakercode = "s" + common.toHex(b2)
                add = "small_" if b1 == 0xf else ""
                sjis += "<" + add + speakercode + ">"
            elif b1 == 0x13:
                if not allowunk:
                    return ""
                sjis += "<13" + common.toHex(b2) + ">"
            elif b1 == 0x14:
                b3 = f.readByte()
                sjis += "<14" + common.toHex(b2) + common.toHex(b3) + ">"
            elif not common.checkShiftJIS(b1, b2):
                if not allowunk and b1 > 0x4:
                    return ""
                f.seek(-1, 1)
                sjis += "<" + common.toHex(b1) + ">"
                i += 1
            else:
                f.seek(-2, 1)
                try:
                    sjis += f.read(2).decode(encoding).replace("〜", "～")
                except UnicodeDecodeError:
                    if not allowunk:
                        return ""
                    common.logError("[ERROR] UnicodeDecodeError")
                    sjis += "[ERROR" + str(f.tell() - 2) + "]"
                i += 2
    sjis = sjis.replace("<03><01>", "$$")
    sjis = sjis.replace("$$<04>", "$$$")
    return sjis


def writeShiftJIS(f, s, maxlen=-1):
    common.logDebug("Writing", s, "at", common.toHex(f.tell()))
    s = s.replace("～", "〜")
    s = s.replace("$$$", "$$<04>")
    s = s.replace("$$", "<03><01>")
    i = 0
    x = 0
    while x < len(s):
        c = s[x]
        if c == "|":
            if maxlen > 0 and i + 1 > maxlen:
                common.logError("Line too long", s, maxlen)
                break
            f.writeByte(0xa)
            x += 1
            i += 1
        elif c == "<":
            code = s[x+1:].split(">", 1)[0]
            x += len(code) + 2
            if code in colorcodesrev:
                if maxlen > 0 and i + 2 > maxlen:
                    common.logError("Line too long", s, maxlen)
                    break
                i += 2
                f.writeByte(0x7)
                f.writeByte(colorcodesrev[code])
            elif code.startswith("small_") or code in speakercodesrev:
                if maxlen > 0 and i + 2 > maxlen:
                    common.logError("Line too long", s, maxlen)
                    break
                i += 2
                if code.startswith("small_"):
                    code = code[6:]
                    f.writeByte(0xf)
                else:
                    f.writeByte(0x10)
                f.writeByte(speakercodesrev[code])
            elif code.startswith("sound"):
                if maxlen > 0 and i + 2 > maxlen:
                    common.logError("Line too long", s, maxlen)
                    break
                code = code[5:]
                i += 2
                f.writeByte(0x6)
                f.writeByte(int(code, 16))
            elif code.startswith("symbol"):
                if maxlen > 0 and i + 2 > maxlen:
                    common.logError("Line too long", s, maxlen)
                    break
                code = code[6:]
                i += 2
                f.writeByte(0xe)
                f.writeByte(int(code, 16))
            elif code.startswith("w"):
                if maxlen > 0 and i + 2 > maxlen:
                    common.logError("Line too long", s, maxlen)
                    break
                code = code[1:]
                i += 2
                f.writeByte(0x5)
                f.writeByte(int(code))
            elif code == "instant":
                if maxlen > 0 and i + 2 > maxlen:
                    common.logError("Line too long", s, maxlen)
                    break
                i += 2
                f.writeByte(0x9)
                f.writeByte(0x1)
            else:
                nbytes = len(code) // 2
                if maxlen > 0 and i + nbytes > maxlen:
                    common.logError("Line too long", s, maxlen)
                    break
                i += nbytes
                f.write(bytes.fromhex(code))
        else:
            if maxlen > 0 and i + 2 > maxlen:
                common.logError("Line too long", s, maxlen)
                break
            x += 1
            i += 2
            f.write(c.encode("shift_jis"))
    f.writeByte(0)
    common.logDebug("Done!")
