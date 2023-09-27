// push constant 17
@17
D=A
@SP
A=M
M=D
@SP
M=M+1
// push constant 17
@17
D=A
@SP
A=M
M=D
@SP
M=M+1
// eq
@SP
M=M-1
A=M
D=M
@NEG_1
D;JLT
@SP
A=M-1
D=M
@POS_NEG_1
D;JLT
@SAME_SIGN_1
0;JMP

(NEG_1)
@SP
A=M-1
D=M
@SAME_SIGN_1
D;JLT
D=1
@CHECK_COMMAND_1
0;JMP

(POS_NEG_1)
D=-1
@CHECK_COMMAND_1
0;JMP

(SAME_SIGN_1)
@SP
A=M
D=M
@SP
A=M-1
D=M-D
(CHECK_COMMAND_1)
@TRUE_EQ_1
D;JEQ
@SP
A=M-1
M=0
@EQ_1
0;JMP

(TRUE_EQ_1)
@SP
A=M-1
M=-1
(EQ_1)
// push constant 17
@17
D=A
@SP
A=M
M=D
@SP
M=M+1
// push constant 16
@16
D=A
@SP
A=M
M=D
@SP
M=M+1
// eq
@SP
M=M-1
A=M
D=M
@NEG_2
D;JLT
@SP
A=M-1
D=M
@POS_NEG_2
D;JLT
@SAME_SIGN_2
0;JMP

(NEG_2)
@SP
A=M-1
D=M
@SAME_SIGN_2
D;JLT
D=1
@CHECK_COMMAND_2
0;JMP

(POS_NEG_2)
D=-1
@CHECK_COMMAND_2
0;JMP

(SAME_SIGN_2)
@SP
A=M
D=M
@SP
A=M-1
D=M-D
(CHECK_COMMAND_2)
@TRUE_EQ_2
D;JEQ
@SP
A=M-1
M=0
@EQ_2
0;JMP

(TRUE_EQ_2)
@SP
A=M-1
M=-1
(EQ_2)
// push constant 16
@16
D=A
@SP
A=M
M=D
@SP
M=M+1
// push constant 17
@17
D=A
@SP
A=M
M=D
@SP
M=M+1
// eq
@SP
M=M-1
A=M
D=M
@NEG_3
D;JLT
@SP
A=M-1
D=M
@POS_NEG_3
D;JLT
@SAME_SIGN_3
0;JMP

(NEG_3)
@SP
A=M-1
D=M
@SAME_SIGN_3
D;JLT
D=1
@CHECK_COMMAND_3
0;JMP

(POS_NEG_3)
D=-1
@CHECK_COMMAND_3
0;JMP

(SAME_SIGN_3)
@SP
A=M
D=M
@SP
A=M-1
D=M-D
(CHECK_COMMAND_3)
@TRUE_EQ_3
D;JEQ
@SP
A=M-1
M=0
@EQ_3
0;JMP

(TRUE_EQ_3)
@SP
A=M-1
M=-1
(EQ_3)
// push constant 892
@892
D=A
@SP
A=M
M=D
@SP
M=M+1
// push constant 891
@891
D=A
@SP
A=M
M=D
@SP
M=M+1
// lt
@SP
M=M-1
A=M
D=M
@NEG_4
D;JLT
@SP
A=M-1
D=M
@POS_NEG_4
D;JLT
@SAME_SIGN_4
0;JMP

(NEG_4)
@SP
A=M-1
D=M
@SAME_SIGN_4
D;JLT
D=1
@CHECK_COMMAND_4
0;JMP

(POS_NEG_4)
D=-1
@CHECK_COMMAND_4
0;JMP

(SAME_SIGN_4)
@SP
A=M
D=M
@SP
A=M-1
D=M-D
(CHECK_COMMAND_4)
@TRUE_LT_4
D;JLT
@SP
A=M-1
M=0
@LT_4
0;JMP

(TRUE_LT_4)
@SP
A=M-1
M=-1
(LT_4)
// push constant 891
@891
D=A
@SP
A=M
M=D
@SP
M=M+1
// push constant 892
@892
D=A
@SP
A=M
M=D
@SP
M=M+1
// lt
@SP
M=M-1
A=M
D=M
@NEG_5
D;JLT
@SP
A=M-1
D=M
@POS_NEG_5
D;JLT
@SAME_SIGN_5
0;JMP

(NEG_5)
@SP
A=M-1
D=M
@SAME_SIGN_5
D;JLT
D=1
@CHECK_COMMAND_5
0;JMP

(POS_NEG_5)
D=-1
@CHECK_COMMAND_5
0;JMP

(SAME_SIGN_5)
@SP
A=M
D=M
@SP
A=M-1
D=M-D
(CHECK_COMMAND_5)
@TRUE_LT_5
D;JLT
@SP
A=M-1
M=0
@LT_5
0;JMP

(TRUE_LT_5)
@SP
A=M-1
M=-1
(LT_5)
// push constant 891
@891
D=A
@SP
A=M
M=D
@SP
M=M+1
// push constant 891
@891
D=A
@SP
A=M
M=D
@SP
M=M+1
// lt
@SP
M=M-1
A=M
D=M
@NEG_6
D;JLT
@SP
A=M-1
D=M
@POS_NEG_6
D;JLT
@SAME_SIGN_6
0;JMP

(NEG_6)
@SP
A=M-1
D=M
@SAME_SIGN_6
D;JLT
D=1
@CHECK_COMMAND_6
0;JMP

(POS_NEG_6)
D=-1
@CHECK_COMMAND_6
0;JMP

(SAME_SIGN_6)
@SP
A=M
D=M
@SP
A=M-1
D=M-D
(CHECK_COMMAND_6)
@TRUE_LT_6
D;JLT
@SP
A=M-1
M=0
@LT_6
0;JMP

(TRUE_LT_6)
@SP
A=M-1
M=-1
(LT_6)
// push constant 32767
@32767
D=A
@SP
A=M
M=D
@SP
M=M+1
// push constant 32766
@32766
D=A
@SP
A=M
M=D
@SP
M=M+1
// gt
@SP
M=M-1
A=M
D=M
@NEG_7
D;JLT
@SP
A=M-1
D=M
@POS_NEG_7
D;JLT
@SAME_SIGN_7
0;JMP

(NEG_7)
@SP
A=M-1
D=M
@SAME_SIGN_7
D;JLT
D=1
@CHECK_COMMAND_7
0;JMP

(POS_NEG_7)
D=-1
@CHECK_COMMAND_7
0;JMP

(SAME_SIGN_7)
@SP
A=M
D=M
@SP
A=M-1
D=M-D
(CHECK_COMMAND_7)
@TRUE_GT_7
D;JGT
@SP
A=M-1
M=0
@GT_7
0;JMP

(TRUE_GT_7)
@SP
A=M-1
M=-1
(GT_7)
// push constant 32766
@32766
D=A
@SP
A=M
M=D
@SP
M=M+1
// push constant 32767
@32767
D=A
@SP
A=M
M=D
@SP
M=M+1
// gt
@SP
M=M-1
A=M
D=M
@NEG_8
D;JLT
@SP
A=M-1
D=M
@POS_NEG_8
D;JLT
@SAME_SIGN_8
0;JMP

(NEG_8)
@SP
A=M-1
D=M
@SAME_SIGN_8
D;JLT
D=1
@CHECK_COMMAND_8
0;JMP

(POS_NEG_8)
D=-1
@CHECK_COMMAND_8
0;JMP

(SAME_SIGN_8)
@SP
A=M
D=M
@SP
A=M-1
D=M-D
(CHECK_COMMAND_8)
@TRUE_GT_8
D;JGT
@SP
A=M-1
M=0
@GT_8
0;JMP

(TRUE_GT_8)
@SP
A=M-1
M=-1
(GT_8)
// push constant 32766
@32766
D=A
@SP
A=M
M=D
@SP
M=M+1
// push constant 32766
@32766
D=A
@SP
A=M
M=D
@SP
M=M+1
// gt
@SP
M=M-1
A=M
D=M
@NEG_9
D;JLT
@SP
A=M-1
D=M
@POS_NEG_9
D;JLT
@SAME_SIGN_9
0;JMP

(NEG_9)
@SP
A=M-1
D=M
@SAME_SIGN_9
D;JLT
D=1
@CHECK_COMMAND_9
0;JMP

(POS_NEG_9)
D=-1
@CHECK_COMMAND_9
0;JMP

(SAME_SIGN_9)
@SP
A=M
D=M
@SP
A=M-1
D=M-D
(CHECK_COMMAND_9)
@TRUE_GT_9
D;JGT
@SP
A=M-1
M=0
@GT_9
0;JMP

(TRUE_GT_9)
@SP
A=M-1
M=-1
(GT_9)
// push constant 57
@57
D=A
@SP
A=M
M=D
@SP
M=M+1
// push constant 31
@31
D=A
@SP
A=M
M=D
@SP
M=M+1
// push constant 53
@53
D=A
@SP
A=M
M=D
@SP
M=M+1
// add
@SP
M=M-1
A=M
D=M
A=A-1
D=M+D
M=D
// push constant 112
@112
D=A
@SP
A=M
M=D
@SP
M=M+1
// sub
@SP
M=M-1
A=M
D=M
A=A-1
D=M-D
M=D
// neg
@SP
A=M-1
M=-M
// and
@SP
M=M-1
A=M
D=M
A=A-1
M=D&M
// push constant 82
@82
D=A
@SP
A=M
M=D
@SP
M=M+1
// or
@SP
M=M-1
A=M
D=M
A=A-1
M=D|M
// not
@SP
A=M-1
M=!M
