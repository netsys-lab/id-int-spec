### Zero

Metadatum                       | Inst | Length |   Unit  | Description
--------------------------------|-----:|-------:|--------:|-----------------------------------------
Zero 2 bytes                    | 0x00 |      2 |         | Insert two zero bytes
Zero 4 bytes                    | 0x40 |      4 |         | Insert four zero bytes
Zero 6 bytes                    | 0x80 |      6 |         | Insert six zero bytes
Zero 8 bytes                    | 0xC0 |      8 |         | Insert eight zero bytes

### Static SCION AS-level

Metadatum                       | Inst | Length |   Unit  | Description
--------------------------------|-----:|-------:|--------:|-----------------------------------------
ISD                             | 0x01 |      2 |         | SCION ISD identifier
ASN                             | 0x81 |      6 |         | SCION AS number
BR link type                    | 0x02 |      2 |         | Ingress+egress link type (L2, BGP, etc.)

### Static device-level

Metadatum                       | Inst | Length |   Unit  | Description
--------------------------------|-----:|-------:|--------:|-----------------------------------------
Device type/role                | 0x03 |      2 |         | First byte is type, second byte is role
Device vendor                   | 0x41 |      4 |         | MAC address vendor identity
Device model                    | 0x42 |      4 |         | Model number
Software version                | 0x43 |      4 |         | Current software version
Node IPv4 address               | 0x44 |      4 |         | Internal IPv4 address
Node IPv6 address (hi)          | 0xC1 |      8 |         | Internal IPv6 address (high order bytes)
Node IPv6 address (lo)          | 0xC2 |      8 |         | Internal IPv6 address (low order bytes)
Ingress IF speed                | 0x45 |      4 |  Mbit/s | Ingress interface HW speed
Egress IF speed                 | 0x46 |      4 |  Mbit/s | Egress interface HW speed
GPS latitude                    | 0x47 |      4 |  degree | IEEE 754 single-precision
GPS longitude                   | 0x48 |      4 |  degree | IEEE 754 single-precision

### Device hardware status

Metadatum                       | Inst | Length |   Unit  | Description
--------------------------------|-----:|-------:|--------:|-----------------------------------------
Uptime                          | 0x49 |      4 |  second | Device uptime in seconds
CPU/Memory usage                | 0x04 |      2 |         |
CPU temperature                 | 0x05 |      2 |  Kelvin |
ASIC temperature                | 0x06 |      2 |  Kelvin | Temperature of the main switch ASIC
Fan speed                       | 0x07 |      2 |     RPM |
Total power draw                | 0x08 |      2 |    Watt | Total instantaneous power draw of the device
Energy mix                      | 0x09 |      2 |         |
Forwarding energy               | 0x4A |      4 |      nJ | Energy for forwarding the packet
CO2 per packet                  | 0x4B |      4 |      pg |

#### Details
- CPU/Memory usage

  Normalized CPU and memory usage
  - CPU Usage = first byte / 255
  - Memory usage = second byte / 255
  
- Energy mix

  Normalized mix of renewable, nuclear, and fossil energy sources
  - Renewable R = first byte / 255
  - Nuclear   N = second byte / 255
  - Fossil    F = 1 - (R + N)
  

### Ingress/Egress port statistics

Metadatum                       | Inst | Length |   Unit  | Description
--------------------------------|-----:|-------:|--------:|-----------------------------------------
Ingress timestamp               | 0x82 |      6 |      ns |
Egress timestamp                | 0x83 |      6 |      ns |
Ingress link RX util            | 0x4C |      4 |  kbit/s |
Egress link TX util             | 0x4D |      4 |  kbit/s |
Ingress SCION-IF pkt count      | 0x84 |      6 | packets |
Egress SCION-IF pkt count       | 0x85 |      6 | packets |
Ingress SCION-IF pkt drop count | 0x86 |      6 | packets |
Egress SCION-IF pkt drop count  | 0x87 |      6 | packets |
Ingress SCION-IF byte count     | 0x88 |      6 |    byte |
Egress SCION-IF byte count      | 0x89 |      6 |    byte |
Ingress total pkt count         | 0x8A |      6 | packets |
Egress total pkt count          | 0x8B |      6 |         |
Ingress total pkt drop count    | 0x8C |      6 | packets |
Egress total pkt drop count     | 0x8D |      6 | packets |
Ingress total byte count        | 0x8E |      6 |    byte |
Egress total byte count         | 0x8F |      6 |    byte |

### Queue and buffer utilization

Metadatum                       | Inst | Length |   Unit  | Description
--------------------------------|-----:|-------:|--------:|-----------------------------------------
Queue ID                        | 0x4E |      4 |         |
Instantaneous queue length      | 0x4F |      4 | packets |
Average queue length            | 0x50 |      4 | packets |
Buffer ID                       | 0x51 |      4 |         |
Instantaneous buffer occupancy  | 0x52 |      4 | packets |
Average buffer occupancy        | 0x53 |      4 | packets |

### No operation

Metadatum                       | Inst | Length |   Unit  | Description
--------------------------------|-----:|-------:|--------:|-----------------------------------------
NOP                             | 0xFF |      0 |         |
