.nds

;Max length for item names in Item menu
SHORTEN_ITEM_NAME_VALUE equ 0xa*8
;Max length for item name when using one from the Item menu
SHORTEN_ITEM_NAME_USE_VALUE equ 0xa*8
;Max length for equip names in Equip menu (small on the left)
SHORTEN_EQUIP_NAME_LEFT_VALUE equ 0x8*8
;Max length for equip names in Equip menu (longer ones)
;Also used when selecting a slot (at the top)
SHORTEN_EQUIP_NAME_VALUE equ 0xa*8
;Max length for equip names in Status menu
SHORTEN_STATUS_EQUIP_VALUE equ 0xa*8
;Max length for shop windows (same for all 4 equip/item shop)
SHORTEN_SHOP_VALUE equ 0xa*8
;Max length for valuables window
SHORTEN_VALUABLES_VALUE equ 0xf*8
;Max length for jutsu name in Jutsu menu when using one
SHORTEN_JUTSU_USE_VALUE equ 0xa*8

sprintf equ 0x02001094
print_string equ 0x020265c0

.open "NarutoRPG2Data/repack/arm9.bin",0x1ff9000 - 0x92fc0
  .orga 0x92fc0
  .area 0x1000

  ;ASCII to SJIS lookup table, also includes VWF values
  SJIS_LOOKUP:
  .import "NarutoRPG2Data/fontdata.bin"
  .align
  SJIS_LOOKUP_SMALL:
  .import "NarutoRPG2Data/fontdatasmall.bin"
  .align

  SHORTEN_BUFFER:
  .fill 0x20,0

  LOAD_STR:
  .ascii "Load %s?" :: .db 0xa :: .asciiz "    Yes            No"
  DELETE_STR:
  .ascii "Delete %s?" :: .db 0xa :: .asciiz "    Yes            No"
  OVERWRITE_STR:
  .ascii "Overwrite %s?" :: .db 0xa :: .asciiz "    Yes            No"
  .align

  VWF_DATA_SIZE equ 12
  VWF_DATA:
  .dw VWF_DATA + 4
  ;Character start (0-6)
  VWF_CHAR_START equ 0
  .db 0
  ;Character length (2,4,6,8)
  VWF_CHAR_LENGTH equ 1
  .db 0
  ;Need to increase position after drawing glyph
  VWF_DO_INCREASE equ 2
  .db 0
  ;Draw in the previous tile
  VWF_DRAW_PREVIOUS equ 3
  .db 0
  ;Clean up everything after drawing
  VWF_CLEAN equ 4
  .db 0
  ;1 if we're drawing ASCII
  VWF_IS_ASCII equ 5
  .db 0
  VWF_PLACEHOLDER equ 6
  .db 0
  VWF_PLACEHOLDER2 equ 7
  .db 0
  VWF_CHAR equ 8
  .dw 0
  ;Repeat one more time
  .db 0 :: .db 0 :: .db 0 :: .db 0 :: .dw 0 :: .dw 0
  .align
  .macro load_vwf_data,reg
  ldr reg,=VWF_DATA
  ldr reg,[reg]
  .endmacro

  ;r0 = str ptr
  ;r3 = first byte
  ;r2 = second byte
  CONVERT_ASCII:
  ;Set VWF_IS_ASCII to 0 and check
  mov r4,0x0
  cmp r3,0x20
  blt @@store_and_ret
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
  load_vwf_data r12
  strb r4,[r12,VWF_IS_ASCII]
  @@return:
  ;Save the character
  mov r4,r2,lsl 8
  orr r4,r4,r3
  str r4,[r12,VWF_CHAR]
  mov r1,0x0
  bx lr
  .pool

  CHECK_ASCII:
  load_vwf_data r2
  ldrb r2,[r2,VWF_IS_ASCII]
  cmp r2,0x0
  addeq r0,r0,0x2
  addne r0,r0,0x1
  bx lr
  .pool

  VWF_BEGIN_BIG:
  push {r2,lr}
  ldr r2,=SJIS_LOOKUP
  bl VWF_BEGIN
  pop {r2,lr}
  sub sp,sp,0x8
  bx lr

  VWF_BEGIN_SMALL:
  push {r2,lr}
  ldr r2,=SJIS_LOOKUP_SMALL
  bl VWF_BEGIN
  pop {r2,lr}
  sub sp,sp,0x8
  bx lr

  VWF_BEGIN:
  push {r0,r1,r3,r4}
  load_vwf_data r0
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
  pop {r0,r1,r3,r4}
  bx lr
  @@noascii:
  mov r1,0x8
  strb r1,[r0,VWF_CHAR_LENGTH]
  b @@return
  .pool

  VWF:
  ;r0 = 0x11
  ;r1 = 0x22
  ;r2 = src address
  ;r3 = dst address
  ;r4 = palette data
  ;r11 = loop amount
  ;Load values from the font data
  load_vwf_data r5
  ;Check if we need to draw in the previous glyph
  ldrb r6,[r5,VWF_DRAW_PREVIOUS]
  cmp r6,0x1
  subeq r3,r3,r11
  ;Increase graphics ptr by the Character start / 2
  ldrb r5,[r5,VWF_CHAR_START]
  add r3,r3,r5,lsr 1
  ;Setup some registers
  mov r12,r3
  mov r6,0x0
  mov r7,0x0
  @@loop:
  ;If r5+r6 >= 8, draw in the next glyph (-4 to go up one row)
  add r3,r5,r6
  cmp r3,0x8
  mov r3,r12
  addge r3,r3,r11
  subge r3,r3,0x4
  ;Get and store the actual pixel data
  ldrb r8,[r2]
  and r9,r8,r1
  mul r10,r9,r4
  and r9,r8,r0
  orr r9,r9,r10
  strb r9,[r3]
  ;Increase counters
  add r2,r2,0x1
  add r7,r7,0x1
  add r12,r12,0x1
  ;Increase r6 by 2, decrease by 8 if >= 8
  add r6,r6,0x2
  cmp r6,0x8
  subge r6,r6,0x8
  ;Check if we need to loop more
  cmp r7,r11
  blt @@loop
  bx lr

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
  ;Advance character pos be 1 if it's not ascii
  ldrb r1,[r0]
  cmp r1,0x7f
  addge r0,r0,0x1
  ;Check next character
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
  ;Cleanup on choice end
  cmp r1,0xb
  beq @@cleanup
  ;Cleanup on symbol
  cmp r1,0xe
  beq @@cleanup
  ;Cleanup on item symbol
  cmp r1,0x13
  beq @@cleanup
  ;For waits, check the next character
  cmp r1,0x5
  addeq r0,r0,0x2
  beq @@checkagain
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

  ;Move to a separate VWF data struct since this text is only rendered a character every few frames
  VWF_DIALOG_BEGIN:
  push {r0-r1}
  ldr r0,=VWF_DATA
  add r1,r0,0x4 + VWF_DATA_SIZE
  str r1,[r0]
  pop {r0-r1}
  mov r4,0x4000
  bx lr

  ;Move back to the normal VWF data
  VWF_DIALOG_END:
  push {r0-r1}
  ldr r0,=VWF_DATA
  add r1,r0,0x4
  str r1,[r0]
  pop {r0-r1}
  add sp,sp,0x4
  bx lr
  .pool

  ;r0 = original string
  ;r1 = max length
  ;r2 = result
  ;r3 = VWF lookup
  SHORTEN_STR:
  push {r4-r6}
  mov r4,0
  @@loop:
  ldrb r5,[r0],0x1
  ;Check for 0 byte
  cmp r5,0x0
  beq @@return
  ;Check for item code
  cmp r5,0x13
  beq @@copysjis
  ;Check for sjis
  cmp r5,0x7f
  bge @@copysjis
  ;Load length for ASCII
  sub r6,r5,0x20
  lsl r6,r6,0x2
  add r6,r3,r6
  ldrh r6,[r6,0x2]
  ;Check if we can fit it
  add r4,r4,r6
  cmp r4,r1
  bge @@shorten
  ;Write the byte and move on
  strb r5,[r2],0x1
  b @@loop
  @@copysjis:
  ;Check if we can fit 8 pixels
  add r4,r4,8
  cmp r4,r1
  bge @@shorten
  ;Copy 2 bytes and move on
  strb r5,[r2],0x1
  ldrb r5,[r0],0x1
  strb r5,[r2],0x1
  b @@loop
  @@shorten:
  ;Write ... and return
  mov r5,0x2e
  strb r5,[r2],0x1
  strb r5,[r2],0x1
  strb r5,[r2],0x1
  @@return:
  mov r4,0
  strb r4,[r2]
  pop {r4-r6}
  bx lr
  .pool

  .macro shorten,max
  cmp r2,0x0
  beq print_string
  push {r0,r1,r3,lr}
  mov r0,r2
  mov r1,max
  ldr r2,=SHORTEN_BUFFER
  ldr r3,=SJIS_LOOKUP
  bl SHORTEN_STR
  ldr r2,=SHORTEN_BUFFER
  pop {r0,r1,r3,lr}
  b print_string
  .pool
  .endmacro

  SHORTEN_ITEM_NAME:
  shorten SHORTEN_ITEM_NAME_VALUE
  SHORTEN_ITEM_NAME_USE:
  shorten SHORTEN_ITEM_NAME_USE_VALUE
  SHORTEN_EQUIP_NAME_LEFT:
  shorten SHORTEN_EQUIP_NAME_LEFT_VALUE
  SHORTEN_EQUIP_NAME:
  shorten SHORTEN_EQUIP_NAME_VALUE
  SHORTEN_STATUS_EQUIP:
  shorten SHORTEN_STATUS_EQUIP_VALUE
  SHORTEN_JUTSU_USE:
  shorten SHORTEN_JUTSU_USE_VALUE

  .macro shorten_list,reg,max
  push {r0-r3,lr}
  mov r0,reg
  mov r1,max
  mov r2,reg
  ldr r3,=SJIS_LOOKUP
  bl SHORTEN_STR
  pop {r0-r3,lr}
  bx lr
  .pool
  .endmacro

  SHORTEN_SHOP:
  str r8,[r10,0x4]
  shorten_list r8,SHORTEN_SHOP_VALUE
  ;This function is called for every item, not just valuables
  ;If [r5,0x30] is != 0, the item is a valuable
  SHORTEN_VALUABLES:
  ldr r0,[r5,0x30]
  cmp r0,0x0
  bxeq lr
  ldr r2,[r4,0x10]
  add r2,r2,r6
  shorten_list r2,SHORTEN_VALUABLES_VALUE

  LOAD_STR_SPRINTF:
  ldr r1,=LOAD_STR
  b LOAD_STR_SPRINTF_RET
  DELETE_STR_SPRINTF:
  ldr r1,=DELETE_STR
  b DELETE_STR_SPRINTF_RET
  OVERWRITE_STR_SPRINTF:
  ldr r1,=OVERWRITE_STR
  b OVERWRITE_STR_SPRINTF_RET
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
  .area 12*4
  mov r0,0x11
  mov r1,0x22
  mov r2,r5
  push {r7-r12}
  mov r11,0x40
  bl VWF
  pop {r7-r12}
  b 0x02025f6c
  .endarea

  ;Replace the small glyph rendering
  .org 0x02026008
  .area 12*4
  mov r0,0x11
  mov r1,0x22
  mov r2,r6
  mov r3,r12
  push {r7-r12}
  mov r11,0x20
  bl VWF
  pop {r7-r12}
  b 0x02025f6c
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

  ;Hook before and after a timed dialog is rendered
  .org 0x02026d08
  bl VWF_DIALOG_BEGIN
  .org 0x02026d2c
  bl VWF_DIALOG_END

  ;Don't check for line length limits
  .org 0x020278c4
  nop
  .org 0x020278dc
  nop

  ;Extend main menu text boxes
  .org 0x0203bed8
  ;mov r0,0xc
  mov r0,0xd

  ;Shorten some strings when displaying them
  ;Shorten item names in Item menu
  .org 0x020386e0
  bl SHORTEN_ITEM_NAME
  ;Shorten item name when using one from the Item menu
  .org 0x02038efc
  bl SHORTEN_ITEM_NAME_USE
  ;Shorten equip names in Equip menu (small on the left)
  .org 0x02052ca0
  bl SHORTEN_EQUIP_NAME_LEFT
  .org 0x02052cdc
  bl SHORTEN_EQUIP_NAME_LEFT
  .org 0x02052d18
  bl SHORTEN_EQUIP_NAME_LEFT
  ;Shorten equip names in Equip menu (longer ones)
  .org 0x02052eb0
  bl SHORTEN_EQUIP_NAME
  .org 0x02052ee8
  bl SHORTEN_EQUIP_NAME
  .org 0x02052f20
  bl SHORTEN_EQUIP_NAME
  ;Shorten equip name when selecting a slot (at the top)
  .org 0x02052b78
  bl SHORTEN_EQUIP_NAME
  ;Also move them a bit left
  .org 0x02052e98
  ;add r0,r10,0x8
  add r0,r10,0x7
  .org 0x02052eb8
  add r0,r10,0x7
  .org 0x02052ef0
  add r0,r10,0x7
  ;Shorten equip names in Status menu
  .org 0x02058600
  bl SHORTEN_STATUS_EQUIP
  .org 0x02058688
  bl SHORTEN_STATUS_EQUIP
  .org 0x02058718
  bl SHORTEN_STATUS_EQUIP
  ;Also move them a bit left
  .org 0x020585a4
  ;add r1,r8,0x5
  add r1,r8,0x4
  .org 0x020585e8
  add r1,r8,0x4
  .org 0x02058670
  add r1,r8,0x4
  .org 0x020586f4
  add r1,r8,0x4
  .org 0x02058620
  ;add r1,r8,0x7
  add r1,r8,0x6
  .org 0x020586a8
  add r1,r8,0x6
  ;Shorten shop windows (same for all 4 equip/item shop)
  .org 0x0205c2b0
  bl SHORTEN_SHOP
  ;Shorten valuables window
  .org 0x020389ac
  bl SHORTEN_VALUABLES
  ;Shorten jutsu name in Jutsu menu when using one
  .org 0x020569a0
  bl SHORTEN_JUTSU_USE

  ;Change save/load string to move sprintf parameters
  .org 0x02073260
  b LOAD_STR_SPRINTF
  LOAD_STR_SPRINTF_RET:
  .org 0x02073824
  b DELETE_STR_SPRINTF
  DELETE_STR_SPRINTF_RET:
  .org 0x02073528
  b OVERWRITE_STR_SPRINTF
  OVERWRITE_STR_SPRINTF_RET:

  ;Move the save/load location text left
  .org 0x02072444
  ;add r0,r0,0x14
  add r0,r0,0x11

  ;Move location text left
  .org 0x0203b860
  ;add r1,r6,2
  add r1,r6,1

  ;Move location textbox left
  .org 0x0203bc84
  ;mov r1,0x13
  mov r1,0x10
  .org 0x0203bc98
  ;mov r1,0x13
  mov r1,0x10
  .org 0x0203bc48
  ;mov r1,0x13
  mov r1,0x10

  ;Make the location textbox bigger
  .org 0x0203b824
  ;mov r3,0xe
  mov r3,0x10

  ;Move money left 1 tile
  .org 0x0203bbf8
  ;mov r1,0x12
  mov r1,0x11
.close
