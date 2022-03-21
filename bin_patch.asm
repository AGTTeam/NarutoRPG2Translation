.nds

.open "NarutoRPG2Data/repack/arm9.bin",0x02000000
  .org 0x0208a2e0
  .area 0x350
  .align

  ;ASCII to SJIS lookup table
  SJIS_LOOKUP:
  .sjisn "　！”＃＄％＆"
  ;Fix ' since it doesn't get encoded correctly
  .db 0x81 :: .db 0x66
  .sjisn "（）＊＋，―．／０１２３４５６７８９：；〈＝〉？＠"
  .sjisn "ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ［＼］＾＿｀"
  .sjisn "ａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ｛｜｝～"
  .align

  IS_ASCII:
  .dw 0

  ;r0 = str ptr
  ;r3 = first byte
  ;r2 = second byte
  CONVERT_ASCII:
  mov r1,0x0
  push {r0-r1}
  ;Set IS_ASCII to 0 and check
  ldr r0,=IS_ASCII
  cmp r3,0x7f
  strge r1,[r0]
  bge @@return
  ;Return the SJIS character
  ldr r2,=SJIS_LOOKUP
  sub r3,r3,0x20
  lsl r3,r3,0x1
  add r2,r2,r3
  ldrb r3,[r2]
  ldrb r2,[r2,0x1]
  ;Set IS_ASCII to 1
  mov r1,0x1
  str r1,[r0]
  @@return:
  pop {r0-r1}
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

  ;Hook the function that reads characters
  .org 0x02025d50
  b CONVERT_ASCII
  CONVERT_ASCII_RET:

  ;Only move pointer by 1 if the character was ascii
  .org 0x020279f0
  b CHECK_ASCII
  CHECK_ASCII_RET:

  .endarea
.close
