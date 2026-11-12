#!/usr/bin/env python3
"""Regression test: ld64 must sign the method lists that objc category merging creates (arm64e).

The arm64e objc runtime authenticates category_t.instanceMethods/classMethods and
class_ro_t.baseMethods (key DA, discriminator 0xC310, address diversified). Merging
that creates such a list where there was none must emit the same authenticated
fixup, otherwise the runtime traps (brk #0xc472) on the plain pointer.

Usage: LD64=/path/to/aarch64-apple-darwin20-ld python3 -I run.py [clang]
Host only: needs clang with the arm64e Darwin target; no SDK, no guest. Without
LD64 it prints SKIP and exits 0. Exit 1 on any mismatch.

Steps: compile objc-merge.m with clang, clear the cpusubtype caps byte (the in-tree
ld64 predates it and would treat the object as plain arm64), link a dylib against
two tiny stub dylibs with ld64 (merging on, then -no_objc_category_merging as a
control), and read the chained fixups of the result back.
"""
import os
import shutil
import struct
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TARGET = "arm64e-apple-macos13"
KEY_DA, DISC, ADDR = 2, 0xC310, 1
MERGED_SLOTS = {"class_ro_t.baseMethods": 2, "class_ro_t.baseProtocols": 2, "class_ro_t.baseProperties": 2,
                "category_t.instanceMethods": 2, "category_t.classMethods": 2, "category_t.protocols": 2,
                "category_t.instanceProperties": 2, "category_t._classProperties": 1}


def run(cmd):
    r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    if r.returncode != 0:
        sys.exit("FAIL: %s\n%s" % (" ".join(cmd), r.stdout))


def compile_obj(clang, src, out):
    raw = out + ".raw"
    run([clang, "--target=" + TARGET, "-c", src, "-o", raw])
    data = bytearray(open(raw, "rb").read())
    magic, cputype, subtype = struct.unpack_from("<III", data, 0)
    if (magic, cputype, subtype) != (0xFEEDFACF, 0x0100000C, 0x80000002):
        sys.exit("FAIL: unexpected object header %#x %#x %#x" % (magic, cputype, subtype))
    struct.pack_into("<I", data, 8, 0x2)
    open(out, "wb").write(data)


def link(ld64, out, objs, libs=(), extra=(), install=None):
    cmd = [ld64, "-arch", "arm64e", "-fixup_chains", "-platform_version", "macos", "13.0", "13.0",
           "-dylib", "-install_name", install or ("/usr/lib/" + os.path.basename(out)), "-o", out]
    run(cmd + list(extra) + list(objs) + list(libs))


class Image:
    def __init__(self, path):
        d = self.d = open(path, "rb").read()
        ncmds = struct.unpack_from("<I", d, 16)[0]
        self.segs, self.sects, cf = [], {}, None
        off = 32
        for _ in range(ncmds):
            cmd, size = struct.unpack_from("<II", d, off)
            if cmd == 0x19:
                name, vmaddr, vmsize, fileoff, filesize, _p, _p2, nsects, _f = struct.unpack_from("<16sQQQQiiII", d, off + 8)
                self.segs.append((name.rstrip(b"\0"), vmaddr, vmsize, fileoff, filesize))
                for i in range(nsects):
                    s = off + 72 + i * 80
                    sname, _seg, addr, ssize = struct.unpack_from("<16s16sQQ", d, s)
                    self.sects[sname.rstrip(b"\0").decode()] = (addr, ssize)
            elif cmd == 0x80000034:
                cf = struct.unpack_from("<II", d, off + 8)
            off += size
        self.base = self.segs[0][1]
        self.fix = {}
        self._chains(cf[0])

    def foff(self, vm):
        for _n, va, vs, fo, fs in self.segs:
            if va <= vm < va + vs:
                return fo + vm - va
        sys.exit("FAIL: address %#x not in any segment" % vm)

    def u64(self, vm):
        return struct.unpack_from("<Q", self.d, self.foff(vm))[0]

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
                    if auth and not bind:
                        self.fix[vm] = ("auth", (v >> 49) & 3, (v >> 32) & 0xFFFF, (v >> 48) & 1, self.base + (v & 0xFFFFFFFF))
                    elif auth:
                        self.fix[vm] = ("auth", (v >> 49) & 3, (v >> 32) & 0xFFFF, (v >> 48) & 1, None)
                    elif bind:
                        self.fix[vm] = ("bind", 0, 0, 0, None)
                    else:
                        self.fix[vm] = ("plain", 0, 0, 0, v & 0x7FFFFFFFFFF)
                    if nxt == 0:
                        break
                    vm += nxt * 8

    def target(self, vm):
        f = self.fix.get(vm)
        return f[4] if f else None

    def slots(self):
        """Yield (what, slot address, expected) for every list pointer slot in class_ro_t and category_t."""
        cls = self.sects["__objc_classlist"]
        for i in range(cls[1] // 8):
            c = self.target(cls[0] + 8 * i)
            for k in (c, self.target(c)):  # class, then metaclass via isa
                ro = self.target(k + 32)  # class_t.bits
                yield "class_ro_t.baseMethods", ro + 32, "auth"
                yield "class_ro_t.baseProtocols", ro + 40, "plain"
                yield "class_ro_t.baseProperties", ro + 64, "plain"
        cat = self.sects.get("__objc_catlist", (0, 0))
        for i in range(cat[1] // 8):
            c = self.target(cat[0] + 8 * i)
            yield "category_t.instanceMethods", c + 16, "auth"
            yield "category_t.classMethods", c + 24, "auth"
            yield "category_t.protocols", c + 32, "plain"
            yield "category_t.instanceProperties", c + 40, "plain"
            yield "category_t._classProperties", c + 48, "plain"


def check(path, label):
    img = Image(path)
    n = {}
    bad = []
    for what, slot, want in img.slots():
        f = img.fix.get(slot)
        if f is None:
            if img.u64(slot) != 0:
                bad.append((what, slot, "raw value, no fixup"))
            continue
        n[what] = n.get(what, 0) + 1
        got = f[:4]
        if got != (("auth", KEY_DA, DISC, ADDR) if want == "auth" else ("plain", 0, 0, 0)):
            bad.append((what, slot, "%s key=%d disc=%#x addr=%d, expected %s" % (got + (want,))))
    for what, slot, why in bad:
        print("  MISMATCH %s at %#x: %s" % (what, slot, why))
    print("%s: %s, %d mismatches" % (label, ", ".join("%d %s" % (v, k) for k, v in sorted(n.items())), len(bad)))
    return n, bad


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
        stubs = {}
        for name, sym in (("libobjc.A.dylib", "__objc_empty_cache"), ("libext.dylib", None)):
            src = j(name + ".c")
            if sym:
                body = 'char stub __asm__("%s") = 1;\n' % sym
            else:
                body = 'char a __asm__("_OBJC_CLASS_$_ExtA") = 1;\nchar b __asm__("_OBJC_CLASS_$_ExtB") = 1;\n'
            open(src, "w").write(body)
            compile_obj(clang, src, j(name + ".o"))
            link(ld64, j(name), [j(name + ".o")])
            stubs[name] = j(name)
        compile_obj(clang, os.path.join(HERE, "objc-merge.m"), j("objc-merge.o"))
        libs = list(stubs.values())
        failed = False
        for label, extra in (("merged", []), ("control, -no_objc_category_merging", ["-no_objc_category_merging"])):
            out = j("t.dylib")
            link(ld64, out, [j("objc-merge.o")], libs, extra)
            n, bad = check(out, label)
            failed |= bool(bad)
            if not extra and n != MERGED_SLOTS:
                print("  FAIL: expected %s after merging, the test inputs no longer exercise the merge paths" % MERGED_SLOTS)
                failed = True
        if failed:
            sys.exit(1)
        print("PASS")


main()
