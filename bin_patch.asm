.nds

;Max length for item names in Item menu
SHORTEN_ITEM_NAME_VALUE equ 12*8
;Max length for item name when using one from the Item menu
SHORTEN_ITEM_NAME_USE_VALUE equ 11*8
;Max length for item name in battle rewards
SHORTEN_ITEM_NAME_REWARD_VALUE equ 12*8
;Max length for equip names in Equip menu (small on the left)
SHORTEN_EQUIP_NAME_LEFT_VALUE equ 10*8
;Max length for equip names in Equip menu and when selecting a slot (at the top)
SHORTEN_EQUIP_NAME_VALUE equ 11*8
;Max length for equip names in Equip menu when changing a slot
SHORTEN_EQUIP_LIST_VALUE equ 10*8
;Max length for equip names in Status menu
SHORTEN_STATUS_EQUIP_VALUE equ 11*8
;Max length for jutsu list in Status menu
SHORTEN_STATUS_JUTSU_LIST_VALUE equ 13*8
;Max length for shop windows (same for all 4 equip/item shop)
SHORTEN_SHOP_VALUE equ 13*8
;Max length for window after Who will equip x
SHORTEN_WHO_WILL_EQUIP_VALUE equ 11*8
;Max length for valuables window
SHORTEN_VALUABLES_VALUE equ 17*8
;Max length for jutsu name in Jutsu menu when using one
SHORTEN_JUTSU_USE_VALUE equ 11*8
;Max length for jutsu name in battle
SHORTEN_BATTLE_JUTSU_LIST_VALUE equ 13*8
;Max length for jutsu name in battle (additional shorter window)
SHORTEN_ADDITIONAL_BATTLE_JUTSU_LIST_VALUE equ 12*8
;Max length for item name in battle
SHORTEN_BATTLE_ITEM_LIST_VALUE equ 11*8

sprintf equ 0x02001094
strcpy equ 0x020033cc
strcat equ 0x02003328
print_string equ 0x020265c0
print_list equ 0x02029104

.open "NarutoRPG2Data/repack/arm9.bin",0x1ff9000 - 0x92fc0
  .orga 0x92fc0
  .area 0x1200

  ;ASCII to SJIS lookup table, also includes VWF values
  SJIS_LOOKUP:
  .import "NarutoRPG2Data/fontdata.bin"
  .align
  SJIS_LOOKUP_SMALL:
  .import "NarutoRPG2Data/fontdatasmall.bin"
  .align

  SHORTEN_BUFFER:
  .fill 0x30,0
  .align

  SHORTEN_AMOUNT:
  .dw 0

  LOAD_STR:
  ;0x020913d8 "を　ロードしますか？|　はい　　　いいえ"
  .ascii "Load %s?" :: .db 0x0a :: .asciiz "    Yes            No"
  DELETE_STR:
  ;0x02091480 "を　さくじょしますか？|　はい　　　いいえ"
  .ascii "Delete %s?" :: .db 0x0a :: .asciiz "    Yes            No"
  OVERWRITE_STR:
  ;0x020914d8 "のデータに　うわがきしますか？|　はい　　　いいえ"
  .ascii "Overwrite %s?" :: .db 0x0a :: .asciiz "    Yes            No"

  BUY_STR:
  ;0x0208eeb0 "　を<u48>こ　かいました$$"
  .ascii "Bought " :: .db 0x02 :: .db 0x30 :: .ascii "of %c%c%s%s." :: .db 0x03 :: .db 0x01 :: .db 0x00
  SELL_STR:
  ;0x0208eec8 "　を<u48>こ　うりました$$"
  .ascii "Sold " :: .db 0x02 :: .db 0x30 :: .ascii "of %c%c%s%s." :: .db 0x03 :: .db 0x01 :: .db 0x00
  SELL_CONFIRM_STR:
  ;0x0208ef6c "　を<u48>こ　うりますか？|　　はい　　いいえ"
  .ascii "Sell " :: .db 0x02 :: .db 0x30 :: .ascii "of %c%c%s%s?" :: .db 0x0a :: .asciiz "       Yes       No"
  BUY_CONFIRM_STR:
  ;0x0208ef98 "　を　<u48>こ　かいますか？|　　はい　　いいえ"
  .ascii "Buy " :: .db 0x02 :: .db 0x30 :: .ascii "of %c%c%s%s?" :: .db 0x0a :: .asciiz "       Yes       No"
  EQUIP_STR:
  ;0x0208eee0 "の　そうびをへんこうしました$$"
  .ascii "Changed the equipment on %s." :: .db 0x03 :: .db 0x01 :: .db 0x00
  EQUIP_CONFIRM_STR:
  ;0x0208ef44 "　をそうびしますか？|　　はい　　いいえ"
  .ascii "Equip %c%c%s%s?" :: .db 0x0a :: .asciiz "       Yes       No"
  EQUIP_SELECT_STR:
  ;0x0208f0bc "　をだれにそうびしますか？|カーソルでえらんでください$$"
  .ascii "Who will equip %c%c%s%s?" :: .db 0x0a :: .ascii "Use the cursor to select." :: .db 0x03 :: .db 0x01 :: .db 0x00
  CHEMISTRY_UP_STR:
  ;0x0208d940 "とのあいしょうがあがった！"
  .asciiz "Chemistry with %s has gone up!"
  CHEMISTRY_DOWN_STR:
  ;0x0208d940 "とのあいしょうがさがった！"
  .asciiz "Chemistry with %s has gone down!"
  GAINED_SPRINTF_STR:
  .asciiz "%s%s%s"

  UNLOCK_STR:
  .db 0x10 :: .db 0x22 :: .asciiz "You can play"
  UNLOCK2_STR:
  .db 0x10 :: .db 0x24 :: .asciiz "You can use"
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
  ;1 if we should draw the full character
  VWF_DRAW_FULL equ 6
  .db 0
  ;1 if the background is 0x0 instead of 0x11111111
  VWF_BG_TYPE equ 7
  .db 0
  VWF_CHAR equ 8
  .dw 0
  ;Repeat one more time
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
  ;r0 = size multiplier (0x2 or 0x3)
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
  ;Load the char length or set to 0x8 if VWF_CLEAN or VWF_DRAW_FULL are 1
  ldrb r1,[r5,VWF_CHAR_LENGTH]
  ldrb r7,[r5,VWF_CLEAN]
  cmp r7,0x1
  moveq r1,0x8
  ldrb r7,[r5,VWF_DRAW_FULL]
  cmp r7,0x1
  moveq r1,0x8
  lsl r0,r1,r0
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
  ldrb r8,[r2],0x1
  and r9,r8,0x22
  mul r10,r9,r4
  and r9,r8,0x11
  orr r9,r9,r10
  strb r9,[r3]
  ;Increase counters
  add r7,r7,0x1
  add r12,r12,0x1
  ;Increase r6 by 2, check if >= r1 (8 for fullwidth characters)
  add r6,r6,0x2
  cmp r6,r1
  bge @@nextline
  ;Check if we need to loop more
  @@checkloop:
  cmp r7,r0
  blt @@loop
  bx lr
  @@nextline:
  ;Decrease r6 by the char length
  sub r6,r6,r1
  ;Also need to add 0x4-r1/2 to r2 and r12 to advance the pointers
  mov r8,0x4
  sub r8,r8,r1,lsr 0x1
  add r2,r2,r8
  add r12,r12,r8
  b @@checkloop

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
  ldrb r1,[r0,VWF_BG_TYPE]
  ldr r0,[reg,r9]
  ;Fill the new glyph with 0x11 (or 0x0 depending on VWF_BG_TYPE)
  push {r0-r2}
  add r0,r0,amount
  mov r2,0x0
  cmp r1,0x0
  ldreq r2,=0x11111111
  mov r1,0x0
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
  ;For waits and sounds, check the next character
  cmp r1,0x5
  addeq r0,r0,0x2
  beq @@checkagain
  cmp r1,0x6
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
  mov r0,0x1
  strb r0,[r1,VWF_DRAW_FULL]
  pop {r0-r1}
  mov r4,0x4000
  bx lr

  ;Move back to the normal VWF data
  VWF_DIALOG_END:
  push {r0-r2}
  ldr r0,=VWF_DATA
  add r1,r0,0x4 + VWF_DATA_SIZE
  mov r2,0x0
  strb r2,[r1,VWF_DRAW_FULL]
  add r1,r0,0x4
  str r1,[r0]
  pop {r0-r2}
  add sp,sp,0x4
  bx lr
  .pool

  VWF_DIALOG_PREPARE:
  ;Set VWF_CLEAN as 1 when a dialogue line is prepared
  ldr r0,=VWF_DATA
  add r0,r0,4+VWF_DATA_SIZE
  mov r5,0x0
  str r5,[r0]
  str r5,[r0,0x4]
  str r5,[r0,0x8]
  mov r0,0x2
  bx lr
  .pool

  DIALOG_CHECK_STRCMP:
  @@loop:
  ldrb r1,[r0],0x1
  cmp r1,0x00
  moveq r0,0x1
  beq @@return
  ldrb r2,[r4],0x1
  cmp r1,r2
  movne r0,0x0
  bne @@return
  b @@loop
  @@return:
  bx lr

  VWF_DIALOG_CHECK:
  push {r1-r4,lr}
  ;Clean up VWF here as well
  ldr r0,=VWF_DATA
  add r0,r0,4+VWF_DATA_SIZE
  mov r3,0x0
  str r3,[r0]
  str r3,[r0,0x4]
  str r3,[r0,0x8]
  ;Check if we're matching a specific line
  mov r3,r4
  ldr r0,=UNLOCK_STR
  bl DIALOG_CHECK_STRCMP
  cmp r0,0x1
  blne @@next
  bl CHECK_UNLOCK_WIFI
  b @@return
  @@next:
  ldr r0,=UNLOCK2_STR
  mov r4,r3
  bl DIALOG_CHECK_STRCMP
  cmp r0,0x0
  bleq @@return
  bl CHECK_UNLOCK_GIFT
  @@return:
  pop {r1-r4,lr}
  mov r0,r6
  bx lr
  .pool

  .macro unlock_wifi,char_addr,char_mask,tag_addr,jump
  ;Check if the character is available
  ldr r0,=char_addr
  ldrb r0,[r0]
  and r1,r0,char_mask
  cmp r1,char_mask
  beq jump
  ;Check if the tag is available
  ldr r0,=tag_addr
  ldrb r1,[r0]
  cmp r1,0x0
  bgt jump
  ;Add 1 tag
  mov r1,0x1
  strb r1,[r0]
  .endmacro

  CHECK_UNLOCK_WIFI:
  unlock_wifi 0x02099a50,0x1,0x02099981,@@check_jiraiya
  @@check_jiraiya:
  unlock_wifi 0x02099a4f,0x20,0x0209997e,@@return
  @@return:
  bx lr

  .macro unlock_gift,char_addr,char_mask1,char_mask2,tag_addr1,tag_addr2,gift_addr,flag_addr,flag_mask,jump
  ;Check if only one of the characters is unlocked
  ldr r0,=char_addr
  ldrb r0,[r0]
  and r1,r0,char_mask1
  cmp r1,char_mask1
  moveq r1,0x1
  and r2,r0,char_mask2
  cmp r2,char_mask2
  moveq r2,0x1
  cmp r1,r2
  beq jump
  ;Check that we don't already have both tags
  ldr r0,=tag_addr1
  ldrb r1,[r0]
  ldr r0,=tag_addr2
  ldrb r2,[r0]
  and r1,r1,r2
  cmp r1,0x1
  beq jump
  ;Check if the gift is in the inventory
  ldr r0,=gift_addr
  ldrb r1,[r0]
  cmp r1,0x0
  bgt jump
  ;Add 1 gift and reset the flag
  mov r1,0x1
  strb r1,[r0]
  ldr r0,=flag_addr
  ldrb r1,[r0]
  mov r2,flag_mask
  and r1,r1,r2
  strb r1,[r0]
  .endmacro

  CHECK_UNLOCK_GIFT:
  unlock_gift 0x02099a50,0x2,0x8,0x02099982,0x02099984,0x020999ae,0x02099a40,0xbf,@@check_shino_tenten
  @@check_shino_tenten:
  unlock_gift 0x02099a50,0x4,0x10,0x02099983,0x02099985,0x020999af,0x02099a41,0xfd,@@return
  @@return:
  bx lr
  .pool

  ;Strlen function that works with VWF
  STRLEN_VWF:
  push {r3-r4}
  ldr r3,=SJIS_LOOKUP
  mov r2,0
  @@loop:
  ldrb r1,[r0],0x1
  cmp r1,0x0
  beq @@return
  cmp r1,0x7f
  bge @@sjis
  sub r1,r1,0x20
  lsl r1,r1,0x2
  add r1,r3,r1
  ldrh r1,[r1,0x2]
  add r2,r2,r1
  b @@loop
  @@sjis:
  add r0,r0,0x1
  add r2,r2,0x8
  b @@loop
  @@return:
  mov r0,r2,lsr 0x2
  add r0,r0,0x1
  pop {r3-r4}
  bx lr
  .pool

  ;r0 = original string
  ;r1 = max length
  ;r2 = result
  ;r3 = VWF lookup
  SHORTEN_STR:
  push {r4-r9}
  mov r4,0 ;vwf counter
  mov r7,0 ;tile counter
  mov r8,r2 ;last good tile ptr
  mov r9,r2 ;current tile ptr
  @@loop:
  ldrb r5,[r0],0x1
  ;Check for 0 byte
  cmp r5,0x0
  beq @@return
  ;Check for item code, also add an extra 8 to the size
  cmp r5,0x13
  addeq r4,r4,8
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
  b @@check_tile
  @@copysjis:
  ;Check if we can fit 8 pixels
  add r4,r4,8
  cmp r4,r1
  bge @@shorten
  ;Copy 2 bytes and move on
  strb r5,[r2],0x1
  ldrb r5,[r0],0x1
  strb r5,[r2],0x1
  ;Check if we're in a new tile
  @@check_tile:
  lsr r5,r4,3
  cmp r5,r7
  movne r7,r5
  movne r8,r9
  movne r9,r2
  b @@loop
  @@shorten:
  mov r2,r9
  ;Write … and return
  mov r5,0x81
  strb r5,[r2],0x1
  mov r5,0x63
  strb r5,[r2],0x1
  @@return:
  mov r4,0
  strb r4,[r2]
  pop {r4-r9}
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
  SHORTEN_ITEM_NAME_REWARD:
  shorten SHORTEN_ITEM_NAME_REWARD_VALUE
  SHORTEN_EQUIP_NAME_LEFT:
  shorten SHORTEN_EQUIP_NAME_LEFT_VALUE
  SHORTEN_EQUIP_NAME:
  shorten SHORTEN_EQUIP_NAME_VALUE
  SHORTEN_STATUS_EQUIP:
  shorten SHORTEN_STATUS_EQUIP_VALUE
  SHORTEN_JUTSU_USE:
  shorten SHORTEN_JUTSU_USE_VALUE
  SHORTEN_WHO_WILL_EQUIP:
  shorten SHORTEN_WHO_WILL_EQUIP_VALUE

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
  SHORTEN_WIFI_TRADE:
  str r7,[r9,0x4]
  shorten_list r7,SHORTEN_SHOP_VALUE
  ;This function is called for every item, not just valuables
  ;If [r5,0x30] is != 0, the item is a valuable
  SHORTEN_VALUABLES:
  ldr r0,[r5,0x30]
  cmp r0,0x0
  bxeq lr
  ldr r2,[r4,0x10]
  add r2,r2,r6
  shorten_list r2,SHORTEN_VALUABLES_VALUE

  SHORTEN_PRINT_LIST:
  cmp r2,0x0
  beq @@skip
  push {r0,r1,r3,lr}
  mov r0,r2
  ldr r1,=SHORTEN_AMOUNT
  ldr r1,[r1]
  ;If the shorten amount is 0x0, skip this
  cmp r1,0x0
  popeq {r0,r1,r3,lr}
  beq @@skip
  ldr r2,=SHORTEN_BUFFER
  ldr r3,=SJIS_LOOKUP
  bl SHORTEN_STR
  ldr r2,=SHORTEN_BUFFER
  pop {r0,r1,r3,lr}
  @@skip:
  b print_string
  .pool

  .macro wrap_print_list,max,ret,battle
  push {r0-r1}
  ldr r0,=SHORTEN_AMOUNT
  .if battle == 0
    mov r1,max
  .else
    ldr r1,=0x020c0318
    ldr r1,[r1,0x4] ; this is 0 for jutsu, 1 for items
    cmp r1,0x0
    moveq r1,max
    movne r1,SHORTEN_BATTLE_ITEM_LIST_VALUE
  .endif
  str r1,[r0]
  pop {r0-r1}
  bl print_list
  push {r0-r1}
  ldr r0,=SHORTEN_AMOUNT
  mov r1,0
  str r1,[r0]
  pop {r0-r1}
  b ret
  .pool
  .endmacro

  SHORTEN_EQUIP_LIST:
  wrap_print_list SHORTEN_EQUIP_LIST_VALUE,SHORTEN_EQUIP_LIST_RET,0
  SHORTEN_STATUS_JUTSU_LIST:
  wrap_print_list SHORTEN_STATUS_JUTSU_LIST_VALUE,SHORTEN_STATUS_JUTSU_LIST_RET,0
  SHORTEN_BATTLE_LIST:
  wrap_print_list SHORTEN_BATTLE_JUTSU_LIST_VALUE,SHORTEN_BATTLE_LIST_RET,1
  SHORTEN_ADDITIONAL_BATTLE_LIST:
  wrap_print_list SHORTEN_ADDITIONAL_BATTLE_JUTSU_LIST_VALUE,SHORTEN_ADDITIONAL_BATTLE_LIST_RET,0

  LOAD_STR_SPRINTF:
  ldr r1,=LOAD_STR
  b LOAD_STR_SPRINTF_RET
  DELETE_STR_SPRINTF:
  ldr r1,=DELETE_STR
  b DELETE_STR_SPRINTF_RET
  OVERWRITE_STR_SPRINTF:
  ldr r1,=OVERWRITE_STR
  b OVERWRITE_STR_SPRINTF_RET
  GAINED_SPRINTF:
  mov r2,r3
  ldr r3,[r13]
  ldr r1,[r13,0x4]
  str r1,[r13]
  ldr r1,=GAINED_SPRINTF_STR
  b sprintf
  .pool

  .macro get_long_item_name
  push {r0-r2}
  ldr r0,=0x0205d170
  ldr r0,[r0]
  ldr r0,[r0]
  ;Calling this function with that memory address we can retrieve the original long name
  bl 0x0203dd2c
  str r0,[r13,0xc]
  pop {r0-r2}
  .endmacro

  ;For these 2 strings we need to check an address, it's 0 for buying or 1 for selling
  BUY_STR_SPRINTF:
  ldr r1,=0x0221026c
  ldr r1,[r1]
  cmp r1,0x0
  ldr r1,=BUY_STR
  beq @@ret
  ldr r1,=SELL_STR
  @@ret:
  get_long_item_name
  b BUY_STR_SPRINTF_RET

  BUY_CONFIRM_STR_SPRINTF:
  ldr r1,=0x0221026c
  ldr r1,[r1]
  cmp r1,0x0
  ldr r1,=BUY_CONFIRM_STR
  beq @@ret
  ldr r1,=SELL_CONFIRM_STR
  @@ret:
  get_long_item_name
  b BUY_CONFIRM_STR_SPRINTF_RET

  EQUIP_CONFIRM_STR_SPRINTF:
  ldr r1,=EQUIP_CONFIRM_STR
  get_long_item_name
  b EQUIP_CONFIRM_STR_SPRINTF_RET

  EQUIP_SELECT_STR_SPRINTF:
  ldr r1,=EQUIP_SELECT_STR
  get_long_item_name
  b EQUIP_SELECT_STR_SPRINTF_RET

  EQUIP_STR_SPRINTF:
  ldr r1,=EQUIP_STR
  b EQUIP_STR_SPRINTF_RET
  .pool

  KUMITE_SIZE:
  mov r1,0xe
  strb r1,[r0,0x0]
  mov r1,0xc
  b KUMITE_SIZE_RET

  HOT_SPRINGS_SIZE:
  ldr r0,=0x2cb
  b HOT_SPRINGS_SIZE_RET
  .pool

  HOT_SPRINGS_START_SIZE:
  str r1,[sp]
  mov r1,0x2
  b HOT_SPRINGS_START_SIZE_RET

  HOT_SPRINGS_START_SIZE2:
  sub r1,r1,0x2
  mov r0,0x1
  b HOT_SPRINGS_START_SIZE2_RET

  SUMMONING_SHEET_SIZE:
  mov r2,0xf
  strb r2,[r0,0x0]
  mov r2,0xc
  b SUMMONING_SHEET_SIZE_RET

  SWAP_HEADER_IMG:
  cmp r2,0xd
  bne @@return
  mov r12,r3
  ;Swap Status (4) with Weapon (7)
  cmp r12,0x4
  moveq r3,0x7
  cmp r12,0x7
  moveq r3,0x4
  ;Swap Formation (5) with Reward (c)
  cmp r12,0x5
  moveq r3,0xc
  cmp r12,0xc
  moveq r3,0x5
  ;Swap Hot Springs (a) with VS Mode (e)
  cmp r12,0xa
  moveq r3,0xe
  cmp r12,0xe
  moveq r3,0xa
  @@return:
  mov r12,0x0
  bx lr

  MOVE_RYO_RIGHT:
  mov r3,0
  add r0,r0,2
  bx lr

  STRCAT_TWEAK:
  ldr r0,=0x020c0344
  ldr r1,=0x0208c53c
  bl strcat
  pop {r0,r1}
  bl strcat
  pop {r4,lr}
  bx lr
  .pool

  PRINT_PARTY_WRAPPER:
  push {r0-r1,lr}
  push {r0-r1}
  load_vwf_data r0
  mov r1,0x1
  strb r1,[r0,VWF_BG_TYPE]
  pop {r0-r1}
  bl print_string
  load_vwf_data r0
  mov r1,0x0
  strb r1,[r0,VWF_BG_TYPE]
  pop {r0-r1,lr}
  bx lr
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
  mov r0,0x3
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
  mov r0,0x2
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

  ;Hook before a dialog line is prepared to clean VWF
  .org 0x02028838
  bl VWF_DIALOG_PREPARE

  ;Hook when a dialog line is prepared for printing to check it
  .org 0x02026440
  bl VWF_DIALOG_CHECK

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
  ;Shorten equip names in Equip menu when changing a slot
  .org 0x0205346c
  b SHORTEN_EQUIP_LIST
  SHORTEN_EQUIP_LIST_RET:
  ;Shorten equip names in Status menu
  .org 0x02058600
  bl SHORTEN_STATUS_EQUIP
  .org 0x02058688
  bl SHORTEN_STATUS_EQUIP
  .org 0x02058718
  bl SHORTEN_STATUS_EQUIP
  ;Shorten jutsu list in Status menu
  .org 0x0205826c
  b SHORTEN_STATUS_JUTSU_LIST
  SHORTEN_STATUS_JUTSU_LIST_RET:
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
  ;Shorten wifi trade window
  .org 0x0203ee64
  bl SHORTEN_WIFI_TRADE
  ;Shorten equip name in window after "Who will equip x" after purchasing
  .org 0x0205b8b4
  bl SHORTEN_WHO_WILL_EQUIP
  ;Shorten valuables window
  .org 0x020389ac
  bl SHORTEN_VALUABLES
  ;Shorten jutsu name in Jutsu menu when using one
  .org 0x020569a0
  bl SHORTEN_JUTSU_USE
  ;Shorten item/jutsu name in battle
  .org 0x0202f114
  b SHORTEN_BATTLE_LIST
  SHORTEN_BATTLE_LIST_RET:
  ;Shorten additional jutsu window in battle
  .org 0x0202f21c
  b SHORTEN_ADDITIONAL_BATTLE_LIST
  SHORTEN_ADDITIONAL_BATTLE_LIST_RET:
  ;Wrap the print_string function called by print_list
  .org 0x020292b8
  bl SHORTEN_PRINT_LIST

  ;Change save/load strings to move sprintf parameters
  .org 0x02073260
  b LOAD_STR_SPRINTF
  LOAD_STR_SPRINTF_RET:
  .org 0x02073824
  b DELETE_STR_SPRINTF
  DELETE_STR_SPRINTF_RET:
  .org 0x02073528
  b OVERWRITE_STR_SPRINTF
  OVERWRITE_STR_SPRINTF_RET:

  ;Change item-related strings to move sprintf parameters
  .org 0x0205cc24
  b BUY_STR_SPRINTF
  BUY_STR_SPRINTF_RET:
  .org 0x0205ca18
  b BUY_CONFIRM_STR_SPRINTF
  BUY_CONFIRM_STR_SPRINTF_RET:
  .org 0x0205cd98
  b EQUIP_CONFIRM_STR_SPRINTF
  EQUIP_CONFIRM_STR_SPRINTF_RET:
  .org 0x0205ce90
  b EQUIP_SELECT_STR_SPRINTF
  EQUIP_SELECT_STR_SPRINTF_RET:
  .org 0x0205cfdc
  b EQUIP_STR_SPRINTF
  EQUIP_STR_SPRINTF_RET:

  ;Change chemistry string pointers
  .org 0x0208d8fc
  dw CHEMISTRY_UP_STR
  dw CHEMISTRY_DOWN_STR
  ;and the sprintf order/parameters
  .org 0x020383e4
  ldr r1,[r1,r3,lsl 0x2]
  .skip 4
  nop

  ;Wrap print_string for party members to fix issue
  .org 0x0203b390
  bl PRINT_PARTY_WRAPPER

  ;Swap "[name]　をふっかつさせます" with "Revive [name]"
  .org 0x0202cdec
  .area 12*4
  ;If r4 is 0, this is just a normal strcpy and we can return
  cmp r4,0x0
  bleq strcpy
  cmp r4,0x0
  popeq {r4,lr}
  bxeq lr
  ;Otherwise, r0 is a pointer to the buffer, r1 is the character name and r4 is the "Revive" line
  ;Normally the game does a strcat of Name+Japanese space, and then another strcat of the result + Revive
  ;In English we just need "Revive name" so we can just do a single strcat after copying revive to the buffer
  push {r0,r1}
  mov r1,r4
  bl strcpy
  b STRCAT_TWEAK
  .pool
  .endarea

  ;Change the strcat space to an ASCII one
  .org 0x0208c53c
  .asciiz " "

  ;Use a different strlen function for spacing some strings
  .org 0x02029274
  bl STRLEN_VWF
  ;Use the same function for the map text
  .org 0x0206f840
  bl STRLEN_VWF
  .org 0x0206f88c
  bl STRLEN_VWF
  .org 0x0206fa10
  bl STRLEN_VWF
  .org 0x0206fa5c
  bl STRLEN_VWF
  .org 0x0206fcec
  bl STRLEN_VWF
  .org 0x0206fd38
  bl STRLEN_VWF

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

  ;Make the hot springs menu box bigger
  .org 0x020793bc
  ;mov r2,0x9
  mov r2,0xb
  ;Move the hot springs menu box left
  .org 0x0200b218
  ;mov r1,0x16
  mov r1,0x14

  ;Move the hot springs box left and make it bigger
  .org 0x02062f2c
  ;mov r1,0xe
  mov r1,0xd
  .skip 4
  ;mov r3,0x11
  mov r3,0x13
  ;Move the left and right arrows
  .org 0x0206302c
  ;mov r0,0xe
  mov r0,0xd
  .skip 4*4
  ;mov r0,0x1d
  mov r0,0x1e
  ;Move the character names columns
  .org 0x02062fc0
  ;mov r1,0x7
  mov r1,0x8
  .org 0x02062fd8
  ;add r1,r1,0x11
  add r1,r1,0xf
  ;Move the character arrows
  .org 0x02062e98
  ;mov r0,0x38
  mov r0,0x40
  .org 0x02062eb4
  ;add r1,r2,0x78
  add r1,r2,0x6b
  ;Move the "List" background left
  .org 0x02063070
  ;mov r1,0x8
  mov r1,0x7
  ;Move the "List" text left
  .org 0x0206313c
  ;.dw 0x2a9
  .dw 0x2a8
  ;Move the numbers
  .org 0x0206314c
  ;.dw 0x2ca
  .dw 0x2c9
  ;.dw 0x2cb
  .dw 0x2ca
  .org 0x02063100
  ;mov r0,0x2cc
  b HOT_SPRINGS_SIZE
  HOT_SPRINGS_SIZE_RET:
  ;Move press start bg left
  .org 0x02062c28
  b HOT_SPRINGS_START_SIZE
  HOT_SPRINGS_START_SIZE_RET:
  .org 0x02062c3c
  ;mov r3,0xa
  mov r3,0xb
  ;Move the text left
  .org 0x02062c68
  ;mov r1,0x1
  b HOT_SPRINGS_START_SIZE2
  HOT_SPRINGS_START_SIZE2_RET:
  
  ;Move the "木ノ葉おんせん" text left
  .org 0x02062aa8
  ;mov r1,0x83
  mov r1,0x81
  ;Move the character names left
  .org 0x02062a18
  ;add r1,r7,0x1
  mov r1,r7

  ;Move the "火影はおまえだ" text left
  .org 0x020625f8
  ;mov r1,r1,lsl 0x10
  sub r1,r1,0x4
  .skip 8
  ;mov r1,r1,lsr,0x10
  nop

  ;Make the kumite box bigger
  .org 0x0207983c
  ;strb r1,r0[0x0]
  b KUMITE_SIZE
  KUMITE_SIZE_RET:
  ;Move the kumite box left
  .org 0x0200b5d0
  ;mov r1,0x14
  mov r1,0x12

  ;Move Kumite best record text right
  .org 0x02064228
  ;mov r1,0x78
  mov r1,0x79
  ;Move Kumite best record number left
  .org 0x02064294
  ;mov r0,0xe0
  mov r0,0xd8
  ;Move Kumite best record "Wins" left
  .org 0x02064280
  ;mov r1,0x9d
  mov r1,0x9c

  ;Move Kumite "New record achieved" text right
  .org 0x020687b4
  ;.dw 0x186
  .dw 0x187
  ;Move Kumite "New record achieved" number left
  .org 0x0206876c
  ;mov r0,0xe0
  mov r0,0xd8
  ;Move Kumite "New record achieved" "Wins" left
  .org 0x020687bc
  ;.dw 0x17d
  .dw 0x17c

  ;Swap battle number in Kumite battle
  .org 0x02014e50
  ;mov r1,0x26
  mov r1,0x29
  .org 0x02014e6c
  ;mov r1,0x2a
  mov r1,0x26

  ;Make the summoning sheet box bigger
  .org 0x02079500
  ;strb r2,r0[0x0]
  b SUMMONING_SHEET_SIZE
  SUMMONING_SHEET_SIZE_RET:
  ;Move the summoning sheet box left
  .org 0x0200b404
  ;mov r1,0x14
  mov r1,0x11

  ;Make the formation textbox bigger
  .org 0x0205a8fc
  ;mov r1,0xd
  mov r1,0xf

  ;Tweak Members screen
  ;Move the window left
  .org 0x0208eb28
  ;db 0x11
  db 0xe
  ;Make it bigger
  .org 0x02057e9c
  ;mov r3,0xe
  mov r3,0x12
  ;Move the arrow right
  .org 0x02057f00
  ;add r1,r1,0x6
  add r1,r1,0x8
  ;Move the second name right
  .org 0x02057f34
  ;add r0,r3,0x8
  add r0,r3,0xa

  ;Move money left 1 tile
  .org 0x0203bbf8
  ;mov r1,0x12
  mov r1,0x11
  ;Move Ryo a bit to the right
  .org 0x0203b684
  bl MOVE_RYO_RIGHT
  ;Same but for the weapon/armor shop
  .org 0x0207a334
  ;mov r1,0x12
  mov r1,0x11
  .org 0x02079ce0
  bl MOVE_RYO_RIGHT

  ;Note: change text position by 1 for every 8 value
  ;Move battle reward turns left
  .org 0x02068fdc
  ;mov r0,0xe8
  mov r0,0xd0
  ;Move battle reward turns text left
  .org 0x02069154
  ;.dw 0x13e
  .dw 0x13b
  ;Move battle reward ryo left
  .org 0x02069060
  ;mov r0,0xe8
  mov r0,0xd0
  ;Move battle reward ryo text left
  .org 0x02068fc8
  ;mov r1,0xbe
  mov r1,0xbb
  ;Shorten reward item names
  .org 0x0206912c
  bl SHORTEN_ITEM_NAME_REWARD

  ;Remove character name from "[name] gained [skill]!" text
  .org 0x020698bc
  bl GAINED_SPRINTF

  ;Fix levelup stats when stats are >99
  ;Make the numbers bigger
  .org 0x02068c14
  ;ldr r2,[r13,0x14]
  mov r2,0x4
  .org 0x02068c24
  ;ldr r2,[r13,0x14]
  mov r2,0x4
  ;Move everything left
  .org 0x02068c44
  ;add r1,r4,0x18
  add r1,r4,0x16
  ;Move the arrow further left
  .org 0x02068c60
  ;add r0,r4,0x1b
  add r0,r4,0x1a

  ;Swap header images
  .org 0x02036694
  bl SWAP_HEADER_IMG

  ;Move Searching for a partner wifi text left
  .org 0x0203fca4
  ;mov r0,0xa
  mov r0,0x7
  ;Move opponent accepted wifi text left
  .org 0x0204109c
  ;mov r0,0xb
  mov r0,0x7
  .org 0x0203ff2c
  mov r0,0x7

  ;Move sound test left arrow more left
  .org 0x0207df20
  ;mov r0,r8 (0x5)
  mov r0,0x3
  ;Move sound test character name left
  .org 0x0207de4c
  ;add r1,r1,0x8
  add r1,r1,0x6
.close
