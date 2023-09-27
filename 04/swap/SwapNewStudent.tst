// This file is part of nand2tetris, as taught in The Hebrew University, and
// was written by Aviv Yaish. It is an extension to the specifications given
// [here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
// as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
// Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).

load Swap.asm,
output-file SwapNewStudent.out,
compare-to SwapNewStudent.cmp,
output-list RAM[14]%D3.6.3 RAM[15]%D3.6.3 RAM[2048]%D3.6.3 RAM[2049]%D3.6.3 RAM[2050]%D3.6.3 RAM[2051]%D3.6.3 RAM[2052]%D3.6.3 RAM[2053]%D3.6.3;


// test with array of {0}, length of 1
set PC 0,
set RAM[2048] 0,
set RAM[2049] 0,
set RAM[2050] 0,
set RAM[2051] 0,
set RAM[2052] 0,
set RAM[2053] 0,
set RAM[14] 2048,
set RAM[15] 1;
repeat 200 {
  ticktock;
}
output;

// test with array of {-1,1}, length of 2
set PC 0,
set RAM[2048] -1,
set RAM[2049] 1,
set RAM[2050] 0,
set RAM[2051] 0,
set RAM[2052] 0,
set RAM[2053] 0,
set RAM[14] 2048,
set RAM[15] 2;
repeat 200 {
  ticktock;
}
output;

// test with empty array, length of 0
set PC 0,
set RAM[2048] -1,
set RAM[2049] 1,
set RAM[2050] 0,
set RAM[2051] 0,
set RAM[2052] 0,
set RAM[2053] 0,
set RAM[14] 2048,
set RAM[15] 0;
repeat 200 {
  ticktock;
}
output;

// test with array of {2,3,0,5,1,4}, length of 6
set PC 0,
set RAM[2048] 2,
set RAM[2049] 3,
set RAM[2050] 0,
set RAM[2051] 5,
set RAM[2052] 1,
set RAM[2053] 4,
set RAM[14] 2048,
set RAM[15] 6;
repeat 600 {
  ticktock;
}
output;

// test with array of {2,3,-16383,16383,1,4}, length of 6
set PC 0,
set RAM[2048] 2,
set RAM[2049] 3,
set RAM[2050] -16383,
set RAM[2051] 16383,
set RAM[2052] 1,
set RAM[2053] 4,
set RAM[14] 2048,
set RAM[15] 6;
repeat 600 {
  ticktock;
}
output;

// test with array of {0,1,2,3,4,5}, length of 6
set PC 0,
set RAM[2047] -1,
set RAM[2048] 0,
set RAM[2049] 1,
set RAM[2050] 2,
set RAM[2051] 3,
set RAM[2052] 4,
set RAM[2053] 5,
set RAM[14] 2048,
set RAM[15] 6;
repeat 600 {
  ticktock;
}
output;

// test with empty array, length of -1
set PC 0,
set RAM[2048] -1,
set RAM[2049] 1,
set RAM[2050] 0,
set RAM[2051] 0,
set RAM[2052] 0,
set RAM[2053] 0,
set RAM[14] 2048,
set RAM[15] -1;
repeat 200 {
  ticktock;
}
output;