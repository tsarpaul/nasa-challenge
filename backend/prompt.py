import numpy as np
import pandas as pd
import requests



#'Kepler-52 c' for test
name='TRAPPIST-1 d'
def getdict(name):

    promptd={'tempp':'nan','barren':'nan','scolor':'nan','pkind':'nan','objectshape':'nan','plantscolor':'nan','brightness':'nan','skycolor':'nan','life':'nan','nummoon':'nan','numplanet':'nan','numsun':'nan'}

    if name=='Mars' or name=='Venus' or name=='Mercury' or name=='Neptune' or name=='Jupiter' or name=='Uranus':
        return promptd

    response = requests.get(f"https://exoplanetarchive.ipac.caltech.edu/cgi-bin/nstedAPI/nph-nstedAPI?table=cumulative&format=json&where=Kepler_name like '{name}'")
    response2 = requests.get(f"https://exoplanetarchive.ipac.caltech.edu/TAP/sync?query=select+*+from+PSCompPars+where+pl_name+=+'{name}'&format=json")

    df2=pd.read_json(response2.text)

    #Planet temp
    ptemp=float(df2['pl_eqt'].iloc[0])

    if ptemp<63.14:
        promptd['tempp']='very cold'
    elif ptemp>63.14 and ptemp<273.15:
        promptd['tempp']='cold'
    elif ptemp>273.15 and ptemp<373.15:
        promptd['tempp']='warm'
    elif ptemp>373.15 and ptemp<1683:
        promptd['tempp']='hot'
        promptd['barren']='barren'
    elif ptemp>1683:
        promptd['tempp']='very hot'


    #Star color
    stemp=float(df2['st_teff'].iloc[0])

    wavelength=2898/stemp #micron, wien's law

    if wavelength>0.685:
        promptd['scolor']='red'
    elif wavelength>0.600 and wavelength<0.645:
        promptd['scolor']='orange'
    elif wavelength>0.560 and wavelength<0.600:
        promptd['scolor']='yellow'
    elif wavelength<0.450:
        promptd['scolor']='blue'

    #Planet kind
    pmass=float(df2['pl_bmasse'].iloc[0]) #earth mass


    if  pmass<1:
        #terresrial
        promptd['pkind']='rocky'
    elif pmass>1 and pmass<5:
        #super earth
        promptd['pkind']='rocky'
    elif pmass>5 and pmass<15:
        #mini neptune
        promptd['pkind']='neptune'
    elif pmass>15 and pmass<318:
        #gas giant
        promptd['pkind']='jupiter'
    elif pmass>318:
        #super jupiter
        promptd['pkind']='jupiter'


    #gravity

    prad=float(df2['pl_rade'].iloc[0])

    G=6.674*10**-11
    Emass=5.972*10**24
    Erad=6.371*10**6
    g=G*(pmass*Emass)/(prad*Erad)**2


    if g<6:
        promptd['objectshape']='Tall and thin'
    elif g>6 and g<20:
        #super earth
        promptd['objectshape']='terrestrial'
    elif g>20:
        #super jupiter
        promptd['objectshape']='short and wide'

    #Plants color (1 atm pressure)

    stype=str(df2['st_spectype'].iloc[0])

    if 'M' in stype:
        if 'M8' in stype:
            promptd['plantscolor'] = 'white'
        else:
            promptd['plantscolor']= 'magenta'
    elif 'G' in stype:
        promptd['plantscolor']= 'green'
    elif 'K' in stype:
        promptd['plantscolor']= 'orange-purple'
    elif 'A' in stype:
        promptd['plantscolor']= 'brown-purple'
    elif 'F' in stype:
        promptd['plantscolor']= 'blue-green'


    #Apparent magnitude (may need tweaking)

    orbitperiod=float(df2['pl_orbper'].iloc[0]) #days
    orbitperiod=orbitperiod*24*3600

    smass=float(df2['st_mass'].iloc[0]) #solar mass
    smass=smass*1.989*10**30 #kg

    spdistance= (G*smass*orbitperiod**2/(4*np.pi**2))**(1/3) #Distance from planet to star [km] ,assuming circular orbit
    srad=float(df2['st_rad'].iloc[0])*6.96342*10**8 #Sun radius in m


    sb=5.67*10**-8
    f=sb*stemp**4*srad**2/spdistance**2

    m=-2.5*np.log(f)-18.997

    if m>0:
        #terresrial
        promptd['brightness']='dark'
    elif m>-12.6 and m<0:
        #super earth
        promptd['brightness']='dim'
    elif m<-12.6:
        #super jupiter
        promptd['brightness']='bright'

    #Atmosphere
    kb=1.38*10**-23 #m^2*kg*s^-2*k^-1
    mo2=5.3*10**-26 #kg
    mco2=7.3*10**-26 #kg
    mn2=4.7*10**-26 #kg
    mh2o=3*10**-26 #kg
    vo2=np.sqrt(3*kb*ptemp/mo2)
    vco2=np.sqrt(3*kb*ptemp/mco2)
    vn2=np.sqrt(3*kb*ptemp/mn2)
    vh2o=np.sqrt(3*kb*ptemp/mh2o)
    Mmin=prad/(2*G)/Emass*np.array([vo2,vco2,vn2,vh2o])

    #No atmosphere
    if pmass< Mmin.min():
        promptd['skycolor']='black'
        promptd['brightness']='dark'
        promptd['barren'] = 'barren'
    #Only CO2
    elif pmass< Mmin[2]:
        promptd['skycolor'] = 'red'
        promptd['barren'] = 'barren'
    #O2 and N2 cause blue light
    else:
        promptd['skycolor'] = 'blue'

    if promptd['pkind']=='neptune' or promptd['pkind']=='jupiter':
        promptd['skycolor'] = 'black'
        promptd['brightness'] = 'dark'
        promptd['barren'] = 'nan'


    #Checks
    if promptd['tempp'] == 'cold' or promptd['tempp'] == 'very cold':
        promptd['pkind'] = 'icy'

    if promptd['pkind'] == 'icy':
        promptd['barren'] = 'nan'

    if promptd['barren']=='barren':
        promptd['pkind'] = 'nan'

    if promptd['tempp']=='very hot' and promptd['pkind']!='jupiter' and promptd['pkind']!='neptune':
        promptd['pkind']='lava'

    # Habitability
    hab = True

    eccentricity = float(df2['pl_orbeccen'].iloc[0])

    if eccentricity > 0.8 or ptemp > 373 or ptemp < 273 or promptd['barren'] == 'barren':
        hab = False
        promptd['life'] = 'nan'

    # water in atmosphere?
    if pmass < Mmin[3] and ptemp > 273.15:
        hab = False
        promptd['life'] = 'nan'
    # life on gas giants?
    elif promptd['pkind'] == 'neptune' or promptd['pkind'] == 'jupiter':
        hab = False
        promptd['life'] = 'gas'
    else:
        promptd['life'] = 'terrestrial'

    if hab == False:
        promptd['plantscolor'] = 'nan'

    #Number of moons

    nummoons=float(df2['sy_mnum'].iloc[0])
    promptd['nummoon']=nummoons

    #Number of planets

    numplanets=float(df2['sy_pnum'].iloc[0])
    promptd['numplanet']=numplanets

    #Number of suns

    numsuns=float(df2['sy_snum'].iloc[0])
    promptd['numsun']=numsuns

    return promptd

def checknan(obj):
    if obj!='nan':
        return obj
    return ''

def getprompt(name):
    promptd = getdict(name)

    if name=='Mars' or name=='Venus' or name=='Mercury':
        return name+' planet surface'

    if name== 'Neptune' or name=='Jupiter' or name=='Uranus':
        return name+'planet'

    col=''
    #if promptd['pkind']=='icy' or promptd['pkind']=='barren' or promptd['pkind']=='rocky':
    #    col="Colonization of"

    planetstr=f" a {checknan(promptd['tempp'])} {checknan(promptd['barren'])} {checknan(promptd['pkind'])} planet, with a {checknan(promptd['brightness'])} {checknan(promptd['skycolor'])} sky,"

    starstr=""
    if promptd['scolor']!='nan' and promptd['pkind']!='jupiter':
        starstr=f" ,with a {promptd['scolor']} sun above, sun, "

    plantstr=""
    """
    if promptd['plantscolor']!='nan':
        plantstr=f" ,with {promptd['plantscolor']} {checknan(promptd['objectshape'])} plants"
    """

    lifestr=""

    """
    if promptd['life'] != 'nan':
        lifestr = f" ,with {checknan(promptd['objectshape'])} {promptd['life']} life"
    """

    prompt=col+planetstr+starstr+plantstr+lifestr

    if promptd['tempp']=='warm' and promptd['barren']=='nan':
        prompt=prompt+', a lot of waterfalls overflowing with water coming from the tall rocky point mountains, aqua, full of water'

    if promptd['pkind']=='rocky':
        prompt+=', rocky pointy mountains, geographic, valley'

    if promptd['pkind']=='icy':
        prompt+=', ice, '

    if promptd['pkind']=='lava':
        prompt+=', magma, hell, '

    if promptd['barren']=='barren':
        prompt+=', barren, '
        prompt=prompt.replace(' planet','')

    if promptd['pkind']!='jupiter' and promptd['pkind']!='neptune':
        prompt = prompt.replace(' planet', ' surface')


    prompt+=', intricate, perfect composition, cinematic perfect light, 8k artistic photography, interstellar, nature epic, nasa, highly detailed, ultra high quality, ultra realistic, scenery'

    return prompt

def gettype(name):

    if name=='Mars' or name=='Venus' or name=='Mercury':
        return 'rocky'

    if name== 'Neptune'  or name=='Uranus':
        return 'neptune'

    if name == 'Jupiter':
        return 'jupiter'

    promptd=getdict(name)
    if promptd['pkind']=='nan':
        return 'barren'
    return promptd['pkind']

print(getprompt(name))