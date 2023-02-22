.nds

.open "NarutoRPG2Data/repack/arm9.bin",0x1ff9000 - 0x92fc0
  .orga 0x92fc0
  .area 0x700

  ;ASCII to SJIS lookup table, also includes VWF values
  SJIS_LOOKUP:
  .import "NarutoRPG2Data/fontdata.bin"
  .align
  SJIS_LOOKUP_SMALL:
  .import "NarutoRPG2Data/fontdatasmall.bin"
  .align

  VWF_DATA_SIZE equ 12
  VWF_DATA:
  .dw VWF_DATA
  ;Character start (0-6)
  VWF_CHAR_START equ 0
  .db 0
  ;Character length (2,4,6,8)
  VWF_CHAR_LENGTH equ 1
  .db 0
  ;Current character x (0,2,4,6)
  VWF_CHAR_X equ 2
  .db 0
  ;Need to increase position after drawing glyph
  VWF_DO_INCREASE equ 3
  .db 0
  ;Draw in the previous tile
  VWF_DRAW_PREVIOUS equ 4
  .db 0
  ;Clean up everything after drawing
  VWF_CLEAN equ 5
  .db 0
  ;1 if we're drawing ASCII
  VWF_IS_ASCII equ 6
  .db 0
  VWF_PLACEHOLDER equ 7
  .db 0
  VWF_CHAR equ 8
  .dw 0
  .dw 0 :: .dw 0 :: .dw 0
  .align

  .macro load_vwf_data,reg
  ldr reg,=VWF_DATA
  ldr reg,[reg]
  .endmacro

  ;r0 = str ptr
  ;r3 = first byte
  ;r2 = second byte
  CONVERT_ASCII:
  push {r0-r1,r4}
  mov r4,0x0
  ;Set VWF_IS_ASCII to 0 and check
  load_vwf_data r0
  cmp r3,0x7f
  bge @@store_and_ret
  ;Return the SJIS character
  cmp r1,0x0
  ldreq r2,=SJIS_LOOKUP
  ldrne r2,=SJIS_LOOKUP_SMALL
  sub r3,r3,0x20
  lsl r3,r3,0x2
  add r2,r2,r3
  ldrb r3,[r2]
  ldrb r2,[r2,0x1]
  ;Set VWF_IS_ASCII to 1
  mov r4,0x1
  @@store_and_ret:
  strb r4,[r0,VWF_IS_ASCII]
  @@return:
  ;Save the character
  mov r4,r2,lsl 8
  orr r4,r4,r3
  str r4,[r0,VWF_CHAR]
  pop {r0-r1,r4}
  mov r1,0x0
  bx lr
  .pool

  CHECK_ASCII:
  push {r1}
  load_vwf_data r1
  ldrb r1,[r1,VWF_IS_ASCII]
  cmp r1,0x0
  addeq r0,r0,0x2
  addne r0,r0,0x1
  pop {r1}
  bx lr
  .pool

  VWF_BEGIN_BIG:
  sub sp,sp,0x8
  push {r2,lr}
  ldr r2,=SJIS_LOOKUP
  bl VWF_BEGIN
  pop {r2,lr}
  bx lr

  VWF_BEGIN_SMALL:
  sub sp,sp,0x8
  push {r2,lr}
  ldr r2,=SJIS_LOOKUP_SMALL
  bl VWF_BEGIN
  pop {r2,lr}
  bx lr

  VWF_BEGIN:
  push {r0,r1,r4}
  load_vwf_data r0
  mov r1,0x0
  strb r1,[r0,VWF_CHAR_X]
  ;Get the VWF value
  ldrb r1,[r0,VWF_IS_ASCII]
  cmp r1,0x0
  beq @@noascii
  ldr r3,[r0,VWF_CHAR]
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
  strb r1,[r0,VWF_CHAR_LENGTH]
  @@return:
  pop {r0,r1,r4}
  bx lr
  @@noascii:
  mov r1,0x8
  strb r1,[r0,VWF_CHAR_LENGTH]
  b @@return
  .pool

  .macro vwf,reg,amount
  push {r0-r2,r4,reg}
  load_vwf_data r0
  ;Check if we need to draw in the previous glyph
  ldrb r1,[r0,VWF_DRAW_PREVIOUS]
  cmp r1,0x1
  subeq reg,reg,amount
  ;Increase graphics ptr by the Character start / 2
  ldrb r1,[r0,VWF_CHAR_START]
  mov r4,r1,lsr 1
  add reg,reg,r4
  ;Set r1 to char start + current char
  ldrb r4,[r0,VWF_CHAR_X]
  add r1,r1,r4
  ;If r1 >= 8, draw in the next glyph (-4 to go up one row)
  cmp r1,0x8
  addge reg,reg,amount - 0x4
  ;Store the actual pixel data
  strb r2,[reg]
  ;Increase r4 by 2, but set to 0 if 8
  add r4,r4,0x2
  cmp r4,0x8
  moveq r4,0x0
  strb r4,[r0,VWF_CHAR_X]
  ;Return
  pop {r0-r2,r4,reg}
  add reg,reg,0x1
  bx lr
  .pool
  .endmacro

  ;original: strb r2,[r3],0x1
  VWF:
  vwf r3,0x40

  ;original: strb r2,[r12],0x1
  VWF_SMALL:
  vwf r12,0x20

  VWF_END:
  push {r0-r2}
  load_vwf_data r0
  mov r1,0x0
  strb r1,[r0,VWF_DRAW_PREVIOUS]
  ldrb r1,[r0,VWF_CHAR_START]
  ldrb r2,[r0,VWF_CHAR_LENGTH]
  ;Add character length to character start
  add r1,r1,r2
  strb r1,[r0,VWF_CHAR_START]
  ;Check if the value was 0 (r1 == r2)
  cmp r1,r2
  beq @@waszero
  ;Otherwhise, check if it's less than 8
  cmp r1,0x8
  blt @@lessthan8
  ;Move to the next 8x16 space and draw in the previous glyph only if r1-8 > 0
  sub r1,r1,0x8
  strb r1,[r0,VWF_CHAR_START]
  cmp r1,0x0
  beq @@return
  mov r1,0x1
  strb r1,[r0,VWF_DO_INCREASE]
  @@lessthan8:
  mov r1,0x1
  strb r1,[r0,VWF_DRAW_PREVIOUS]
  b @@return
  @@waszero:
  ;If the value was 0, we need to move regardless, and set it to 0 if it's 8
  cmp r1,0x8
  mov r1,0x0
  movlt r1,0x1
  strb r1,[r0,VWF_DRAW_PREVIOUS]
  mov r1,0x1
  strb r1,[r0,VWF_DO_INCREASE]
  bne @@return
  mov r1,0x0
  strb r1,[r0,VWF_CHAR_START]
  @@return:
  ldrb r1,[r0,VWF_CLEAN]
  cmp r1,0x1
  beq @@cleanup
  @@pop:
  pop {r0-r2}
  add sp,sp,0x8
  bx lr
  ;Clean up everything except the "move to next tile" part
  @@cleanup:
  mov r1,0x0
  strb r1,[r0,VWF_CHAR_START]
  strb r1,[r0,VWF_CHAR_LENGTH]
  strb r1,[r0,VWF_CHAR_X]
  strb r1,[r0,VWF_DRAW_PREVIOUS]
  strb r1,[r0,VWF_CLEAN]
  b @@pop
  .pool

  .macro vwf_increase,reg,ret,noret,amount,loopn
  load_vwf_data r0
  ldrb r1,[r0,VWF_DO_INCREASE]
  cmp r1,0x1
  ldrne r0,[reg,r9]
  bne noret
  mov r1,0x0
  strb r1,[r0,VWF_DO_INCREASE]
  ldr r0,[reg,r9]
  ;Fill the new glyph with 0x11
  push {r0-r2}
  add r0,r0,amount
  mov r1,0x0
  ldr r2,=0x11111111
  @@loop:
  str r2,[r0]
  add r0,r0,0x4
  add r1,r1,0x1
  cmp r1,loopn
  bne @@loop
  pop {r0-r2}
  b ret
  .pool
  .endmacro

  VWF_INCREASE:
  vwf_increase r11,VWF_INCREASE_RET,VWF_DONT_INCREASE,0x40,0x10

  VWF_SMALL_INCREASE:
  vwf_increase r8,VWF_SMALL_INCREASE_RET,VWF_SMALL_DONT_INCREASE,0x20,0x8

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
  load_vwf_data r0
  mov r1,0x1
  strb r1,[r0,VWF_CLEAN]
  b @@return
  .pool
  .endarea
.close

.open "NarutoRPG2Data/repack/arm9.bin",0x02000000
  ;Hook the function that reads characters to convert ASCII to SJIS
  .org 0x02025d50
  bl CONVERT_ASCII
  .org 0x02025e14
  bl CONVERT_ASCII

  ;Only move pointer by 1 if the character was ascii
  .org 0x020279f0
  bl CHECK_ASCII

  ;Hook before a glyph is rendered
  .org 0x02025ecc
  bl VWF_BEGIN_BIG

  ;Hook before a small glyph is rendered
  .org 0x02025f8c
  bl VWF_BEGIN_SMALL

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
  bl VWF
  add r5,r5,0x1
  cmp r6,0x40
  blt @loop
  .endarea

  ;Replace the small glyph rendering
  .org 0x02026008
  .area 12*4,0x0
  mov r0,0x11
  mov r1,0x22
  @small_loop:
  ldrb r14,[r6]
  add r5,r5,0x1
  and r2,r14,r1
  mul r3,r2,r4
  and r2,r14,r0
  orr r2,r2,r3
  bl VWF_SMALL
  add r6,r6,0x1
  cmp r5,0x20
  blt @small_loop
  .endarea

  ;Hook after a glyph has been rendered
  .org 0x02025f6c
  bl VWF_END

  ;Hook after a small glyph has been rendered
  .org 0x02026038
  bl VWF_END

  ;Check if we need to skip this section
  .org 0x02027910
  b VWF_INCREASE
  VWF_INCREASE_RET:
  .org 0x0202797c
  VWF_DONT_INCREASE:

  ;Check if we need to skip this section (small font)
  .org 0x02027998
  b VWF_SMALL_INCREASE
  VWF_SMALL_INCREASE_RET:
  .org 0x020279dc
  VWF_SMALL_DONT_INCREASE:

  ;Store the next char to check if we need to clean up the VWF
  .org 0x020278a4
  bl CHECK_NEXT_CHAR

  ;Don't check for line length limits
  .org 0x020278c4
  nop
  .org 0x020278dc
  nop
.close
