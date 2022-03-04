import os
import click
from hacktools import common, nds, nitro

version = "0.5.0"
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
@click.option("--dat", is_flag=True, default=False)
@click.option("--img", is_flag=True, default=False)
def extract(rom, dat, img):
    all = not rom and not dat and not img
    if all or rom:
        nds.extractRom(romfile, infolder, outfolder)
    if all or dat:
        import format_dat
        format_dat.extract(data)
    if all or img:
        import format_img
        format_img.extract(data)


@common.cli.command()
@click.option("--no-rom", is_flag=True, default=False)
@click.option("--dat", is_flag=True, default=False)
@click.option("--img", is_flag=True, default=False)
def repack(no_rom, dat, img):
    all = not dat and not img
    if all or dat:
        import format_dat
        format_dat.repack(data)
    if all or img:
        import format_img
        format_img.repack(data)
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
    common.runCLI(common.cli)
