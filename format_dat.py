import codecs
import os
from hacktools import common


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


def extract(data):
    datfolder = data + "extract/data/rom/text/msg/"
    outfolder = data + "dat_output/"
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
                        if sjis.endswith(">>"):
                            sjis = sjis[:-2]
                        if sjis.endswith("|"):
                            sjis = sjis[:-1]
                        common.logDebug("Reading ptr", i, "at", common.toHex(ptr), sjis)
                        sjissplit = sjis.split(">>>")
                        for subsjis in sjissplit:
                            if subsjis != "":
                                out.write(subsjis + "=\n")


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
    0x2c: "tenten",
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


def readShiftJIS(f, encoding="shift_jis"):
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
                sjis += "<13" + common.toHex(b2) + ">"
            elif b1 == 0x14:
                b3 = f.readByte()
                sjis += "<14" + common.toHex(b2) + common.toHex(b3) + ">"
            elif not common.checkShiftJIS(b1, b2):
                f.seek(-1, 1)
                sjis += "<" + common.toHex(b1) + ">"
                i += 1
            else:
                f.seek(-2, 1)
                try:
                    sjis += f.read(2).decode(encoding).replace("〜", "～")
                except UnicodeDecodeError:
                    common.logError("[ERROR] UnicodeDecodeError")
                    sjis += "[ERROR" + str(f.tell() - 2) + "]"
                i += 2
    sjis = sjis.replace("<03><01>", ">>")
    sjis = sjis.replace("|>>", ">>")
    sjis = sjis.replace(">><04>", ">>>")
    return sjis
