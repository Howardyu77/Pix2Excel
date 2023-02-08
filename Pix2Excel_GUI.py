
import PySimpleGUI as sg
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from latex2sympy2 import latex2sympy, latex2latex
import xlwings as xw
import win32com.client as win32
import comtypes, comtypes.client
import xlsxwriter
import re
import matplotlib.pyplot as plt
from IPython.display import display, Math
from PIL import Image
import sys 
from pix2tex import cli as pix2tex
model = pix2tex.LatexOCR()
#sys.path.append("C:\\Python310\Lib\site-packages")



def remove_tex_sym_format(tex_str, format):
    #this function identify and remove speical latex fonts symtax 
    # print(format)
    pattern = r"\\" + format + r"{(.*?)}"
    
    pattern1 = "\\" + format + "{"
    # print(pattern)
    # print(pattern1)
    matches = re.findall(pattern, tex_str)
    # print(matches)
    matches = set(matches)

    tex_str = tex_str.replace(pattern1, "")
    # print(tex_str)
    for letter in matches:
        tex_str = tex_str.replace(letter+"}",letter)
    # print(tex_str)
    return tex_str

def simplify_latex(tex_str):
    #sometimes latex will have special fonts for maths symbols, remove them to avoid complications.
    format_to_remove = ['mathbf','mathrm',"mathit",'mathnormal','mathcal','mathscr','mathbb','varmathbb','mathbbm','mathbbmss','mathbbmtt','mathds','mathbbb','mathfrak']
    
    for format in format_to_remove:
        tex_str = remove_tex_sym_format(tex_str, format)

    tex_str = tex_str.replace("\\bf", "")
    tex_str = tex_str.replace("\\bigr", "")
    tex_str = tex_str.replace("\\bigl", "")
    tex_str = tex_str.replace("\\big", "")
    return tex_str

def python2vba(math_str):
    #convert python equation syntax into excel syntax
    math_str = math_str.replace("**"," ^ ")
    math_str = math_str.replace("sqrt","Sqr")
    math_str = math_str.replace("sin","Sin")
    math_str = math_str.replace("cos","Cos")
    math_str = math_str.replace("tan","Tan")
    math_str = math_str.replace("exp","Exp")
    math_str = math_str.replace("{","")
    math_str = math_str.replace("}","")
    math_str = math_str.replace("pi","3.1415926535897931")
    return math_str

def replace_speical_vars(tex_str): # the names C, O, S, I, N, E and Q are predefined symbols in sympy so we need to replace them first then change them back later
    for letter in ("C", "O", "S", "I", "N", "E","Q"):
        new_letter = "L_{" + letter.lower() + "}"
        tex_str = tex_str.replace(letter,new_letter)
    return tex_str

def undo_special_vars(tex_str):
    #after converting a latex equ into python syntax, recover the original charaters
    for letter in ("C", "O", "S", "I", "N", "E","Q"):
        new_letter = "L_" + letter.lower()
        tex_str = tex_str.replace(new_letter,letter)
    return tex_str
    
def print_latex(tex_str):
    display(Math(tex_str))



def pix2latex(path):
    #OCR the picture into latex
    img = Image.open(path)
    str_formula = model(img)
    str_formula = simplify_latex(str_formula)
    return str_formula

def upload_to_excel(str_UDF):
    #this function, upload the excel UDFs string into vba, so that the UDFs can be used in excel
    xl = win32.gencache.EnsureDispatch('Excel.Application')
    xl.Visible = True
    ss = xl.ActiveWorkbook
    sh = ss.ActiveSheet
    xlmodule = ss.VBProject.VBComponents.Add(1)  # vbext_ct_StdModule
    xlmodule.CodeModule.AddFromString(str_UDF)

def latex2excel(str_formula,str_func_name):
    #put everything together and generate a excel UDFs string it takes the following form
    #Function function_name(args)
    #   function's operation
    #End Function
    
    str_function = "Function "
    str_end_function = "End Function"
    str_formula = replace_speical_vars(str_formula)#pre-process latex formula strings
    sympy_formula = latex2sympy(str_formula)#convert latex to python syntax
    sym = str(tuple(sympy_formula.free_symbols))#.free_symbols returns a list of unique symbols that used in the formula, so that we can use this as UDFs' arguments

    #recover original charaters
    str_formula = undo_special_vars(str_formula)
    sym = undo_special_vars(sym)

    #convert python to excel sytax
    sym = python2vba(sym)
    str_formula = python2vba(str(sympy_formula))

    #complie excel UDFs sytax
    str_UDF = str_function + str_func_name + sym + "\n" + "\t" + str_func_name + "=" + str_formula + "\n" + str_end_function
    #send to excel
    upload_to_excel(str_UDF)



############################## Below are codes for user interface######################
#This UI is to show what is scan into latex and users need to ensure the scan latex is correct, then it can be uploaded to excel
_VARS = {'window': False,
         'fig_agg': False,
         'pltFig': False}

dataSize = 1000  # For synthetic data


def draw_figure(canvas, figure):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg


# \\  -------- PYSIMPLEGUI -------- //

AppFont = 'Any 16'
sg.theme('DarkTeal12')

#this sets the layout
layout = [[sg.Canvas(key='figCanvas')],
        [sg.Text("Select a photo: ",font=('Helvetica', 13, 'bold'),justification='left',size=(16, 1)),sg.Combo("",size=(50, 1),auto_size_text=True, key='-FILENAME-'),sg.FileBrowse('Browse', target='-FILENAME-')],
           [sg.T("Scan result in latex:",font=('Helvetica', 13, 'bold'),size=(16, 1)),sg.Multiline(size=(50,3), disabled=True, autoscroll=False, key="Output")],
          [sg.T("Latex input:",font=('Helvetica', 13, 'bold'),size=(16, 1)),sg.Input(key='Input',size=(50,5))],
          [sg.T("Function name:",font=('Helvetica', 13, 'bold'),size=(16, 1)),sg.Input(key='Functionname',size=(50,5))],
          [sg.Button('Regenerate Latex',font=('Helvetica', 13, 'bold')),sg.Button('Upload to Excel',font=('Helvetica', 13, 'bold')),sg.Button('Scan photo',font=('Helvetica', 13, 'bold'))]]

_VARS['window'] = sg.Window('Picture to excel formula',
                            layout,
                            finalize=True,
                            resizable=True,
                            location=(100, 100),
                            element_justification="Left")

# \\  -------- PYSIMPLEGUI -------- //


# \\  -------- PYPLOT -------- //


def makeSynthData():
    xData = np.random.randint(100, size=dataSize)
    yData = np.linspace(0, dataSize, num=dataSize, dtype=int)
    return (xData, yData)


def drawChart(str_latex):
    _VARS['pltFig'] = plt.figure()
    plt.clf() 
    plt.text(0,0.5,'$%s$' %str_latex,size=15)
    plt.axis('off')
    _VARS['fig_agg'] = draw_figure(
        _VARS['window']['figCanvas'].TKCanvas, _VARS['pltFig'])


# Recreate Synthetic data, clear existing figre and redraw plot.

def updateChart(str_latex):
    _VARS['fig_agg'].get_tk_widget().forget()
    dataXY = makeSynthData()
    # plt.cla()
    plt.clf()
    plt.text(0,0.5,'$%s$' %str_latex,size=15)
    plt.axis('off')
    _VARS['fig_agg'] = draw_figure(
        _VARS['window']['figCanvas'].TKCanvas, _VARS['pltFig'])

# \\  -------- PYPLOT -------- //




# MAIN LOOP
switch = 0
while True:

    
    event, values = _VARS['window'].read(timeout=200)
    path = values['-FILENAME-']
    
    if event == sg.WIN_CLOSED or event == 'Exit':
        break
    
    if event == "Scan photo" and switch==0:
        if len(values['-FILENAME-'])==0:
            sg.popup("Please select a photo first")
        else:
            str_latex = pix2latex(path)
            drawChart(str_latex)
            _VARS['window']["Output"].print(str_latex)
            switch = 1
    
    elif event == "Scan photo" and switch==1:
        if len(values['-FILENAME-'])==0:
            sg.popup("Please select a photo first")
        else:
            str_latex = pix2latex(path)
            _VARS['window']["Output"].print(str_latex)
            updateChart(str_latex)
    
    elif event == 'Regenerate Latex':
        if len(values['Output'])==0:
            if len(values['-FILENAME-'])==0:
                sg.popup("Please select a photo first")
            else:
                str_latex = pix2latex(path)
                drawChart(str_latex)
                _VARS['window']["Output"].print(str_latex)
                switch = 1
        else:
            if len(values['Input'])!=0 and switch == 0:
                print(values['Input'])
                input_str = values['Input'].replace("\r","")
                drawChart(values['Input'])
            elif len(values['Input'])==0 and switch != 0:
                str_latex = pix2latex(path)
                _VARS['window']["Output"].print(str_latex)
                updateChart(str_latex) 
            else:
                updateChart(values['Input'])
    
    elif event == 'Upload to Excel':
        if len(values['Functionname']) != 0:
            option = sg.popup_ok_cancel("Are you sure you want to upload this formula to Excel")
            if option == "OK" and len(values['Input'])==0:
                sg.popup("Please copy the scan result into the Latex input box/Or enter your own latex function")
            elif option == "OK" and len(values['Input'])!=0:
                str_formula = values['Input']
                str_func_name = values['Functionname']
                latex2excel(str_formula,str_func_name)
            else:
                sg.popup("Action aborted")
        else:
            sg.popup("Please enter a function name first")
_VARS['window'].close()
