import math
import os
from PIL import Image
from hacktools import common, nitro


fontfiles = ["sys_bg_a_001", "sys_bg_a_002", "sys_bg_a_003", "sys_bg_a_004"]


def extract(data):
    infolder = data + "extract/data/rom/"
    outfolder = data + "out_ACG/"
    outfont = data + "out_FONT/"

    common.logMessage("Extracting ACG to", outfolder, "...")
    totfiles = 0
    common.makeFolder(outfolder)
    nob = readNOB(infolder)
    for file in common.showProgress(common.getFiles(infolder, ".acg")):
        if file.startswith("map/anm/"):
            continue
        totfiles += 1
        ncgr, nscr, cells, palettes, mapfile = readImage(infolder, file, nob)
        if ncgr is None:
            continue
        common.makeFolders(outfolder + os.path.dirname(file))
        pngfile = outfolder + file.replace(".acg", ".png")
        if cells is not None:
            nitro.drawNCER(pngfile, cells, ncgr, palettes)
        else:
            usewidth = ncgr.width
            useheight = ncgr.height
            if file.startswith("map/") and nscr is not None:
                usewidth = nscr.width
                useheight = nscr.height
            nitro.drawNCGR(pngfile, nscr, ncgr, palettes, usewidth, useheight)
        if file.startswith("map/"):
            mapimg = Image.open(pngfile)
            if "_a2" not in file:
                mapbg = mapimg.crop(box=(0, 0, mapimg.width, mapimg.height // 2))
                mapfg = mapimg.crop(box=(0, mapimg.height // 2, mapimg.width, mapimg.height))
                mergedimg = Image.new("RGBA", (mapimg.width, mapimg.height // 2), (0, 0, 0, 0))
                mergedimg.paste(mapbg, (0, 0))
                mergedimg.paste(mapfg, (0, 0), mapfg)
            else:
                mergedimg = Image.open(pngfile.replace("_a2.png", "_merged.png"))
                mergedimg.paste(mapimg, (0, 0), mapimg)
            mergedimg.save(pngfile.replace(".png", "_merged.png"), "PNG")
    common.logMessage("Done! Extracted", totfiles, "files")
    # Split font
    common.logMessage("Extracting FONT to", outfont, "...")
    common.makeFolder(outfont)
    for i in range(len(fontfiles)):
        fontfolder = outfont + fontfiles[i] + "/"
        common.makeFolder(fontfolder)
        img = Image.open(outfolder + "sys/bg/" + fontfiles[i] + ".png")
        img = img.convert("RGBA")
        height = 16 if i <= 1 else 8
        for j in range(img.height // height):
            crop = img.crop((0, height * j, 8, height * (j + 1)))
            crop.save(fontfolder + str(j).zfill(3) + ".png", "PNG")
    common.logMessage("Done!")


def repack(data):
    acgin = data + "extract/data/rom/"
    acgout = data + "repack/data/rom/"
    workfolder = data + "work_ACG/"
    workfont = data + "work_FONT/"

    common.logMessage("Repacking FONT from", workfont, "...")
    for i in range(len(fontfiles)):
        fontfolder = workfont + fontfiles[i] + "/"
        if os.path.isdir(fontfolder) or i == 3:
            common.makeFolders(workfolder + os.path.dirname("sys/bg/" + fontfiles[i] + ".png"))
            common.copyFile(workfolder.replace("work_", "out_") + "sys/bg/" + fontfiles[i] + ".png", workfolder + "sys/bg/" + fontfiles[i] + ".png")
            imgfile = workfolder + "sys/bg/" + fontfiles[i] + ".png"
            img = Image.open(imgfile)
            img = img.convert("RGBA")
            height = 16 if i <= 1 else 8
            for j in range(img.height // height):
                if i != 3:
                    fontimg = fontfolder + str(j).zfill(3) + ".png"
                else:
                    fontimg = workfont + fontfiles[i - 1] + "/" + str(j).zfill(3) + ".png"
                if os.path.isfile(fontimg):
                    crop = Image.open(fontimg)
                    crop = crop.convert("RGBA")
                    # The 4th font is just a copy of the 3rd with transparency instead of a white background
                    if i == 3:
                        pixels = crop.load()
                        for x in range(crop.width):
                            for y in range(crop.height):
                                if pixels[x, y] == (248, 248, 248, 255) or pixels[x, y] == (255, 255, 255, 255):
                                    pixels[x, y] = (0, 0, 0, 0)
                    img.paste(crop, (0, height * j))
            img.save(imgfile, "PNG")
    common.logMessage("Done!")
    common.logMessage("Repacking ACG from", workfolder, "...")
    totfiles = 0
    nob = readNOB(acgin)
    open("tempcell.bin", "w").close()
    for file in common.showProgress(common.getFiles(acgin, ".acg")):
        if file.startswith("map/anm/"):
            continue
        common.logDebug("Processing", file, "...")
        totfiles += 1
        pngfile = file.replace(".acg", ".png")
        if os.path.isfile(workfolder + pngfile):
            ncgr, nscr, cells, palettes, mapfile = readImage(acgin, file, nob)
            usewidth = ncgr.width
            useheight = ncgr.height
            if file.startswith("map/") and nscr is not None:
                usewidth = nscr.width
                useheight = nscr.height
            if nscr is None and cells is None:
                common.copyFile(acgin + file, acgout + file)
                nitro.writeNCGR(acgout + file, ncgr, workfolder + pngfile, palettes, usewidth, useheight)
            elif cells is None:
                common.copyFile(acgin + file, acgout + file)
                common.copyFile(acgin + mapfile, acgout + mapfile)
                nitro.writeMappedNSCR(acgout + file, acgout + mapfile, ncgr, nscr, workfolder + pngfile, palettes, usewidth, useheight, transptile=file.startswith("map/"), writelen=False, useoldpal=file.startswith("map/"))
            else:
                common.copyFile(acgin + file, acgout + file)
                nitro.writeNCER(acgout + file, "tempcell.bin", ncgr, cells, workfolder + pngfile, palettes)
    os.remove("tempcell.bin")
    common.logMessage("Done! Repacked", totfiles, "files")


def readImage(infolder, file, nob=None):
    # Read palette
    palfile = file.replace(".acg", ".acl")
    mergefiles = []
    if palfile.startswith("sys/obj/sys_ob_b_000"):
        mergefiles = ["sys/obj/sys_ob_b_000.acl", "sys/obj/sys_ob_b_002.acl", "sys/obj/sys_ob_b_003.acl"]
    elif palfile.startswith("sys/obj/sys_ob_c_000"):
        mergefiles = ["sys/obj/sys_ob_c_000.acl", "sys/obj/sys_ob_c_001.acl", "sys/obj/sys_ob_c_002.acl"]
    if len(mergefiles) > 0:
        with common.Stream(infolder + "temp.acl", "wb") as f:
            for mergefile in mergefiles:
                with common.Stream(infolder + mergefile, "rb") as fin:
                    f.write(fin.read())
        palfile = "temp.acl"
    if not os.path.isfile(infolder + palfile):
        if palfile.startswith("b_chr/mon_shadow/b_kage"):
            palfile = "b_chr/mon_shadow/b_kage_000.acl"
        elif palfile.startswith("b_name"):
            palfile = "b_name/b_name.acl"
        elif palfile.startswith("f_chr"):
            palfile = "f_chr/f_chr_000.acl"
        elif palfile.startswith("f_ef"):
            palfile = "f_ef/f_efe_013.acl"
        elif palfile.startswith("f_name"):
            palfile = "f_name/f_name_000.acl"
        elif palfile.startswith("jyutu_name"):
            palfile = "jyutu_name/jyutu_name_000.acl"
        elif palfile.startswith("map/dj_022"):
            palfile = "map/dj_022/dj_022.acl"
        elif palfile.startswith("sys/bg"):
            palfile = "sys/bg/sys_bg_a_000.acl"
        elif palfile.startswith("title/bg_naruto"):
            palfile = "title/bg_naruto.acl"
        elif palfile.startswith("title/bg_sakura"):
            palfile = "title/bg_sakura.acl"
        elif palfile.startswith("title/bg_sasuke"):
            palfile = "title/bg_sasuke.acl"
        elif palfile.startswith("zmap/obj"):
            palfile = "zmap/obj/zm_icon_000.acl"
    if not os.path.isfile(infolder + palfile):
        if palfile == "sys/obj/sys_ob_a_001.acl":
            palfile = "sys/obj/sys_ob_a_000.acl"
        else:
            common.logError("Palette file", palfile, "not found")
            return None, None, None, {}, ""
    size = os.path.getsize(infolder + palfile)
    colornum = 0x10
    pallen = size
    if "sys_bg_a_001" in file or "sys_bg_a_002" in file or "sys_bg_a_003" in file or "sys_bg_a_004" in file:
        colornum = 4
        pallen = 8
    palettes = []
    # For maps, we need to load some common palettes from other files
    if file.startswith("map/"):
        with common.Stream(infolder + "sys/bg/sys_bg_a_000.acl", "rb") as f:
            for i in range(3):
                palette = []
                for j in range(colornum):
                    palette.append(common.readPalette(f.readUShort()))
                palettes.append(palette)
        with common.Stream(infolder + "sys/bg/sys_bg_c_000.acl", "rb") as f:
            f.seek(0x20)
            for i in range(1):
                palette = []
                for j in range(colornum):
                    palette.append(common.readPalette(f.readUShort()))
                palettes.append(palette)
    with common.Stream(infolder + palfile, "rb") as f:
        for i in range(pallen // (colornum * 2)):
            palette = []
            for j in range(colornum):
                palette.append(common.readPalette(f.readUShort()))
            palettes.append(palette)
    indexedpalettes = {i: palettes[i % colornum] for i in range(len(palettes))}
    if os.path.isfile(infolder + "temp.acl"):
        os.remove(infolder + "temp.acl")
    # Read tiles
    size = os.path.getsize(infolder + file)
    with common.Stream(infolder + file, "rb") as f:
        ncgr = nitro.NCGR()
        ncgr.width = 256
        if file.startswith("f_name") or file.startswith("jyutu_name"):
            ncgr.width = 32
        elif file.startswith("b_name") or file.startswith("face/kao"):
            ncgr.width = 40
        elif "sys_bg_a_001" in file or "sys_bg_a_002" in file or "sys_bg_a_003" in file or "sys_bg_a_004" in file:
            ncgr.width = 8
        elif file.startswith("sys/obj/sys_ob_f"):
            ncgr.width = 32
        ncgr.height = math.ceil(size * 2 / ncgr.width / 8) * 8
        ncgr.bpp = 4
        ncgr.tilesize = 8
        ncgr.lineal = False
        ncgr.tilelen = (ncgr.width // 8) * (ncgr.height // 8) * 0x40
        ncgr.tileoffset = f.tell()
        tiledata = f.read(ncgr.tilelen)
        try:
            nitro.readNCGRTiles(ncgr, tiledata)
        except IndexError:
            pass
    # Read maps
    nscr = None
    mapfile = file.replace(".acg", ".asc")
    if os.path.isfile(infolder + mapfile) and "cut_in" not in file:
        size = os.path.getsize(infolder + mapfile)
        nscr = nitro.NSCR()
        nscr.mapoffset = 0
        with common.Stream(infolder + mapfile, "rb") as f:
            # Look for the CLRF magic
            all = f.read()
            clrf = all.find(b"CLRF")
            if clrf != -1:
                size = clrf
            f.seek(0)
            nscr.width = ncgr.width
            nscr.height = ncgr.height = math.ceil(size / 8 / (nscr.width / 8)) * 8
            for j in range((nscr.width // 8) * (nscr.height // 8)):
                map = nitro.readMapData(f.readUShort())
                map.pal = map.pal % len(palettes)
                nscr.maps.append(map)
    else:
        mapfile = file.replace(".acg", ".dqm")
        if os.path.isfile(infolder + mapfile):
            size = os.path.getsize(infolder + mapfile)
            nscr = nitro.NSCR()
            nscr.width = mapwidths[file]
            nscr.height = math.ceil((size / 2) / (nscr.width / 8)) * 8
            nscr.mapoffset = 0
            with common.Stream(infolder + mapfile, "rb") as f:
                for j in range((nscr.width // 8) * (nscr.height // 8)):
                    try:
                        map = nitro.readMapData(f.readUShort())
                        nscr.maps.append(map)
                    except:
                        common.logError("Wrong size", mapfile)
                        nscr = None
                        break
    # Read cells
    cellfile = file.replace(".acg", ".nob")
    cells = None
    if os.path.isfile(infolder + cellfile):
        with common.Stream(infolder + cellfile, "rb") as f:
            data = f.read()
        if data in nob:
            cells = nitro.readManualCells([jutsucells[nob[data]]])
    if cells is None:
        foldername = file.split("/")[0]
        if file in manualcells:
            cells = nitro.readManualCells(manualcells[file])
        elif foldername in manualcells:
            cells = nitro.readManualCells(manualcells[foldername])
    return ncgr, nscr, cells, indexedpalettes, mapfile


def readNOB(infolder):
    # Read the jutsu NOB files
    nob = {}
    for i in range(len(jutsucells)):
        if not os.path.isfile(infolder + jutsucells[i]["file"]):
            continue
        with common.Stream(infolder + jutsucells[i]["file"], "rb") as f:
            data = f.read()
        nob[data] = i
    return nob


jutsucells = [
    {"file": "jyutu_name/jyutu_name_05a.nob", "cells": [
        {"width": 32, "height": 16},
    ]},
    {"file": "jyutu_name/jyutu_name_00c.nob", "cells": [
        {"width": 32, "height": 16},
        {"width": 16, "height": 16, "x": 32},
    ]},
    {"file": "jyutu_name/jyutu_name_00d.nob", "cells": [
        {"width": 32, "height": 16},
        {"width": 32, "height": 16, "x": 32},
    ]},
    {"file": "jyutu_name/jyutu_name_00b.nob", "cells": [
        {"width": 32, "height": 16},
        {"width": 32, "height": 16, "x": 32},
        {"width": 16, "height": 16, "x": 64},
    ]},
    {"file": "jyutu_name/jyutu_name_001.nob", "cells": [
        {"width": 32, "height": 16},
        {"width": 32, "height": 16, "x": 32},
        {"width": 32, "height": 16, "x": 64},
    ]},
    {"file": "jyutu_name/jyutu_name_06e.nob", "cells": [
        {"width": 32, "height": 16},
        {"width": 32, "height": 16, "x": 32},
        {"width": 32, "height": 16, "x": 64},
    ]},
    {"file": "jyutu_name/jyutu_name_00a.nob", "cells": [
        {"width": 32, "height": 16},
        {"width": 32, "height": 16, "x": 32},
        {"width": 32, "height": 16, "x": 64},
        {"width": 16, "height": 16, "x": 96},
    ]},
    {"file": "jyutu_name/jyutu_name_02c.nob", "cells": [
        {"width": 32, "height": 16},
        {"width": 32, "height": 16, "x": 32},
        {"width": 32, "height": 16, "x": 64},
        {"width": 16, "height": 16, "x": 96},
    ]},
    {"file": "jyutu_name/jyutu_name_046.nob", "cells": [
        {"width": 32, "height": 16},
        {"width": 32, "height": 16, "x": 32},
        {"width": 32, "height": 16, "x": 64},
        {"width": 16, "height": 16, "x": 96},
    ]},
    {"file": "jyutu_name/jyutu_name_00e.nob", "cells": [
        {"width": 32, "height": 16},
        {"width": 32, "height": 16, "x": 32},
        {"width": 32, "height": 16, "x": 64},
        {"width": 32, "height": 16, "x": 96},
    ]},
    {"file": "jyutu_name/jyutu_name_08c.nob", "cells": [
        {"width": 32, "height": 16},
        {"width": 32, "height": 16, "x": 32},
        {"width": 32, "height": 16, "x": 64},
        {"width": 32, "height": 16, "x": 96},
    ]},
    {"file": "jyutu_name/jyutu_name_040.nob", "cells": [
        {"width": 32, "height": 16},
        {"width": 32, "height": 16, "x": 32},
        {"width": 32, "height": 16, "x": 64},
        {"width": 32, "height": 16, "x": 96},
    ]},
    {"file": "jyutu_name/jyutu_name_078.nob", "cells": [
        {"width": 32, "height": 16},
        {"width": 32, "height": 16, "x": 32},
        {"width": 32, "height": 16, "x": 64},
        {"width": 32, "height": 16, "x": 96},
    ]},
    {"file": "jyutu_name/jyutu_name_004.nob", "cells": [
        {"width": 32, "height": 16},
        {"width": 32, "height": 16, "x": 32},
        {"width": 32, "height": 16, "x": 64},
        {"width": 32, "height": 16, "x": 96},
        {"width": 16, "height": 16, "x": 128},
    ]},
    {"file": "jyutu_name/jyutu_name_03d.nob", "cells": [
        {"width": 32, "height": 16},
        {"width": 32, "height": 16, "x": 32},
        {"width": 32, "height": 16, "x": 64},
        {"width": 32, "height": 16, "x": 96},
        {"width": 32, "height": 16, "x": 128},
    ]},
    {"file": "jyutu_name/jyutu_name_006.nob", "cells": [
        {"width": 32, "height": 16},
        {"width": 32, "height": 16, "x": 32},
        {"width": 32, "height": 16, "x": 64},
        {"width": 32, "height": 16, "x": 96},
        {"width": 32, "height": 16, "x": 128},
        {"width": 16, "height": 16, "x": 160},
    ]},
]

manualcells = {
    "f_name": [
        {"cells": [
            {"width": 32, "height": 16},
            {"width": 32, "height": 16, "x": 32},
            {"width": 32, "height": 16, "x": 64},
        ]},
    ],
    "b_name": [
        {"cells": [
            {"width": 32, "height": 16},
            {"width": 8, "height": 16, "x": 32},
        ]},
    ],
    "title/tl_naruto.acg": [
        {"cells": [
            {"width": 32, "height": 8, "x": 72},
            {"width": 64, "height": 32, "y": 8},
            {"width": 32, "height": 32, "x": 64, "y": 8},
            {"width": 16, "height": 32, "x": 96, "y": 8},
            {"width": 32, "height": 16, "y": 40},
            {"width": 32, "height": 16, "x": 32, "y": 40},
            {"width": 32, "height": 16, "x": 64, "y": 40},
            {"width": 16, "height": 16, "x": 96, "y": 40},
        ]}
    ],
    "title/botan.acg": [
        {"cells": [
            {"width": 32, "height": 16},
            {"width": 32, "height": 16, "x": 32},
            {"width": 32, "height": 16, "x": 64},
            {"width": 32, "height": 16, "x": 96},
            {"width": 16, "height": 16, "x": 128},
            {"width": 8, "height": 16, "x": 144},
        ]}
    ],
    "title/tl_rpg.acg": [
        {"cells": [
            {"width": 32, "height": 32},
            {"width": 32, "height": 24, "x": 32},
            {"width": 64, "height": 32, "x": 64},
            {"width": 72, "height": 8, "x": 72, "y": 32},
            {"width": 16, "height": 8, "x": 128, "y": 24},
        ]}
    ],
    "title/t_cp.acg": [
        {"cells": [
            {"width": 32, "height": 8},
            {"width": 32, "height": 8, "y": 8},
            {"width": 16, "height": 8, "x": 32},
            {"width": 16, "height": 8, "x": 32, "y": 8},
            {"width": 32, "height": 16, "x": 48, "y": 8},
            {"width": 32, "height": 8, "x": 80},
            {"width": 64, "height": 8, "x": 80, "y": 8},
            {"width": 16, "height": 16, "x": 144},
            {"width": 8, "height": 8, "x": 136},
            {"width": 36, "height": 8, "x": 160, "y": 8},
            {"width": 64, "height": 8, "x": 0, "y": 16},
        ]}
    ],
    "sys/bg/sys_bg_c_000.acg": [
        {"cells": [
            {"width": 8, "height": 8},
        ]},
        {"cells": [
            {"width": 16, "height": 48},
        ]},
        {"cells": [
            {"width": 56, "height": 8},
        ]},
        {"cells": [
            {"width": 16, "height": 192},
        ]},
        {"pal": 1, "cells": [
            {"width": 56, "height": 32},
        ]},
        {"pal": 1, "cells": [
            {"width": 16, "height": 320},
        ]}
    ],
    "sys/obj/sys_ob_b_000.acg": [
        {"cells": [
            {"width": 16, "height": 16},
        ]},
        {"cells": [
            {"width": 192, "height": 8},
        ]},
        {"cells": [
            {"width": 192, "height": 8},
            {"width": 96, "height": 8, "y": 8},
        ]},
        {"pal": 1, "repeat": 3, "cells": [
            {"width": 32, "height": 16},
        ]},
        {"pal": 1, "cells": [
            {"width": 32, "height": 16},
            {"width": 8, "height": 16, "x": 32},
        ]},
        {"pal": 1, "cells": [
            {"width": 32, "height": 16},
        ]},
        {"pal": 1, "cells": [
            {"width": 32, "height": 16},
            {"width": 8, "height": 16, "x": 32},
        ]},
        {"pal": 2, "cells": [
            {"width": 16, "height": 8, "x": 6},
            {"width": 16, "height": 8, "y": 8},
            {"width": 16, "height": 8, "y": 16},
            {"width": 8, "height": 16, "x": 16, "y": 8}
        ]},
        {"pal": 2, "cells": [
            {"width": 32, "height": 16},
            {"width": 32, "height": 16, "x": 32},
            {"width": 32, "height": 16, "x": 64},
            {"width": 8, "height": 16, "x": 96},
        ]},
        {"pal": 2, "cells": [
            {"width": 128, "height": 64},
            {"width": 48, "height": 8, "y": 64},
        ]},
    ],
    "sys/obj/sys_ob_c_000.acg": [
        # Some symbols
        {"pal": 1, "repeat": 4, "cells": [
            {"width": 8, "height": 8}
        ]},
        # Lv.
        {"pal": 1, "cells": [
            {"width": 16, "height": 8}
        ]},
        # Numbers and /
        {"pal": 1, "repeat": 11, "cells": [
            {"width": 8, "height": 8}
        ]},
        # Money
        {"pal": 2, "cells": [
            {"width": 32, "height": 16},
            {"width": 8, "height": 16, "x": 32},
        ]},
        # Ryo
        {"pal": 2, "cells": [
            {"width": 16, "height": 16},
        ]},
        # Empty
        {"cells": [
            {"width": 8, "height": 8},
        ]},
        # Top Secret
        {"pal": 2, "cells": [
            {"width": 32, "height": 32},
            {"width": 16, "height": 32, "x": 32},
            {"width": 8, "height": 32, "x": 48},
        ]},
        # Shuriken
        {"pal": 2, "cells": [
            {"width": 16, "height": 16},
        ]},
        # Item, Equip, Jutsu
        {"pal": 2, "repeat": 3, "cells": [
            {"width": 32, "height": 16},
            {"width": 32, "height": 8, "y": 16},
        ]},
        # Status
        {"pal": 2, "cells": [
            {"width": 32, "height": 16},
            {"width": 32, "height": 8, "y": 16},
            {"width": 16, "height": 16, "x": 32},
            {"width": 16, "height": 8, "x": 32, "y": 16},
        ]},
        # Formation
        {"pal": 2, "cells": [
            {"width": 32, "height": 16},
            {"width": 32, "height": 8, "y": 16},
            {"width": 8, "height": 16, "x": 32},
            {"width": 8, "height": 8, "x": 32, "y": 16},
        ]},
        # Member
        {"pal": 2, "cells": [
            {"width": 32, "height": 16},
            {"width": 32, "height": 8, "y": 16},
            {"width": 8, "height": 8, "x": 32, "y": 8},
        ]},
        # Weapon, Armor
        {"pal": 2, "repeat": 2, "cells": [
            {"width": 32, "height": 16},
            {"width": 32, "height": 8, "y": 16},
        ]},
        {"pal": 2, "repeat": 2, "cells": [
            {"width": 32, "height": 16},
            {"width": 32, "height": 8, "y": 16},
            {"width": 8, "height": 16, "x": 32},
            {"width": 8, "height": 8, "x": 32, "y": 16},
        ]},
        {"pal": 2, "cells": [
            {"width": 32, "height": 16},
            {"width": 32, "height": 8, "y": 16},
            {"width": 16, "height": 16, "x": 32},
            {"width": 16, "height": 8, "x": 32, "y": 16},
            {"width": 8, "height": 16, "x": 48, "y": 8},
        ]},
        {"pal": 2, "repeat": 2, "cells": [
            {"width": 32, "height": 16},
            {"width": 32, "height": 8, "y": 16},
            {"width": 32, "height": 16, "x": 32},
            {"width": 32, "height": 8, "x": 32, "y": 16},
        ]},
        {"pal": 2, "cells": [
            {"width": 32, "height": 16},
            {"width": 32, "height": 8, "y": 16},
            {"width": 32, "height": 16, "x": 32},
            {"width": 32, "height": 8, "x": 32, "y": 16},
            {"width": 32, "height": 16, "x": 64},
            {"width": 32, "height": 8, "x": 64, "y": 16},
        ]},
        {"pal": 2, "cells": [
            {"width": 32, "height": 16},
            {"width": 32, "height": 8, "y": 16},
        ]},
        {"pal": 1, "cells": [
            {"width": 32, "height": 16},
            {"width": 8, "height": 16, "x": 32},
        ]},
        {"pal": 1, "repeat": 2, "cells": [
            {"width": 32, "height": 16},
        ]},
        {"pal": 1,  "cells": [
            {"width": 32, "height": 16},
            {"width": 16, "height": 16, "x": 32},
            {"width": 8, "height": 16, "x": 48},
        ]},
        {"pal": 1, "cells": [
            {"width": 32, "height": 16},
            {"width": 32, "height": 16, "x": 32},
            {"width": 8, "height": 8, "x": 64, "y": 2},
        ]},
        {"pal": 1, "repeat": 3, "cells": [
            {"width": 32, "height": 16},
        ]},
        {"pal": 2, "repeat": 3, "cells": [
            {"width": 64, "height": 8},
        ]},
        {"pal": 2, "cells": [
            {"width": 48, "height": 8},
        ]},
        {"pal": 2, "cells": [
            {"width": 32, "height": 24},
            {"width": 32, "height": 24, "x": 32},
            {"width": 8, "height": 24, "x": 64},
        ]},
    ],
    "sys/obj/sys_ob_d_000.acg": [
        {"cells": [
            {"width": 32, "height": 32, "x": 8, "y": 8},
            {"width": 32, "height": 32, "x": 40, "y": 8},
            {"width": 16, "height": 8, "x": 16},
            {"width": 24, "height": 8, "x": 48},
            {"width": 8, "height": 16, "y": 16},
            {"width": 16, "height": 8, "x": 16, "y": 40},
            {"width": 24, "height": 8, "x": 48, "y": 40},
            {"width": 8, "height": 16, "x": 72, "y": 16},
        ]},
        {"cells": [
            {"width": 32, "height": 32, "x": 8, "y": 8},
            {"width": 32, "height": 32, "x": 40, "y": 8},
            {"width": 16, "height": 8, "x": 16},
            {"width": 24, "height": 8, "x": 48},
            {"width": 16, "height": 8, "x": 16, "y": 40},
            {"width": 24, "height": 8, "x": 48, "y": 40},
            {"width": 8, "height": 16, "x": 72, "y": 16},
        ]},
        {"cells": [
            {"width": 32, "height": 32, "x": 8, "y": 8},
            {"width": 32, "height": 32, "x": 40, "y": 8},
            {"width": 24, "height": 8, "x": 16},
            {"width": 24, "height": 8, "x": 48},
            {"width": 8, "height": 8, "y": 8},
            {"width": 16, "height": 8, "x": 16, "y": 40},
            {"width": 24, "height": 8, "x": 48, "y": 40},
            {"width": 8, "height": 24, "x": 72, "y": 16},
        ]},
    ],
}


mapwidths = {
    "map/dj_000/dj_000.acg": 768,
    "map/dj_001/dj_001.acg": 768,
    "map/dj_002/dj_002.acg": 768,
    "map/dj_003/dj_003.acg": 768,
    "map/dj_004/dj_004.acg": 768,
    "map/dj_005/dj_005.acg": 512,
    "map/dj_006/dj_006.acg": 512,
    "map/dj_007/dj_007.acg": 512,
    "map/dj_008/dj_008.acg": 1024,
    "map/dj_009/dj_009.acg": 688,
    "map/dj_00a/dj_00a.acg": 880,
    "map/dj_00b/dj_00b.acg": 512,
    "map/dj_00c/dj_00c.acg": 512,
    "map/dj_00d/dj_00d.acg": 512,
    "map/dj_00e/dj_00e.acg": 1280,
    "map/dj_00f/dj_00f.acg": 768,
    "map/dj_010/dj_010.acg": 512,
    "map/dj_011/dj_011.acg": 512,
    "map/dj_012/dj_012.acg": 512,
    "map/dj_013/dj_013.acg": 512,
    "map/dj_014/dj_014.acg": 1280,
    "map/dj_015/dj_015.acg": 1280,
    "map/dj_016/dj_016.acg": 512,
    "map/dj_017/dj_017.acg": 512,
    "map/dj_018/dj_018.acg": 512,
    "map/dj_019/dj_019.acg": 1024,
    "map/dj_01a/dj_01a.acg": 512,
    "map/dj_01b/dj_01b.acg": 608,
    "map/dj_01c/dj_01c.acg": 512,
    "map/dj_01d/dj_01d.acg": 512,
    "map/dj_01e/dj_01e.acg": 512,
    "map/dj_01f/dj_01f.acg": 512,
    "map/dj_020/dj_020.acg": 512,
    "map/dj_021/dj_021.acg": 512,
    "map/dj_022/dj_022.acg": 768,
    "map/dj_022/dj_022_a2.acg": 768,
    "map/dj_023/dj_023.acg": 592,
    "map/dj_024/dj_024.acg": 512,
    "map/dj_025/dj_025.acg": 464,
    "map/dj_026/dj_026.acg": 896,
    "map/dj_027/dj_027.acg": 512,
    "map/dj_028/dj_028.acg": 512,
    "map/dj_029/dj_029.acg": 512,
    "map/dj_02a/dj_02a.acg": 448,
    "map/mp_000/mp_000.acg": 256,
    "map/mp_001/mp_001.acg": 320,
    "map/mp_002/mp_002.acg": 384,
    "map/mp_003/mp_003.acg": 256,
    "map/mp_004/mp_004.acg": 256,
    "map/mp_005/mp_005.acg": 272,
    "map/mp_006/mp_006.acg": 304,
    "map/mp_007/mp_007.acg": 256,
    "map/mp_008/mp_008.acg": 256,
    "map/mp_009/mp_009.acg": 272,
    "map/mp_00a/mp_00a.acg": 256,
    "map/mp_00b/mp_00b.acg": 256,
    "map/mp_00c/mp_00c.acg": 336,
    "map/mp_00d/mp_00d.acg": 512,
    "map/mp_00e/mp_00e.acg": 512,
    "map/mp_00f/mp_00f.acg": 432,
    "map/mp_010/mp_010.acg": 256,
    "map/mp_011/mp_011.acg": 256,
    "map/mp_012/mp_012.acg": 256,
    "map/mp_013/mp_013.acg": 256,
    "map/mp_014/mp_014.acg": 256,
    "map/mp_015/mp_015.acg": 256,
    "map/mp_016/mp_016.acg": 256,
    "map/mp_017/mp_017.acg": 256,
    "map/mp_018/mp_018.acg": 496,
    "map/mp_019/mp_019.acg": 272,
    "map/mp_01a/mp_01a.acg": 512,
    "map/mp_01b/mp_01b.acg": 320,
    "map/mp_01c/mp_01c.acg": 288,
    "map/mp_01d/mp_01d.acg": 288,
    "map/mp_01e/mp_01e.acg": 256,
    "map/mp_01f/mp_01f.acg": 304,
    "map/mp_020/mp_020.acg": 288,
    "map/mp_021/mp_021.acg": 320,
    "map/mp_022/mp_022.acg": 352,#2 map files
    "map/mp_023/mp_023.acg": 256,
    "map/mp_024/mp_024.acg": 304,
    "map/mp_025/mp_025.acg": 304,
    "map/mp_026/mp_026.acg": 256,
    "map/mp_027/mp_027.acg": 256,
    "map/mp_028/mp_028.acg": 256,
    "map/mp_029/mp_029.acg": 368,
    "map/mp_02a/mp_02a.acg": 512,
    "map/mp_02b/mp_02b.acg": 256,
    "map/mp_02c/mp_02c.acg": 256,
}
