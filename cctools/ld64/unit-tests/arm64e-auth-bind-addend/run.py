#!/usr/bin/env python3
# Copyright (C) 2026 Lubos Dolezel
"""Regression test: an arm64e authenticated bind to a symbol plus an addend keeps the addend.

dyld_chained_ptr_arm64e_auth_bind has no addend field, so ld64 has to put the addend in the import table
(an import format with an addend field). Before the fix `sym + 16` was linked as `sym`.

Usage: LD64=/path/to/aarch64-apple-darwin20-ld python3 -I run.py [clang]
Host only: needs a clang with the arm64e Darwin target whose assembler emits authenticated pointer relocations
(Apple's does; some other builds quietly emit plain pointers, which this test reports); no SDK, no guest. Without LD64 it
prints SKIP and exits 0. Exit 1 on any mismatch.

Steps: assemble binds.s and a stub dylib that defines the imported symbols, link a dylib against the stub with
ld64, and decode the chained fixups of the result (starts, import table, each bind's ordinal, addend and
authentication) back.
"""
import os
import shutil
import struct
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TARGET = "arm64e-apple-macos13"
KEY_DA = 2

# symbol, addend, discriminator, address diversified
EXPECTED = {
    "_auth_plain": ("auth", 0, 0x1234, 0),
    "_auth_plus16": ("auth", 16, 0x1234, 0),
    "_auth_plus16_other": ("auth", 16, 0x4321, 1),
    "_auth_plus_big": ("auth", 0x123456, 0x1234, 0),
    "_auth_minus": ("auth", -8, 0x1234, 0),
    "_plain_plus16": ("plain", 16, 0, 0),
    "_plain_none": ("plain", 0, 0, 0),
}
IMPORT_NAMES = {"_auth_plain": "_ext1", "_auth_plus16": "_ext1", "_auth_plus16_other": "_ext2",
                "_auth_plus_big": "_ext3", "_auth_minus": "_ext3", "_plain_plus16": "_ext1", "_plain_none": "_ext2"}


def run(cmd):
    r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    if r.returncode != 0:
        sys.exit("FAIL: %s\n%s" % (" ".join(cmd), r.stdout))
    return r.stdout


def assemble(clang, src, out):
    raw = out + ".raw"
    run([clang, "--target=" + TARGET, "-c", "-x", "assembler", src, "-o", raw])
    data = bytearray(open(raw, "rb").read())
    magic, cputype, subtype = struct.unpack_from("<III", data, 0)
    # Newer clang puts a capability byte in the cpusubtype (0x80000002); older clang writes a plain 2. The in-tree
    # ld64 predates the capability byte and would treat such an object as plain arm64.
    if (magic, cputype) != (0xFEEDFACF, 0x0100000C) or subtype not in (0x2, 0x80000002):
        sys.exit("FAIL: unexpected object header %#x %#x %#x" % (magic, cputype, subtype))
    struct.pack_into("<I", data, 8, 0x2)
    open(out, "wb").write(data)


def link(ld64, out, objs, libs=()):
    run([ld64, "-arch", "arm64e", "-fixup_chains", "-platform_version", "macos", "13.0", "13.0", "-dylib",
         "-install_name", "/usr/lib/" + os.path.basename(out), "-o", out] + list(objs) + list(libs))


class Image:
    """The symbols, sections and chained fixups of a 64-bit arm64e dylib."""

    def __init__(self, path):
        d = self.d = open(path, "rb").read()
        ncmds = struct.unpack_from("<I", d, 16)[0]
        self.segs, self.symtab, cf = [], None, None
        off = 32
        for _ in range(ncmds):
            cmd, size = struct.unpack_from("<II", d, off)
            if cmd == 0x19:
                name, vmaddr, vmsize, fileoff, filesize = struct.unpack_from("<16sQQQQ", d, off + 8)
                self.segs.append((name.rstrip(b"\0"), vmaddr, vmsize, fileoff, filesize))
            elif cmd == 0x2:
                self.symtab = struct.unpack_from("<IIII", d, off + 8)
            elif cmd == 0x80000034:
                cf = struct.unpack_from("<II", d, off + 8)
            off += size
        self.base = self.segs[0][1]
        self.imports = self._imports(cf[0])
        self.fix = {}
        self._chains(cf[0])

    def foff(self, vm):
        for _n, va, vs, fo, _fs in self.segs:
            if va <= vm < va + vs:
                return fo + vm - va
        sys.exit("FAIL: address %#x not in any segment" % vm)

    def u64(self, vm):
        return struct.unpack_from("<Q", self.d, self.foff(vm))[0]

    def symbols(self):
        symoff, nsyms, stroff, _strsize = self.symtab
        out = {}
        for i in range(nsyms):
            strx, _type, _sect, _desc, value = struct.unpack_from("<IBBHQ", self.d, symoff + 16 * i)
            end = self.d.index(b"\0", stroff + strx)
            out[self.d[stroff + strx:end].decode()] = value
        return out

    def _imports(self, cfoff):
        d = self.d
        _ver, _starts, imports_off, symbols_off, count, fmt, _sym_fmt = struct.unpack_from("<IIIIIII", d, cfoff)
        out = []
        for i in range(count):
            if fmt == 1:
                v = struct.unpack_from("<I", d, cfoff + imports_off + 4 * i)[0]
                addend = 0
            elif fmt == 2:
                v, addend = struct.unpack_from("<Ii", d, cfoff + imports_off + 8 * i)
            elif fmt == 3:
                v, addend = struct.unpack_from("<Qq", d, cfoff + imports_off + 16 * i)
                s = cfoff + symbols_off + (v >> 32)
                out.append((d[s:d.index(b"\0", s)].decode(), addend))
                continue
            else:
                sys.exit("FAIL: import format %d" % fmt)
            name_offset = v >> 9
            s = cfoff + symbols_off + name_offset
            out.append((d[s:d.index(b"\0", s)].decode(), addend))
        self.import_format = fmt
        return out

    def _chains(self, cfoff):
        d = self.d
        starts = cfoff + struct.unpack_from("<I", d, cfoff + 4)[0]
        segcount = struct.unpack_from("<I", d, starts)[0]
        for i in range(segcount):
            so = struct.unpack_from("<I", d, starts + 4 + 4 * i)[0]
            if so == 0:
                continue
            s = starts + so
            _size, page_size, fmt, seg_off, _mvp, page_count = struct.unpack_from("<IHHQIH", d, s)
            if fmt != 1:
                sys.exit("FAIL: pointer format %d, expected DYLD_CHAINED_PTR_ARM64E" % fmt)
            for p in range(page_count):
                ps = struct.unpack_from("<H", d, s + 22 + 2 * p)[0]
                if ps == 0xFFFF:
                    continue
                vm = self.base + seg_off + p * page_size + ps
                while True:
                    v = self.u64(vm)
                    auth, bind, nxt = v >> 63, (v >> 62) & 1, (v >> 51) & 0x7FF
                    if bind and auth:
                        name, addend = self.imports[v & 0xFFFF]
                        self.fix[vm] = ("auth", name, addend, (v >> 32) & 0xFFFF, (v >> 48) & 1, (v >> 49) & 3)
                    elif bind:
                        name, addend = self.imports[v & 0xFFFFFF]
                        inline = (v >> 32) & 0x7FFFF
                        if inline & 0x40000:
                            inline -= 0x80000
                        self.fix[vm] = ("plain", name, addend + inline, 0, 0, 0)
                    else:
                        self.fix[vm] = ("rebase", None, 0, 0, 0, 0)
                    if nxt == 0:
                        break
                    vm += nxt * 8


def main():
    ld64 = os.environ.get("LD64")
    if not ld64:
        print("SKIP: LD64 not set")
        return
    clang = sys.argv[1] if len(sys.argv) > 1 else shutil.which("clang")
    if not clang:
        sys.exit("FAIL: no clang")
    with tempfile.TemporaryDirectory() as tmp:
        j = lambda n: os.path.join(tmp, n)
        stub_src = j("stub.s")
        open(stub_src, "w").write(
            "\t.section __DATA,__data\n" + "".join("\t.globl %s\n%s:\n\t.space 64\n" % (n, n) for n in ("_ext1", "_ext2", "_ext3")))
        assemble(clang, stub_src, j("stub.o"))
        link(ld64, j("libstub.dylib"), [j("stub.o")])
        assemble(clang, os.path.join(HERE, "binds.s"), j("binds.o"))
        link(ld64, j("t.dylib"), [j("binds.o")], [j("libstub.dylib")])
        img = Image(j("t.dylib"))
        syms = img.symbols()
        failed = False
        for sym, (kind, addend, disc, addr) in sorted(EXPECTED.items()):
            f = img.fix.get(syms[sym])
            want = (kind, IMPORT_NAMES[sym], addend)
            got = f[:3] if f else None
            ok = got == want and (kind != "auth" or (f[3], f[4], f[5]) == (disc, addr, KEY_DA))
            print("%-20s %s%s" % (sym, got, "" if ok else "   MISMATCH, expected %s disc %#x addr %d" % (want, disc, addr)))
            failed |= not ok
        if failed:
            sys.exit(1)
        print("PASS")


main()
