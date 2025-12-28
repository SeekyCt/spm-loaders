/* Control section layout */
SECTIONS {
	. = 0x80004200;

	.first : { *(.first) }

	.text : { *(.text .text.*) }
    .ctors : { KEEP( *(.ctors*) ) }
	.rodata : { *(.rodata .rodata.*) }
 	.data : { *(.data .data.*) }
	.bss : { *(.bss .bss.*) }

    ctors_start = ADDR(.ctors);
    ctors_end = ctors_start + SIZEOF(.ctors);
}
