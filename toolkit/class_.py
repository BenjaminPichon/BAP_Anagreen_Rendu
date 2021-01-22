# -*- coding: utf-8 -*-
import sys
import numpy as np
class flux() :
    '''
        FLUX OBJECT HELP:
        =================
        
        This object gather all the attributes of a flux.
        
        ex :    
        fh1 = flux(id=1, 
                   exchanger="ech1", 
                   type="eau", 
                   timeserieIn=[170.2, 170.3, 170.3, 169.5,170.2], 
                   timeserieOut=[59.9, 59.3, 60.2, 60.0, 60.0], 
                   capteur=["capt1","capt2"], 
                   chaudfroid="chaud",
                   debit=1,
                   Cp=3)
        
        :returns: A flux objects with all the parameters related 
        :rtype: object
    '''
    def __init__(self, **kwargs):
        self.id             = kwargs['id']
        self.name           = kwargs['name']
        self.exchanger     = kwargs['exchanger']
        self.flow           = kwargs['flow']
        self.type           = kwargs['type']
        self.timeserieIn    = kwargs['timeserieIn']
        self.timeserieOut   = kwargs['timeserieOut']
        self.pressure       = kwargs['pressure']
        self.d              = kwargs['d']
        self.sensor         = kwargs['sensor']
        self.hotCold        = kwargs['hotCold']
        self.Cp             = kwargs['Cp'] # ici on a Cp = cp * debit
    # create a method which computes the average of the data collected by the sensor
    def mean(self) :
        '''
            MEAN HELP:
            ==========
            
            This function computes the mean of the timeseries of in and out flux.
            It returns a tuple of float : (mean_in, mean_out)
        '''
        return (np.mean(self.timeserieIn), np.mean(self.timeserieOut))
    def std(self) :
        '''
            STD HELP:
            This function computes the standard deviation of the timeseries of in and out flux.
            It returns a tuple of float : (std_in, std_out)
        '''
        return (np.std(self.timeserieIn), np.std(self.timeserieOut))
    
    def num_step(self) :
        '''
            This function computes the number of steps of a given TS
        '''
        num1 = len(self.timeserieOut)
        num2 = len(self.timeserieIn)
        if num1 != num2 :
            print("WARNING: The number of steps in IN and OUT temperatures are different.")
            print("WARNING: this might create troubles when computing the cascade en enthalpies.")
        else :
            return num1
        
    def Q(self) :
        '''
            Q HELP:
            =======
            This functions lets you compute the quantity of energy corresponding to a given flux
            
            :returns: list of  Q values
            :rtype: list
        '''
        numStep = self.num_step()
        Q = []
        for step in range(numStep) :
            deltaT = self.timeserieIn[step] - self.timeserieOut[step]
            Q.append(deltaT * self.Cp)
        return Q
    def dt(self) :
        '''
            dt HELP:
            =======
            This functions lets you compute the delta T between the IN and OUT temp of a given flux
            
            :returns: list of Temp values
            :rtype: list
        '''
        TList = []
        numStep = self.num_step()
        for step in range(numStep) :
            DT = self.timeserieIn[step] - self.timeserieOut[step]
            TList.append(DT)
        return TList
            
      
        
class exchanger() :
    '''
        EXCHANGER OBJECT HELP:
        ======================
        
        This object gather all the attributes of an exchanger.
        
        ex :    
        fh1 = exchanger(id=1,
                   name="bc001",
                   type='eau/fumée',
                   sensor='sensor001',
                   position=[1,2]
                   )
        :returns: An exchanger object with all the parameters related.
        :rtype: object
    '''
    def __init__(self, **kwargs):
        self.id        = kwargs['id']
        self.name      = kwargs['name']
        self.type      = kwargs['type']
        self.sensor    = kwargs['sensor']
        self.position  = kwargs['position']
        self.flux      = kwargs['flux']
        
class hen():
    '''
    HEAT EXCHANGER NETWORK HELP:
    ============================
    
    This object stores all the informations relative to a given heat exchanger network.
    
    '''
    def __init__(self, **kwargs):
        self.id                             = kwargs['id']
        self.totalSavedEnergy               = kwargs['totalSavedEnergy']
        # list of ids corresponding the the flux id 
        self.config                         = kwargs['config']
        self.totalRecycledEnergy            = kwargs['totalRecycledEnergy']
        self.totalRecycledEnergyFromStorage = kwargs['totalRecycledEnergyFromStorage']
        
            
    def show_hen(hen_list) :
        '''
            SHOW HEAT EXCHANGER NETWORK HELP :
            ==================================
            
            This fucntion helps you see the composition of
            each HEN in flux couples.
            
            :param hen_list: List of the generated HEN.
            :type hen_list: list
            :returns: Prints the composition of all the created HEN.
        '''
        for henId, hen in enumerate(hen_list) :
            print("Network #{}".format(henId))
            for couple in hen : 
                print("=> flux {} {} flux {} {} ".format(couple[0].hotCold, couple[0].id ,couple[1].hotCold, couple[1].id))
        return 0
            
    
