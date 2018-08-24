#!/usr/bin/env python
# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import numpy as np
import Tkinter as tk
import tkFileDialog
from scipy.optimize import curve_fit
import pandas as pd
import tkMessageBox
import time

# Define User interface
root = tk.Tk()
root.title("Gas Mixing Furnace CO₂/CO calculator")
root.geometry("460x150")
L1 = tk.Label(root, text="Temperature [ºC]")
L1.grid(row=0, column=0)
E1 = tk.Entry(root, bd=2)
E1.grid(row=0, column=1,columnspan=2,)

L2 = tk.Label(root, text="Oxygen Fugacity [log fO₂]")
L2.grid(row=1, column=0)
E2 = tk.Entry(root, bd=2)
E2.grid(row=1, column=1,columnspan=2)

L3 = tk.Label(root, text="Time [min]")
L3.grid(row=2, column=0)
E3 = tk.Entry(root, bd=2)
E3.grid(row=2, column=1,columnspan=2)

L4 = tk.Label(root, text="T steps [ºC]")
L4.grid(row=3, column=0)
E4 = tk.Entry(root, bd=2)
E4.grid(row=3, column=1,columnspan=2)

# Button callbacks:
def start_cd():
    T_UI = map(float, E1.get().split(','))
    if len(T_UI) >= 4:
        T_UI=[273+n for n in T_UI]# C to K
        T_resolution = float(E4.get())  # C (or K - its an interval)
        T_steps = round((max(T_UI) - min(T_UI)) / T_resolution)
        T = np.linspace(min(T_UI), max(T_UI), T_steps+1)  #

        fo2_UI = map(float, E2.get().split(','))
        fo2_UI = [10 ** n for n in fo2_UI]
        abc_param=interp_fo2(T_UI,fo2_UI)
        CO2_percent = getCO2_percent(T,abc_param)
        CO2_percent = [round(n,2) for n in CO2_percent]
        fo2=func_fo2(T, *abc_param)
        plot_T_fo2_CO2(T, fo2, CO2_percent)
    else:
        tkMessageBox.showerror('Not enough data','Please insert more than 4 data points')

def export_csv():
    fpath = tkFileDialog.asksaveasfilename(initialfile="out.csv")

    T_UI = map(float, E1.get().split(','))
    T_UI = [273 + n for n in T_UI]  # C to K
    T_resolution = float(E4.get())  # C (or K - its an interval)
    T_steps = round((max(T_UI) - min(T_UI)) / T_resolution)
    T = np.linspace(min(T_UI), max(T_UI), T_steps + 1)  #
    Tc = T - 273 # K to C
    Tcorrected = Tc + (0.0825 * Tc - 55.982) # obtained from linear interpolation of data in graph(Joana's calibration). (MIDDLE FURNACE)
    # Tcorrected = Tc + (0.04792 * T - 76)  # obtained from linear interpolation of data in graph. (LAST FURNACE)

    time_UI = float(E3.get())
    t_seconds = np.linspace(0, time_UI * 60, len(T))

    fo2_UI = map(float, E2.get().split(','))
    fo2_UI = [10 ** n for n in fo2_UI]
    abc_param = interp_fo2(T_UI, fo2_UI)
    CO2_percent = getCO2_percent(T, abc_param)
    CO2_percent = [round(n, 2) for n in CO2_percent] # (MIDDLE FURNACE)
    #CO2_percent = [2*(round(n, 2)) for n in CO2_percent]  # (LAST FURNACE)

    CO_percent = [100-n for n in CO2_percent] # (MIDDLE FURNACE)
    #CO_percent = [200-n for n in CO2_percent]  # (LAST FURNACE)

    fo2 = func_fo2(T, *abc_param)

    data2export = [Tc, fo2, t_seconds, Tcorrected, CO2_percent, CO_percent]
    data2export= zip(*data2export)
    df = pd.DataFrame(data2export, columns=["T(C)", "log fo2", "time(s)", "T_corrected(C)", "CO2(%)", "CO(%)"])
    df.to_csv(fpath, index=False)

def getDatafromfile():# 1st line:T,2nd line:fO2
    fpath = tkFileDialog.askopenfilename()
    with open(fpath, "r") as filestream:
        E1.delete('0','end')
        E2.delete('0','end')
        E1.insert('0',filestream.readline())
        E2.insert('0',filestream.readline())

def clear_ui():
    E1.delete('0', 'end')
    E2.delete('0', 'end')
    E3.delete('0', 'end')
    E4.delete('0', 'end')

def quit_ui():
    root.destroy()

B1 = tk.Button(root, text="Open file", command=getDatafromfile)
B1.grid(row=0, column=3, rowspan=2,sticky='nesw')

B2 = tk.Button(root, text="Start", command=start_cd)
B2.grid(row=4, column=0,sticky='nesw')

B3 = tk.Button(root, text="Export", command=export_csv)
B3.grid(row=4, column=1,sticky='nesw')

B4 = tk.Button(root, text="Clear", command=clear_ui)
B4.grid(row=4, column=2,sticky='nesw')

B5 = tk.Button(root, text="Quit", command=quit_ui)
B5.grid(row=4, column=3,sticky='nesw')

# Functions:
def func_fo2(T, a, b, c):
    return ((a/T) + b + c * (P-1)/T)

def interp_fo2(T_UI,fo2_UI): #interpolate fo2 using input T and fo2
    abc_param, pcov = curve_fit(func_fo2, T_UI,np.log10(fo2_UI)) # fit curve to data points (T IN k fo2 in log)
    return abc_param

P = 1  # Furnace pressure (bar)
def getKp(T):
    # C02 = CO + 1/2 02
    R = 8.314  # atm.l/(mol.K)
    # CO delta g of formation
    A_CO = -214104
    B_CO = 25.2183
    C_CO = -262.1545
    delta_g0_CO = (A_CO+ (B_CO*T*np.log10(T)) +C_CO*T)/2 # J/mol
    # CO2 delta g of formation
    A_CO2 = -392647
    B_CO2 = 4.5855
    C_CO2 = -16.9762
    delta_g0_CO2=A_CO2+B_CO2*T*np.log10(T)+C_CO2*T # J/mol
    # overall delta g and Kp:
    delta_g = delta_g0_CO2-delta_g0_CO
    Kp = np.exp(-delta_g/(R*T))
    return Kp

def getCO2_percent(T,abc_param):
    # Calculate %CO2 for some common buffers and user input:
    Kp=getKp(T)
    # fO2=((Xco2/Xco)**2)*(1/Kp)**2
    fo2=func_fo2(T, *abc_param)

    Xco2_co_UI=((10**fo2)**0.5)*Kp
    xCO_UI=1/(1+Xco2_co_UI)
    xCO2_UI=1-xCO_UI
    xCO2_pct=[100 * n for n in xCO2_UI]
    return xCO2_pct
    # print "CO2:", round(xCO2_UI,2)

    # # QFM
    # fo2_QFM=10**((-25096.3/T) + 8.735 + 0.11 * (P-1)/T) # log
    # Xco2_co_QFM=(fo2_QFM**0.5)*Kp
    # xCO_QFM=1/(1+Xco2_co_QFM)
    # xCO2_QFM=1-xCO_QFM
    # # IW
    # fo2_IW=10**((-27489/T) + 6.702 + 0.055 * (P-1)/T) # log
    # Xco2_co_IW=(fo2_IW**0.5)*Kp
    # xCO_IW=1/(1+Xco2_co_IW)
    # xCO2_IW=1-xCO_IW

    # print "CO %", round(xCO*100,2), "CO2%", xCO2*100

def plot_T_fo2_CO2(T,fo2,CO2_percent):
    time_UI=float(E3.get())

    fo2_QFM = (-25096.3 / T) + 8.735 + 0.11 * (P - 1) / T  # log (T in K, P in bar)
    fo2_IW = (-27489 / T) + 6.702 + 0.055 * (P - 1) / T
    fo2_NNO= (-24930 / T) + 9.36 + 0.046 * (P - 1) / T
    fo2_MH= (-25700.6 / T) + 14.558 + 0.019 * (P - 1) / T
    fo2_CCO= (-24332.6 / T) + 7.295 + 0.052 * (P - 1) / T
    fo2_list=[(fo2_QFM,fo2_IW,fo2_NNO,fo2_MH,fo2_CCO,fo2)]

    Tc = T - 273 # K to C
    axis_lim=[min(Tc), max(Tc), min(map(min,*fo2_list)), max(map(max,*fo2_list))]
    plt.axis(axis_lim) #limits
    plt.ion()
    start_timeT = time.time()

    for i in range(len(T)):
        start_time = time.clock()
        # print "T(oC), fo2= " ,Tc[:i+1], fo2[:i+1]
        # print "time steps: ",((time_UI*60)/len(T))

        plt.clf()
        plt.axis(axis_lim)  # limits
        plt.plot(Tc[:i+1], fo2_QFM[:i+1], 'r', label='QF-M')  # Plot X x Y
        plt.plot(Tc[:i+1], fo2_IW[:i+1], 'g', label='I-W')  # Plot X x Y
        plt.plot(Tc[:i+1], fo2_NNO[:i+1], 'b', label='N-NO')  # Plot X x Y
        plt.plot(Tc[:i+1], fo2_MH[:i+1], 'c', label='M-H')  # Plot X x Y
        plt.plot(Tc[:i+1], fo2_CCO[:i+1], 'm', label='C-CO')  # Plot X x Y
        # plot user input
        plt.plot(Tc[:i+1], fo2[:i+1], 'k--', label='data')  # Plot X x Y

        #annotate CO2%,CO%,T_corrected(T),fo2
        Tcorrected = Tc+(0.07931*T-70.95) # obtained from linear interpolation of data in graph. (MIDDLE FURNACE)
        #Tcorrected=Tc+(0.04792*T-76) # obtained from linear interpolation of data in graph. (LAST FURNACE)

        text1 = "$CO_2 = {:.2f}, CO = {:.2f}$".format(CO2_percent[i],100-CO2_percent[i]) #(MIDDLE FURNACE)
        # text1 = "$CO_2 = {:.2f}, CO = {:.2f}$".format(2*CO2_percent[i],2*(100-CO2_percent[i])) # (LAST FURNACE)

        text2 = "$T_c = {:.2f} ({:.2f})$".format(Tcorrected[i],Tc[i])
        text3 = "$fO_2 = {:.2f}$".format(fo2[i])
        t_seconds=((time_UI*60)/(len(T)-1))*(i)
        t_min, t_sec = divmod(t_seconds, 60)
        text4 = "$Time (m:s) = {:g}:{:g}$".format(int(t_min),int(t_sec))

        text= text1+'\n'+text2+'\n'+text3+'\n'+text4



        plt.annotate(text, xy=(1, 0), xytext=(-10, +60), fontsize=9,
                    xycoords='axes fraction', textcoords='offset points',
                    bbox=dict(facecolor='white', alpha=0.8),
                    horizontalalignment='right', verticalalignment='top')
        plt.legend()
        plt.xlabel('$T (^oC)$')  # X label
        plt.ylabel('$log fo_2$')  # Y label
        plt.title(' Gas mixing furnace: $fo_2$ control')  # title
        # # print (time_UI * 60) / (len(T)-1), ((time_UI*60)/(len(T)-1))*(i)
        print (text + '\n')
        plt.pause(1e-17)
        exe_time = time.clock() - start_time
        tpause = ((time_UI * 60) / (len(T) - 1)) - exe_time
        time.sleep(tpause)
        # # print exe_time

        # plt.pause(1e-17)
    exe_timeT = time.time() - start_timeT
    print "end of experiment. Total time " + str(exe_timeT-tpause) +" s"
    plt.show()

root.mainloop()