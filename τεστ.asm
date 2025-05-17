
L0:
j Lmain
Lmain:

L1:
addi sp, sp, 32
move gp, sp

L2:
li t1, 0
sw t1, -12(sp)

L3:
li t1, 1
sw t1, -16(sp)

L4:
li t1, 0
sw t1, -20(sp)

L5:
lw t1, -12(sp)
mv a0, t1
li a7, 1
ecall

L6:
lw t1, -12(sp)
lw t2, -16(sp)
add t1, t1, t2
sw t1, -32(sp)

L7:
lw t1, -32(sp)
sw t1, -24(sp)

L8:
lw t1, -16(sp)
sw t1, -12(sp)

L9:
lw t1, -24(sp)
sw t1, -16(sp)

L10:
lw t1, -20(sp)
li t2, 1
add t1, t1, t2
sw t1, -36(sp)

L11:
lw t1, -36(sp)
sw t1, -20(sp)

L12:
li t1, 1
sw t1, -28(sp)

L13:
li t1, 1
sw t1, -20(sp)

L14:
lw t1, -28(sp)
mv a0, t1
li a7, 1
ecall

L15:
lw t1, -40(sp)
sw t1, -28(sp)

L16:
lw t1, -20(sp)
li t2, 1
add t1, t1, t2
sw t1, -44(sp)

L17:
lw t1, -44(sp)
sw t1, -20(sp)

L18:
li a0, 0
li a7, 93
ecall
