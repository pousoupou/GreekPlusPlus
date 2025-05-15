L0: j Lmain
L1: sw ra, -0(sp)
L2:
lw t1, -12(sp)
li t2, 1
add t1, t1, t2
sw t1, -20(sp)
L3:
lw t1, -20(sp)
sw t1, -24(gp)
L4:
li t1, 4
sw t1, -20(gp)
L5:
lw ra, -0(sp)
jr ra
Lmain:
L6:
addi sp, sp, 24
move gp, sp
L7:
li t1, 1
sw t1, -12(sp)
L8:
addi fp, sp, 20
lw t0, -12(sp)
sw t0, -12(fp)
L9:
addi t0, sp, -16
sw t0, -16(fp)
L10:
sw sp, -4(fp)
addi sp, sp, 28
jal L1
addi sp, sp, -28
