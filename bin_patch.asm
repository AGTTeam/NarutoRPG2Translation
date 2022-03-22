.nds

.open "NarutoRPG2Data/repack/arm9.bin",0x02000000
  .org 0x0208a2e0
  .area 0x350
  .align

  ;ASCII to SJIS lookup table, also includes VWF values
  SJIS_LOOKUP:
  .import "NarutoRPG2Data/fontdata.bin"
  .dw 0
  .align

  IS_ASCII:
  .dw 0
  .dw 0

  ;r0 = str ptr
  ;r3 = first byte
  ;r2 = second byte
  CONVERT_ASCII:
  mov r1,0x0
  push {r0-r1,r4}
  ;Set IS_ASCII to 0 and check
  ldr r0,=IS_ASCII
  cmp r3,0x7f
  strge r1,[r0]
  bge @@return
  ;Return the SJIS character
  ldr r2,=SJIS_LOOKUP
  sub r3,r3,0x20
  lsl r3,r3,0x2
  add r2,r2,r3
  ldrb r3,[r2]
  ldrb r2,[r2,0x1]
  ;Set IS_ASCII to 1
  mov r1,0x1
  str r1,[r0]
  @@return:
  ;Save the character
  mov r4,r2,lsl 8
  orr r4,r4,r3
  str r4,[r0,0x4]
  pop {r0-r1,r4}
  b CONVERT_ASCII_RET
  .pool

  CHECK_ASCII:
  push {r1}
  ldr r1,=IS_ASCII
  ldr r1,[r1]
  cmp r1,0x0
  addeq r0,r0,0x2
  addne r0,r0,0x1
  pop {r1}
  b CHECK_ASCII_RET
  .pool

  VWF_DATA:
  ;Character start (0-6)
  .db 0
  ;Character length (2,4,6,8)
  .db 0
  ;Current character x (0,2,4,6)
  .db 0
  ;Need to increase stuff after drawing glyph
  .db 0

  .macro VWF_STR_BEGIN_MACRO
    push {r0-r1}
    ldr r0,=VWF_DATA
    mov r1,0x0
    ldrb r1,[r0]
    pop {r0-r1}
  .endmacro

  VWF_STR_BEGIN1:
  mov r4,0x4000
  VWF_STR_BEGIN_MACRO
  b VWF_STR_BEGIN1_RET

  VWF_STR_BEGIN2:
  mov r6,0x8000
  VWF_STR_BEGIN_MACRO
  b VWF_STR_BEGIN2_RET

  VWF_BEGIN:
  sub sp,sp,0x8
  push {r0-r4}
  ldr r0,=VWF_DATA
  mov r1,0x0
  strb r1,[r0,0x2]
  ;Get the VWF value
  ldr r3,=IS_ASCII
  ldr r3,[r3,0x4]
  ldr r2,=SJIS_LOOKUP
  mov r1,0x8
  @@loop:
  ldrh r4,[r2]
  cmp r4,0x0
  beq @@return
  cmp r3,r4
  addne r2,r2,0x4
  bne @@loop
  @@return:
  ldrh r1,[r2,0x2]
  strb r1,[r0,0x1]
  pop {r0-r4}
  b VWF_BEGIN_RET
  .pool

  ;original: strb r2,[r3],0x1
  VWF:
  push {r0-r4}
  ldr r0,=VWF_DATA
  ;Increase graphics ptr by the Character start / 2
  ldrb r1,[r0,0x0]
  mov r4,r1,lsr 1
  add r3,r3,r4
  ;Set r1 to char start + current char
  ldrb r4,[r0,0x2]
  add r1,r1,r4
  ;If r1 >= 8, draw in the next glyph (+0x40) but go up one row (-0x8)
  cmp r1,0x8
  addge r3,r3,0x40 - 0x4
  ;Store the actual pixel data
  strb r2,[r3]
  ;Increase r4 by 2, but set to 0 if 8
  add r4,r4,0x2
  cmp r4,0x8
  moveq r4,0x0
  strb r4,[r0,0x2]
  ;Return
  pop {r0-r4}
  add r3,r3,0x1
  b VWF_RET
  .pool

  VWF_END:
  push {r0-r2}
  ldr r0,=VWF_DATA
  ldrb r1,[r0,0x0]
  ldrb r2,[r0,0x1]
  ;Add character length to character start
  add r1,r1,r2
  ;If >= 8, decrease it by 8
  strb r1,[r0,0x0]
  cmp r1,0x8
  blt @@return
  ;Move to the next 8x16 space
  sub r1,r1,0x8
  strb r1,[r0,0x0]
  mov r1,0x1
  strb r1,[r0,0x3]
  @@return:
  pop {r0-r2}
  add sp,sp,0x8
  b VWF_END_RET
  .pool

  VWF_INCREASE:
  ldr r0,=VWF_DATA
  ldrb r1,[r0,0x3]
  cmp r1,0x1
  ldrne r0,[r11,r9]
  bne VWF_DONT_INCREASE
  mov r1,0x0
  strb r1,[r0,0x3]
  ldr r0,[r11,r9]
  b VWF_INCREASE_RET
  .pool
  .endarea

  ;Hook the function that reads characters
  .org 0x02025d50
  b CONVERT_ASCII
  CONVERT_ASCII_RET:

  ;Only move pointer by 1 if the character was ascii
  .org 0x020279f0
  b CHECK_ASCII
  CHECK_ASCII_RET:

  ;Hook before a glyph is rendered
  .org 0x02025ecc
  b VWF_BEGIN
  VWF_BEGIN_RET:

  ;Replace the glyph rendering
  .org 0x02025f3c
  .area 12*4,0x0
  mov r0,0x11
  mov r1,0x22
  @loop:
  ldrb r14,[r5]
  add r6,r6,0x1
  and r2,r14,r1
  mul r12,r2,r4
  and r2,r14,r0
  orr r2,r2,r12
  ;strb r2,[r3],0x1
  b VWF
  VWF_RET:
  add r5,r5,0x1
  cmp r6,0x40
  blt @loop
  .endarea

  ;Hook after a glyph has been rendered
  .org 0x02025f6c
  b VWF_END
  VWF_END_RET:

  ;Check if we need to skip this section
  .org 0x02027910
  b VWF_INCREASE
  VWF_INCREASE_RET:
  .org 0x0202797c
  VWF_DONT_INCREASE:

  ;Reset variables when a string starts rendering
  .org 0x02026d08
  b VWF_STR_BEGIN1
  VWF_STR_BEGIN1_RET:
  .org 0x020266a8
  b VWF_STR_BEGIN2
  VWF_STR_BEGIN2_RET:

  ;Don't check for line length limits
  .org 0x020278c4
  nop
  .org 0x020278dc
  nop
.close
