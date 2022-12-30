/* Control section layout */
SECTIONS {
	. = 0x80004200;

	.first : { *(.first) }

	.text : { *(.text .text.*) }
	.rodata : { *(.rodata .rodata.*) }
 	.data : { *(.data .data.*) }
	.bss : { *(.bss .bss.*) }
}
