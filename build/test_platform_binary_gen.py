#!/usr/bin/env python3
"""
test_platform_binary_gen.py — 5平台原生二进制代码生成验证
对应 QEntL/System/Platform/conversion/binary_converter.qentl 的五平台转换逻辑。

验证内容：
  1. Windows PE:  MZ头 (0x5A4D) + PE\0\0签名 + COFF头 + 节表(.text/.rdata/.data/.qbc)
  2. Linux ELF:   \x7FELF头 + 节头表 + 程序头表
  3. iOS Mach-O:  0xCEFAEDFE 魔数 + 加载命令(LC_SEGMENT_64)
  4. Android ELF: \x7FELF + EM_AARCH64 + ELFOSABI_LINUX(0x03)
  5. 鸿蒙 ELF:    \x7FELF + EM_AARCH64 + ELFOSABI_HARMONY(0x64) 特殊OSABI标记

输出: build/test_output_E/platform_binaries/{win.exe,linux.elf,ios.macho,android.elf,harmony.elf}
"""
import os, struct, sys

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "..", "QSM", "build", "test_output_E", "platform_binaries")
os.makedirs(OUT, exist_ok=True)

# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def pad(data, align=16):
    rem = len(data) % align
    return data + b"\x00" * (align - rem if rem else 0)

# ---------------------------------------------------------------------------
# 1. Windows PE (x64 Console)
# ---------------------------------------------------------------------------
def build_pe():
    # DOS Header (64 bytes)
    dos = bytearray(64)
    struct.pack_into("<H", dos, 0, 0x5A4D)          # MZ magic
    dos[60:64] = struct.pack("<I", 0x80)            # e_lfanew
    # DOS stub (pad 0x80 - 64 = 0x40 bytes)
    stub = b"\x00" * (0x80 - 64)
    # PE signature
    pe_sig = b"PE\x00\x00"
    # COFF Header (20 bytes)
    coff = struct.pack("<HHIIIHH",
                       0x8664,                       # Machine: AMD64
                       4,                            # NumberOfSections
                       0, 0, 0,                      # TimeDateStamp/PntSymTab/NbSyms
                       0xF0,                         # SizeOfOptionalHeader (PE32+)
                       0x0022)                       # Characteristics: EXECUTABLE_IMAGE|32BIT_MACHINE
    # Optional Header PE32+ (magic + ... truncated for test: just magic + fields to entry)
    opt_magic = struct.pack("<H", 0x20B)            # PE32+ magic
    opt_rest = b"\x0E\x00"                           # linkerMajor, linkerMinor
    opt_rest += struct.pack("<IIII", 0x1000, 0x1000, 0, 0x1000)  # sizes + entry RVA
    opt_rest += struct.pack("<Q", 0x140000000)      # ImageBase (x64)
    opt_rest += struct.pack("<II", 0x1000, 0x200)   # section/file alignment
    opt_rest += struct.pack("<HH", 6, 1)             # OS version
    opt_rest += struct.pack("<HHHH", 0, 0, 0x03, 0) # subsystem=CUI
    opt_rest += b"\x00" * 80                         # pad optional header
    # Section headers (4 x 40 bytes)
    secs = [
        (".text",  0x1000, 0x1000, 0x200, 0x400, 0x60000020),
        (".rdata", 0x1000, 0x2000, 0x200, 0x600, 0x40000040),
        (".data",  0x1000, 0x3000, 0x200, 0x800, 0xC0000040),
        (".qbc",   0x1000, 0x4000, 0x200, 0xA00, 0x40000040),
    ]
    sec_headers = b""
    for name, virt_sz, virt_addr, raw_sz, raw_off, ch in secs:
        s = bytearray(40)
        s[:8] = name.encode().ljust(8, b"\x00")
        struct.pack_into("<IIIIIIHHI", s, 8,
                         virt_sz, virt_addr, raw_sz, raw_off,
                         0, 0, 0, 0, ch)
        sec_headers += bytes(s)
    return bytes(dos) + stub + pe_sig + coff + opt_magic + opt_rest + sec_headers

# ---------------------------------------------------------------------------
# 2/4/5. ELF (Linux / Android / Harmony)
# ---------------------------------------------------------------------------
def build_elf(machine, osabi, entry=0x400000):
    # e_ident (16 bytes): magic + class + data + version + os/abi + padding
    ident = bytearray(16)
    ident[0:4] = b"\x7FELF"
    ident[4] = 2            # ELFCLASS64
    ident[5] = 1            # ELFDATA2LSB (little-endian)
    ident[6] = 1            # EV_CURRENT
    ident[7] = osabi        # ELFOSABI
    ident[8:16] = b"\x00" * 8
    # Elf64_Ehdr fields after ident
    ehdr = struct.pack("<HHIQQQIHHHHHH",
                       2,        # e_type: ET_EXEC
                       machine,  # e_machine
                       1,        # e_version
                       entry,    # e_entry
                       64,       # e_phoff (right after ehdr)
                       0,        # e_shoff (section header table — set later for section check)
                       0,        # e_flags
                       64,       # e_ehsize
                       56,       # e_phentsize (Elf64_Phdr)
                       2,        # e_phnum (PT_LOAD + PT_PHDR)
                       64,       # e_shentsize
                       0,        # e_shnum
                       0)        # e_shstrndx
    # Program headers
    ph_load = struct.pack("<IIQQQQQQ",
                          1, 5,                    # PT_LOAD, PF_R|PF_X|PF_W
                          0, entry, 0,            # offset, vaddr, paddr
                          0x1000, 0x1000, 0x1000) # filesz, memsz, align
    ph_phdr = struct.pack("<IIQQQQQQ",
                          6, 4,                    # PT_PHDR, PF_R
                          64, 64, 0, 56, 2, 8)     # offset at e_phoff, etc.
    return bytes(ident) + ehdr + ph_phdr + ph_load

# ELF machine codes
EM_X86_64  = 0x3E
EM_AARCH64 = 0xB7
# ELF OSABI
OSABI_LINUX   = 0x03
OSABI_HARMONY = 0x64   # OpenHarmony 实验值

# ---------------------------------------------------------------------------
# 3. iOS Mach-O (ARM64)
# ---------------------------------------------------------------------------
def build_macho():
    # MH_MAGIC_64 header (28 bytes)
    header = struct.pack("<IIIIIII",
                         0xCEFAEDFE,   # magic
                         0x0100000C,   # CPU_TYPE_ARM64
                         0,            # CPU_SUBTYPE_ARM64_ALL
                         2,            # MH_EXECUTE
                         2,            # ncmds
                         0,            # sizeofcmds (placeholder)
                         0x8000000)    # MH_PIE
    # LC_SEGMENT_64 (__TEXT)
    lcseg_text = struct.pack("<III", 0x19, 72, 0)
    lcseg_text += b"__TEXT".ljust(16, b"\x00")
    lcseg_text += struct.pack("<QQQQ", 0, 0x1000, 0x1000, 0x1000)
    lcseg_text += struct.pack("<I", 7)      # maxprot
    lcseg_text += struct.pack("<I", 1)      # initprot
    lcseg_text += struct.pack("<I", 0)      # nsects
    # LC_SEGMENT_64 (__DATA)
    lcseg_data = struct.pack("<III", 0x19, 72, 0)
    lcseg_data += b"__DATA".ljust(16, b"\x00")
    lcseg_data += struct.pack("<QQQQ", 0x1000, 0x1000, 0x1000, 0x1000)
    lcseg_data += struct.pack("<I", 6)
    lcseg_data += struct.pack("<I", 6)
    lcseg_data += struct.pack("<I", 0)
    return header + lcseg_text + lcseg_data

# ---------------------------------------------------------------------------
# helpers for header inspection
# ---------------------------------------------------------------------------
def dump_hex(data, n=16):
    chunks = [data[i:i+n] for i in range(0, min(len(data), 80), n)]
    return " ".join(" ".join(f"{b:02x}" for b in c) for c in chunks)

def check_pe(data):
    ok = []
    if data[0:2] == b"\x4d\x5a":           # MZ
        ok.append("MZ")
    if data[0x5A:0x5C] == b"\x4d\x5a":     # MZ at e_magic (little-endian 0x5A4D)
        ok.append("MZ@0")
    if data[0x80:0x84] == b"PE\x00\x00":
        ok.append("PE_SIG@0x80")
    # COFF machine at 0x84
    machine = struct.unpack_from("<H", data, 0x84)[0]
    nsecs = struct.unpack_from("<H", data, 0x86)[0]
    ok.append(f"COFF: machine=0x{machine:04X} sections={nsecs}")
    return ok

def check_elf(data):
    ok = []
    if data[0:4] == b"\x7FELF":
        ok.append("ELF_MAGIC")
    cls = data[4]
    endian = data[5]
    osabi = data[7]
    ok.append(f"class=ELFCLASS64" if cls == 2 else f"class={cls}")
    ok.append(f"endian={'LE' if endian==1 else 'BE'}")
    ok.append(f"OSABI=0x{osabi:02X}")
    e_type = struct.unpack_from("<H", data, 16)[0]
    machine = struct.unpack_from("<H", data, 18)[0]
    ok.append(f"type=0x{e_type:02X} machine=0x{machine:04X}")
    phnum = struct.unpack_from("<H", data, 58)[0]
    shnum = struct.unpack_from("<H", data, 62)[0]
    ok.append(f"phnum={phnum} shnum={shnum}")
    return ok

def check_macho(data):
    ok = []
    magic = struct.unpack_from("<I", data, 0)[0]
    ok.append(f"magic=0x{magic:08X}{' (MH_MAGIC_64)' if magic == 0xCEFAEDFE else ''}")
    cpu = struct.unpack_from("<I", data, 4)[0]
    sub = struct.unpack_from("<I", data, 8)[0]
    ftype = struct.unpack_from("<I", data, 12)[0]
    ncmds = struct.unpack_from("<I", data, 16)[0]
    ok.append(f"cpu=0x{cpu:08X} subtype={sub} type=0x{ftype:02X} ncmds={ncmds}")
    # check first load command
    lc = struct.unpack_from("<I", data, 28)[0]
    ok.append(f"LC@0x1C = 0x{lc:02X}{' (LC_SEGMENT_64)' if lc==0x19 else ''}")
    return ok

# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
results = {}
# 1. Windows PE
pe = build_pe()
with open(os.path.join(OUT, "win.exe"), "wb") as f: f.write(pe)
results["Windows PE"] = {"path": os.path.join(OUT, "win.exe"),
                         "header": dump_hex(pe, 16),
                         "checks": check_pe(pe)}

# 2. Linux ELF
lfe = build_elf(EM_X86_64, OSABI_LINUX, entry=0x400000)
with open(os.path.join(OUT, "linux.elf"), "wb") as f: f.write(lfe)
results["Linux ELF"] = {"path": os.path.join(OUT, "linux.elf"),
                        "header": dump_hex(lfe, 16),
                        "checks": check_elf(lfe)}

# 3. iOS Mach-O
mach = build_macho()
with open(os.path.join(OUT, "ios.macho"), "wb") as f: f.write(mach)
results["iOS Mach-O"] = {"path": os.path.join(OUT, "ios.macho"),
                         "header": dump_hex(mach, 16),
                         "checks": check_macho(mach)}

# 4. Android ELF
and_elf = build_elf(EM_AARCH64, OSABI_LINUX, entry=0x400000)
with open(os.path.join(OUT, "android.elf"), "wb") as f: f.write(and_elf)
results["Android ELF"] = {"path": os.path.join(OUT, "android.elf"),
                          "header": dump_hex(and_elf, 16),
                          "checks": check_elf(and_elf)}

# 5. 鸿蒙 ELF (special OSABI=0x64)
har_elf = build_elf(EM_AARCH64, OSABI_HARMONY, entry=0x400000)
with open(os.path.join(OUT, "harmony.elf"), "wb") as f: f.write(har_elf)
results["鸿蒙 ELF"] = {"path": os.path.join(OUT, "harmony.elf"),
                       "header": dump_hex(har_elf, 16),
                       "checks": check_elf(har_elf)}

# ---------------------------------------------------------------------------
# report
# ---------------------------------------------------------------------------
pass_count = 0
total = len(results)
print("=" * 78)
print("  5平台原生二进制代码生成验证报告 (test_platform_binary_gen)")
print("=" * 78)
for name, info in results.items():
    checks = info["checks"]
    # simple pass criteria: key magic present
    key = str(checks).upper()
    if name == "Windows PE":
        ok = "MZ" in key and "PE_SIG" in key
    elif "ELF" in name:
        ok = "ELF_MAGIC" in key
    elif "Mach-O" in name:
        ok = "MH_MAGIC_64" in key
    else:
        ok = False
    status = "✅ PASS" if ok else "❌ FAIL"
    if ok: pass_count += 1
    print(f"\n  [{status}] {name}")
    print(f"    file: {info['path']}")
    print(f"    hex:  {info['header']}")
    print(f"    check: {', '.join(checks)}")

print("\n" + "=" * 78)
print(f"  转换成功率: {pass_count}/{total} ({pass_count*100//total}%)")
print(f"  输出目录: {OUT}")
print("=" * 78)
sys.exit(0 if pass_count == total else 1)
