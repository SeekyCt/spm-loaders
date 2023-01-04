/*
    Place a branch to the main function at the start of the binary
*/

.section .first, "ax"

/*
    Entrypoint
*/

.global entry
.type entry, @function
entry:
    b loaderMain
.size entry, . - entry
