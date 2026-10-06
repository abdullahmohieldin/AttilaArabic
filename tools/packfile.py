#!/usr/bin/env python3
"""
Napoleon Total War Pack File Manager
A Python library and CLI for reading/writing .pack files.

Supports PFH0, PFH4, and PFH5 formats (Empire, Napoleon, and newer Total War games).
"""

import struct
import os
import argparse
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Optional, BinaryIO


# Pack file type constants
PACK_TYPES = {
    0: "boot",
    1: "release",
    2: "patch",
    3: "mod",
    4: "movie"
}

# Header format identifiers
PFH0 = b"PFH0"
PFH4 = b"PFH4"
PFH5 = b"PFH5"


def normalize_pack_path(path: str) -> str:
    """Normalize a pack file path to use backslashes (internal format)."""
    return path.replace('/', '\\')


@dataclass
class PackedFile:
    """Represents a single file entry in a pack file."""
    path: str
    size: int
    offset: int  # Offset in the pack file where data starts
    data: Optional[bytes] = None  # Loaded on demand

    def __repr__(self):
        return f"PackedFile(path='{self.path}', size={self.size})"


@dataclass
class PackHeader:
    """Pack file header information."""
    version: bytes  # PFH0, PFH4, PFH5
    pack_type: int
    flags: int
    pack_index_count: int  # Number of dependency pack references
    pack_index_size: int
    file_count: int
    file_index_size: int
    timestamp: int

    @property
    def pack_type_name(self) -> str:
        return PACK_TYPES.get(self.pack_type, "unknown")


class PackFile:
    """
    Handles reading and writing Total War pack files.

    Supports:
    - PFH0: Empire Total War (early)
    - PFH4: Napoleon Total War, Empire Total War
    - PFH5: Newer Total War games
    """

    def __init__(self, filepath: Optional[str] = None):
        self.filepath = filepath
        self.header: Optional[PackHeader] = None
        self.files: Dict[str, PackedFile] = {}
        self.pack_dependencies: List[str] = []
        self._file_handle: Optional[BinaryIO] = None

        if filepath and os.path.exists(filepath):
            self.load(filepath)

    def load(self, filepath: str) -> None:
        """Load a pack file and parse its index."""
        self.filepath = filepath
        self.files.clear()
        self.pack_dependencies.clear()

        with open(filepath, "rb") as f:
            # Read and validate header
            self.header = self._read_header(f)

            # Read pack dependencies (if any)
            if self.header.pack_index_count > 0:
                self.pack_dependencies = self._read_pack_index(f, self.header)

            # Calculate where file data starts
            header_size = self._get_header_size(self.header.version)
            data_start = header_size + self.header.pack_index_size + self.header.file_index_size

            # Read file index
            self.files = self._read_file_index(f, self.header, data_start)

    def _get_header_size(self, version: bytes) -> int:
        """Get header size based on pack version."""
        if version == PFH0:
            return 24
        elif version == PFH4:
            return 28
        elif version == PFH5:
            return 32  # Base size, can be extended
        return 28  # Default to PFH4

    def _read_header(self, f: BinaryIO) -> PackHeader:
        """Read and parse the pack file header."""
        version = f.read(4)

        if version not in (PFH0, PFH4, PFH5):
            raise ValueError(f"Unknown pack format: {version}. Expected PFH0, PFH4, or PFH5")

        if version == PFH0:
            # PFH0: 24 bytes total (same as PFH4 without timestamp)
            # type+flags(4), pack_idx_count(4), pack_idx_size(4),
            # file_count(4), file_idx_size(4)
            type_flags = struct.unpack("<I", f.read(4))[0]
            pack_index_count = struct.unpack("<I", f.read(4))[0]
            pack_index_size = struct.unpack("<I", f.read(4))[0]
            file_count = struct.unpack("<I", f.read(4))[0]
            file_index_size = struct.unpack("<I", f.read(4))[0]

            return PackHeader(
                version=version,
                pack_type=type_flags & 0xF,
                flags=(type_flags >> 4),
                pack_index_count=pack_index_count,
                pack_index_size=pack_index_size,
                file_count=file_count,
                file_index_size=file_index_size,
                timestamp=0
            )

        elif version == PFH4:
            # PFH4: 28 bytes total
            # type+flags(4), pack_idx_count(4), pack_idx_size(4),
            # file_count(4), file_idx_size(4), timestamp(4)
            type_flags = struct.unpack("<I", f.read(4))[0]
            pack_index_count = struct.unpack("<I", f.read(4))[0]
            pack_index_size = struct.unpack("<I", f.read(4))[0]
            file_count = struct.unpack("<I", f.read(4))[0]
            file_index_size = struct.unpack("<I", f.read(4))[0]
            timestamp = struct.unpack("<I", f.read(4))[0]

            return PackHeader(
                version=version,
                pack_type=type_flags & 0xF,
                flags=(type_flags >> 4),
                pack_index_count=pack_index_count,
                pack_index_size=pack_index_size,
                file_count=file_count,
                file_index_size=file_index_size,
                timestamp=timestamp
            )

        else:  # PFH5
            # PFH5: 32 bytes base
            type_flags = struct.unpack("<I", f.read(4))[0]
            pack_index_count = struct.unpack("<I", f.read(4))[0]
            pack_index_size = struct.unpack("<I", f.read(4))[0]
            file_count = struct.unpack("<I", f.read(4))[0]
            file_index_size = struct.unpack("<I", f.read(4))[0]
            timestamp = struct.unpack("<I", f.read(4))[0]
            f.read(4)  # Additional unknown bytes

            return PackHeader(
                version=version,
                pack_type=type_flags & 0xF,
                flags=(type_flags >> 4),
                pack_index_count=pack_index_count,
                pack_index_size=pack_index_size,
                file_count=file_count,
                file_index_size=file_index_size,
                timestamp=timestamp
            )

    def _read_pack_index(self, f: BinaryIO, header: PackHeader) -> List[str]:
        """Read pack dependency references."""
        dependencies = []
        for _ in range(header.pack_index_count):
            name = self._read_null_string(f)
            dependencies.append(name)
        return dependencies

    def _read_file_index(self, f: BinaryIO, header: PackHeader, data_start: int) -> Dict[str, PackedFile]:
        """Read the file index and build file entries."""
        files = {}
        current_offset = data_start

        for _ in range(header.file_count):
            # Read file size (4 bytes)
            size = struct.unpack("<I", f.read(4))[0]

            # Read null-terminated file path
            raw_path = self._read_null_string(f)
            # Normalize to backslashes for consistent internal representation
            path = normalize_pack_path(raw_path)

            # Create file entry
            entry = PackedFile(
                path=path,
                size=size,
                offset=current_offset
            )
            files[path] = entry
            current_offset += size

        return files

    def _read_null_string(self, f: BinaryIO) -> str:
        """Read a null-terminated string from the file."""
        chars = []
        while True:
            c = f.read(1)
            if c == b'\x00' or c == b'':
                break
            chars.append(c)
        return b''.join(chars).decode('utf-8', errors='replace')

    def list_files(self) -> List[str]:
        """Return a list of all file paths in the pack."""
        return list(self.files.keys())

    def has_file(self, path: str) -> bool:
        """Check if a file exists in the pack."""
        return normalize_pack_path(path) in self.files

    def get_file(self, path: str) -> Optional[bytes]:
        """Read and return the contents of a file from the pack."""
        path = normalize_pack_path(path)
        if path not in self.files:
            return None

        entry = self.files[path]

        # If data already loaded, return it
        if entry.data is not None:
            return entry.data

        # Read from pack file
        with open(self.filepath, "rb") as f:
            f.seek(entry.offset)
            entry.data = f.read(entry.size)

        return entry.data

    def extract_file(self, pack_path: str, output_path: str) -> bool:
        """Extract a single file from the pack to disk."""
        data = self.get_file(pack_path)
        if data is None:
            return False

        # Create output directory if needed
        os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)

        with open(output_path, "wb") as f:
            f.write(data)
        return True

    def extract_all(self, output_dir: str) -> int:
        """Extract all files to the specified directory. Returns count extracted."""
        count = 0
        for path in self.files:
            output_path = os.path.join(output_dir, path)
            if self.extract_file(path, output_path):
                count += 1
        return count

    def set_file(self, path: str, data: bytes) -> None:
        """Add or replace a file in the pack (in memory)."""
        path = normalize_pack_path(path)
        if path in self.files:
            # Update existing entry
            self.files[path].data = data
            self.files[path].size = len(data)
        else:
            # Add new entry
            self.files[path] = PackedFile(
                path=path,
                size=len(data),
                offset=0,  # Will be calculated on save
                data=data
            )

    def set_file_from_disk(self, pack_path: str, disk_path: str) -> None:
        """Add or replace a file from disk."""
        with open(disk_path, "rb") as f:
            data = f.read()
        self.set_file(pack_path, data)

    def remove_file(self, path: str) -> bool:
        """Remove a file from the pack."""
        path = normalize_pack_path(path)
        if path in self.files:
            del self.files[path]
            return True
        return False

    def save(self, filepath: Optional[str] = None) -> None:
        """Save the pack file to disk."""
        filepath = filepath or self.filepath
        if not filepath:
            raise ValueError("No filepath specified")

        # Ensure all file data is loaded
        for path, entry in self.files.items():
            if entry.data is None:
                self.get_file(path)

        # Determine version to use - default to PFH0 for Napoleon Total War compatibility
        version = self.header.version if self.header else PFH0
        pack_type = self.header.pack_type if self.header else 3  # mod

        # Build file index
        file_index = bytearray()
        for path, entry in self.files.items():
            file_index.extend(struct.pack("<I", entry.size))
            file_index.extend(path.encode('utf-8'))
            file_index.append(0)  # Null terminator

        # Build pack index (dependencies)
        pack_index = bytearray()
        for dep in self.pack_dependencies:
            pack_index.extend(dep.encode('utf-8'))
            pack_index.append(0)

        # Build header
        header = bytearray()
        header.extend(version)

        type_flags = pack_type  # Just type for now, no special flags

        if version == PFH0:
            # PFH0: same as PFH4 but without timestamp (24 bytes total)
            header.extend(struct.pack("<I", type_flags))
            header.extend(struct.pack("<I", len(self.pack_dependencies)))
            header.extend(struct.pack("<I", len(pack_index)))
            header.extend(struct.pack("<I", len(self.files)))
            header.extend(struct.pack("<I", len(file_index)))
        elif version == PFH4:
            header.extend(struct.pack("<I", type_flags))
            header.extend(struct.pack("<I", len(self.pack_dependencies)))
            header.extend(struct.pack("<I", len(pack_index)))
            header.extend(struct.pack("<I", len(self.files)))
            header.extend(struct.pack("<I", len(file_index)))
            header.extend(struct.pack("<I", self.header.timestamp if self.header else 0))
        else:  # PFH5
            header.extend(struct.pack("<I", type_flags))
            header.extend(struct.pack("<I", len(self.pack_dependencies)))
            header.extend(struct.pack("<I", len(pack_index)))
            header.extend(struct.pack("<I", len(self.files)))
            header.extend(struct.pack("<I", len(file_index)))
            header.extend(struct.pack("<I", self.header.timestamp if self.header else 0))
            header.extend(b'\x00' * 4)

        # Write the file
        with open(filepath, "wb") as f:
            f.write(header)
            f.write(pack_index)
            f.write(file_index)

            # Write file data in index order
            for path in self.files:
                entry = self.files[path]
                if entry.data:
                    f.write(entry.data)

        self.filepath = filepath

    def info(self) -> str:
        """Return a summary of the pack file."""
        if not self.header:
            return "No pack file loaded"

        lines = [
            f"Pack File: {self.filepath}",
            f"Version: {self.header.version.decode()}",
            f"Type: {self.header.pack_type_name} ({self.header.pack_type})",
            f"Files: {len(self.files)}",
            f"Dependencies: {len(self.pack_dependencies)}",
        ]

        if self.pack_dependencies:
            lines.append("Dependency packs:")
            for dep in self.pack_dependencies:
                lines.append(f"  - {dep}")

        return "\n".join(lines)


def main():
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description="Napoleon Total War Pack File Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List files in a pack
  python packfile.py list mymod.pack

  # Extract a specific file
  python packfile.py extract mymod.pack db/units_tables/data --output units.tsv

  # Extract all files
  python packfile.py extract-all mymod.pack --output ./extracted/

  # Replace a file in a pack
  python packfile.py replace mymod.pack db/units_tables/data units_modified.tsv

  # Add a new file to a pack
  python packfile.py add mymod.pack db/new_table/data newfile.tsv

  # Show pack info
  python packfile.py info mymod.pack
"""
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Info command
    info_parser = subparsers.add_parser("info", help="Show pack file information")
    info_parser.add_argument("packfile", help="Path to the pack file")

    # List command
    list_parser = subparsers.add_parser("list", help="List files in a pack")
    list_parser.add_argument("packfile", help="Path to the pack file")
    list_parser.add_argument("--filter", "-f", help="Filter paths containing this string")

    # Extract command
    extract_parser = subparsers.add_parser("extract", help="Extract a file from the pack")
    extract_parser.add_argument("packfile", help="Path to the pack file")
    extract_parser.add_argument("filepath", help="Path of file within the pack")
    extract_parser.add_argument("--output", "-o", help="Output file path", required=True)

    # Extract-all command
    extract_all_parser = subparsers.add_parser("extract-all", help="Extract all files")
    extract_all_parser.add_argument("packfile", help="Path to the pack file")
    extract_all_parser.add_argument("--output", "-o", help="Output directory", required=True)

    # Replace command
    replace_parser = subparsers.add_parser("replace", help="Replace a file in the pack")
    replace_parser.add_argument("packfile", help="Path to the pack file")
    replace_parser.add_argument("filepath", help="Path of file within the pack")
    replace_parser.add_argument("source", help="Source file to insert")
    replace_parser.add_argument("--output", "-o", help="Output pack file (default: overwrite)")

    # Add command
    add_parser = subparsers.add_parser("add", help="Add a new file to the pack")
    add_parser.add_argument("packfile", help="Path to the pack file")
    add_parser.add_argument("filepath", help="Path for the file within the pack")
    add_parser.add_argument("source", help="Source file to add")
    add_parser.add_argument("--output", "-o", help="Output pack file (default: overwrite)")

    # Remove command
    remove_parser = subparsers.add_parser("remove", help="Remove a file from the pack")
    remove_parser.add_argument("packfile", help="Path to the pack file")
    remove_parser.add_argument("filepath", help="Path of file to remove")
    remove_parser.add_argument("--output", "-o", help="Output pack file (default: overwrite)")

    # Create command
    create_parser = subparsers.add_parser("create", help="Create a new empty pack file")
    create_parser.add_argument("packfile", help="Path for the new pack file")
    create_parser.add_argument("--type", "-t", type=int, choices=[0, 1, 2, 3, 4], default=3,
                               help="Pack type: 0=boot, 1=release, 2=patch, 3=mod (default), 4=movie")
    create_parser.add_argument("--version", "-v", choices=['PFH0', 'PFH4', 'PFH5'], default='PFH4',
                               help="Pack format version (default: PFH4 for Napoleon TW)")

    # Set-type command
    settype_parser = subparsers.add_parser("set-type", help="Change pack type")
    settype_parser.add_argument("packfile", help="Path to the pack file")
    settype_parser.add_argument("type", type=int, choices=[0, 1, 2, 3, 4],
                                help="Pack type: 0=boot, 1=release, 2=patch, 3=mod, 4=movie")
    settype_parser.add_argument("--output", "-o", help="Output pack file (default: overwrite)")

    # Dump command (full extraction with DB parsing)
    dump_parser = subparsers.add_parser("dump", help="Dump pack contents to readable formats")
    dump_parser.add_argument("packfile", help="Path to the pack file")
    dump_parser.add_argument("--output", "-o", help="Output directory (default: <packname>_dump/)")
    dump_parser.add_argument("--db-format", choices=['json', 'csv'], default='json',
                            help="Output format for DB tables")
    dump_parser.add_argument("--unluac", metavar='PATH', help="Path to unluac.jar for Lua decompilation")
    dump_parser.add_argument("--no-lua-decompile", action='store_true', help="Skip Lua decompilation")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    try:
        # Handle create command separately (no existing file to load)
        if args.command == "create":
            new_pack = PackFile()
            version_map = {'PFH0': PFH0, 'PFH4': PFH4, 'PFH5': PFH5}
            new_pack.header = PackHeader(
                version=version_map[args.version],
                pack_type=args.type,
                flags=0,
                pack_index_count=0,
                pack_index_size=0,
                file_count=0,
                file_index_size=0,
                timestamp=0
            )
            new_pack.save(args.packfile)
            print(f"Created {args.packfile} (type: {PACK_TYPES[args.type]}, version: {args.version})")
            return 0

        pack = PackFile(args.packfile)

        if args.command == "info":
            print(pack.info())

        elif args.command == "list":
            files = pack.list_files()
            if args.filter:
                files = [f for f in files if args.filter.lower() in f.lower()]
            for f in sorted(files):
                entry = pack.files[f]
                print(f"{entry.size:>10}  {f}")

        elif args.command == "extract":
            if pack.extract_file(args.filepath, args.output):
                print(f"Extracted: {args.filepath} -> {args.output}")
            else:
                print(f"Error: File not found in pack: {args.filepath}")
                return 1

        elif args.command == "extract-all":
            count = pack.extract_all(args.output)
            print(f"Extracted {count} files to {args.output}")

        elif args.command == "replace":
            if not pack.has_file(args.filepath):
                print(f"Error: File not found in pack: {args.filepath}")
                return 1
            pack.set_file_from_disk(args.filepath, args.source)
            output = args.output or args.packfile
            pack.save(output)
            print(f"Replaced {args.filepath} in {output}")

        elif args.command == "add":
            pack.set_file_from_disk(args.filepath, args.source)
            output = args.output or args.packfile
            pack.save(output)
            print(f"Added {args.filepath} to {output}")

        elif args.command == "remove":
            if pack.remove_file(args.filepath):
                output = args.output or args.packfile
                pack.save(output)
                print(f"Removed {args.filepath} from {output}")
            else:
                print(f"Error: File not found in pack: {args.filepath}")
                return 1

        elif args.command == "set-type":
            pack.header.pack_type = args.type
            output = args.output or args.packfile
            pack.save(output)
            print(f"Set {output} type to {PACK_TYPES[args.type]} ({args.type})")

        elif args.command == "dump":
            from pack_dump import PackDumper
            dumper = PackDumper(
                pack_path=args.packfile,
                output_dir=args.output,
                unluac_path=args.unluac,
                db_format=args.db_format,
                decompile_lua=not args.no_lua_decompile
            )
            dumper.dump_all()

    except Exception as e:
        print(f"Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main() or 0)
