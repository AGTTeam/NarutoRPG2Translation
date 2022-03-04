import math
import os
from hacktools import common, nitro


def extract(data):
    infolder = data + "extract/data/rom/"
    outfolder = data + "out_ACG/"
    common.makeFolder(outfolder)
    nob = readNOB(infolder)
    for file in common.showProgress(common.getFiles(infolder, ".acg")):
        if "map/anm" in file:
            continue
        ncgr, nscr, cells, palettes = readImage(infolder, file, nob)
        common.makeFolders(outfolder + os.path.dirname(file))
        pngfile = outfolder + file.replace(".acg", ".png")
        if cells is not None:
            nitro.drawNCER(pngfile, cells, ncgr, palettes)
        else:
            nitro.drawNCGR(pngfile, nscr, ncgr, palettes, ncgr.width, ncgr.height)


def repack(data):
    pass


def readImage(infolder, file, nob):
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
    size = os.path.getsize(infolder + palfile)
    with common.Stream(infolder + palfile, "rb") as f:
        pallen = size
        colornum = 0x10
        palettes = []
        for i in range(pallen // (colornum * 2)):
            palette = []
            for j in range(colornum):
                palette.append(common.readPalette(f.readUShort()))
            palettes.append(palette)
        indexedpalettes = {i: palettes[i % colornum] for i in range(len(palettes))}
    if os.path.isfile(infolder + "temp.acl"):
        os.remove(infolder + "temp.acl")
    if file.startswith("map/"):
        if "mp_00f" in file:
            indexedpalettes[0] = indexedpalettes[3]
        else:
            indexedpalettes[0] = indexedpalettes[2]
    # Read tiles
    size = os.path.getsize(infolder + file)
    with common.Stream(infolder + file, "rb") as f:
        ncgr = nitro.NCGR()
        ncgr.tiles = []
        ncgr.width = 256
        if file.startswith("f_name") or file.startswith("jyutu_name"):
            ncgr.width = 32
        elif file.startswith("b_name") or file.startswith("face/kao"):
            ncgr.width = 40
        elif "sys_bg_a_001" in file or "sys_bg_a_002" in file or "sys_bg_a_003" in file:
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
        with common.Stream(infolder + mapfile, "rb") as f:
            # Look for the CLRF magic
            all = f.read()
            clrf = all.find(b"CLRF")
            if clrf != -1:
                size = clrf
            f.seek(0)
            nscr.width = ncgr.width
            nscr.height = ncgr.height = math.ceil(size / 8 / (nscr.width / 8)) * 8
            nscr.maps = []
            for j in range((nscr.width // 8) * (nscr.height // 8)):
                map = nitro.readMapData(f.readUShort())
                map.pal = map.pal % len(palettes)
                nscr.maps.append(map)
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
    return ncgr, nscr, cells, indexedpalettes


def readNOB(infolder):
    # Read the jutsu NOB files
    nob = {}
    for i in range(len(jutsucells)):
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
        {"pal": 1, "repeat": 4, "cells": [
            {"width": 8, "height": 8}
        ]},
        {"pal": 1, "cells": [
            {"width": 16, "height": 8}
        ]},
        {"pal": 1, "repeat": 11, "cells": [
            {"width": 8, "height": 8}
        ]},
        {"pal": 2, "cells": [
            {"width": 32, "height": 16},
            {"width": 8, "height": 16, "x": 32},
        ]},
        {"pal": 2, "cells": [
            {"width": 16, "height": 16},
        ]},
        {"cells": [
            {"width": 8, "height": 8},
        ]},
        {"pal": 2, "cells": [
            {"width": 32, "height": 32},
            {"width": 16, "height": 32, "x": 32},
            {"width": 8, "height": 32, "x": 48},
        ]},
        {"pal": 2, "cells": [
            {"width": 16, "height": 16},
        ]},
        {"pal": 2, "repeat": 3, "cells": [
            {"width": 32, "height": 16},
            {"width": 32, "height": 8, "y": 16},
        ]},
        {"pal": 2, "cells": [
            {"width": 32, "height": 16},
            {"width": 32, "height": 8, "y": 16},
            {"width": 16, "height": 16, "x": 32},
            {"width": 16, "height": 8, "x": 32, "y": 16},
        ]},
        {"pal": 2, "cells": [
            {"width": 32, "height": 16},
            {"width": 32, "height": 8, "y": 16},
            {"width": 8, "height": 16, "x": 32},
            {"width": 8, "height": 8, "x": 32, "y": 16},
        ]},
        {"pal": 2, "cells": [
            {"width": 32, "height": 16},
            {"width": 32, "height": 8, "y": 16},
            {"width": 8, "height": 8, "x": 32, "y": 8},
        ]},
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
