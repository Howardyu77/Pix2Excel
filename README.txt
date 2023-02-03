Donwload the file from this link: https://github.com/Howardyu77/Pix2Excel/releases/tag/v1
1. Make sure you have python installed locally.
2. Type cmd in the address bar of the window of this folder and hit return (that will launch the terminal already set to this current directory).
3. copy and paste the belowed expression into the cmd window.
	pip install -r requirements.txt
4. This script does not work with too complex maths formulas yet, due to the difference between latex, python, VBA syntax. The following maths functions are known to be problematic
   [log/ln, integration, derivative, sum]
5. Prior to uploading formula to Excel, you have to open the workbook, to which you want the formula be uploaded.
6. Once the formula is uploaded, click on the fx botton to the left of the Formula bar in Excel --> select a category --> select "User Defined" --> Ok
7. At the formula bar, type the name you given to the function, and it will show up. After selecting the function, hit ctrl+shift+A, then the variable names will show up,too.
