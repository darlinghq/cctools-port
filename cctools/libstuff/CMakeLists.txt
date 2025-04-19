include_directories(${CMAKE_CURRENT_SOURCE_DIR}/../include)
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/../include/foreign)

add_definitions(
    -DHAVE_BCMP=1
    -DHAVE_BCOPY=1
    -DHAVE_BSD_STDLIB_H=1
    -DHAVE_BZERO=1
    -DHAVE_CLOCK_GETTIME=1
    -DHAVE_DISPATCH_DISPATCH_H=1
    -DHAVE_DLFCN_H=1
    -DHAVE_EXECINFO_H=1
    -DHAVE_INDEX=1
    -DHAVE_INTTYPES_H=1
    # -DHAVE_REALLOCF=1
    -DHAVE_RINDEX=1
    -DHAVE_STAT_ST_MTIM=1
    -DHAVE_STDINT_H=1
    -DHAVE_STDIO_H=1
    -DHAVE_STDLIB_H=1
    -DHAVE_STRINGS_H=1
    -DHAVE_STRING_H=1
    -DHAVE_SYS_STAT_H=1
    -DHAVE_SYS_TYPES_H=1
    -DHAVE_UNISTD_H=1
    -DHAVE_UTIMENSAT=1

    -DPACKAGE_NAME="cctools-darling"
    -DPACKAGE_VERSION="1021.4"
    -DPROGRAM_PREFIX="${APPLE_TARGET_TRIPLET_PRIMARY}-"

    -DSTDC_HEADERS=1
    -D__STDC_CONSTANT_MACROS=1
    -D__STDC_LIMIT_MACROS=1

    -D__DARWIN_UNIX03
)

# i386 has a different CPU type/subtype, but Darling only supports x86_64
if(TARGET_x86_64 OR TARGET_i386)
	add_compile_definitions(
		EMULATED_HOST_CPU_TYPE=16777223
		EMULATED_HOST_CPU_SUBTYPE=3
	)
elseif(TARGET_ARM64)
	add_compile_definitions(
		EMULATED_HOST_CPU_TYPE=16777228
		EMULATED_HOST_CPU_SUBTYPE=0
	)
endif()


set(libstuff_sources
    allocate.c
    apple_version.c
    arch.c
    arch_usage.c
    best_arch.c
    breakout.c
    bytesex.c
    checkout.c
    crc32.c
    dylib_roots.c
    dylib_table.c
    port.c
    errors.c
    execute.c
    fatal_arch.c
    fatals.c
    diagnostics.c
    get_arch_from_host.c
    get_toc_byte_sex.c
    guess_short_name.c
    hash_string.c
    hppa.c
    llvm.c
    lto.c
    macosx_deployment_target.c
    ofile.c
    ofile_error.c
    ofile_get_word.c
    print.c
    reloc.c
    rnd.c
    seg_addr_table.c
    set_arch_flag_name.c
    swap_headers.c
    symbol_list.c
    SymLoc.c
    unix_standard_mode.c
    version_number.c
    writeout.c
    write64.c
    coff_bytesex.c
    args.c
    align.c
    depinfo.c
    xcode.c
)

add_library(cctools_port_libstuff STATIC
    ${libstuff_sources}
)
