#!/usr/bin/env python3

from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass
from enum import IntEnum
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
    n.variable("builddir", BUILDDIR)
    n.variable("outdir", OUTDIR)
    n.variable("toolsdir", TOOLSDIR)

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
        command = "$cc $ldflags $flags $ldscripts $in -o $out -Wl,-Map,$map",
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
    n.rule(
        "makegecko",
        command = "$python $makegecko $in $out",
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
                else:
                    other[ext].append(SourceFile(path))

        return sources, other

    def _build(self, n: Writer):
        """Dummy - this file will always exist"""

        print("Exists - ", self.path)

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
        print("Build - ", self.path, [s.path for s in self.sources])

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

def build_elf(
    dest: str,
    map_dest: str,
    sources: List["CompilableSourceFile"],
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

#####################
# Project Specifics #
#####################

class GameVersion:
    """Information for a version of the game"""

    """Name of the version (rgX region rg revision X)"""
    name: str

    """LST for this version's symbols"""
    lst: File

    """Linker script for this version's symbols"""
    ldscript: File

    """Preprocessor define for this version"""
    define: str

    def __init__(self, name: str, ldscript_dest: str):
        # Save name
        self.name = name

        # Get preprocessor define
        self.define = f"SPM_{self.name.upper()}"

        # Get lst file
        lst_name = "eu0" if name == "eu1" else name
        self.lst = SourceFile(
            os.path.join("$spm_headers", "linker", f"spm.{lst_name}.lst")
        )

        # Get linker script
        self.ldscript = BuiltFile(
            ldscript_dest,
            "lst2ld",
            [self.lst]
        )

class Payload(ABC):
    """A payload's properties"""

    @abstractmethod
    def get_built(self, dest: str, builddir: str, game_ver: GameVersion) -> BuiltFile:
        """Get the BuiltFile for an implementation"""

        raise NotImplementedError

class RelLoader3(Payload):
    """Rel Loader payload"""

    SRCDIR = "relloader3"
    LDFLAGS = ' '.join([
        "-e loaderMain",
        "-u header",
    ])

    def get_built(self, dest: str, builddir: str, game_ver: GameVersion) -> BuiltFile:
        # Setup source files
        sources, other = SourceFile.collect_files(
            self.SRCDIR,
            {
                "flags" : ' '.join([
                    f"-D{game_ver.define}",
                ])
            }
        )
        ldscripts = other.pop(".ld") if ".ld" in other else []
        assert len(other) == 0, f"Unsupported files in {self.SRCDIR} {other}"

        ldscripts.append(game_ver.ldscript)

        # Make ELF
        elf_path = os.path.join(builddir, "relloader3.elf")
        map_path = elf_path + ".map"
        elf = build_elf(elf_path, map_path, sources, builddir, self.LDFLAGS, ldscripts)

        # Make bin
        return BuiltFile(
            dest,
            "objcopy",
            [elf]
        )

class ImplementationType(IntEnum):
    GECKO_CODE = 0
    DOL_PATCH = 1
    RIIVOLUTION = 2
    SAVE_EXPLOIT = 3

class Implementation(ABC):
    """An implementation's properties"""

    file: BuiltFile

    # Set by subclass
    type: ImplementationType
    version: int

    def __init__(self, dest: str, builddir: str, payload: Payload, game_ver: GameVersion):
        self.file = self._get_built(dest, builddir, payload, game_ver)
    
    @abstractmethod
    def _get_built(self, dest: str, builddir: str, payload: Payload, game_ver: GameVersion) -> BuiltFile:
        """Get the BuiltFile for this implementation"""

        raise NotImplementedError

class ImplGecko(Implementation):
    """Gecko Code loader implementation"""

    type = ImplementationType.GECKO_CODE
    version = 1

    def _get_built(self, dest: str, builddir: str, payload: Payload, game_ver: GameVersion) -> BuiltFile:
        """Get the BuiltFile for this implementation"""

        # Make payload
        payload_path = os.path.join(builddir, "payload.bin")
        payload_built = payload.get_built(payload_path, builddir, game_ver)

        return BuiltFile(
            dest,
            "makegecko",
            [payload_built]
        )

class ImplRiivo(Implementation):
    """Riivolution loader implementation"""

    version = 1
    type = ImplementationType.RIIVOLUTION

    def _get_built(self, dest: str, builddir: str, payload: Payload, game_ver: GameVersion) -> BuiltFile:
        payload_built = payload.get_built(dest, builddir, game_ver)

        return payload_built

    # TODO

class ImplSave(Implementation):
    """Specific details of the save exploit implementation
    
    Detailed in README.md"""

    version = 1
    type = ImplementationType.SAVE_EXPLOIT

    SRCDIR = "saveloader"
    LDFLAGS = ' '.join([
        "-e entry",
    ])

    def _get_saveloader(self, dest: str, builddir: str, payload: Payload, game_ver: GameVersion) -> BuiltFile:
        # Make payload
        payload_path = os.path.join(builddir, "payload.bin")
        payload_built = payload.get_built(payload_path, builddir, game_ver)

        # Setup source files
        as_safe_path = payload_built.path.replace('\\', '/')
        source = CompilableSourceFile(
            os.path.join(self.SRCDIR, "saveloader.s"),
            {
                "flags" : ' '.join([
                    f"-D{game_ver.define}",
                    f"-DPAYLOAD_PATH=\"{as_safe_path}\""
                ])
            },
            [payload_built]
        )

        # Make ELF
        elf_path = os.path.join(builddir, "saveloader.elf")
        map_path = elf_path + ".map"
        elf = build_elf(
            elf_path,
            map_path,
            [source],
            builddir,
            self.LDFLAGS,
            [game_ver.ldscript],
            [payload_built]
        )

        # Make bin
        return BuiltFile(
            dest,
            "objcopy",
            [elf]
        )

    def _get_built(self, dest: str, builddir: str, payload: Payload, game_ver: GameVersion) -> BuiltFile:
        # Make saveloader
        saveloader_path = os.path.join(builddir, "saveloader.bin")
        saveloader = self._get_saveloader(saveloader_path, builddir, payload, game_ver)

        # Make save file
        return BuiltFile(
            dest,
            "makewiimario",
            [saveloader],
            {
                "savename" : f"Rel Loader 3 {game_ver.name} v{self.version}",
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
        relloader = RelLoader3()
        impl_save = ImplSave(
            os.path.join("$outdir", f"wiimario_{game_ver.name}"),
            os.path.join(builddir, "save"),
            relloader,
            game_ver
        )
        impl_save.file.build(n)
        n.default(impl_save.file.path)

        impl_gecko = ImplGecko(
            os.path.join("$outdir", f"gecko_{game_ver.name}.txt"),
            os.path.join(builddir, "gecko"),
            relloader,
            game_ver
        )
        impl_gecko.file.build(n)
        n.default(impl_gecko.file.path)

        impl_riivo = ImplRiivo(
            os.path.join("$outdir", f"relloader3_{game_ver.name}.bin"),
            os.path.join(builddir, "riivo"),
            relloader,
            game_ver
        )
        impl_riivo.file.build(n)
        n.default(impl_riivo.file.path)

        n.build(
            game_ver.name,
            rule="phony",
            inputs=[
                impl_gecko.file.path,
                impl_save.file.path,
                impl_riivo.file.path
            ]
        )

    # Write to file
    with open("build.ninja", 'w') as f:
        f.write(outbuf.getvalue())
    n.close()

game_versions = {
    name : GameVersion(
        name,
        os.path.join("$builddir", name, "symbols.ld")
    )
    for name in [
        "eu0",
        "eu1",
        "us0",
        "us1",
        "us2",
        "jp0",
        "jp1",
        "kr0"        
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
