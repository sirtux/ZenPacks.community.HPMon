################################################################################
#
# This program is part of the HPMon Zenpack for Zenoss.
# Copyright (C) 2008, 2009, 2010, 2011 Egor Puzanov.
#
# This program can be used under the GNU General Public License version 2
# You can find full information here: http://www.zenoss.com/oss
#
################################################################################

__doc__="""HPFcaCntlrMap

HPFcaCntlrMap maps the cpqFcaCntlrTable table to cpqFcaCntlr objects

$Id: HPFcaCntlrMap.py,v 1.3 2011/01/05 00:18:09 egor Exp $"""

__version__ = '$Revision: 1.3 $'[11:-2]

from Products.DataCollector.plugins.CollectorPlugin import GetTableMap
from Products.DataCollector.plugins.DataMaps import MultiArgs
from HPExpansionCardMap import HPExpansionCardMap

class HPFcaCntlrMap(HPExpansionCardMap):
    """Map HP/Compaq insight manager cpqFcaCntlrTable table to model."""

    maptype = "cpqFcaCntlr"
    modname = "ZenPacks.community.HPMon.cpqFcaCntlr"

    snmpGetTableMaps = (
        GetTableMap('cpqFcaCntlrTable',
                    '.1.3.6.1.4.1.232.16.2.2.1.1',
                    {
                        '.1': 'chassis',
                        '.3': 'setProductKey',
                        '.4': 'FWRev',
                        '.5': 'status',
                        '.8': 'wwpn',
                        '.9': 'serialNumber',
                        '.10': 'role',
                        '.11': 'redundancyType',
                        '.14': 'wwnn',
                    }
        ),
        GetTableMap('cpqSsChassisTable',
                    '.1.3.6.1.4.1.232.8.2.2.1.1',
                    {
                        '.4': 'name',
                    }
        ),
    )

    models = {1: 'Unknown Fibre Channel Array Controller',
            2: 'Compaq StorageWorks RAID Array 4000/4100 Controller',
            3: 'Compaq StorageWorks Modular Smart Array 1000 Controller',
            4: 'HP StorageWorks Modular Smart Array 500 Controller',
            5: 'Compaq StorageWorks Enterprise/Modular RAID Array Controller',
            6: 'Compaq StorageWorks Enterprise Virtual Array Controller',
            7: 'HP StorageWorks Modular Smart Array 500 G2 Controller',
            8: 'HP StorageWorks Modular Smart Array 20 Controller',
            9: 'HP StorageWorks Modular Smart Array 1500 CS Controller',
            10: 'HP StorageWorks Modular Smart Array 1510i Controller',
            11: 'HP StorageWorks Modular Smart Array 2060s Controller',
            12: 'HP StorageWorks Modular Smart Array 2070s Controller',
            }

    redundancyTypes =  {1: 'other',
                        2: 'No Redundancy',
                        3: 'Active-Standby',
                        4: 'Primary-Secondary',
                        5: 'Active-Active',
                        }

    def process(self, device, results, log):
        """collect snmp information from this device"""
        log.info('processing %s for device %s', self.name(), device.id)
        getdata, tabledata = results
        chassismap = {}
        for oid, chassis in tabledata.get('cpqSsChassisTable', {}).iteritems():
            chassismap[oid.strip('.')] = chassis['name']
        external = 'community.snmp.HPSsChassisMap' in getattr(device,
                                                        'zCollectorPlugins', [])
        if not device.id in HPExpansionCardMap.oms:
            HPExpansionCardMap.oms[device.id] = []
        for oid, card in tabledata.get('cpqFcaCntlrTable', {}).iteritems():
            try:
                om = self.objectMap(card)
                om.snmpindex = oid.strip('.')
                om.id=self.prepId("cpqFcaCntlr%s"%om.snmpindex.replace('.','_'))
                om.slot = getattr(om, 'slot', 0)
                model = self.models.get(int(getattr(om, 'setProductKey', 1)),
                    '%s (%s)'%(self.models[1], getattr(om, 'setProductKey', 1)))
                om.setProductKey = MultiArgs(model, model.split()[0])
                om.redundancyType = self.redundancyTypes.get(getattr(om,
                                        'redundancyType', 1), om.redundancyType)
                om.chassis = chassismap.get(om.chassis, '')
                om.external = external
            except AttributeError:
                continue
            HPExpansionCardMap.oms[device.id].append(om)
        return

