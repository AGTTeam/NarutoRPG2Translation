.nds

.open "NarutoRPG2jp/repack/arm9.bin",0x1ff9000 - 0x92fc0
  .orga 0x92fc0
  .area 0x1200

  UNLOCK_STR:
  .db 0x10 :: .db 0x22 :: .sjis "「ここは　"
  UNLOCK2_STR:
  .db 0x10 :: .db 0x24 :: .sjis "「ここでは"
  .align

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
  ;Check if we're matching a specific line
  push {r1-r4,lr}
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
  .endarea
.close

.open "NarutoRPG2jp/repack/arm9.bin",0x02000000
  ;Hook when a dialog line is prepared for printing to check it
  .org 0x02026440
  bl VWF_DIALOG_CHECK
.close
