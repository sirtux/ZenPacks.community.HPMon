################################################################################
#
# This program is part of the HPMon Zenpack for Zenoss.
# Copyright (C) 2008, 2009, 2010, 2011 Egor Puzanov.
#
# This program can be used under the GNU General Public License version 2
# You can find full information here: http://www.zenoss.com/oss
#
################################################################################

__doc__="""HPExpansionCardMap

HPExpansionCardMap maps the cpqSePciSlotTable table to cards objects

$Id: HPExpansionCardMap.py,v 1.3 2011/01/05 00:13:35 egor Exp $"""

__version__ = '$Revision: 1.3 $'[11:-2]

from Products.DataCollector.plugins.CollectorPlugin import SnmpPlugin, GetTableMap
from Products.DataCollector.plugins.DataMaps import MultiArgs

class HPExpansionCardMap(SnmpPlugin):
    """Map HP/Compaq insight manager PCI table to model."""

    maptype = "HPExpansionCardMap"
    modname = "ZenPacks.community.HPMon.cpqSePciSlot"
    relname = "cards"
    compname = "hw"
    deviceProperties = \
                SnmpPlugin.deviceProperties + ( 'zHPExpansionCardMapIgnorePci',)

    oms = {}

    snmpGetTableMaps = (
        GetTableMap('cpqSePciSlotTable',
                    '.1.3.6.1.4.1.232.1.2.13.1.1',
                    {
                        '.3': 'slot',
                        '.5': 'setProductKey',
                    }
        ),
    )

    def process(self, device, results, log):
        """collect snmp information from this device"""
        log.info('processing %s for device %s', self.name(), device.id)
        if not device.id in self.oms:
            self.oms[device.id] = []
        rm = self.relMap()
        ignorepci = getattr(device, 'zHPExpansionCardMapIgnorePci', False)
        if not ignorepci:
            getdata, tabledata = results
            pcimap = {}
            for om in self.oms[device.id]:
                if om.modname == "ZenPacks.community.HPMon.cpqSiMemModule":
                    continue
                pcimap[int(om.slot)] = 1
            for oid, card in tabledata.get('cpqSePciSlotTable', {}).iteritems():
                try:
                    om = self.objectMap(card)
                    om.snmpindex = oid.strip('.')
                    if int(om.slot) == 0: continue
                    if int(om.slot) in pcimap: continue
                    om.id = self.prepId("cpqSePciSlot%d" % om.slot)
                    if not getattr(om, 'setProductKey', ''):
                        om.setProductKey = 'Unknown Card'
                    om.setProductKey = MultiArgs(om.setProductKey,
                                                om.setProductKey.split()[0])
                except AttributeError:
                    continue
                self.oms[device.id].append(om)
        for om in self.oms[device.id]:
            rm.append(om)
        del self.oms[device.id]
        return rm
