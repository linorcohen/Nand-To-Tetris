// This file is part of nand2tetris, as taught in The Hebrew University, and
// was written by Aviv Yaish. It is an extension to the specifications given
// [here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
// as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
// Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).

// The program should swap between the max. and min. elements of an array.
// Assumptions:
// - The array's start address is stored in R14, and R15 contains its length
// - Each array value x is between -16384 < x < 16384
// - The address in R14 is at least >= 2048
// - R14 + R15 <= 16383
//
// Requirements:
// - Changing R14, R15 is not allowed.

// i = 0
@i
M=0

// biggest = R14 + i (address)
    @i
    D=M
    @R14
    D=D+M
    @biggest
    M=D

// smallest = R14 + i (address)
    @i
    D=M
    @R14
    D=D+M
    @smallest
    M=D

(LOOP)
// if (i == R15) goto END
    @i
    D=M
    @R15
    D=D-M
    @END_LOOP
    D;JEQ

// if (array[i] > biggest)
    @i
    D=M
    @R14
    D=D+M
    A=D //load address for R14 + i
    D=M //load value for R14 + i
    @biggest
    A=M //load address for biggest
    D=D-M 
    @SET_MAX
    D;JGT

// if (array[i] < smallest)
    @i
    D=M
    @R14
    D=D+M
    A=D //load address for R14 + i
    D=M //load value for R14 + i
    @smallest
    A=M //load address for biggest
    D=D-M 
    @SET_MIN
    D;JLT

    @CONTINUE
    0;JMP

(SET_MIN)
//smallest = array[i].address
    @i
    D=M
    @R14
    D=D+M
    @smallest
    M=D
    @CONTINUE
    0;JMP


(SET_MAX)
//biggest = array[i].address
    @i
    D=M
    @R14
    D=D+M
    @biggest
    M=D

(CONTINUE)
//i = i + 1
    @i
    M=M+1
    @LOOP
    0;JMP

(END_LOOP)

// temp = min
@smallest
A=M
D=M
@R0
M=D
// min = max
@biggest
A=M
D=M
@smallest
A=M
M=D
// max = temp
@R0
D=M
@biggest
A=M
M=D

(END)
@END
0;JMP