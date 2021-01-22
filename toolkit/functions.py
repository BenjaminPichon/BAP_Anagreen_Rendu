# -*- coding: utf-8 -*-
## needed imports
import sys
import numpy as np
import pandas as pd 
import copy
#import matplotlib.pyplot as plt
from itertools import permutations 
import doctest
import re
import pickle
import class_ as cl

# =============================================================================
# MISC FUNCTIONS
# =============================================================================

def search_in_colname(df, pattern) :
    '''
        SEARCH IN COLUMNS NAMES HELP :
        ==============================
        
        Takes a string as a search pattern and return all the 
        columns names containing the searched patterns.
        It is not case sensitive.
        
        :param pattern: Researched pattern
        :type pattern: str
        :param df: DataFrame in which the column names are parsed
        :type df: Pandas DataFrame
        
        :returns: Column name 
        :rtype: str
    '''
    # thanks to the lower tricks this function is not case sensitive
    match = [col for col in [x.lower() for x in df.columns] if str(pattern.lower()) in col]
    return match
def tuple2series(tuplelist) :
    '''
        Converts a tuple into a Pandas Series
        
        :returns: Pandas Series of corresponding tuple
        :rtype: pd.Series
    '''
    return pd.Series(dict(tuplelist))

# =============================================================================
# PREPROCESSING OF THE RAW DATA
# =============================================================================


def fill_missing_value(df, axis=1) :
    '''
        FILL MISSING VALUE HELP :
        =========================
        
        This function fills the missing values in a given columns by the median
        of that same column.
        
        :returns: a Pandas DataFrame where the missing value are filled
        :rtype: pd.DataFrame
    '''
    # must import sys first
    import sys
    # check if required module are imported, if not import them.
    # this is just a trick not to have to import blindly
    module_name_list = ["numpy", "pandas"]
    for module in module_name_list :
        if module not in sys.modules:
            import module
            print("{} was missing and has been imported.".format(module))
    # now do the actual missing value filling
    df_filled = df.fillna(df.median())
    print("Number of total missing values is: \n Before filling: {} \n After filling: {}".format(df.isna().sum().sum(), df_filled.isna().sum().sum()))
    return df_filled

def del_corr_columns(dataset, threshold, verbose=0) : 
    '''
        DELETE CORRELATED FEATURES HELP :
        =================================
        
        This function removes all the duplicated columns keeping only one.
        Two columns or features are considered correlated when their correlation
        coeffiscient is above the specified threshold.
        
        dependencies : copy, pandas
        
        :param dataset: Pandas DataFrame
        :type dataset: pd.DataFrame
        :param threshold: correlation thresold over which two variables are considered highly correlated.
        :type threshold: float
        :returns: Pandas DataFrame 
        :rtype: pd.DataFrame
    '''
    newdataset = dataset.copy()
    col_corr = set() # Set of all the names of deleted columns
    corr_matrix = newdataset.corr().abs()
    for i in range(len(corr_matrix.columns)):
        for j in range(i): # this loop allows to look at half of the correlation matrix
            if corr_matrix.iloc[i, j] >= threshold:
                if verbose == 1 :
                    print("{} vs {} corr = {}".format(corr_matrix.columns[i], corr_matrix.columns[j], corr_matrix.iloc[i, j] ))
                    print("{} will be deleted".format(corr_matrix.columns[i]))
                colname = corr_matrix.columns[i] # getting the name of column
                col_corr.add(colname)
                if colname in newdataset.columns:
                    del newdataset[colname] # deleting the column from the dataset
    print("{} columns were deleted.".format(len(col_corr)))

    return newdataset

def preprocessing_df(df, corr_treshold) :
    '''
    PREPORCESSING DATAFRAME HELP :
    ==============================
    
    General function for preprocessing data.
    
    :returns: Returns a the DataFrame processed
    :rtype: pd.DataFrame
    
    dependencies: search_in_colnam(), pandas, del_corr_columns, fill_mv,
    
    '''
    # make all the culmns name lower case
    print("Making all the columns name lowercase ...")
    df.columns = [x.lower() for x in df.columns]
    print("Done")
    print("Removing the flat 'consigne' lines ...")
    consigne_column_list = search_in_colname(df, 'consigne')
    df.drop(consigne_column_list, axis=1)
    print("Done")
    # remove all the correlated columns
    print("Removing the correlated features ...")
    df_processed0 = del_corr_columns(df, corr_treshold)
    print("Done")
    print("Filling the missing values with the median")
    df_processed1 = fill_mv(df_processed0)
    print("Done")
    return df_processed1

def gen_linear_trend(npoints=1000, coef=1, rest=0):
    '''
        GENERATE LINEAR TREND HELP :
        ============================
        
        This function generate a time serie of linear trend. Either steady, positive or negative.
        
        :rtype: tuple
        :returns: a tuple containing the x and y values randomly generated.
    '''

    # check if required module are imported, if not import them.
    # this is just a trick not to have to import blindly
    module_name_list = ["numpy"]
    for module in module_name_list :
        if module not in sys.modules:
            import module
            print("{} was missing and has been imported.".format(module))
    # generate random X
    x = np.linspace(0,100,npoints)
    # apply the modulation to the random X
    y=[]
    for i in x :
        result = (coef * i + rest) + 5*abs(coef)*np.random.randn()
        y.append(result)
    
    return(x,y)
# =============================================================================
# ANALYZIS (CHARACTERIZATION + PLOTTING) OF THE FLUX
# =============================================================================

def generate_random_flux(id, meanIn, stdIn, meanOut, stdOut, npoints, hotCold, Cp=4180, flow=1) :
    '''
        GENERATE RANDOM FLUX HELP :
        ===========================
        
        This function lets you create a flux object and fill its properties.
        In particular it generates ranom timeseries for the temperatures taking 
        as parameters mean and std values.
        
        dependency : flux object, numpy
                
        :rtype: flux obj
        :returns: an flux object with the specified parameters and randomly generated time series for the in and out temperatures. 
    '''
    # flux generated are stable around a fixed value, no increasing or decreasing trends.
    tsIn = np.random.normal(meanIn, stdIn, npoints)
    tsOut = np.random.normal(meanOut, stdOut, npoints)
    flux = cl.flux(id=id, name='Flux randomly generated', exchanger="ech1", 
                   type="eau", timeserieIn=tsIn, timeserieOut=tsOut, 
                   sensor=["capt1","capt2"], hotCold=hotCold, 
                   flow=flow, Cp=Cp)
    return flux


def classify_TS(pandasSerie, nchunk=100) :
    # 1 preprocess
    arr = np.array((pandasSerie.index,pandasSerie.values)).transpose()
    lchunk = np.array_split(arr, nchunk)
    # 2 loop over all chunk and classify them into the 4 predefined categories
    dfout = pd.DataFrame(columns=['chunkNumber','trend']) # df for the results do be stored into
    chunktype = []
    for chunk in range(len(lchunk)) :
        # try a linear regression for each chunk and based on the value of a conclude on the trend
        from sklearn import linear_model
        X = lchunk[chunk][:,0].reshape(-1,1)
        Y = lchunk[chunk][:,1].reshape(-1,1)
        lm=linear_model.LinearRegression()
        lm.fit(X,Y)
        if np.sqrt(lm.score(X,Y)) >= 0.75 :
            if lm.coef_ <= 1 and lm.coef_ >= -1 :
                dfout = dfout.append(pd.DataFrame({"chunkNumber" : [chunk],"trend":["steady"]}), ignore_index=True)
            elif lm.coef_ <= -1 :
                dfout = dfout.append(pd.DataFrame({"chunkNumber" : [chunk],"trend":["negative"]}), ignore_index=True)
            elif lm.coef_ >= 1 :
                dfout = dfout.append(pd.DataFrame({"chunkNumber" : [chunk],"trend":["positive"]}), ignore_index=True)
        else : 
            dfout = dfout.append(pd.DataFrame({"chunkNumber" : [chunk],"trend":["undetermined"]}), ignore_index=True)
    ser = pd.Series(dict(chunktype))
    print(ser.value_counts(normalize=True))
    return dfout

#def plot_sensor_TL(df) :
#    '''
#        PLOT SENSOR TIME TREND HELP :
#        =============================
#        
#        This function lets you plot the trends computed with the function
#        with classify_TS(). It displays with different colors the positive,
#        negative, steady or undetermined trends computed in each time bin. 
#        
#        dependencies: classify_TS(), pandas, matplotlib
#                
#        :rtype: plot
#        :returns: A plot evidencing the various trends indentified by classify_TS().
#    '''
#    fig, ax = plt.subplots()
#    counter = 0
#    counterundeter = 0
#    counterpos = 0
#    counterneg = 0
#    countersteady = 0
#
#    for i in df["trend"] :
#        if i == "undetermined" :
#            if counterundeter == 0:
#                ax.scatter(counter,1, marker='s',color="yellow", label='Undetermined')
#                counterundeter += 1
#            else :
#                ax.scatter(counter,1, marker='s',color="yellow")
#        elif i == "steady" :
#            if countersteady == 0:
#                ax.scatter(counter,1, marker='s',color="grey", label='Steady trend')
#                countersteady +=1
#            else :
#                ax.scatter(counter,1, marker='s',color="grey")
#        elif i == "positive" :
#            if counterpos == 0:
#                ax.scatter(counter,1, marker='s',color="red", label='Positive trend')
#                counterpos += 1
#            else :
#                ax.scatter(counter,1, marker='s',color="red")
#        elif i == "negative" :
#            if counterneg == 0:
#                ax.scatter(counter,1, marker='s',color="blue", label='Negative trend')
#                counterneg += 1
#            else :
#                ax.scatter(counter,1, marker='s',color="blue")
#        else :
#            print("Something went wrong...!")
#        counter +=1
#
#    plt.ylabel("")
#    plt.xlabel("Time")
#    fig.set_size_inches(16,4)
#    ax.legend()
#    plt.show()

# =============================================================================
# IMPLEMENTATION OF THE PINCH METHOD
# =============================================================================

def compute_nflux(lflux) :
    '''
        COMPUTE NUMBER OF FLUX HELP : 
        =============================
        
        This function will compute the number of hot and cold flux.
        Returns in a tuple (nfluxchaud, nfluxfroid)
                
        :rtype: tuple
        :returns: A tuple of (nfluxhot, nfluxCold).
    '''
    nfluxchaud = 0
    nfluxfroid = 0
    for i in lflux :
        if i.hotCold == 'hot' :
            nfluxchaud+=1
        elif i.hotCold == 'cold': 
            nfluxfroid+=1
        else :
            print('Error: type of flux (hotCold) cannot be understood')
            return 1
    return (nfluxchaud,nfluxfroid)

def make_temp_list(lflux, step) :
    # step is defined as the position in the array of temperature both in and out
    '''
        MAKE TEMPERATURE LIST HELP :
        ============================
        
        This function returns the list of all the unique temperatures sorting 
        from biggest to smallest.
                
        :rtype: list
        :returns: a list of temperatuers sorted in decreasing order
    '''
    templist = []
    for flux in lflux :
        templist.append([flux.timeserieIn[step], flux.timeserieOut[step]])
    temp = np.array(templist, dtype=float).flatten()
    temp_sorted = np.sort(temp)[::-1]
    temp_uniq = np.unique(temp_sorted)[::-1]
    return temp_uniq

def compute_cascade(lflux_shifted, step, verbose=False) :
    '''
        COMPUTE ENTHALPIE CASCADE HELP :
        ================================
        
        This function is the main function to compute the MER (Minimal energy
        required) of a given system. 
        It takes a list of flux as an input and returns the MER and the values
        of the cascade.
        Important : it returns a shifted cascade. Meaning the lowest value of
        enthalpie is shifted so it is equal to 0.
        
        :param lflux_shifted: list of flux with temperatures shifted. Use shift_temp() to do so.
        :type lflux_shifted: list 
        :param step: Time step in the time series
        :type step: int
        :returns: returns the MER and the value of the cascade
        :rtype: tuple(MER, cascade)
        
        dependency : make_temp_list 
        
        >>> compute_cascade(lflux_shifted, 0, verbose=False)[0]
        array([19.2 , 79.8 , 80.25, 82.65,  0.  , 75.25, 60.55, 59.55])
        >>> np.round(compute_cascade(lflux_shifted, 0, verbose=False)[1], 2)
        78.75
    '''

#    print("Make sure you provided a list of shifted flux")
#    print("If NOT you can do it with the correpsonding function: shift_temp(lflux, DT)")
    
    temp_list = make_temp_list(lflux_shifted, step)
    
    sum_hot_list=[]
    sum_cold_list=[]
    Rslicelist=[]
    Rsliceprev = 0
    # loop sur toutes les intervales de température
    for cascId, temp in enumerate(temp_list) :
        if cascId == 0 :
            wind = [temp, temp]
        else :
            wind = [temp_list[cascId-1], temp]
        if verbose == True :
            print("Temp wind: "+str(wind))
        deltaT = wind[0]-wind[1]
        if deltaT < 0 :
            print("Error : DeltaT must be >= 0")
            print("Error : DeltaT = {}".format(deltaT))
            return 1
        if verbose == True :
            print("DeltaT = {}".format(deltaT))
            print("Flux total nbr: "+str(len(lflux_shifted)))
            print("---------")
        Rslice = 0 # initiailise the amount of energie in the current slice
        sum_hot = 0 
        sum_cold = 0
        # Loop over flux 
        for flux_id, flux in enumerate(lflux_shifted) :
            if verbose == True :
                print("Flux index: "+str(flux_id))
            # test if the flux exist in a given interval
            if min([flux.timeserieIn[step], flux.timeserieOut[step]]) <= wind[1] and max([flux.timeserieIn[step], flux.timeserieOut[step]]) >= wind[0] :
                if verbose == True :
                    print("{} < [{}-{}] > {}".format(min([flux.timeserieIn[step], flux.timeserieOut[step]]), wind[1], wind[0], max([flux.timeserieIn[step], flux.timeserieOut[step]]))) 
                if flux.hotCold == 'hot':
                    if verbose == True :
                        print("Found hot flux")
                        print("Sum hot = {} \n lflux.Cp = {} \n deltaT = {}".format(sum_hot, flux.Cp[step], deltaT))
                    sum_hot+=flux.Cp[step]*deltaT
                    if verbose == True :
                        print("RHot = "+str(sum_hot))
                if flux.hotCold == 'cold':
                    if verbose == True :
                        print("Found cold flux")
                        print("Sum cold = {} \n lflux.Cp = {} \n deltaT = {}".format(sum_cold, flux.Cp[step], deltaT))
                    sum_cold+=flux.Cp[step]*deltaT
                    if verbose == True :
                        print("RCold = "+str(sum_cold))
            else :
                if verbose == True :
                    print("Flux named '{}' with temp TS '{}' does not exist in interval [{}-{}]".format(flux.name, [flux.timeserieIn[step], flux.timeserieOut[step]] ,wind[1], wind[0]))
        sum_hot_list.append(sum_hot)
        sum_cold_list.append(sum_cold)
        Rslice = Rsliceprev + sum_hot - sum_cold
        if verbose == True :
            print("Corresponding energy of the current interval is :"+str(Rslice))
        Rslicelist.append(Rslice)
        # update the n-1 (or +1 as we are going from n to 1 and not from 1 to n as usual) occurence so it is added to the calculation of n occurence
        Rsliceprev = Rslice
        if verbose == True :
            print("\n")
            print("---------")
        # The MER (minimal energy required) is defined as the minimum energy 
        # required for the system to operate.
        # It is given by the lower value(negative if the systems needs heating)
        # of the cascade.
        Rslicearr = np.array(Rslicelist)
        

        # Now we shift the full values of Rslice so the minimum is 0
        # This is explained by the fact that the sum of hot and cold flux in a given interval
        # can't be bellow 0 because we cannot trasnfert negative heat from an interval
        # to the next
        Rslicearr = Rslicearr+np.abs(min(Rslicearr))
        MER = Rslicearr[0] + Rslicearr[-1]
    return(Rslicearr, MER)

#def plot_cascade(cascade_data, temp_list) :
#    '''
#        PLOT CASCADE HELP :
#        ===================
#        
#        This function helps you plot the cascade of enthalpies.
#        
#        :param cascade_data: list of cascade value obtained as in the pinch method (see compute_cascade())
#        :type cascade_data: list or np.array
#        :param temp_list: list of temperatures as obtained by make_temp_list()
#        :type temp_list: list or np.array
#                
#        :rtype: plot
#        :returns: A plot of the cascade of enthalpies
#    '''
#    f, axes = plt.subplots()
#    plt.plot(cascade_data, temp_list)
#    plt.ylabel("Temperatures")
#    plt.xlabel("Energy")
#    plt.title("Great composite curve")
#    plt.show()
#    
def shift_temp(lflux, DT) :
    '''
        SHIFT TEMPERATURE FUNCTION HELP :
        =================================
        
        This function shift the temperature of +0.5*DT for cold flux and 
        -0.5*DT for hot flux.
        It takes as an input a list of flux objects.
        It return a deep copy of the list of flux objects with shifted 
        temperatures. 
                
        :rtype: pd.DataFrame
        :returns: A copy of the input dataframe with all the temperatures shifted of 1/2 DT.
    '''
    if type(DT) == str :
        DT = int(DT)
    tmp = copy.deepcopy(lflux)
    #   Loop over all flux
    for flux in tmp :
#            if it's a hot flux decrease all temp by DT/2
        if flux.hotCold == 'hot' :
            # change both in and out temperatures
            for step, _ in enumerate(flux.timeserieIn) :
                flux.timeserieIn[step] = flux.timeserieIn[step] - (DT/2)
            for step, _ in enumerate(flux.timeserieOut) :
                flux.timeserieOut[step] = flux.timeserieOut[step] - (DT/2)
        if flux.hotCold == 'cold' :
            # change both in and out temperatures
            for step, _ in enumerate(flux.timeserieIn) :
                flux.timeserieIn[step] = flux.timeserieIn[step] + (DT/2)    
            for step, _ in enumerate(flux.timeserieOut) :
                flux.timeserieOut[step] = flux.timeserieOut[step] + (DT/2)   
    return tmp
    
def find_overlap(list1, list2):
    '''
        FIND OVERLAP HELP :
        ===================
        
        This function find the overlapping portion of two
        ranges of temperatures.
                
        :rtype: list or int
        :returns: the min and max value of the computedd overlapping window. It no overlap exists, returns 0.
        
        >>> find_overlap([10, 20],[15,25])
        [15, 20]
        >>> find_overlap([10, 20],[35,47])
        0
    '''
    if min(list1) >= max(list2) or min(list2) >= max(list1) :
#        print("No overlap was found")
        overlap=0
    else :
        min_l = [min(list1),min(list2)]
        max_l = [max(list1),max(list2)]
        overlap = [max(min_l),min(max_l)]
    return overlap

def generate_networks(lfluxhot, lfluxcold) :    
    '''
        GENERATE HEN HELP :
        ===================
        
        This function generates all the combination possible of hot and
        cold couples of flux. 
        
        dependency : permutations
        
        :rtype: list
        :returns: List of all the possible HEN. 
    '''
    lfluxcold_permuations = permutations(lfluxcold)
    network_list = []
    
    for perm in lfluxcold_permuations:
        network_list.append([[a, b] for a, b in zip(lfluxhot, perm)])
    return network_list

def compute_composite_curve(lfluxHotOrCold, verbose=0):
    sumList=[]
    sumPrev = 0
    tempList = np.sort(make_temp_list(lfluxHotOrCold))
    # only useful when there are several hot and cold flux
    # loop sur toutes les intervales de température
#    temp_list_hot = [200,150,100,60][::-1]
#    temp_list_cold = [220,120,80,50][::-1]

    for i in range(len(tempList)-1) :
        wind = [tempList[i], tempList[i+1]]
        if verbose == 1 :
            print("Temp wind: "+str(wind))
        deltaT = np.abs(wind[0]-wind[1])
        if verbose == 1 :
            print("DeltaT = {}".format(deltaT))
            print("Flux total nbr: "+str(len(lfluxHotOrCold)))
            print("---------")
        # on loop sur tous les flux et en fonction de si chaud ou froid j'ajoute le DG a une différentes somme
        sum = 0 # initiailise the amount of energie in the current slice
        for id , j in enumerate(lfluxHotOrCold) :
            # /!\ attention il faut implémenter l'adaptation au type de flux du Cp car la on prend eau par defaut pour tous
            # probablement faire un objet flux qui décrit ses propriétés
            if verbose == 1 :
                print("Flux index: "+str(id))
            # test if the flux exist in a given interval
            if min(j.timeserie) <= min(wind) and max(j.timeserie) >= max(wind) :
                if verbose == 1 :
                    print("{} < [{}-{}] > {}".format(min(j.timeserie), min(wind), max(wind), max(j.timeserie))) 
                    print("Found flux")
                sum+=j.Cp[step]*deltaT
                if verbose == 1 :
                    print("somme = {} \n lflux[j].Cp = {} \n deltaT = {}".format(sum, j.Cp[step], deltaT))
                    print("Rchaud = "+str(sum))
            else :
                if verbose == 1 :
                    print("Flux named '{}' with temp TS '{}' does not exist in interval [{}-{}]".format(j.name, j.timeserie,wind[1], wind[0]))
        if verbose == 1 :
            print("Somme = "+str(sum))
        sum = sumPrev + sum
        sumList.append(sum)
        sumPrev = sum
        if verbose == 1 :
            print("\n")
            print("---------")
    # We add the 0 value as the first occurence of the lsit as we don't know 
    # where should the composite curve be shifted. It will depend on the DTmin
    sumList.insert(0,0)
    return np.array([sumList, tempList])

# =============================================================================
def flux_object_to_df(flux_obj) :
    '''
         This function transforms a flux object to a DataFrame Pandas.
             
        :rtype: pd.DataFrame
        :returns: A dataFrame containing all the attribute of the object as columns
    '''
    dico = vars(flux_obj)
    df = pd.DataFrame.from_dict(dico, orient='index').transpose()
    return df
# =============================================================================

def save_obj(obj, outputFileName) :
    '''
        This function save an object to a pickle file.
        The corresponding function to read the saved object is load_obj()
        
        :param obj: object to save
        :type obj: python object
        :param outputFileName: name of the output file to store the object in
        :type outputFileName: str
        :rtype: pickle obj file
        :returns: A pickle object file containing the saved object
    '''
    
    with open(outputFileName, 'wb') as output:
        pickle.dump(obj, output)
    return

def load_obj(inputFileName) :
    '''
        This function loads an object from a pickle file.
        The corresponding function to read the saved object is load_obj()
               
        :param inputFileName: Input file containng the pickle object saved with the function save_obj().
        :type inputFileName: pickle obj file
        :rtype: python object
        :returns: An object as saved on the pickle file
    '''
    with open(inputFileName, 'rb') as input:
        obj = pickle.load(input)
    return obj

# =============================================================================
# PLOT FUNCTIONS
# =============================================================================

#def plot_tot_stored(energydf) : 
#    plt.figure()
#    networkNbr = len(energydf.networkNumber.unique())
#    for hen_id in range(networkNbr):
#        plt.plot(energydf.step[energydf.networkNumber == hen_id],
#                 energydf.totalstoredEnergy[energydf.networkNumber == hen_id],
#                 label = "Network #{}".format(hen_id))
#    plt.xlabel("step")
#    plt.ylabel("Total stored Energy")
#    plt.legend()
#    plt.show()
#    return
#
#def plot_tot_recycled(energydf) : 
#    plt.figure()
#    networkNbr = len(energydf.networkNumber.unique())
#    for hen_id in range(networkNbr):
#        plt.plot(energydf.step[energydf.networkNumber == hen_id],
#                 energydf.totalRecycledEnergy[energydf.networkNumber == hen_id],
#                 label = "Network #{}".format(hen_id))
#    plt.xlabel("step")
#    plt.ylabel("Total recycled Energy")
#    plt.legend()
#    plt.show()
#    return



# executed only if this script is exectued. Not if it is imported in another file.
if __name__ == "__main__":
    fh1 = cl.flux(id=1, name='chaud 1', exchangeur="ech1", type="eau", 
                    timeserieIn=[170.2, 170.3, 170.3, 169.5,
                    170.2], timeserieOut=[59.9, 59.3, 60.2, 
                    60.0, 60.0], sensor=["capt1","capt2"], 
                    hotCold="hot", flow=1, Cp=3)
    fh2 = cl.flux(id=2, name='chaud 2', exchangeur="ech1", type="eau", 
                        timeserieIn=[150.0 , 150.3, 149.5, 150.1,
                        151.0], timeserieOut=[30.5, 30.4, 30.1, 29.7, 29.9], 
                        sensor=["capt1","capt2"], hotCold="hot", flow=1, Cp=1.5)
    fc1 = cl.flux(id=3, name='froid 1', exchangeur="ech1", type="eau", 
                        timeserieIn=[20.0, 20.3, 19.1, 20.2, 20.7], timeserieOut=[135.1, 134.0, 134.7, 135.0,
                        134.8], sensor=["capt1","capt2"], hotCold="cold", 
                        flow=1, Cp=2)
    fc2 = cl.flux(id=4, name='froid 2', exchangeur="ech1", type="eau", 
                         timeserieIn=[80.0, 80.5, 79.8, 79.4, 80.4], timeserieOut=[139.9, 139.8, 
                         139.3, 140.1, 140.2], sensor=["capt1","capt2"]
                         , hotCold="cold", flow=1, Cp=4)
    lflux = [fc1, fc2, fh1, fh2]
    lflux_shifted = shift_temp(lflux, 10)
    doctest.testmod()
    
    
