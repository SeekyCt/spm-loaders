#!/usr/bin/env python3

from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass
from io import StringIO
from itertools import chain
import os
import sys
from typing import Dict, List, Optional, Tuple

from ninja_syntax import Writer

##################
# Constant Paths #
##################

# Project dirs
INCDIR = "include"
BUILDDIR = "build"
OUTDIR = "out"
TOOLSDIR = "tools"
DUMPDIR = "dump"

# Libraries
SPM_HEADERS = "spm-headers"

##############
# Tool Paths #
##############

# Python
PYTHON = sys.executable

# Devkitppc
DEVKITPPC = os.environ.get("DEVKITPPC")
assert DEVKITPPC is not None, "Error: DEVKITPPC environment variable not set"
CC = os.path.join("$devkitppc", "bin", "powerpc-eabi-gcc")
OBJCOPY = os.path.join("$devkitppc", "bin", "powerpc-eabi-objcopy")

# Project tools
LST2LD = os.path.join("$toolsdir", "lst2ld.py")
MAKEGECKO = os.path.join("$toolsdir", "makegecko.py")
MAKEWIIMARIO = os.path.join("$toolsdir", "makewiimario.py")
PATCHDOL = os.path.join("$toolsdir", "patchdol.py")

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
    "-DGEKKO", # CPU preprocessor define
    "-mcpu=750", # Set CPU to 750cl
    "-meabi", # Set ppc abi to eabi
    "-mhard-float", # Enable hardware floats
    "-nostdlib", # Don't link std lib
    "-lgcc", # Link gcc helper functions
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
    "-Os", # Optimisation for space
    "-Wall", # Enable all warnings
    "-Wextra", # Enable even more warnings
    "-Wpedantic", # Enable even more warnings than that
    "-Wshadow", # Enable variable shadowing warning
    "-Werror", # Error on warnings
    "-fmax-errors=1", # Stop after 1 error
])

# C++ flags
# Passed only to C++ compilation
CXXFLAGS = ' '.join([
    "$cflags",

    "-fno-exceptions", # Disable C++ exceptions
    "-fno-rtti", # Disable runtime type info
    "-std=gnu++17", # Use C++17 with GNU extensions
    "-Wno-vla", # Enable variable-length arrays
])

# Asm flags
# Passed only to asm compilation
ASFLAGS = ' '.join([
    "$machdep",
    "$includes",

    "-x assembler-with-cpp", # Enable C preprocessor
])

# Linker flags
LDFLAGS = ' '.join([
    "$machdep",

    "-g", # Output debug info
    ','.join([
        "-Wl", # Pass the following options to the linker
        "--gc-sections", # Strip unused sections
        "--force-group-allocation", # Merge section groups
    ]),
])

###################
# Ninja Variables #
###################

def emit_vars(n: Writer):
    """Emits the variables to a ninja file"""

    # Project dirs
    n.variable("incdir", INCDIR)
    n.variable("builddir", BUILDDIR)
    n.variable("outdir", OUTDIR)
    n.variable("toolsdir", TOOLSDIR)
    n.variable("dumpdir", DUMPDIR)

    # Libraries
    n.variable("spm_headers", SPM_HEADERS)

    # Python
    n.variable("python", PYTHON)

    # Devkitppc
    n.variable("devkitppc", DEVKITPPC)
    n.variable("cc", CC)
    n.variable("objcopy", OBJCOPY)

    # Project tools
    n.variable("makegecko", MAKEGECKO)
    n.variable("makewiimario", MAKEWIIMARIO)
    n.variable("lst2ld", LST2LD)
    n.variable("patchdol", PATCHDOL)

    # Tool flags
    n.variable("includes", INCLUDES)
    n.variable("machdep", MACHDEP)
    n.variable("cflags", CFLAGS)
    n.variable("cxxflags", CXXFLAGS)
    n.variable("asflags", ASFLAGS)
    n.variable("ldflags", LDFLAGS)
    n.newline()

###############
# Ninja Rules #
###############

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
    #     flags: extra linker flags
    n.rule(
        "ld",
        command = "$cc $in $ldflags $flags $ldscripts -o $out -Wl,-Map,$map",
        description = "LD $out"
    )
    n.newline()

    # .elf -> .bin conversion
    n.rule(
        "objcopy",
        command = "$objcopy $in $out -O binary --set-section-flags .bss=alloc,load,contents",
        description = "OBJCOPY $out"
    )

    # .bin -> gecko .txt conversion
    n.rule(
        "makegecko",
        command = "$python $makegecko $in $out --revision $revision",
        description = "makegecko $out"
    )

    # relloader & saveloader .bin -> wiimario conversion
    # Variables to pass in:
    #    savename: name of the save file to generate
    #    game_ver: version of the game to build for
    n.rule(
        "makewiimario",
        command = "$python $makewiimario $in \"$savename\" $game_ver $out"
    )

    # dol & paylod bin -> dol patching
    n.rule(
        "patchdol",
        command = "$python $patchdol $in $out"
    )

##################
# Ninja Wrappers #
##################

@dataclass
class File(ABC):
    """A file involved in the build process"""

    """Path to the file"""
    path: str

    """Whether the build statement for the file has been emitted"""
    _built = False
    
    @abstractmethod
    def _build(self, n: Writer):
        """Emits the build statement for this file"""

        pass

    def build(self, n: Writer):
        """Emits the build statement for this file if not already done"""

        if not self._built:
            self._built = True
            self._build(n)


"""Variables to pass into a ninja build statement"""
NinjaVars = Dict[str, str]


@dataclass
class SourceFile(File):
    """An existing source file - build method stubbed"""

    """File extensions to ignore in collect"""
    IGNORE_EXTENSIONS = [".h"]

    """A collection of files grouped by file extension"""
    FilesByExtension = Dict[str, List[File]]

    @classmethod
    def collect_files(cls, dir_path: str, variables: Optional[NinjaVars] = None
                     ) -> Tuple[List["CompilableSourceFile"], FilesByExtension]:
        """Finds all files recursively in a directory
        
        Files with known rules are returned as CompilableSourceFile instances
        Other files are returned in a FilesByExtension dictionary"""

        sources = []
        other = defaultdict(list)
        for name in os.listdir(dir_path):
            # Build full path
            path = os.path.join(dir_path, name)

            if os.path.isdir(path):
                # Add files from directory
                new_sources, new_other = cls.collect_files(path, variables)
                sources.extend(new_sources)
                other |= new_other
            else:
                # Split file extension
                _, ext = os.path.splitext(name)

                # Add file based on extension
                if CompilableSourceFile.is_compilable(ext):
                    sources.append(CompilableSourceFile(path, variables))
                elif ext not in cls.IGNORE_EXTENSIONS:
                    other[ext].append(SourceFile(path))

        return sources, other

    def _build(self, n: Writer):
        """Dummy - this file will always exist"""

        pass

@dataclass
class CompilableSourceFile(SourceFile):
    """A source file which can be compiled"""

    """Variables to pass into build"""
    variables: Optional[NinjaVars] = None

    """Extra implicit dependencies of the built source file"""
    extra_deps: Optional[List[File]] = None

    """Mapping of compilable file extensions to build rules"""
    EXTENSIONS = {
        ".c" : "cc",
        ".cpp" : "cxx",
        ".s" : "as",
        ".S" : "as",
    }

    @classmethod
    def is_compilable(cls, ext: str) -> bool:
        """Checks whether a rule is known to compile an extension"""
        return ext in cls.EXTENSIONS

    def get_built(self, builddir: str) -> "BuiltFile":
        """Get the BuiltFile for this source file"""

        # Get dest path
        dest = os.path.join(builddir, self.path + ".o")

        # Get rule
        _, ext = os.path.splitext(self.path)
        rule = self.EXTENSIONS[ext]

        return BuiltFile(dest, rule, [self], self.variables, self.extra_deps)

@dataclass
class BuiltFile(File):
    """A file produced in the build process"""

    """Rule to build this file with"""
    rule: str

    """Sources this file requires to build"""
    sources: List[File]

    """Variables to build with"""
    variables: Optional[Dict[str, str]] = None

    """Implicit dependencies for this file"""
    extra_deps: Optional[List[File]] = None

    def _build(self, n: Writer):
        # Build dependencies
        for source in chain(self.sources, self.extra_deps or []):
            source.build(n)

        # Emit build statement
        n.build(
            self.path,
            rule = self.rule,
            inputs = [s.path for s in self.sources],
            implicit = [d.path for d in self.extra_deps or []],
            variables = self.variables,
        )

    def make_default(self, n: Writer):
        self.build(n)
        n.default(self.path)

def build_elf(
    dest: str,
    map_dest: str,
    sources: List[CompilableSourceFile],
    builddir: str,
    ldflags: str = "",
    ldscripts: Optional[List[File]] = None,
    extra_deps: Optional[List[File]] = None
):
    """Builds an ELF file from a list of sources"""

    # Get object files for all sources
    ofiles = [source.get_built(builddir) for source in sources]

    # Make build
    return BuiltFile(
        dest,
        "ld",
        ofiles,
        {
            "map" : map_dest,
            "flags" : ldflags,
            "ldscripts" : ' '.join([f"-T{ld.path}" for ld in ldscripts or []])
        },
        (extra_deps or []) + (ldscripts or [])
    )

def build_phony(name: str, files: List[BuiltFile]) -> BuiltFile:
    """Adds a phony build rule for some files"""

    return BuiltFile(
        name,
        "phony",
        [f for f in files]
    )

#####################
# Project Specifics #
#####################

class GameVersion:
    """Information for a version of the game"""

    """Name of the version (rgX region rg revision X)"""
    name: str

    """Region name"""
    region: str

    """Revision number"""
    revision: int

    """LST for this version's symbols"""
    lst: File

    """Linker script for this version's symbols"""
    ldscript: File

    """Preprocessor define for this version"""
    define: str

    """Path to the main.dol file for this version"""
    dol: File

    def __init__(self, region: str, revision: int):
        # Save region and revision
        self.region = region
        self.revision = revision

        # Build name
        self.name = f"{region}{revision}"

        # Get preprocessor define
        self.define = f"SPM_{self.name.upper()}"

        # Get lst file and dol
        dol_name = "eu0" if self.name == "eu1" else self.name
        self.dol = SourceFile(
            os.path.join("$dumpdir", dol_name, "main.dol")
        )
        self.lst = SourceFile(
            os.path.join("$spm_headers", "linker", f"spm.{dol_name}.lst")
        )

        # Get linker script
        self.ldscript = BuiltFile(
            os.path.join("$builddir", self.name, "symbols.ld"),
            "lst2ld",
            [self.lst]
        )

def build_relloader3(dest: str, builddir: str, game_ver: GameVersion) -> BuiltFile:
    """Builds the relloader3 payload"""

    # Setup source files
    sources, other = SourceFile.collect_files(
        "relloader3",
        {
            "flags" : ' '.join([
                f"-D{game_ver.define}",
            ])
        }
    )
    ldscripts = other.pop(".ld") if ".ld" in other else []
    assert len(other) == 0, f"Unsupported files in srcdir {[x for x in other.values()]}"

    ldscripts.append(game_ver.ldscript)

    # Make ELF
    elf_path = os.path.join(builddir, "relloader3.elf")
    map_path = elf_path + ".map"
    elf = build_elf(
        elf_path,
        map_path,
        sources,
        builddir,
        ' '.join([
            "-e loaderMain",
            "-u header",
        ]),
        ldscripts
    )

    # Make bin
    return BuiltFile(
        dest,
        "objcopy",
        [elf]
    )

def build_impl_gecko(dest: str, payload: BuiltFile, game_ver: GameVersion) -> BuiltFile:
    """Builds the gecko code implementation of a payload"""

    return BuiltFile(
        dest,
        "makegecko",
        [payload],
        {
            "revision" : str(game_ver.revision),
        }
    )

def build_impl_riivo(dest: str, payload: BuiltFile) -> BuiltFile:
    """Builds the riivolution implementation of a payload"""

    # TODO
    return payload

def build_impl_dol(dest: str, payload: BuiltFile, game_ver: GameVersion) -> BuiltFile:
    """Builds the dol implementation of a payload"""

    return BuiltFile(
        dest,
        "patchdol",
        [game_ver.dol, payload]
    )

def build_saveloader(dest: str, builddir: str, payload: BuiltFile, game_ver: GameVersion
                    ) -> BuiltFile:
    """Builds the saveloader makewiimario "payload" """

    # Setup source files
    as_safe_path = payload.path.replace('\\', '/')
    source = CompilableSourceFile(
        os.path.join("saveloader", "saveloader.s"),
        {
            "flags" : ' '.join([
                f"-D{game_ver.define}",
                f"-DPAYLOAD_PATH=\"{as_safe_path}\""
            ])
        },
        [payload]
    )

    # Make ELF
    elf_path = os.path.join(builddir, "saveloader.elf")
    map_path = elf_path + ".map"
    elf = build_elf(
        elf_path,
        map_path,
        [source],
        builddir,
        ' '.join([
                "-e entry",
        ]),
        [game_ver.ldscript],
        [payload]
    )

    # Make bin
    return BuiltFile(
        dest,
        "objcopy",
        [elf]
    )

def build_impl_save(dest: str, builddir: str, payload: BuiltFile, game_ver: GameVersion
                   ) -> BuiltFile:
    """Builds the save exploit implementation of a payload"""

    # Make saveloader
    saveloader_path = os.path.join(builddir, "saveloader.bin")
    saveloader = build_saveloader(saveloader_path, builddir, payload, game_ver)

    # Make save file
    return BuiltFile(
        dest,
        "makewiimario",
        [saveloader],
        {
            "savename" : f"Rel Loader 3 {game_ver.name}",
            "game_ver" : game_ver.name
        }
    )

def main(game_versions: List[GameVersion]):
    outbuf = StringIO()
    n = Writer(outbuf)
    n.variable("ninja_required_version", "1.3")
    n.newline()

    emit_vars(n)
    emit_rules(n)

    for game_ver in game_versions:
        builddir = os.path.join("$builddir", game_ver.name)

        # Build rel loader
        relloader = build_relloader3(
            os.path.join("$outdir", f"relloader_{game_ver.name}.bin"),
            os.path.join(builddir, "relloader3"),
            game_ver
        )

        # Build implementations
        implementations = []
        implementations.append(
            build_impl_save(
                os.path.join("$outdir", f"wiimario_{game_ver.name}"),
                os.path.join(builddir, "save"),
                relloader,
                game_ver
            )
        )
        implementations.append(
            build_impl_gecko(
                os.path.join("$outdir", f"gecko_{game_ver.name}.txt"),
                relloader,
                game_ver
            )
        )
        implementations.append(
            build_impl_riivo(
                os.path.join("$outdir", f"riivolution_{game_ver.name}.bin"),
                relloader,
            )
            )
        if os.path.exists(os.path.join(DUMPDIR, game_ver.name, "main.dol")):
            implementations.append(
                build_impl_dol(
                    os.path.join("$outdir", f"{game_ver.name}.dol"),
                    relloader,
                    game_ver
                )
            )
        else:
            print(f"Note: dol not found for {game_ver.name}, skipping dol patch")

        # Make alias
        phony = build_phony(
            game_ver.name,
            [
                relloader,
                *implementations
            ]
        )
        phony.make_default(n)

    # Write to file
    with open("build.ninja", 'w') as f:
        f.write(outbuf.getvalue())
    n.close()

game_versions = {
    f"{region}{revision}" : GameVersion(
        region, revision
    )
    for region, revision in [
        ("eu", 0),
        ("eu", 1),
        ("us", 0),
        ("us", 1),
        ("us", 2),
        ("jp", 0),
        ("jp", 1),
        ("kr", 0)        
    ]
}

if __name__ == "__main__":
    # Enable versions passed in comand line, default to all
    target_versions = []
    for ver in sys.argv[1:]:
        target_versions.append(game_versions[ver])
    if len(target_versions) == 0:
        target_versions = [game_versions[ver] for ver in game_versions]

    # Make script
    main(target_versions)
