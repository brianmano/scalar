from asammdf import MDF, Signal #import asammdf 
f_in = "examples\data-processing\LOG\00000001-663CD123.MF4"

mdf = MDF(f_in) #read mf4 data 

f_out = f_in.replace(".MF4", ".csv") 

mdf.export(fmt='csv', filename= f_out) #write to csv 