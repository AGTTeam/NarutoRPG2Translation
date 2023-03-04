import codecs
import os
import click
import ndspy.soundArchive
import ndspy.soundStream
from hacktools import common, nds

version = "0.11.0"
data = "NarutoRPG2Data/"
romfile = data + "naruto.nds"
rompatch = data + "naruto_patched.nds"
bannerfile = data + "repack/banner.bin"
patchfile = data + "patch.xdelta"
infolder = data + "extract/"
replacefolder = data + "replace/"
outfolder = data + "repack/"


@common.cli.command()
@click.option("--rom", is_flag=True, default=False)
@click.option("--bin", is_flag=True, default=False)
@click.option("--dat", is_flag=True, default=False)
@click.option("--img", is_flag=True, default=False)
@click.option("--en", default=0)
def extract(rom, bin, dat, img, en):
    datafolder = data
    if en > 0:
        datafolder = datafolder.replace("Data/", "en" + str(en) + "/")
    all = not rom and not bin and not dat and not img
    if all or rom:
        nds.extractRom(romfile.replace(data, datafolder), infolder.replace(data, datafolder), outfolder.replace(data, datafolder) if en == 0 else "")
    if all or bin:
        import format_bin
        format_bin.extract(datafolder)
    if all or dat:
        import format_dat
        format_dat.extract(datafolder)
    if all or img:
        import format_img
        format_img.extract(datafolder)


@common.cli.command()
@click.option("--no-rom", is_flag=True, default=False)
@click.option("--bin", is_flag=True, default=False)
@click.option("--dat", is_flag=True, default=False)
@click.option("--img", is_flag=True, default=False)
@click.option("--snd", is_flag=True, default=False)
def repack(no_rom, bin, dat, img, snd):
    all = not bin and not dat and not img and not snd
    if all or bin:
        import format_bin
        format_bin.repack(data)
    if all or dat:
        import format_dat
        format_dat.repack(data)
    if all or img:
        import format_img
        format_img.repack(data)
    if os.path.isdir(data + "sound") and os.path.isdir(data + "voice_matching") and snd:
        infile = "voice_matching/jpn_to_eng.txt"
        common.logMessage("Repacking sound from", infile, "...")
        with codecs.open(data + infile, "r", "utf-8") as input:
            section = common.getSection(input, "")
        jp = ndspy.soundArchive.SDAT.fromFile(data + "extract/data/rom/sound/sound_data.sdat")
        en1 = ndspy.soundArchive.SDAT.fromFile(data + "sound/en1.sdat")
        en2 = ndspy.soundArchive.SDAT.fromFile(data + "sound/en2.sdat")
        for i in range(len(jp.streams)):
            name = jp.streams[i][0]
            fullname = "jp/" + name
            if fullname in section:
                newname = section[fullname][0]
                if newname != "":
                    sourcedat = None
                    if newname.startswith("en1/"):
                        sourcedat = en1
                    elif newname.startswith("en2/"):
                        sourcedat = en2
                    if sourcedat is not None:
                        found = False
                        for name, stream in sourcedat.streams:
                            if name == newname[4:]:
                                jp.streams[i] = (name, stream)
                                found = True
                                break
                        if not found:
                            common.logError("Stream", newname, "not found")
                    else:
                        stream = ndspy.soundStream.STRM.fromFile(data + "sound/" + newname + ".strm")
                        jp.streams[i] = (name, stream)
        jp.saveToFile(data + "repack/data/rom/sound/sound_data.sdat")
        common.logMessage("Done!")
    if not no_rom:
        if os.path.isdir(replacefolder):
            common.mergeFolder(replacefolder, outfolder)
        nds.editBannerTitle(bannerfile, "Naruto RPG 2\n~Chidori VS Rasengan~\nTOMY")
        nds.repackRom(romfile, rompatch, outfolder, patchfile)


if __name__ == "__main__":
    click.echo("NarutoRPG2Translation version " + version)
    if not os.path.isdir(data):
        common.logError(data, "folder not found.")
        quit()
    if not os.path.isfile(romfile):
        common.logError(romfile, "file not found.")
        quit()
    common.runCLI(common.cli)
