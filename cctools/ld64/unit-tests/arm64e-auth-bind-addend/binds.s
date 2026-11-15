// Pointers into other images: authenticated binds (data key A, as in a vtable or typeinfo pointer) with and
// without an addend, and plain binds for comparison.
	.section	__DATA,__data
	.p2align	3
	.globl	_auth_plain
_auth_plain:
	.quad	_ext1@AUTH(da,0x1234)
	.globl	_auth_plus16
_auth_plus16:
	.quad	(_ext1+16)@AUTH(da,0x1234)
	.globl	_auth_plus16_other
_auth_plus16_other:
	.quad	(_ext2+16)@AUTH(da,0x4321,addr)
	.globl	_auth_plus_big
_auth_plus_big:
	.quad	(_ext3+0x123456)@AUTH(da,0x1234)
	.globl	_auth_minus
_auth_minus:
	.quad	(_ext3-8)@AUTH(da,0x1234)
	.globl	_plain_plus16
_plain_plus16:
	.quad	_ext1+16
	.globl	_plain_none
_plain_none:
	.quad	_ext2
