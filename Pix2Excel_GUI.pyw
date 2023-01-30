
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
from pix2tex import cli as pix2tex
from PIL import Image
import sys 
sys.path.append("C:\\Python310\Lib\site-packages")

model = pix2tex.LatexOCR()


def simplify_latex(tex_str):
    # tex_str = tex_str.replace(" ","*")
    matches = re.findall(r"\\mathrm{(.*?)}", tex_str)
    matches = set(matches)

    matchesbf = set(re.findall(r"\\mathbf{(.*?)}", tex_str))

    tex_str = tex_str.replace("\\mathrm{", "")
    tex_str = tex_str.replace("\\mathbf{", "")

    for letter in matches:
        tex_str = tex_str.replace(letter+"}",letter)

    for letter in matchesbf:
        tex_str = tex_str.replace(letter+"}",letter)

    tex_str = tex_str.replace("\\bf", "")
    tex_str = tex_str.replace("\\bigr", "")
    tex_str = tex_str.replace("\\bigl", "")
    tex_str = tex_str.replace("\\big", "")
    return tex_str

def python2vba(math_str):
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
    for letter in ("C", "O", "S", "I", "N", "E","Q"):
        new_letter = "L_" + letter.lower()
        tex_str = tex_str.replace(new_letter,letter)
    return tex_str
    
def print_latex(tex_str):
    display(Math(tex_str))



def pix2latex(path):
    img = Image.open(path)
    str_formula = model(img)
    str_formula = simplify_latex(str_formula)
    return str_formula

def upload_to_excel(str_UDF):
    xl = win32.gencache.EnsureDispatch('Excel.Application')
    xl.Visible = True
    ss = xl.ActiveWorkbook
    sh = ss.ActiveSheet
    xlmodule = ss.VBProject.VBComponents.Add(1)  # vbext_ct_StdModule
    xlmodule.CodeModule.AddFromString(str_UDF)

def latex2excel(str_formula,str_func_name):

    str_function = "Function "
    str_end_function = "End Function"
    str_formula = replace_speical_vars(str_formula)
    sympy_formula = latex2sympy(str_formula)
    sym = str(tuple(sympy_formula.free_symbols))

    
    str_formula = undo_special_vars(str_formula)
    sym = undo_special_vars(sym)

    sym = python2vba(sym)
    str_formula = python2vba(str(sympy_formula))

    str_UDF = str_function + str_func_name + sym + "\n" + "\t" + str_func_name + "=" + str_formula + "\n" + str_end_function
    upload_to_excel(str_UDF)


# VARS CONSTS:

# New figure and plot variables so we can manipulate them

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
    # New Button (check the layout) and event catcher for the plot update
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
            updateChart(str_latex)
    elif event == 'Regenerate Latex':
        if len(values['Input'])!=0 and switch == 0:
            print(values['Input'])
            input_str = values['Input'].replace("\r","")
            drawChart(values['Input'])
        elif len(values['Input'])==0 and switch != 0:
            str_latex = pix2latex(path)
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