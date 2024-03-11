import codecs
import os
from hacktools import common

# Wordwrapping values, one is bigger for voice lines without a speaker image
wordwrap = 206
wordwrap2 = 176
# Wordwrapping value for formation help
wordwrapformation = 112
# Wordwrapping value for battle help (item/jutsu)
wordwrapbattle = 118
# Wordwrapping value for battle messages
wordwrapbattlemsg = 206


def extract(data):
    datfolder = data + "extract/data/rom/text/"
    outfolder = data + "dat_output/"
    common.logMessage("Extracting DAT to", outfolder, "...")
    common.makeFolder(outfolder)
    for file in common.showProgress(common.getFiles(datfolder)):
        if file.startswith("event/"):
            continue
        common.logDebug("Processing", file)
        filesize = os.path.getsize(datfolder + file)
        outfile = file[4:] if file.startswith("msg/") else file
        fixedsize = fixedmax = 0
        if file in fixedfiles:
            fixedsize, fixedmax = fixedfiles[file]
        if file.startswith("param/") and fixedsize == 0:
            continue
        common.makeFolders(outfolder + os.path.dirname(outfile))
        with codecs.open(outfolder + outfile, "w", "utf-8") as out:
            with common.Stream(datfolder + file, "rb") as f:
                if fixedsize > 0:
                    i = 0
                    foundstr = []
                    maxlen = 0
                    maxlen2 = 0
                    minlenzero = 0xffff
                    while True:
                        f.seek(i * fixedsize)
                        if f.tell() >= filesize:
                            break
                        sjis = readShiftJIS(f)
                        strend = f.tell()
                        # Check what the maximum length of the strings is
                        strlen = strend - (i * fixedsize)
                        if strlen > maxlen:
                            maxlen = strlen
                        while f.tell() < filesize and f.peek(1)[0] == 0:
                            f.seek(1, 1)
                        strlenzero = f.tell() - 1 - (i * fixedsize)
                        if strlenzero < minlenzero:
                            minlenzero = strlenzero
                        f.seek(strend)
                        # Write the string in the file
                        if sjis not in foundstr:
                            foundstr.append(sjis)
                            if sjis != "":
                                out.write(sjis + "=\n")
                        # This particular file has two strings for each item
                        if "msg_f_iteminst" in file or "msg_f_jyutuinst" in file:
                            f.seek(i * fixedsize + 0x6a)
                            sjis = readShiftJIS(f)
                            strlen = f.tell() - (i * fixedsize + 0x6a)
                            if strlen > maxlen2:
                                maxlen2 = strlen
                            if sjis not in foundstr:
                                foundstr.append(sjis)
                                if sjis != "":
                                    out.write(sjis + "=\n")
                        i += 1
                    common.logDebug("Maximum string length for", file, "is", common.toHex(maxlen), common.toHex(maxlen2), common.toHex(minlenzero))
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
                        # There's a bugged line in the msg_map_mp_022s file that we need to tweak manually
                        if "<03><naruto>" in sjis:
                            sjis = sjis.replace("<03><naruto>", "$$$")
                        common.logDebug(sjis)
                        common.logDebug("Reading ptr", i, "at", common.toHex(ptr), sjis)
                        sjissplit = sjis.split("$$$")
                        for subsjis in sjissplit:
                            if subsjis.endswith("|"):
                                subsjis = subsjis[:-1]
                            if subsjis != "":
                                if "msg_staffroll" in file:
                                    out.write(subsjis + "\n")
                                else:
                                    out.write(subsjis + "=\n")
    common.logMessage("Done!")


def repack(data):
    datin = data + "extract/data/rom/text/"
    datout = data + "repack/data/rom/text/"
    fontconfig = data + "fontconfig.txt"
    infolder = data + "dat_input/"
    chartot = transtot = 0

    if not os.path.isdir(infolder):
        common.logError("Input folder", infolder, "not found")
        return

    sections = {}
    speakercodevalues = speakercodes.values()
    common.logMessage("Repacking DAT from", infolder, "...")
    glyphs = readFontGlyphs(fontconfig)
    allstaffroll = []
    for file in common.getFiles(infolder):
        if os.path.isfile(file.replace("/", "/[COMPLETE]")) or os.path.isfile(file.replace("/", "/[TEST]")):
            continue
        filename = file[4:] if file.startswith("msg/") else file
        filename = filename.replace("[COMPLETE]", "").replace("[TEST]", "")
        if "#" in filename:
            filename = filename.split("#")[0] + ".dat"
        with codecs.open(infolder + file, "r", "utf-8") as input:
            if "msg_staffroll" in filename:
                for line in input:
                    allstaffroll.append(line.rstrip("\r\n").replace("\ufeff", ""))
            else:
                section = common.getSection(input, "")
                chartot, transtot = common.getSectionPercentage(section, chartot, transtot)
                sections[filename] = section
    common.makeFolder(datout)
    for file in common.showProgress(common.getFiles(datin)):
        filesize = os.path.getsize(datin + file)
        common.makeFolders(datout + os.path.dirname(file))
        common.copyFile(datin + file, datout + file)
        if file.startswith("event/"):
            continue
        common.logDebug("Processing", file)
        filename = file[4:] if file.startswith("msg/") else file
        fixedsize = fixedmax = 0
        if file in fixedfiles:
            fixedsize, fixedmax = fixedfiles[file]
        if file.startswith("param/") and fixedsize == 0:
            continue
        with common.Stream(datin + file, "rb") as fin:
            with common.Stream(datout + file, "rb+") as f:
                if fixedsize > 0:
                    i = 0
                    while True:
                        fin.seek(i * fixedsize)
                        f.seek(fin.tell())
                        if fin.tell() >= filesize:
                            break
                        sjis = getTranslation(sections, filename, readShiftJIS(fin))
                        if "msg_f_iteminst" in filename or "msg_f_jyutuinst" in filename:
                            writeShiftJIS(f, sjis, fixedmax)
                            fin.seek(i * fixedsize + 0x6a)
                            f.seek(fin.tell())
                            sjis = getTranslation(sections, filename, readShiftJIS(fin))
                            writeShiftJIS(f, sjis, 0x35)
                        else:
                            if "msg_menufieldcmd" in filename:
                                sjis = common.wordwrap(sjis, glyphs, wordwrap, detectTextCode, strip=False)
                            elif "msg_menujinkei" in filename:
                                sjis = common.wordwrap(sjis, glyphs, wordwrapformation, detectTextCode, strip=False)
                            elif "msg_b_jyutuinst" in filename or ("msg_b_iteminst" in filename and i < 54):
                                sjis = common.wordwrap(sjis, glyphs, wordwrapbattle, detectTextCode, strip=False)
                            elif "msg_f_kumiteinst" in filename:
                                sjis = common.wordwrap(sjis, glyphs, wordwrap, detectTextCode, strip=False)
                            writeShiftJIS(f, sjis, fixedmax)
                        i += 1
                else:
                    ptrnum = fin.readUInt()
                    f.seek(0x404)
                    for i in range(ptrnum):
                        fin.seek(4 + i * 2)
                        ptr = fin.readUShort()
                        fin.seek(ptr)
                        sjis = readShiftJIS(fin)
                        add1 = add2 = buggedline = False
                        if sjis.endswith("$$"):
                            sjis = sjis[:-2]
                            add1 = True
                        if sjis.endswith("|"):
                            sjis = sjis[:-1]
                            add2 = True
                        # There's a bugged line in the msg_map_mp_022s file that we need to tweak manually
                        if "<03><naruto>" in sjis:
                            sjis = sjis.replace("<03><naruto>", "$$$")
                            buggedline = True
                        sjissplit = sjis.split("$$$")
                        usewordwrap = wordwrap
                        for j in range(len(sjissplit)):
                            add3 = False
                            if sjissplit[j].endswith("|"):
                                sjissplit[j] = sjissplit[j][:-1]
                                add3 = True
                            if sjissplit[j] != "":
                                if "msg_staffroll" in filename:
                                    sjissplit[j] = allstaffroll.pop(0).split("#")[0]
                                else:
                                    sjissplit[j] = getTranslation(sections, filename, sjissplit[j])
                                maxlines = 2
                                # Check if the string starts with a speaker
                                if sjissplit[j].startswith(">>"):
                                    usewordwrap = wordwrap
                                    sjissplit[j] = sjissplit[j].lstrip(">")
                                else:
                                    checkspeaker = sjissplit[j]
                                    if checkspeaker != "":
                                        while checkspeaker[0] == "<":
                                            speakercode = checkspeaker.split(">")[0][1:]
                                            if speakercode != "narrator" and (speakercode in speakercodevalues or speakercode.replace("small_", "") in speakercodevalues):
                                                usewordwrap = wordwrap2
                                                break
                                            else:
                                                checkspeaker = checkspeaker[len(speakercode) + 2:]
                                    if "msgbattle/" in filename:
                                        maxlines = 1
                                        usewordwrap = wordwrapbattlemsg
                                    if "msg_staffroll" in filename:
                                        maxlines = 999
                                sjissplit[j] = common.wordwrap(sjissplit[j], glyphs, usewordwrap, detectTextCode, strip=False)
                                if sjissplit[j].count("|") > maxlines - 1:
                                    common.logWarning("Line \"" + sjissplit[j] + "\"has too many line breaks, splitting...")
                                    if maxlines == 2:
                                        tmp = sjissplit[j].split("|")
                                        sjissplit[j] = ""
                                        while len(tmp) > 0:
                                            if sjissplit[j] != "":
                                                sjissplit[j] += "$$$"
                                            if len(tmp) == 1:
                                                sjissplit[j] += tmp[0]
                                                tmp = tmp[1:]
                                            else:
                                                sjissplit[j] += tmp[0] + "|" + tmp[1]
                                                tmp = tmp[2:]
                                    else:
                                        tmp = sjissplit[j].split("|")
                                        sjissplit[j] = "$$$".join(tmp)
                                    common.logWarning(" \"" + sjissplit[j] + "\"")
                            if add3:
                                sjissplit[j] += "|"
                        sjis = "$$$".join(sjissplit)
                        if buggedline:
                            sjis = sjis.replace("$$$", "<03><naruto>")
                        if add2:
                            sjis += "|"
                        if add1:
                            sjis += "$$"
                        f.writeUShortAt(4 + i * 2, f.tell())
                        writeShiftJIS(f, sjis)
    common.logMessage("Done! Translation is at {0:.2f}%".format((100 * transtot) / chartot))


def getTranslation(sections, file, sjis):
    if file not in sections:
        return sjis
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


# A list of the files with fixed sizes and hardcoded lengths
# The tuple is (item size, max str size)
# The max values are pretty conservative to avoid issues
fixedfiles = {
    "msg/msgchrname/msg_chrname.dat": (0xc, 0xb),
    "msg/msginst/msg_b_iteminst.dat": (0x6a, 0x34),
    "msg/msginst/msg_b_jyutuinst.dat": (0x6a, 0x34),
    "msg/msginst/msg_f_extraiteminst.dat": (0x6a, 0x5c),
    "msg/msginst/msg_f_iteminst.dat": (0xa0, 0x54),
    "msg/msginst/msg_f_jyutuinst.dat": (0xa0, 0x34),
    "msg/msginst/msg_f_kumiteinst.dat": (0x6a, 0x54),
    "msg/msginst/msg_fieldhelpinst.dat": (0x6a, 0x11),
    "msg/msgmenu/msg_menudougu.dat": (0x6a, 0x31),
    "msg/msgmenu/msg_menufield.dat": (0x16, 0x15),
    "msg/msgmenu/msg_menufieldcmd.dat": (0x6a, 0x5c),
    "msg/msgmenu/msg_menujinkei.dat": (0x36, 0x34),
    "msg/msgmenu/msg_menujyutu.dat": (0x6a, 0x25),
    "msg/msgmenu/msg_menusoubi.dat": (0x6a, 0x2d),
    "param/item_data.dat": (0xbc, 0x19),
    "param/jyutu_data.dat": (0x2c, 0x19),
    "param/kumite_data.dat": (0x4c, 0x19),
    "param/mon_param.dat": (0xd4, 0x11),
}


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
            elif b1 == 0x1 and b2 == 0x30:
                sjis += "<0130>"
            elif b1 == 0x2:
                sjis += "<u" + str(b2) + ">"
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
                sjis += "<13" + common.toHex(b2) + ">"
            elif b1 == 0x14:
                b3 = f.readByte()
                sjis += "<14" + common.toHex(b2) + common.toHex(b3) + ">"
            elif not common.checkShiftJIS(b1, b2):
                if not allowunk and b1 > 0x4 and b1 != 0x11:
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


def writeShiftJISBIN(f, s, maxlen=0, encoding="shift_jis"):
    return writeShiftJIS(f, s, maxlen-1, True)


def logLongError(type, x, s, maxlen):
    common.logError("Line", s, "too long while writing", type, str(x) + "/" + str(len(s)), "maxlen", str(maxlen))


def writeShiftJIS(f, s, maxlen=-1, silent=False):
    common.logDebug("Writing", s, "at", common.toHex(f.tell()))
    s = s.replace("'", "^")
    s = s.replace("’", "^")
    s = s.replace("\"", "{")
    s = s.replace("“", "{")
    s = s.replace("”", "}")
    s = s.replace("～", "〜")
    s = s.replace("$$$", "$$<04>")
    s = s.replace("$$", "<03><01>")
    i = 0
    x = 0
    failed = False
    while x < len(s):
        c = s[x]
        if c == "|":
            if maxlen > 0 and i + 1 > maxlen:
                if not silent:
                    logLongError("0xa", x, s, maxlen)
                failed = True
                break
            f.writeByte(0xa)
            x += 1
            i += 1
        elif c == "<":
            code = s[x+1:].split(">", 1)[0]
            x += len(code) + 2
            if code in colorcodesrev:
                if maxlen > 0 and i + 2 > maxlen:
                    if not silent:
                        logLongError("<code>", x, s, maxlen)
                    failed = True
                    break
                i += 2
                f.writeByte(0x7)
                f.writeByte(colorcodesrev[code])
            elif code.startswith("small_") or code in speakercodesrev:
                if maxlen > 0 and i + 2 > maxlen:
                    if not silent:
                        logLongError("speaker", x, s, maxlen)
                    failed = True
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
                    if not silent:
                        logLongError("sound", x, s, maxlen)
                    failed = True
                    break
                code = code[5:]
                i += 2
                f.writeByte(0x6)
                f.writeByte(int(code, 16))
            elif code.startswith("symbol"):
                if maxlen > 0 and i + 2 > maxlen:
                    if not silent:
                        logLongError("symbol", x, s, maxlen)
                    failed = True
                    break
                code = code[6:]
                i += 2
                f.writeByte(0xe)
                f.writeByte(int(code, 16))
            elif code.startswith("w") or code.startswith("u"):
                codestart = code[0]
                if maxlen > 0 and i + 2 > maxlen:
                    if not silent:
                        logLongError("w/u", x, s, maxlen)
                    failed = True
                    break
                code = code[1:]
                i += 2
                if codestart == "w":
                    f.writeByte(0x5)
                else:
                    f.writeByte(0x2)
                f.writeByte(int(code))
            elif code == "instant":
                if maxlen > 0 and i + 2 > maxlen:
                    if not silent:
                        logLongError("instant", x, s, maxlen)
                    failed = True
                    break
                i += 2
                f.writeByte(0x9)
                f.writeByte(0x1)
            elif code == "0B" or code == "0b":
                # For choices, there's an extra 0 byte after this
                if maxlen > 0 and i + 2 > maxlen:
                    if not silent:
                        logLongError("0xb", x, s, maxlen)
                    failed = True
                    break
                i += 2
                f.writeByte(0xb)
                f.writeByte(0x0)
            else:
                nbytes = len(code) // 2
                if maxlen > 0 and i + nbytes > maxlen:
                    if not silent:
                        logLongError("code", x, s, maxlen)
                    failed = True
                    break
                i += nbytes
                f.write(bytes.fromhex(code))
        else:
            chardata = c.encode("shift_jis")
            if maxlen > 0 and i + len(chardata) > maxlen:
                if not silent:
                    logLongError("chr", x, s, maxlen)
                failed = True
                break
            x += 1
            i += len(chardata)
            f.write(chardata)
    f.writeByte(0)
    if not silent:
        common.logDebug("Done!")
    if failed:
        return -1
    return i
