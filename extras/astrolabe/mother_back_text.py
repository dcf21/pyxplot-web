# Horrible fudge way to write text in circles around the mother
# $Id$

out1 = open("mother_back_text.dat","w")
out2 = open("mother_back_text_simple.dat","w")
out3 = open("mother_front_text_simple.dat","w")
out4 = open("plate_text_simple.dat","w")

# Signs of the zodiac
strings = [["ARIES",r"\aries"],["TAURUS",r"\taurus"],["GEMINI",r"\gemini"],["CANCER",r"\cancer"],["LEO",r"\leo"],["VIRGO",r"\virgo"],["LIBRA",r"\libra"],["SCORPIO",r"\scorpio"],["SAGITTARIUS",r"\sagittarius"],["CAPRICORNUS",r"\capricornus"],["AQUARIUS",r"\aquarius"],["PISCES",r"\pisces"]]

LetterSep = 2.0
for i in range(len(strings)):
 item = strings[i]
 [word,after] = item
 L = len(word) + 1
 ang = 15 + 30*i

 for j in range(len(word)):
  out1.write("RT = RT1 ; theta=%f*unit(deg) ; text \"%s\" at RT*cos(theta),RT*sin(theta) rot theta+90*unit(deg) hal c val c\n"%(ang - LetterSep*L/2 + j*LetterSep, word[j]))
  out2.write("RT = RT1 ; theta=%f*unit(deg) ; text \"%s\" at RT*cos(theta),RT*sin(theta) rot theta+90*unit(deg) hal c val c\n"%(ang - LetterSep*L/2 + j*LetterSep, word[j]))
 j=j+2
 out1.write("RT = RT1 ; theta=%f*unit(deg) ; text \"%s\" at RT*cos(theta),RT*sin(theta) rot theta+90*unit(deg) hal c val c\n"%(ang - LetterSep*L/2 + j*LetterSep, after))
 out2.write("RT = RT1 ; theta=%f*unit(deg) ; text \"%s\" at RT*cos(theta),RT*sin(theta) rot theta+90*unit(deg) hal c val c\n"%(ang - LetterSep*L/2 + j*LetterSep, after))

# Months
strings = [["JANUARY",-79],["FEBRUARY",-48],["MARCH",-20],["APRIL",11],["MAY",41],["JUNE",72-1],["JULY",102-2],["AUGUST",133-2],["SEPTEMBER",164-4],["OCTOBER",194-3],["NOVEMBER",225-2],["DECEMBER",255-2]]

LetterSep1 = 2.2
LetterSep2 = 3.0
for i in range(len(strings)):
 item = strings[i]
 [word,daynum] = item
 L = len(word)
 ang1 = (daynum+15  )*360.0/365.0
 ang2 = (daynum+15+9)*360.0/365.0

 for j in range(len(word)):
  out1.write("RT = RT2 ; theta=%f*unit(deg) ; text \"%s\" at RT*cos(theta),RT*sin(theta) rot theta+90*unit(deg) hal c val c\n"%(ang1 - LetterSep1*L/2 + j*LetterSep1, word[j]))
  out2.write("RT = RT2 ; theta=%f*unit(deg) ; text \"%s\" at RT*cos(theta),RT*sin(theta) rot theta+90*unit(deg) hal c val c\n"%(ang1 - LetterSep1*L/2 + j*LetterSep1, word[j]))
  out1.write("RT = RT3 ; theta=%f*unit(deg) ; text \"%s\" at RT*cos(theta),RT*sin(theta) rot theta+90*unit(deg) hal c val c\n"%(ang2 - LetterSep2*L/2 + j*LetterSep2, word[j]))

# Times on front of the mother
strings = [[" Midnight"]]
LetterSep = 1.8
for i in range(len(strings)):
 item = strings[i]
 [word] = item
 L = len(word)
 ang = -90.0 - 360.0/24*i

 for j in range(L):
  out3.write("theta=%f*unit(deg) ; text \"\\footnotesize %s\" at RT*cos(theta),RT*sin(theta) rot theta-90*unit(deg) hal c val b\n"%(ang + LetterSep*L/2 - j*LetterSep, word[j]))

# Name text on the plate
strings = [["Name:"]]
LetterSep = 1.8
for i in range(len(strings)):
 item = strings[i]
 [word] = item
 L = len(word)
 ang = -113.0

 for j in range(L):
  out4.write("theta=%f*unit(deg) ; text \"%s\" at RT*cos(theta),RT*sin(theta) rot theta+90*unit(deg) hal c val b\n"%(ang - LetterSep*L/2 + j*LetterSep, word[j]))

out1.close()
out2.close()
out3.close()
out4.close()
