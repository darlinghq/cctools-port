project(otool)
include_directories(BEFORE ${CMAKE_CURRENT_SOURCE_DIR}/../include)
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/../include/foreign)

add_definitions(-U__APPLE__
	-DEMULATED_HOST_CPU_TYPE=16777223
	-DEMULATED_HOST_CPU_SUBTYPE=3
	-D__STDC_LIMIT_MACROS=1
	-D__STDC_CONSTANT_MACROS=1
	-DHAVE_EXECINFO_H=1
	-D__DARWIN_UNIX03
	-U__APPLE__
	-U_POSIX_C_SOURCE
	-DPROGRAM_PREFIX="x86_64-apple-darwin11-"
	-DSTDC_HEADERS=1 -DHAVE_SYS_TYPES_H=1 -DHAVE_SYS_STAT_H=1 -DHAVE_STDLIB_H=1 -DHAVE_STRING_H=1 -DHAVE_MEMORY_H=1 -DHAVE_STRINGS_H=1 -DHAVE_INTTYPES_H=1 -DHAVE_STDINT_H=1 -DHAVE_UNISTD_H=1 -DHAVE_DLFCN_H=1
	-Du_short=uint16_t -Du_int=uint32_t
	-DPACKAGE_NAME="otool"
	-DPACKAGE_VERSION="1.0"
	-D_DARWIN_C_SOURCE
	)

set(otool_sources
	main.c
	ofile_print.c
	m68k_disasm.c
	i860_disasm.c
	m88k_disasm.c
	i386_disasm.c
	ppc_disasm.c
	hppa_disasm.c
	sparc_disasm.c
	arm_disasm.c
	print_objc.c
	print_objc2_32bit.c
	print_objc2_64bit.c
	print_bitcode.c
	coff_print.c
	arm64_disasm.c
	dyld_bind_info.c
	../libstuff/allocate.c
	../libstuff/arch.c
	../libstuff/bytesex.c
	../libstuff/errors.c
	../libstuff/execute.c
	../libstuff/guess_short_name.c
	../libstuff/hppa.c
	../libstuff/llvm.c
	../libstuff/ofile.c
	../libstuff/reloc.c
	../libstuff/apple_version.c
	../libstuff/llvm.c
	../libstuff/arch.c
	../libstuff/port.c
	../libstuff/ofile_error.c
	../libstuff/fatals.c
	../libstuff/print.c
	../libstuff/get_arch_from_host.c
	../libstuff/set_arch_flag_name.c
	../libstuff/get_toc_byte_sex.c
	../libstuff/rnd.c
	../libstuff/swap_headers.c
	../libstuff/arch_usage.c
	../libstuff/coff_bytesex.c
)

add_darling_executable(otool ${otool_sources})
target_link_libraries(otool stdcxx objc)

install(TARGETS otool DESTINATION libexec/darling/bin)

install(FILES ../man/otool.1 DESTINATION libexec/darling/usr/share/man/man1)
