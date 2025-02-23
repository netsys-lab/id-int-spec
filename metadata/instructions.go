// ID-INT instructions
const (
    IdIntINop              = 0x00
    IdIntIIsd              = 0x01
    IdIntIBrLinkType       = 0x02
    IdIntIDeviceTypeRole   = 0x03
    IdIntICpuMemUsage      = 0x04
    IdIntICpuTemp          = 0x05
    IdIntIAsicTemp         = 0x06
    IdIntIFanSpeed         = 0x07
    IdIntITotalPower       = 0x08
    IdIntIEnergyMix        = 0x09
    IdIntIDeviceVendor     = 0x41
    IdIntIDeviceModel      = 0x42
    IdIntISoftwareVersion  = 0x43
    IdIntINodeIpv4Addr     = 0x44
    IdIntIIngressIfSpeed   = 0x45
    IdIntIEgressIfSpeed    = 0x46
    IdIntIGpsLat           = 0x47
    IdIntIGpsLong          = 0x48
    IdIntIUptime           = 0x49
    IdIntIFwdEnergy        = 0x4A
    IdIntICo2Emission      = 0x4B
    IdIntIIngressLinkRx    = 0x4C
    IdIntIEgressLinkTx     = 0x4D
    IdIntIQueueId          = 0x4E
    IdIntIInstQueueLen     = 0x4F
    IdIntIAvgQueueLen      = 0x50
    IdIntIBufferId         = 0x51
    IdIntIInstBufferOcc    = 0x52
    IdIntIAvgBufferOcc     = 0x53
    IdIntIAsn              = 0x81
    IdIntIIngressTstamp    = 0x82
    IdIntIEgressTstamp     = 0x83
    IdIntIIgScifPktCnt     = 0x84
    IdIntIEgScifPktCnt     = 0x85
    IdIntIIgScifPktDrop    = 0x86
    IdIntIEgScifPktDrop    = 0x87
    IdIntIIgScifBytes      = 0x88
    IdIntIEgScifBytes      = 0x89
    IdIntIIgPktCnt         = 0x8A
    IdIntIEgPktCnt         = 0x8B
    IdIntIIgPktDrop        = 0x8C
    IdIntIEgPktDrop        = 0x8D
    IdIntIIgBytes          = 0x8E
    IdIntIEgBytes          = 0x8F
    IdIntINodeIpv6AddrH    = 0xC1
    IdIntINodeIpv6AddrL    = 0xC2
)
