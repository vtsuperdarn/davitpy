# -*- coding: utf-8 -*-
# Copyright (C) 2012  VT SuperDARN Lab
# Full license can be found in LICENSE.txt
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""gmeBase module

A base class for gme data.  Allows definition of common routines

Classes
-----------------------------
gmeData     a gme data record
-----------------------------

Module author:: AJ, 20130129

"""
import logging

class gmeData:
    """a class to represent a a record of gme data.  Other classes will extend this class

    Attributes
    ----------
    time : datetime
        an object identifying which time these data are for
    dataSet : str
        a string indicating the dataset
    info : str
        information about where the data come from.  *Please be courteous and give
        credit to data providers when credit is due.*

    Methods
    -------
    parseDb
    toDbDict

    Notes
    -----
    If any of the members have a value of None, this means that they could not
    be read for that specific time

    Example
    -------
            emptyObj = gme.base.gmeData()

    written by AJ, 20130131

    """
    def parseDb(self,dbDict):
        """This method is used to parse a dictionary of gme data from the mongodb
        into a :class:`gmeData` object.  

        Parameters
        ----------
        dbDict : dict
            the dictionary from the mongodb

        Returns
        -------
        Nothing

        Notes
        -----
        In general, users will not need to use this.

        Belongs to class gmeData

        Example
        -------
            myObj.parseDb(mongoDbDict)

        written by AJ, 20130129

        """
        #iterate over the mongo dict
        for attr, val in dbDict.iteritems():
            #check for mongo _id attribute
            if(attr == '_id'): pass
            elif(attr == 'kp'):
                for i in range(len(dbDict['kp'])):
                    num = str(int(dbDict['kp'][i]))
                    mod = dbDict['kp'][i] - int(dbDict['kp'][i])
                    if(mod == .3): mod = '-'
                    elif(mod == .7): mod = '+'
                    else: mod = ''
                    self.kp.append(num+mod) 
            else:
                #assign the value to our object
                try: setattr(self,attr,val)
                except Exception,e:
                    logging.exception(e)
                    logging.exception('problem assigning ' + attr)


    def toDbDict(self):
        """This method is used to convert a :class:`gmeData` object into a
        mongodb data dictionary.

        Parameters
        ----------
        Nothing

        Returns
        -------
        dbDict : dict
            a dictionary in the correct format for writing to the mongodb

        Notes
        -----
        In general, users will not need to worry about this

        Belongs to class gmeData

        Example
        -------
            mongoDbDict = myObj.todbDict()

        written by AJ, 20130129

        """
        #initialize a new dictionary
        dbDict = {}
        #create dictionary entries for all out our attributes
        for attr, val in self.__dict__.iteritems():
            if(attr == 'kp'):
                dbDict['kp'] = []
                for i in range(len(self.kp)):
                    num = int(self.kp[i][0:1])
                    mod = self.kp[i][1:2]
                    if(mod == '+'): num += .7
                    elif(mod == '-'): num += .3
                    else: num += .5
                    dbDict['kp'].append(num)
            else: dbDict[attr] = val
        return dbDict


    def __repr__(self):
        myStr = self.dataSet+' record FROM: '+str(self.time)+'\n'
        for key,var in self.__dict__.iteritems():
            myStr += key+' = '+str(var)+'\n'
        return myStr

    
    def __init__(self):
        self.time = None
        self.dataSet = None
        self.info = None
