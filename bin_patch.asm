.nds

.open "NarutoRPG2Data/repack/arm9.bin",0x1ff9000 - 0x92fc0
  .orga 0x92fc0
  .area 0x600

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
  ;Need to increase position after drawing glyph
  .db 0
  ;Draw in the previous tile
  .db 0
  ;Clean up everything after drawing
  .db 0
  .align

  VWF_BEGIN:
  sub sp,sp,0x8
  push {r0-r4}
  ldr r0,=VWF_DATA
  mov r1,0x0
  strb r1,[r0,0x2]
  ;Get the VWF value
  ldr r3,=IS_ASCII
  ldr r1,[r3,0x0]
  cmp r1,0x0
  beq @@noascii
  ldr r3,[r3,0x4]
  ldr r2,=SJIS_LOOKUP
  mov r1,0x8
  @@loop:
  ldrh r4,[r2]
  cmp r4,0x0
  beq @@found
  cmp r3,r4
  addne r2,r2,0x4
  bne @@loop
  @@found:
  ldrh r1,[r2,0x2]
  strb r1,[r0,0x1]
  @@return:
  pop {r0-r4}
  b VWF_BEGIN_RET
  @@noascii:
  mov r1,0x8
  strb r1,[r0,0x1]
  b @@return
  .pool

  ;original: strb r2,[r3],0x1
  VWF:
  push {r0-r4}
  ldr r0,=VWF_DATA
  ;Check if we need to draw in the previous glyph
  ldrb r1,[r0,0x4]
  cmp r1,0x1
  subeq r3,r3,0x40
  ;Increase graphics ptr by the Character start / 2
  ldrb r1,[r0,0x0]
  mov r4,r1,lsr 1
  add r3,r3,r4
  ;Set r1 to char start + current char
  ldrb r4,[r0,0x2]
  add r1,r1,r4
  ;If r1 >= 8, draw in the next glyph (+0x40) but go up one row (-0x4)
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
  mov r1,0x0
  strb r1,[r0,0x4]
  ldrb r1,[r0,0x0]
  ldrb r2,[r0,0x1]
  ;Add character length to character start
  add r1,r1,r2
  strb r1,[r0,0x0]
  ;Check if the value was 0 (r1 == r2)
  cmp r1,r2
  beq @@waszero
  ;Otherwhise, check if it's less than 8
  cmp r1,0x8
  blt @@lessthan8
  ;Move to the next 8x16 space and draw in the previous glyph only if r1-8 > 0
  sub r1,r1,0x8
  strb r1,[r0,0x0]
  cmp r1,0x0
  beq @@return
  mov r1,0x1
  strb r1,[r0,0x3]
  @@lessthan8:
  mov r1,0x1
  strb r1,[r0,0x4]
  b @@return
  @@waszero:
  ;If the value was 0, we need to move regardless, and set it to 0 if it's 8
  cmp r1,0x8
  mov r1,0x0
  movlt r1,0x1
  strb r1,[r0,0x4]
  mov r1,0x1
  strb r1,[r0,0x3]
  bne @@return
  mov r1,0x0
  strb r1,[r0,0x0]
  @@return:
  ldrb r1,[r0,0x5]
  cmp r1,0x1
  beq @@cleanup
  @@pop:
  pop {r0-r2}
  add sp,sp,0x8
  b VWF_END_RET
  ;Clean up everything except the "move to next tile" part
  @@cleanup:
  mov r1,0x0
  strb r1,[r0,0x0]
  strb r1,[r0,0x1]
  strb r1,[r0,0x2]
  str r1,[r0,0x4]
  b @@pop
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
  ;Fill the new glyph with 0x11
  push {r0-r2}
  add r0,r0,0x40
  mov r1,0x0
  ldr r2,=0x11111111
  @@loop:
  str r2,[r0]
  add r0,r0,0x4
  add r1,r1,0x1
  cmp r1,0x10
  bne @@loop
  pop {r0-r2}
  b VWF_INCREASE_RET
  .pool

  CHECK_NEXT_CHAR:
  push {r0-r1}
  @@checkagain:
  ldrb r1,[r0,0x1]
  ;Cleanup on string end
  cmp r1,0x0
  beq @@cleanup
  ;Cleanup on sentence end
  cmp r1,0x3
  beq @@cleanup
  ;Cleanup on line break
  cmp r1,0xa
  beq @@cleanup
  ;Cleanup on symbol
  cmp r1,0xe
  beq @@cleanup
  ;For colors, we need to check the next character as well since it might be at the end of a line
  cmp r1,0x7
  addeq r0,r0,0x2
  beq @@checkagain
  ;Jump to the normal function
  @@return:
  pop {r0-r1}
  b 0x02025cfc
  @@cleanup:
  ldr r0,=VWF_DATA
  mov r1,0x1
  strb r1,[r0,0x5]
  b @@return
  .pool
  .endarea
.close

.open "NarutoRPG2Data/repack/arm9.bin",0x02000000
  ;Hook the function that reads characters to convert ASCII to SJIS
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
  ;Treat alt text the same as normal text, not sure this is needed
  .org 0x020278f0
  beq 0x020278f8

  ;Store the next char to check if we need to clean up the VWF
  .org 0x020278a4
  bl CHECK_NEXT_CHAR

  ;Don't check for line length limits
  .org 0x020278c4
  nop
  .org 0x020278dc
  nop
.close
