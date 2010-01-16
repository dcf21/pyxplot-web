from math import *

R1     = 9
D12    = 0.07*R1
iEarth = 23.5
R2     = R1 - D12*3 - 0.1
R4     = R2 * tan((90-iEarth)/2*pi/180)
R5     = R4 * tan((90-iEarth)/2*pi/180)

y_ecl = (R2-R5)/2
R_ecl_outer = (R2+R5)/2
R_ecl_inner = R_ecl_outer*0.9

out = open("rete_text.dat","w")

# Signs of the zodiac
strings = [["ARIES",r"\aries"],["TAURUS",r"\taurus"],["GEMINI",r"\gemini"],["CANCER",r"\cancer"],["LEO",r"\leo"],["VIRGO",r"\virgo"],["LIBRA",r"\libra"],["SCORPIO",r"\scorpio"],["SAGITTARIUS",r"\sagittarius"],["CAPRICORNUS",r"\capricornus"],["AQUARIUS",r"\aquarius"],["PISCES",r"\pisces"]]

for i in range(len(strings)):
 item = strings[i]
 [word,after] = item
 L = len(word)
 theta0 = 90 + 15 + 30*i
 LetterSep = 1.8 + 0.5*sin(theta0/180*pi)

 for j in range(len(word)):
  theta = theta0 + (j - L/2)*LetterSep

  alpha = asin(y_ecl * sin(theta*pi/180) / R_ecl_outer)/pi*180 # Sine rule
  psi   = (theta + alpha)*pi/180 # Angles in triangle add up to 180 degrees

  out.write("text \"%s\" at -RT*sin(%f),y_ecl+RT*cos(%f) rot %f hal c val c\n"%(word[j],psi,psi,180+psi*180/pi))

out.close()
