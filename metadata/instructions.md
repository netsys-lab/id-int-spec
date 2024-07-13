Inst | Length | Written in | Metadatum
----:|-------:|-----------:|-------------------------------------
0x00 |      2 |    ingress | Zero 2 bytes
0x01 |      2 |    ingress | ISD
0x02 |      2 |    ingress | BR link type
0x03 |      2 |    ingress | Device type/role
0x04 |      2 |    ingress | CPU/Memory usage
0x05 |      2 |    ingress | CPU temperature
0x06 |      2 |    ingress | ASIC temperature
0x07 |      2 |    ingress | Fan speed
0x08 |      2 |    ingress | Total power draw
0x09 |      2 |    ingress | Energy mix
0x40 |      4 |    ingress | Zero 4 bytes
0x41 |      4 |    ingress | Device vendor
0x42 |      4 |    ingress | Device model
0x43 |      4 |    ingress | Software version
0x44 |      4 |    ingress | Node IPv4 address
0x45 |      4 |    ingress | Ingress IF speed
0x46 |      4 |    ingress | Egress IF speed
0x47 |      4 |    ingress | GPS latitude
0x48 |      4 |    ingress | GPS longitude
0x49 |      4 |    ingress | Uptime
0x4A |      4 |     egress | Forwarding energy
0x4B |      4 |     egress | CO2 per packet
0x4C |      4 |    ingress | Ingress link RX util
0x4D |      4 |     egress | Egress link TX util
0x4E |      4 |     egress | Queue ID
0x4F |      4 |     egress | Instantaneous queue length
0x50 |      4 |     egress | Average queue length
0x51 |      4 |     egress | Buffer ID
0x52 |      4 |     egress | Instantaneous buffer occupancy
0x53 |      4 |     egress | Average buffer occupancy
0x80 |      6 |    ingress | Zero 6 bytes
0x81 |      6 |    ingress | ASN
0x82 |      6 |    ingress | Ingress timestamp
0x83 |      6 |     egress | Egress timestamp
0x84 |      6 |    ingress | Ingress SCION-IF pkt count
0x85 |      6 |     egress | Egress SCION-IF pkt count
0x86 |      6 |    ingress | Ingress SCION-IF pkt drop count
0x87 |      6 |     egress | Egress SCION-IF pkt drop count
0x88 |      6 |    ingress | Ingress SCION-IF byte count
0x89 |      6 |     egress | Egress SCION-IF byte count
0x8A |      6 |    ingress | Ingress total pkt count
0x8B |      6 |     egress | Egress total pkt count
0x8C |      6 |    ingress | Ingress total pkt drop count
0x8D |      6 |     egress | Egress total pkt drop count
0x8E |      6 |    ingress | Ingress total byte count
0x8F |      6 |     egress | Egress total byte count
0xC0 |      8 |    ingress | Zero 8 bytes
0xC1 |      8 |    ingress | Node IPv6 address (hi)
0xC2 |      8 |    ingress | Node IPv6 address (lo)
0xFF |      0 |    ingress | NOP
