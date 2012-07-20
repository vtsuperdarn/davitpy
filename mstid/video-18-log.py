run test.py
reset
logstart
logstop
# Fri, 13 Jul 2012 23:40:06
!ls -l
# Fri, 13 Jul 2012 23:40:15
!head video-18-log.py
# Fri, 13 Jul 2012 23:43:27
!wget http://surveys.ngdc.noaa.gov/mgg/NOS/coast/H12001-H14000/H12279/BAG/H12279_VB_4m_MLLW_1of1.bag.gz
# Fri, 13 Jul 2012 23:43:51
!gunzip *.gz
# Fri, 13 Jul 2012 23:43:52
ll
# Fri, 13 Jul 2012 23:44:16
!file H12279_VB_4m_MLLW_1of1.bag
# Fri, 13 Jul 2012 23:44:39
!md5 H12279_VB_4m_MLLW_1of1.bag
# Fri, 13 Jul 2012 23:44:51
!md5sum H12279_VB_4m_MLLW_1of1.bag
# Fri, 13 Jul 2012 23:46:47
history
# Fri, 13 Jul 2012 23:47:23
import h5py
# Fri, 13 Jul 2012 23:47:46
bag = h5py.File('H12279_VB_4m_MLLW_1of1.bag')
# Fri, 13 Jul 2012 23:48:10
bag.filename
#[Out]# u'H12279_VB_4m_MLLW_1of1.bag'
# Fri, 13 Jul 2012 23:48:17
bag.name
#[Out]# u'/'
# Fri, 13 Jul 2012 23:48:31
bag.items
#[Out]# <bound method File.items of <HDF5 file "H12279_VB_4m_MLLW_1of1.bag" (mode r+)>>
# Fri, 13 Jul 2012 23:48:44
bag.items()
#[Out]# [(u'BAG_root', <HDF5 group "/BAG_root" (4 members)>)]
# Fri, 13 Jul 2012 23:49:08
bag.items()[0][1]
#[Out]# <HDF5 group "/BAG_root" (4 members)>
# Fri, 13 Jul 2012 23:49:48
bag['/BAG_root'].items()
#[Out]# [(u'elevation', <HDF5 dataset "elevation": shape (1696, 1820), type "<f4">),
#[Out]#  (u'metadata', <HDF5 dataset "metadata": shape (4971,), type "|S1">),
#[Out]#  (u'tracking_list', <HDF5 dataset "tracking_list": shape (0,), type "|V19">),
#[Out]#  (u'uncertainty',
#[Out]#   <HDF5 dataset "uncertainty": shape (1696, 1820), type "<f4">)]
# Fri, 13 Jul 2012 23:50:39
root = bag['BAG_root']
# Fri, 13 Jul 2012 23:50:50
type(root)
#[Out]# h5py._hl.group.Group
# Fri, 13 Jul 2012 23:50:59
root.name
#[Out]# u'/BAG_root'
# Fri, 13 Jul 2012 23:51:05
root.parent
#[Out]# <HDF5 group "/" (1 members)>
# Fri, 13 Jul 2012 23:51:15
root.items
#[Out]# <bound method Group.items of <HDF5 group "/BAG_root" (4 members)>>
# Fri, 13 Jul 2012 23:51:19
root.items()
#[Out]# [(u'elevation', <HDF5 dataset "elevation": shape (1696, 1820), type "<f4">),
#[Out]#  (u'metadata', <HDF5 dataset "metadata": shape (4971,), type "|S1">),
#[Out]#  (u'tracking_list', <HDF5 dataset "tracking_list": shape (0,), type "|V19">),
#[Out]#  (u'uncertainty',
#[Out]#   <HDF5 dataset "uncertainty": shape (1696, 1820), type "<f4">)]
# Fri, 13 Jul 2012 23:51:28
root.values()
#[Out]# [<HDF5 dataset "elevation": shape (1696, 1820), type "<f4">,
#[Out]#  <HDF5 dataset "metadata": shape (4971,), type "|S1">,
#[Out]#  <HDF5 dataset "tracking_list": shape (0,), type "|V19">,
#[Out]#  <HDF5 dataset "uncertainty": shape (1696, 1820), type "<f4">]
# Fri, 13 Jul 2012 23:52:26
metadata_node = root['metadata']
# Fri, 13 Jul 2012 23:52:39
type(metadata_node)
#[Out]# h5py._hl.dataset.Dataset
# Fri, 13 Jul 2012 23:52:51
whos 
# Fri, 13 Jul 2012 23:53:38
metadata_node = root['/BAG_root/metadata']
# Fri, 13 Jul 2012 23:53:43
whos
# Fri, 13 Jul 2012 23:54:10
metadata=''.join(metadata_node.value)
# Fri, 13 Jul 2012 23:54:32
metadata_node.value
#[Out]# array(['<', '?', 'x', ..., '>', '\n', ''], 
#[Out]#       dtype='|S1')
# Fri, 13 Jul 2012 23:55:13
metadata
#[Out]# '<?xml version="1.0"?>\n<smXML:MD_Metadata xmlns:smXML="http://metadata.dgiwg.org/smXML" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:gml="http://www.opengis.net/gml"><identificationInfo><smXML:BAG_DataIdentification><citation><smXML:CI_Citation><title>Surface created from: N:\\SG904NRT210\\Surveys\\H12779\\Caris\\Fieldsheets\\H12279_VBES_1mB\\H12779_4m_SAR_Final.csar</title><date><smXML:CI_Date><date>2011-08-18</date><dateType>creation</dateType></smXML:CI_Date></date><citedResponsibleParty><smXML:CI_ResponsibleParty><individualName>Chief, Pacific Hydrographic Branch</individualName><organisationName>NOAA, NOS, OCS, Hydrographic Surveys Division</organisationName><positionName>Chief, Pacific Hydrographic Branch</positionName><role>pointOfContact</role></smXML:CI_ResponsibleParty></citedResponsibleParty></smXML:CI_Citation></citation><abstract>Project: S-G904-NRT2-10; Survey: H12779</abstract><status>historicalArchive</status><spatialRepresentationType>grid</spatialRepresentationType><language>en</language><topicCategory>elevation</topicCategory><extent><smXML:EX_Extent><geographicElement><smXML:EX_GeographicBoundingBox><westBoundLongitude>-81.36</westBoundLongitude><eastBoundLongitude>-81.28</eastBoundLongitude><southBoundLatitude>30.69</southBoundLatitude><northBoundLatitude>30.75</northBoundLatitude></smXML:EX_GeographicBoundingBox></geographicElement></smXML:EX_Extent></extent><verticalUncertaintyType>Unknown</verticalUncertaintyType></smXML:BAG_DataIdentification></identificationInfo><metadataConstraints><smXML:MD_LegalConstraints><useConstraints>otherRestrictions</useConstraints><otherConstraints>This Dataset is not a standalone navigational product</otherConstraints></smXML:MD_LegalConstraints></metadataConstraints><metadataConstraints><smXML:MD_SecurityConstraints><classification>unclassified</classification><userNote>Unclassified </userNote></smXML:MD_SecurityConstraints></metadataConstraints><dataQualityInfo><smXML:DQ_DataQuality><scope><smXML:DQ_Scope><level>dataset</level></smXML:DQ_Scope></scope><lineage><smXML:LI_Lineage><source><smXML:LI_Source><description>BASE = N:\\SG904NRT210\\Surveys\\H12779\\Caris\\Fieldsheets\\H12279_VBES_1mB\\H12779_4m_SAR.csar</description></smXML:LI_Source></source><processStep><smXML:BAG_ProcessStep><description>Software: CARIS HIPS and SIPS; Version: 7.1.0; Method: Finalize; Parameters: Additional_Attributes = Density,Depth,Mean,Std_Dev,Uncertainty,Weight,</description><dateTime>2011-08-18T17:20:10Z</dateTime><processor><smXML:CI_ResponsibleParty><individualName>adam.argento</individualName><role>processor</role></smXML:CI_ResponsibleParty></processor><trackingId>-1</trackingId></smXML:BAG_ProcessStep></processStep></smXML:LI_Lineage></lineage></smXML:DQ_DataQuality></dataQualityInfo><spatialRepresentationInfo><smXML:MD_Georectified><numberOfDimensions>2</numberOfDimensions><axisDimensionProperties><smXML:MD_Dimension><dimensionName>row</dimensionName><dimensionSize>1696</dimensionSize><resolution><smXML:Measure><smXML:value>4</smXML:value><smXML:uom_r/></smXML:Measure></resolution></smXML:MD_Dimension></axisDimensionProperties><axisDimensionProperties><smXML:MD_Dimension><dimensionName>column</dimensionName><dimensionSize>1820</dimensionSize><resolution><smXML:Measure><smXML:value>4</smXML:value><smXML:uom_r/></smXML:Measure></resolution></smXML:MD_Dimension></axisDimensionProperties><cellGeometry>point</cellGeometry><transformationParameterAvailability>false</transformationParameterAvailability><checkPointAvailability>0</checkPointAvailability><cornerPoints><gml:Point><gml:coordinates decimal="." cs="," ts=" ">465512,3394828 472788,3401608</gml:coordinates></gml:Point></cornerPoints></smXML:MD_Georectified></spatialRepresentationInfo><referenceSystemInfo><smXML:MD_CRS><projection><smXML:RS_Identifier><code>UTM</code></smXML:RS_Identifier></projection><ellipsoid><smXML:RS_Identifier><code>WGS84</code></smXML:RS_Identifier></ellipsoid><datum><smXML:RS_Identifier><code>WGS84</code></smXML:RS_Identifier></datum><projectionParameters><smXML:MD_ProjectionParameters><zone>17</zone><longitudeOfCentralMeridian>-81</longitudeOfCentralMeridian><falseEasting>500000</falseEasting></smXML:MD_ProjectionParameters></projectionParameters></smXML:MD_CRS></referenceSystemInfo><referenceSystemInfo><smXML:MD_CRS><datum><smXML:RS_Identifier><code>MLLW</code></smXML:RS_Identifier></datum></smXML:MD_CRS></referenceSystemInfo><language>en</language><contact><smXML:CI_ResponsibleParty><individualName>Chief, Pacific Hydrographic Branch</individualName><organisationName>NOAA, NOS, OCS, Hydrographic Surveys Division</organisationName><positionName>Chief, Pacific Hydrographic Branch</positionName><role>pointOfContact</role></smXML:CI_ResponsibleParty></contact><dateStamp>2011-08-18</dateStamp><metadataStandardName>ISO 19115</metadataStandardName><metadataStandardVersion>2003</metadataStandardVersion></smXML:MD_Metadata>\n'
# Fri, 13 Jul 2012 23:55:21
whos
# Fri, 13 Jul 2012 23:55:35
metadata[:50]
#[Out]# '<?xml version="1.0"?>\n<smXML:MD_Metadata xmlns:smX'
# Fri, 13 Jul 2012 23:56:08
import numpy
# Fri, 13 Jul 2012 23:56:25
from matplotlib import pyplot
# Fri, 13 Jul 2012 23:56:41
pyplot.interactive(True)
# Fri, 13 Jul 2012 23:56:56
root.items
#[Out]# <bound method Group.items of <HDF5 group "/BAG_root" (4 members)>>
# Fri, 13 Jul 2012 23:56:59
root.items()
#[Out]# [(u'elevation', <HDF5 dataset "elevation": shape (1696, 1820), type "<f4">),
#[Out]#  (u'metadata', <HDF5 dataset "metadata": shape (4971,), type "|S1">),
#[Out]#  (u'tracking_list', <HDF5 dataset "tracking_list": shape (0,), type "|V19">),
#[Out]#  (u'uncertainty',
#[Out]#   <HDF5 dataset "uncertainty": shape (1696, 1820), type "<f4">)]
# Fri, 13 Jul 2012 23:57:49
elev_node = root['elevation']
# Fri, 13 Jul 2012 23:58:03
type(elevation_node)
# Fri, 13 Jul 2012 23:58:14
type(elev_node)
#[Out]# h5py._hl.dataset.Dataset
# Fri, 13 Jul 2012 23:58:17
whos
# Fri, 13 Jul 2012 23:58:43
elev=elev_node.value
# Fri, 13 Jul 2012 23:58:44
whos
# Fri, 13 Jul 2012 23:58:54
whos ndarray
# Fri, 13 Jul 2012 23:59:14
elev.shape
#[Out]# (1696, 1820)
# Fri, 13 Jul 2012 23:59:40
elev.min()
#[Out]# -16.997538
# Fri, 13 Jul 2012 23:59:47
elev.max()
#[Out]# 1000000.0
# Sat, 14 Jul 2012 00:00:51
elev.mean()
#[Out]# 928695.93995438528
# Sat, 14 Jul 2012 00:02:29
elev[elev>9.0e5] = numpy.NaN
# Sat, 14 Jul 2012 00:02:43
pyplot.figure(1)
#[Out]# <matplotlib.figure.Figure at 0x3707cd0>
# Sat, 14 Jul 2012 00:03:40
pyplot.subplot(121)
#[Out]# <matplotlib.axes.AxesSubplot at 0x41f1f10>
# Sat, 14 Jul 2012 00:04:15
pyplot.imshow(elev)
#[Out]# <matplotlib.image.AxesImage at 0x4b24b50>
# Sat, 14 Jul 2012 00:05:03
elev.min()
#[Out]# nan
# Sat, 14 Jul 2012 00:05:33
elev1d = elev.reshape(elev.size)
# Sat, 14 Jul 2012 00:05:35
whos
# Sat, 14 Jul 2012 00:05:40
whos ndarray
# Sat, 14 Jul 2012 00:06:25
evel1d_finite = [ ]
# Sat, 14 Jul 2012 00:08:23
for item in elev1d: 
    if numpy.isfinite(item):
        elev1d_finite.append(item)
        
# Sat, 14 Jul 2012 00:09:19
elev1d_finite = [ ]
# Sat, 14 Jul 2012 00:09:23
for item in elev1d: 
    if numpy.isfinite(item):
        elev1d_finite.append(item)
        
# Sat, 14 Jul 2012 00:09:39
whos
# Sat, 14 Jul 2012 00:10:15
elev1d_finite = numpy.array(elev1d_finite)
# Sat, 14 Jul 2012 00:10:20
whos ndarray
# Sat, 14 Jul 2012 00:12:27
100*float(len(elev1d)- len(elev1d_finite) )/ len(elev1d))
# Sat, 14 Jul 2012 00:12:51
100*float(len(elev1d)- len(elev1d_finite) )/ len(elev1d))
# Sat, 14 Jul 2012 00:12:55
100*float(len(elev1d)- len(elev1d_finite) )/ len(elev1d)
#[Out]# 90.3909003732117
# Sat, 14 Jul 2012 00:13:29
pyplot.subplot(122)
#[Out]# <matplotlib.axes.AxesSubplot at 0x41f1350>
# Sat, 14 Jul 2012 00:14:01
pyplot.hist(elev1d_finite, bins=50)
#[Out]# (array([   64,   430,   964,  2971,  3682,  4194,  5451,  6258,  8005,
#[Out]#         9517,  8730,  6540,  7343,  8806,  8945,  9563, 11631, 12973,
#[Out]#        14778, 16986, 18588, 18695, 15810, 13882, 11646,  9764,  8725,
#[Out]#         7520,  7028,  6451,  5646,  4783,  4031,  3502,  3116,  2657,
#[Out]#         1936,  1318,   918,   707,   470,   313,   265,   273,   187,
#[Out]#          157,   168,   118,    70,    31]),
#[Out]#  array([-16.99753761, -16.83523399, -16.67293037, -16.51062675,
#[Out]#        -16.34832314, -16.18601952, -16.0237159 , -15.86141228,
#[Out]#        -15.69910866, -15.53680504, -15.37450142, -15.2121978 ,
#[Out]#        -15.04989418, -14.88759056, -14.72528694, -14.56298332,
#[Out]#        -14.4006797 , -14.23837608, -14.07607246, -13.91376884,
#[Out]#        -13.75146523, -13.58916161, -13.42685799, -13.26455437,
#[Out]#        -13.10225075, -12.93994713, -12.77764351, -12.61533989,
#[Out]#        -12.45303627, -12.29073265, -12.12842903, -11.96612541,
#[Out]#        -11.80382179, -11.64151817, -11.47921455, -11.31691093,
#[Out]#        -11.15460732, -10.9923037 , -10.83000008, -10.66769646,
#[Out]#        -10.50539284, -10.34308922, -10.1807856 , -10.01848198,
#[Out]#         -9.85617836,  -9.69387474,  -9.53157112,  -9.3692675 ,
#[Out]#         -9.20696388,  -9.04466026,  -8.88235664]),
#[Out]#  <a list of 50 Patch objects>)
# Sat, 14 Jul 2012 00:14:12
pyplot.hist(elev1d_finite, bins=100)
#[Out]# (array([  11,   53,  158,  272,  323,  641, 1289, 1682, 1763, 1919, 1969,
#[Out]#        2225, 2576, 2875, 3062, 3196, 3719, 4286, 4700, 4817, 4721, 4009,
#[Out]#        3384, 3156, 3483, 3860, 4340, 4466, 4511, 4434, 4696, 4867, 5530,
#[Out]#        6101, 6273, 6700, 7136, 7642, 8011, 8975, 9299, 9289, 9491, 9204,
#[Out]#        8461, 7349, 7146, 6736, 6095, 5551, 5033, 4731, 4445, 4280, 3818,
#[Out]#        3702, 3578, 3450, 3200, 3251, 2880, 2766, 2504, 2279, 2099, 1932,
#[Out]#        1851, 1651, 1534, 1582, 1435, 1222, 1063,  873,  723,  595,  489,
#[Out]#         429,  380,  327,  273,  197,  167,  146,  139,  126,  121,  152,
#[Out]#         108,   79,   79,   78,   81,   87,   66,   52,   37,   33,   26,
#[Out]#           5]),
#[Out]#  array([-16.99753761, -16.9163858 , -16.83523399, -16.75408218,
#[Out]#        -16.67293037, -16.59177856, -16.51062675, -16.42947495,
#[Out]#        -16.34832314, -16.26717133, -16.18601952, -16.10486771,
#[Out]#        -16.0237159 , -15.94256409, -15.86141228, -15.78026047,
#[Out]#        -15.69910866, -15.61795685, -15.53680504, -15.45565323,
#[Out]#        -15.37450142, -15.29334961, -15.2121978 , -15.13104599,
#[Out]#        -15.04989418, -14.96874237, -14.88759056, -14.80643875,
#[Out]#        -14.72528694, -14.64413513, -14.56298332, -14.48183151,
#[Out]#        -14.4006797 , -14.31952789, -14.23837608, -14.15722427,
#[Out]#        -14.07607246, -13.99492065, -13.91376884, -13.83261703,
#[Out]#        -13.75146523, -13.67031342, -13.58916161, -13.5080098 ,
#[Out]#        -13.42685799, -13.34570618, -13.26455437, -13.18340256,
#[Out]#        -13.10225075, -13.02109894, -12.93994713, -12.85879532,
#[Out]#        -12.77764351, -12.6964917 , -12.61533989, -12.53418808,
#[Out]#        -12.45303627, -12.37188446, -12.29073265, -12.20958084,
#[Out]#        -12.12842903, -12.04727722, -11.96612541, -11.8849736 ,
#[Out]#        -11.80382179, -11.72266998, -11.64151817, -11.56036636,
#[Out]#        -11.47921455, -11.39806274, -11.31691093, -11.23575912,
#[Out]#        -11.15460732, -11.07345551, -10.9923037 , -10.91115189,
#[Out]#        -10.83000008, -10.74884827, -10.66769646, -10.58654465,
#[Out]#        -10.50539284, -10.42424103, -10.34308922, -10.26193741,
#[Out]#        -10.1807856 , -10.09963379, -10.01848198,  -9.93733017,
#[Out]#         -9.85617836,  -9.77502655,  -9.69387474,  -9.61272293,
#[Out]#         -9.53157112,  -9.45041931,  -9.3692675 ,  -9.28811569,
#[Out]#         -9.20696388,  -9.12581207,  -9.04466026,  -8.96350845,  -8.88235664]),
#[Out]#  <a list of 100 Patch objects>)
# Sat, 14 Jul 2012 00:14:17
pyplot.hist(elev1d_finite, bins=200)
#[Out]# (array([   4,    7,   19,   34,   65,   93,  129,  143,  149,  174,  263,
#[Out]#         378,  530,  759,  877,  805,  895,  868,  970,  949,  957, 1012,
#[Out]#        1042, 1183, 1209, 1367, 1417, 1458, 1553, 1509, 1609, 1587, 1775,
#[Out]#        1944, 2098, 2188, 2261, 2439, 2379, 2438, 2431, 2290, 2145, 1864,
#[Out]#        1769, 1615, 1569, 1587, 1723, 1760, 1823, 2037, 2158, 2182, 2212,
#[Out]#        2254, 2210, 2301, 2122, 2312, 2373, 2323, 2461, 2406, 2711, 2819,
#[Out]#        3007, 3094, 3113, 3160, 3306, 3394, 3556, 3580, 3710, 3932, 3940,
#[Out]#        4071, 4382, 4593, 4573, 4726, 4771, 4518, 4859, 4632, 4633, 4571,
#[Out]#        4434, 4027, 3789, 3560, 3625, 3521, 3460, 3276, 3107, 2988, 2829,
#[Out]#        2722, 2566, 2467, 2445, 2286, 2235, 2210, 2171, 2109, 1942, 1876,
#[Out]#        1870, 1832, 1864, 1714, 1744, 1706, 1645, 1555, 1711, 1540, 1436,
#[Out]#        1444, 1443, 1323, 1218, 1286, 1172, 1107, 1031, 1068,  986,  946,
#[Out]#         969,  882,  833,  818,  793,  741,  814,  768,  719,  716,  670,
#[Out]#         552,  516,  547,  432,  441,  364,  359,  318,  277,  254,  235,
#[Out]#         224,  205,  192,  188,  163,  164,  141,  132,  108,   89,   86,
#[Out]#          81,   79,   67,   65,   74,   57,   69,   65,   56,   72,   80,
#[Out]#          57,   51,   33,   46,   35,   44,   40,   38,   41,   40,   37,
#[Out]#          50,   29,   37,   30,   22,   25,   12,   16,   17,   20,    6,
#[Out]#           4,    1]),
#[Out]#  array([-16.99753761, -16.95696171, -16.9163858 , -16.8758099 ,
#[Out]#        -16.83523399, -16.79465809, -16.75408218, -16.71350628,
#[Out]#        -16.67293037, -16.63235447, -16.59177856, -16.55120266,
#[Out]#        -16.51062675, -16.47005085, -16.42947495, -16.38889904,
#[Out]#        -16.34832314, -16.30774723, -16.26717133, -16.22659542,
#[Out]#        -16.18601952, -16.14544361, -16.10486771, -16.0642918 ,
#[Out]#        -16.0237159 , -15.98313999, -15.94256409, -15.90198818,
#[Out]#        -15.86141228, -15.82083637, -15.78026047, -15.73968456,
#[Out]#        -15.69910866, -15.65853275, -15.61795685, -15.57738094,
#[Out]#        -15.53680504, -15.49622913, -15.45565323, -15.41507732,
#[Out]#        -15.37450142, -15.33392551, -15.29334961, -15.2527737 ,
#[Out]#        -15.2121978 , -15.17162189, -15.13104599, -15.09047009,
#[Out]#        -15.04989418, -15.00931828, -14.96874237, -14.92816647,
#[Out]#        -14.88759056, -14.84701466, -14.80643875, -14.76586285,
#[Out]#        -14.72528694, -14.68471104, -14.64413513, -14.60355923,
#[Out]#        -14.56298332, -14.52240742, -14.48183151, -14.44125561,
#[Out]#        -14.4006797 , -14.3601038 , -14.31952789, -14.27895199,
#[Out]#        -14.23837608, -14.19780018, -14.15722427, -14.11664837,
#[Out]#        -14.07607246, -14.03549656, -13.99492065, -13.95434475,
#[Out]#        -13.91376884, -13.87319294, -13.83261703, -13.79204113,
#[Out]#        -13.75146523, -13.71088932, -13.67031342, -13.62973751,
#[Out]#        -13.58916161, -13.5485857 , -13.5080098 , -13.46743389,
#[Out]#        -13.42685799, -13.38628208, -13.34570618, -13.30513027,
#[Out]#        -13.26455437, -13.22397846, -13.18340256, -13.14282665,
#[Out]#        -13.10225075, -13.06167484, -13.02109894, -12.98052303,
#[Out]#        -12.93994713, -12.89937122, -12.85879532, -12.81821941,
#[Out]#        -12.77764351, -12.7370676 , -12.6964917 , -12.65591579,
#[Out]#        -12.61533989, -12.57476398, -12.53418808, -12.49361217,
#[Out]#        -12.45303627, -12.41246037, -12.37188446, -12.33130856,
#[Out]#        -12.29073265, -12.25015675, -12.20958084, -12.16900494,
#[Out]#        -12.12842903, -12.08785313, -12.04727722, -12.00670132,
#[Out]#        -11.96612541, -11.92554951, -11.8849736 , -11.8443977 ,
#[Out]#        -11.80382179, -11.76324589, -11.72266998, -11.68209408,
#[Out]#        -11.64151817, -11.60094227, -11.56036636, -11.51979046,
#[Out]#        -11.47921455, -11.43863865, -11.39806274, -11.35748684,
#[Out]#        -11.31691093, -11.27633503, -11.23575912, -11.19518322,
#[Out]#        -11.15460732, -11.11403141, -11.07345551, -11.0328796 ,
#[Out]#        -10.9923037 , -10.95172779, -10.91115189, -10.87057598,
#[Out]#        -10.83000008, -10.78942417, -10.74884827, -10.70827236,
#[Out]#        -10.66769646, -10.62712055, -10.58654465, -10.54596874,
#[Out]#        -10.50539284, -10.46481693, -10.42424103, -10.38366512,
#[Out]#        -10.34308922, -10.30251331, -10.26193741, -10.2213615 ,
#[Out]#        -10.1807856 , -10.14020969, -10.09963379, -10.05905788,
#[Out]#        -10.01848198,  -9.97790607,  -9.93733017,  -9.89675426,
#[Out]#         -9.85617836,  -9.81560246,  -9.77502655,  -9.73445065,
#[Out]#         -9.69387474,  -9.65329884,  -9.61272293,  -9.57214703,
#[Out]#         -9.53157112,  -9.49099522,  -9.45041931,  -9.40984341,
#[Out]#         -9.3692675 ,  -9.3286916 ,  -9.28811569,  -9.24753979,
#[Out]#         -9.20696388,  -9.16638798,  -9.12581207,  -9.08523617,
#[Out]#         -9.04466026,  -9.00408436,  -8.96350845,  -8.92293255,  -8.88235664]),
#[Out]#  <a list of 200 Patch objects>)
# Sat, 14 Jul 2012 00:15:02
elev1d_finite.min()
#[Out]# -16.997538
# Sat, 14 Jul 2012 00:15:06
elev1d_finite.max()
#[Out]# -8.8823566
# Sat, 14 Jul 2012 00:15:10
elev1d_finite.mean()
#[Out]# -13.7989192733795
# Sat, 14 Jul 2012 00:15:18
elev1d_finite.std()
#[Out]# 1.3002059403468114
