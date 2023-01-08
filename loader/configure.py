#!/usr/bin/env python3

from io import StringIO
import os
import sys
from typing import List

from ninja_syntax import Writer

#########
# Paths #
#########

# Python
PYTHON = sys.executable

# Project dirs
INCDIR = "include"
BUILDDIR = "build"
OUTDIR = "out"
TOOLSDIR = "tools"

# Project files
LST2LD = os.path.join("$toolsdir", "lst2ld.py")
MAKEGECKO = os.path.join("$toolsdir", "makegecko.py")
MAKEWIIMARIO = os.path.join("$toolsdir", "makewiimario.py")

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
        INCDIR,
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
    "-nostdinc", # Disable including std lib headers
    "-ffreestanding", # Tell compiler environment isn't hosted
])

# Base C flags
# Passed to C and C++ Compilation
CFLAGS = ' '.join([
    "$machdep",
    "$includes",

    "-ffunction-sections", # Allow function deadstripping
    "-fdata-sections", # Allow data deadstripping
    "-g", # Emit debug info
    "-O3", # High optimisation for speed
    "-Wall", # Enable all warnings
    "-Wextra", # Enable even more warnings
    "-Wpedantic", # Enable even more warnings than that
    "-Wshadow", # Enable variable shadowing warning
    "-Werror" # Error on warnings
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
    n.variable("builddir", BUILDDIR)
    n.variable("outdir", OUTDIR)
    n.variable("toolsdir", TOOLSDIR)

    n.variable("makegecko", MAKEGECKO)
    n.variable("makewiimario", MAKEWIIMARIO)
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
    #     flags: extra compiler flags
    n.rule(
        "cc",
        command = "$cc -MMD -MT $out -MF $out.d $cflags $flags -c $in -o $out",
        depfile = "$out.d",
        deps = "gcc",
        description = "CC $out"
    )

    # .cpp -> .o compilation
    # Variables to pass in:
    #     flags: extra compiler flags
    n.rule(
        "cxx",
        command = "$cc -MMD -MT $out -MF $out.d $cxxflags $flags -c $in -o $out",
        depfile = "$out.d",
        deps = "gcc",
        description = "CXX $out"
    )

    # .s -> .o compilation
    # Variables to pass in:
    #     flags: extra compiler flags
    n.rule(
        "as",
        command = "$cc -MD -MT $out -MF $out.d $asflags $flags -c $in -o $out",
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
    #     dest: address to load the payload at
    #     entry: addres to branch to in the payload
    #     hook: address to insert the branch to the payload
    n.rule(
        "makegecko",
        command = "$python $makegecko $in $dest $entry $hook $out",
        description = "makegecko $out"
    )

    # relloader & saveloader .bin -> wiimario conversion
    # Variables to pass in:
    #    savename: name of the save file to generate
    #    version: version of the game to build for
    n.rule(
        "makewiimario",
        command = "$python $makewiimario $in \"$savename\" $version $out"
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

def get_symbols_ld(ver: str) -> str:
    """Gets the symbols ld script path for a version"""

    return os.path.join("$builddir", f"symbols_{ver}.ld")

def build_symbols_ld(n: Writer, ver: str):
    """Builds the symbols ld script for a version"""

    lst_ver = "eu0" if ver == "eu1" else ver
    n.build(
        get_symbols_ld(ver),
        rule = "lst2ld",
        inputs = os.path.join("$spm_headers", "linker", f"spm.{lst_ver}.lst")
    )

# Ninja rule to run for a file extension
OFILE_EXT_RULES = {
    ".c" : "cc",
    ".cpp" : "cxx",
    ".s" : "as",
    ".S" : "as"
}

def build_module_elf(
    n: Writer,
    builddir: str,
    outdir: str,
    name: str,
    ver: str,
    extra_flags: str = "",
    extra_deps: List[str] = None
) -> str:
    """Builds an ELF for a module on a specific version"""

    # Handle source files
    ofiles = []
    ver_flags = f"-DSPM_{ver.upper()}"
    ldscripts = [get_symbols_ld(ver)]
    for path in find_files(name):
        # Choose rule based on file extension
        _, ext = os.path.splitext(path)
        if ext in OFILE_EXT_RULES:
            ofile = os.path.join(builddir, path + ".o")
            ofiles.append(ofile)
            rule = OFILE_EXT_RULES[ext]
            n.build(
                ofile,
                rule = rule,
                inputs = path,
                implicit = extra_deps or [],
                variables = { "flags" : f"{ver_flags} {extra_flags}" }
            )
        elif ext == ".ld":
            ldscripts.append(path)
        elif ext == ".h":
            pass
        else:
            assert False, f"Unknown file type {ext} for {path}"

    # Emit elf build
    elf_name = os.path.join(outdir, f"{name}_{ver}.elf")
    map_name = f"{elf_name}.map"
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

    return elf_name

# Loader Specifics #

BASE_ADDR = "80004200"
ENTRY_ADDR = "80004220"
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

REL_LOADER_VERSION = 1
IMPL_RIIVO_VERSION = 1
IMPL_GECKO_VERSION = 1
IMPL_SAVE_VERSION = 1

def build_relloader(
    n: Writer, 
    builddir: str,
    outdir: str,
    impl_type: str,
    impl_version: str,
    ver: str
) -> str:

    # Emit ELF build
    elf_name = build_module_elf(
        n,
        builddir,
        outdir,
        "relloader",
        ver,
        ' '.join([
            f"-DREL_LOADER_VERSION={REL_LOADER_VERSION}",
            f"-DIMPLEMENTATION_TYPE={impl_type}",
            f"-DIMPLEMENTATION_VERSION={impl_version}"
        ])
    )

    # Emit bin build
    bin_name = f"{elf_name}.bin"
    n.build(
        bin_name,
        rule = "objcopy",
        inputs = elf_name
    )

    return bin_name

def build_saveloader(
    n: Writer, 
    builddir: str,
    outdir: str,
    payload_path: str,
    ver: str
) -> str:
    # Emit ELF build
    as_safe_path = payload_path.replace('\\', '/')
    elf_name = build_module_elf(
        n,
        builddir,
        outdir,
        "saveloader",
        ver,
        ' '.join([
            f"-DPAYLOAD_PATH=\"{as_safe_path}\"",
            f"-DPAYLOAD_DEST=0x{BASE_ADDR}",
            f"-DPAYLOAD_ENTRY=0x{ENTRY_ADDR}",
            f"-DPAYLOAD_HOOK=0x{HOOK_ADDRS[ver]}"
        ]),
        [payload_path]
    )

    # Emit bin build
    bin_name = f"{elf_name}.bin"
    n.build(
        bin_name,
        rule = "objcopy",
        inputs = elf_name
    )

    return bin_name

def impl_gecko(n: Writer, ver: str) -> str:
    builddir = os.path.join("$builddir", ver, "gecko")
    outdir = os.path.join("$outdir", ver, "gecko")
    
    bin_path = build_relloader(n, builddir, outdir, 0, IMPL_GECKO_VERSION, ver)

    # Emit gecko build
    gecko_path = os.path.join(outdir, f"gecko_{ver}.txt")
    n.build(
        gecko_path,
        rule = "makegecko",
        inputs = bin_path,
        variables = {
            "dest" : BASE_ADDR,
            "entry" : ENTRY_ADDR,
            "hook" : HOOK_ADDRS[ver]
        }
    )

    return gecko_path

def impl_riivo(n: Writer, ver: str) -> str:
    builddir = os.path.join("$builddir", ver, "riivo")
    outdir = os.path.join("$outdir", ver, "riivo")

    bin_path = build_relloader(n, builddir, outdir, 2, IMPL_RIIVO_VERSION, ver)

    return bin_path

def impl_save(n: Writer, ver: str) -> str:
    builddir = os.path.join("$builddir", ver, "save")
    outdir = os.path.join("$outdir", ver, "save")

    bin_path = build_relloader(n, builddir, outdir, 2, IMPL_SAVE_VERSION, ver)

    # Build saveloader
    saveloader = build_saveloader(n, builddir, outdir, bin_path, ver)

    save_path = os.path.join(outdir, f"wiimario_{ver}")
    n.build(
        save_path,
        rule = "makewiimario",
        inputs = [saveloader],
        variables = {
            "savename" : f"Rel Loader 3 [{ver} {REL_LOADER_VERSION} {IMPL_SAVE_VERSION}]",
            "version" : ver
        }
    )

    return save_path

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
        # Generate symbols script
        build_symbols_ld(n, ver)

        riivo_path = impl_riivo(n, ver)
        gecko_path = impl_gecko(n, ver)
        save_path = impl_save(n, ver)

        # Add build shortcuts
        n.build(
            ver,
            rule = "phony",
            inputs = [
                riivo_path,
                gecko_path,
                save_path
            ]
        )
        n.default(ver)

    # Write to file
    with open("build.ninja", 'w') as f:
        f.write(outbuf.getvalue())
    n.close()

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

if __name__=="__main__":
    # Enable versions passed in comand line, default to all
    target_versions = sys.argv[1:]
    for v in target_versions:
        assert v in versions, f"Unknown version {v}"
    if len(target_versions) == 0:
        target_versions = versions

    # Make script
    main(target_versions)
