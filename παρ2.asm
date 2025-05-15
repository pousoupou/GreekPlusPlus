
L0:
j Lmain

L1:
sw ra, -0(sp)

L2:
lw t1, -16(gp)
sw t1, -20(gp)

L3:
lw t0, -4(sp)
addi t0, t0, -12
lw t1, (t0)
lw t0, -4(sp)
addi t0, t0, -16
lw t0, (t0)
sw t1, (t0)

L4:
lw ra, -0(sp)
jr ra

L5:
sw ra, -0(sp)

L6:
li t1, 2
sw t1, -16(gp)

L7:
sw sp, -4(fp)
addi sp, sp, 20
jal L1
addi sp, sp, -20

L8:
lw ra, -0(sp)
jr ra
Lmain:

L9:
addi sp, sp, 28
move gp, sp

L10:
li t1, 3
sw t1, -12(sp)

L11:
li t1, 4
sw t1, -16(sp)

L12:
addi fp, sp, 24
lw t0, -12(sp)
sw t0, -12(fp)

L13:
addi t0, sp, -16
sw t0, -16(fp)

L14:
sw sp, -4(fp)
addi sp, sp, 24
jal L1
addi sp, sp, -24

L15:
lw t1, -16(sp)

L16:
lw t1, -20(sp)
