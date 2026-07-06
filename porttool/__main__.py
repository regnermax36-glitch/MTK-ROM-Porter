#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path
from os import name
from .utils import portutils
from .configs import support_chipset_portstep, support_chipset

if name == 'nt':
    from multiprocessing.dummy import freeze_support
    freeze_support()

def main():
    parser = argparse.ArgumentParser(description="MTK ROM Porter")
    parser.add_argument("--base", required=True, help="Base ZIP containing boot.img and system.img")
    parser.add_argument("--port", required=True, help="Port ZIP package path")
    parser.add_argument("--out", default="out", help="Output directory")

    parser.add_argument("--chipset", default=support_chipset[0], choices=support_chipset, help="Chipset type")
    parser.add_argument("--type", choices=['zip', 'img'], default='zip', help="Output type (zip or img)")

    args = parser.parse_args()

    base_zip = Path(args.base)
    if not base_zip.exists() or not base_zip.is_file():
        print(f"Error: Base ZIP {base_zip} does not exist.")
        sys.exit(1)

    portzip = Path(args.port)
    if not portzip.exists():
        print(f"Error: Port ZIP package {portzip} does not exist.")
        sys.exit(1)

    # Extract base ZIP
    from zipfile import ZipFile
    base_dir = Path("base_extracted")
    base_dir.mkdir(parents=True, exist_ok=True)
    with ZipFile(base_zip, 'r') as zipf:
        zipf.extractall(base_dir)

    bootimg = base_dir / "boot.img"
    sysimg = base_dir / "system.img"

    if not bootimg.exists():
        print(f"Error: Base boot image {bootimg} was not found in the extracted base ZIP.")
        sys.exit(1)
    if not sysimg.exists():
        print(f"Error: Base system image {sysimg} was not found in the extracted base ZIP.")
        sys.exit(1)

    # Prepare items config
    newdict = support_chipset_portstep[args.chipset]

    # Load default flags from config
    for key, value in newdict['flags'].items():
        newdict[key] = value

    # Magisk settings
    newdict['patch_magisk'] = False
    newdict['magisk_apk'] = "magisk.apk"
    newdict['target_arch'] = "arm64"

    genimg = (args.type == 'img')

    print(
        f"Base boot path: {bootimg}\n"
        f"Base system image path: {sysimg}\n"
        f"Port package path: {portzip}\n"
        f"Output directory: {args.out}\n"
        f"Chipset scheme: {args.chipset}\n"
        f"Output type: {args.type}\n"
    )

    p = portutils(
        newdict,
        str(bootimg),
        str(sysimg),
        str(portzip),
        genimg=genimg,
        outdir=args.out
    )
    p.start()

if __name__ == '__main__':
    main()
