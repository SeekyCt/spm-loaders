/* Control section layout */
SECTIONS {
	. = mario_pouch_work + 0x368;

	.first : { *(.first) }

	.text : { *(.text .text.*) }
	.rodata : { *(.rodata .rodata.*) }
 	.data : { *(.data .data.*) }
	.bss : { *(.bss .bss.*) }
}
