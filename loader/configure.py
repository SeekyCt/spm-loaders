#!/usr/bin/env python3

from io import StringIO
import os
import sys
from typing import List

from ninja_syntax import Writer

###############
# Definitions #
###############

BASE_ADDR = "80004200"
HOOK_ADDRS = {
    "eu0" : "801a84d4",
    "eu1" : "801a84d4",
    # TODO
    "us0" : "0",
    "us1" : "0",
    "us2" : "0",
    "jp0" : "0",
    "jp1" : "0",
    "kr0" : "0",
}

#########
# Paths #
#########

# Python
PYTHON = sys.executable

# Project dirs
SRCDIR = "src"
INCDIR = "include"
LINKDIR = "linker"
BUILDDIR = "build"
OUTDIR = "out"
TOOLSDIR = "tools"

# Project files
LST2LD = os.path.join("$toolsdir", "lst2ld.py")
MAKEGECKO = os.path.join("$toolsdir", "makegecko.py")

# Libraries
SPM_HEADERS = os.path.join("..", "spm-headers")

#########
# Tools #
#########

# Devkitppc
DEVKITPPC = os.environ.get("DEVKITPPC")
assert DEVKITPPC is not None, "Error: DEVKITPPC environment variable not set"
CC = os.path.join("$devkitppc", "bin", "powerpc-eabi-gcc")
OBJCOPY = os.path.join("$devkitppc", "bin", "powerpc-eabi-objcopy")

##############
# Tool Flags #
##############

# C/C++/Asm include flags
INCLUDES = ' '.join(
    "-I " + d
    for d in [
        "$incdir",
        os.path.join("$spm_headers", "include"),
        os.path.join("$spm_headers", "mod"),
    ]
)

# Machine-dependant flags
# Passed to C, C++ and asm compilation, and the linker
MACHDEP = ' '.join([
    "-mno-sdata", # Disable SDA sections since not main binary
    "-mgcn", # Use ogc linker
    "-DGEKKO", # CPU preprocessor define
    "-mcpu=750", # Set CPU to 750cl
    "-meabi", # Set ppc abi to eabi
    "-mhard-float", # Enable hardware floats
    "-nostdlib", # Don't link std lib
    "-mregnames", # Enable r prefix for registers in asm
])

# Base C flags
# Passed to C and C++ Compilation
CFLAGS = ' '.join([
    "$machdep",
    "$includes",

    "-nostdinc", # Disable including std lib headers
    "-ffreestanding", # Tell compiler environment isn't hosted
    "-ffunction-sections", # Allow function deadstripping
    "-fdata-sections", # Allow data deadstripping
    "-g", # Emit debug info
    "-O3", # High optimisation for speed
    "-Wall", # Enable all warnings
    "-Wextra", # Enable even more warnings
    "-Wshadow", # Enable variable shadowing warning
])

# C++ flags
# Passed only to C++ compilation
CXXFLAGS = ' '.join([
    "$cflags",

    "-fno-exceptions", # Disable C++ exceptions
    "-fno-rtti", # Disable runtime type info
    "-std=gnu++17", # Use C++17 with GNU extensions
])

# Asm flags
# Passed only to asm compilation
ASFLAGS = ' '.join([
    "$machdep",

    "-x assembler-with-cpp", # Enable C preprocessor
])

# Linker flags
LDFLAGS = ' '.join([
    "$machdep",

    "-e entry", # Set entry to _prolog
    "-g", # Output debug info
    ','.join([
        "-Wl", # Pass the following options to the linker
        "--gc-sections", # Strip unused sections
        "--force-group-allocation", # Merge section groups
    ]),
])

#######################
# Ninja file creation #
#######################

def emit_vars(n: Writer):
    """Emits the variables to a ninja file"""

    # Python
    n.variable("python", PYTHON)

    # Project dirs
    n.variable("srcdir", SRCDIR)
    n.variable("incdir", INCDIR)
    n.variable("linkdir", LINKDIR)
    n.variable("builddir", BUILDDIR)
    n.variable("outdir", OUTDIR)
    n.variable("toolsdir", TOOLSDIR)

    n.variable("makegecko", MAKEGECKO)
    n.variable("lst2ld", LST2LD)

    # Libraries
    n.variable("spm_headers", SPM_HEADERS)

    # Devkitppc
    n.variable("devkitppc", DEVKITPPC)
    n.variable("cc", CC)
    n.variable("objcopy", OBJCOPY)

    # Tool flags
    n.variable("includes", INCLUDES)
    n.variable("machdep", MACHDEP)
    n.variable("cflags", CFLAGS)
    n.variable("cxxflags", CXXFLAGS)
    n.variable("asflags", ASFLAGS)
    n.variable("ldflags", LDFLAGS)
    n.newline()

def emit_rules(n: Writer):
    """Emits the rules to a ninja file"""

    # .c -> .o compilation
    # Variables to pass in:
    #     verflags: defines for the region being compiled
    n.rule(
        "cc",
        command = "$cc -MMD -MT $out -MF $out.d $cflags -c $in -o $out",
        depfile = "$out.d",
        deps = "gcc",
        description = "CC $out"
    )

    # .cpp -> .o compilation
    # Variables to pass in:
    #     verflags: defines for the region being compiled
    n.rule(
        "cxx",
        command = "$cc -MMD -MT $out -MF $out.d $cxxflags $verflags -c $in -o $out",
        depfile = "$out.d",
        deps = "gcc",
        description = "CXX $out"
    )

    # .s -> .o compilation
    n.rule(
        "as",
        command = "$cc -MD -MT $out -MF $out.d $asflags -c $in -o $out",
        depfile = "$out.d",
        deps = "gcc",
        description = "AS $out"
    )

    # .lst -> .ld conversion
    n.rule(
        "lst2ld",
        command = "$python $lst2ld $in $out",
        description = "lst2ld $out"
    )

    # .o & .ld -> .elf linking
    # Variables to pass in:
    #     map: map file output path
    n.rule(
        "ld",
        command = "$cc $ldflags $ldscripts $in -o $out -Wl,-Map,$map",
        description = "LD $out"
    )
    n.newline()

    # .elf -> .bin conversion
    n.rule(
        "objcopy",
        command = "$objcopy $in $out -O binary",
        description = "OBJCOPY $out"
    )

    # .bin -> gecko .txt conversion
    # Variables to pass in:
    #     hookaddr: address to insert the branch to the payload
    #     baseaddr: address to load the bin at
    n.rule(
        "makegecko",
        command = "$python $makegecko $hookaddr $baseaddr $in $out",
        description = "makegecko $out"
    )

def find_files(path: str) -> List[str]:
    """Finds all files recursively in a directory"""

    ret = []
    for iname in os.listdir(path):
        # Build full path
        ipath = os.path.join(path, iname)

        if os.path.isdir(ipath):
            # Add all files within dir
            ret.extend(find_files(ipath))
        else:
            # Add file
            ret.append(ipath)

    return ret

def emit_build(n: Writer, ver: str):
    """Emits the build statements for a version to a ninja file"""

    # Emit source builds
    ofiles = []
    verflags = f"-DSPM_{ver.upper()}"
    for path in find_files(SRCDIR):
        # Get output name
        ofile = os.path.join("$builddir", ver, path + ".o")
        ofiles.append(ofile)

        # Choose rule based on file extension
        _, ext = os.path.splitext(path)
        if ext == ".c":
            # C source code
            n.build(
                ofile,
                rule = "cc",
                inputs = path,
                variables = { "verflags" : verflags }
            )
        elif ext == ".cpp":
            # C++ source code
            n.build(
                ofile,
                rule = "cxx",
                inputs = path,
                variables = { "verflags" : verflags }
            )
        elif ext in (".s", ".S"):
            # Asm source code
            n.build(
                ofile,
                rule = "as",
                inputs = path
            )
        else:
            assert False, f"Unknown file type {ext} for {path}"
    
    # Get ld scripts
    symbols = os.path.join("$builddir", ver, "symbols.ld")
    lst_ver = "eu0" if ver == "eu1" else ver
    lst = os.path.join("$spm_headers", "linker", f"spm.{lst_ver}.lst")
    n.build(
        symbols,
        rule = "lst2ld",
        inputs = lst
    )
    ldscripts = [
        os.path.join("$linkdir", "ldscript.ld"),
        symbols
    ]

    # Emit elf build
    elf_name = os.path.join("$outdir", f"{ver}.elf")
    map_name = os.path.join("$outdir", f"{ver}.map")
    n.build(
        elf_name,
        rule = "ld",
        inputs = ofiles,
        implicit = ldscripts,
        implicit_outputs = map_name,
        variables = {
            "map" : map_name,
            "ldscripts" : [f"-T{ld}" for ld in ldscripts]
        }
    )

    # Emit bin build
    bin_name = os.path.join("$outdir", f"{ver}.bin")
    n.build(
        bin_name,
        rule = "objcopy",
        inputs = elf_name
    )

    # Emit gecko build
    gecko_name = os.path.join("$outdir", f"{ver}.txt")
    n.build(
        gecko_name,
        rule = "makegecko",
        inputs = bin_name,
        variables = {
            "baseaddr" : BASE_ADDR,
            "hookaddr" : HOOK_ADDRS[ver]
        }
    )

    # Make a default target
    n.default(gecko_name)

    # Add short phony
    n.build(
        ver,
        rule = "phony",
        inputs = [gecko_name]
    )

versions = [
    "eu0",
    "eu1",
    "jp0",
    "jp1",
    "us0",
    "us1",
    "us2",
    "kr0",
]

def main(versions: List[str]):
    # Setup ninja
    outbuf = StringIO()
    n = Writer(outbuf)
    n.variable("ninja_required_version", "1.3")
    n.newline()

    # Emit
    emit_vars(n)
    emit_rules(n)
    for ver in versions:
        emit_build(n, ver)

    # Write to file
    with open("build.ninja", 'w') as f:
        f.write(outbuf.getvalue())
    n.close()

if __name__=="__main__":
    # Enable versions passed in comand line, default to all
    target_versions = sys.argv[1:]
    for v in target_versions:
        assert v in versions, f"Unknown version {v}"
    if len(target_versions) == 0:
        target_versions = versions

    # Make script
    main(target_versions)
