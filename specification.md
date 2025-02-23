ID-INT: Inter-Domain In-band Network Telemetry
==============================================

ID-INT (Inter-Domain In-band Network Telemetry) is an extension to the SCION
Internet architecture that allows routers of different ASes to share telemetry
information with other routers and end hosts via hop-by-hop extension header
options.

ID-INT has many applications, including:
- Providing richer network debugging information than possible with ping and
  traceroute
- Intra-AS path tracing
- Intelligent path selection
- Telemetry-augmented congestion control
- SLA verification
- Carbon aware routing

ID-INT Features:
- Fully implementable in the data plane on the router's fast path
- Universal set of telemetry instructions useful to SCION
- Per-AS telemetry aggregation to reduce header size and protect confidential
  information
- Telemetry is authenticated using MACs
- Telemetry can optionally be encrypted
- Uses DRKey to efficiently derive cryptographic keys in routers
- Support for source authentication

ID-INT Data Plane Specification
-------------------------------

ID-INT defines two new types of option headers that are inserted in the SCION
hop-by-hop extension header. The new options are the *IdIntOption* and
*IdIntEntry*. IdIntOption is the main ID-INT header containing instructions
for border routers and marking the packet as an ID-INT probe. IdIntEntries
contain the telemetry responses from routers and must immediately follow the
IdIntOption without any other option types in between. In other words, a packet
may have at most one IdIntOption, but usually contains more than on IdIntEntry
option.

IdIntEntries form a stack that grows from top (lowest address) to bottom
(highest address). The space for all IdIntEntry options is preallocated by the
INT source. Unused space is filled with *PadN* options that immediately follow
the last IdIntEntry option. IdIntEntries must be aligned at 4-byte boundaries
and have a length that is a multiple of 4 bytes, therefore the padding options
also must be a multiple of 4 bytes in size.

An ID-INT SCION packet with not other hop-by-hop options and additional
end-to-end options has to following layout:
```
###[ IP ]###
###[ UDP ]###
###[ SCION ]###
        NextHdr   = HopByHopExt
        \Path      \
         |###[ SCION Path ]###
         |  \InfoFields\
         |  \HopFields \
###[ SCION Hop-by-Hop Options ]###
           NextHdr   = EndToEndExt
           ExtLen    = 24
           \Options   \
            |###[ ID-INT ]###
            |  opt_type  = 2
            |  \stack     \
            |   |###[ IdIntEntry ]###
            |   |  opt_type  = 3
            |   |  flags     = source
            |   |###[ IdIntEntry ]###
            |   |###[ IdIntEntry ]###
            |   |###[ PadN ]###
            |   |  OptType   = 1
            |   |  OptDataLen= 2
            |   |  OptData   = 0000
###[ SCION End-to-End Options ]###
              NextHdr   = UDP
###[ UDP ]###
```

```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|            SCION Main, Address, and Path Header               |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|    NextHdr    |     ExtLen    |                               |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+                               |
|                       ID-INT Main Option                      |
/                              ...                              /
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                        Source Telemetry                       |
/                              ...                              /
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
/                 ... more telemetry options ...                /
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|        One or multiple PadN options bringing the total        /
|        length of the telemetry stack to AllocStackLen         /
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
/          Remaining HBH option not related to ID-INT           /
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

In the following, we describe the layout and semantics of the IdIntOption and
IdIntEntry header and the telemetry data they contain.

### ID-INT Main Option Header (IdIntOption)

The ID-INT main option header is between 22 and 46 bytes long depending on
whether a verifier address is included and how long the host part of this
address is. The option must be aligned two bytes past a four byte boundary, i.e.
as 4n+2 for an integer n. Such alignment allows the main option header to
directly follow the HBH option header without additional padding. If another
option precedes the ID-INT main option header, padding options must be inserted.

```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
                                +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
                                |    OptType    |   OptDatLen   |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
| Ver |I|D|E|X|R|Mod|Vrf|VT |VL |   StackLen    |      TOS      |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
| DelayHops |      Reserved     | InstF | AF1 | AF2 | AF3 | AF4 |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|     Inst1     |     Inst2     |     Inst3     |     Inst4     |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                        Source Timestamp                       |
|                               +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-|
|                               |          Source Port          |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|         VerifierISD           |                               | \
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+                               | |
|                          VerifierAS                           | | If Vrf == 0
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+ |
|                       VerifierHostAddr (4-16 bytes)           | |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+ /
```

##### **OptType**
SCION hop-by-hop option type.

#### **OptDataLen**
Length of the ID-INT main header in bytes. Does not include the telemetry stack
entries which are stored in their own options.

##### **Ver** (Version)
Version of the telemetry header. Currently 0.

##### **Flags**
- `I` Infrastructure Mode. If ID-INT probes are exchanged between infrastructure
      nodes (e.g., border routers) instead of end host, this flag must be set.
      In infrastructure mode, the border router of the destination AS may remove
      the ID-INT option headers before the packet reaches the destination host,
      otherwise the ID-INT options must not be removed.
- `D` Discard Packet. Discard the packet at the telemetry sink. In Host-ID-INT
      mode, the sink is the end host or ID-INT compatible application. If the
      discard flag is set, the end host stack or application should ignore the
      packet's payload. In Infrastructure mode, the entire packet should be
      discarded by the sink before it is delivered to an end host.
- `E` Encrypted telemetry. Enable encryption of the telemetry payload in the
      IdIntEntry options.
- `X` Telemetry stack space exhausted. Set by ID-INT nodes when no more
      telemetry data could be added to the telemetry stack, because the
      source-allocated space was exhausted.
- `R` Reserved. Must be set to zero.

##### **Mod** (Aggregation Mode)
- `0` Unlimited stack entries per AS. All border routers and internal routers
      report telemetry.
- `1` At most one stack entry per AS.
- `2` Telemetry stack entries from ingress and egress BR.
- `3` Stack entries from ingress/egress BR and one internal router.

##### **Vrf** (Verifier)
- `0` Verifier is a 3rd party
- `1` Destination
- `2` Source
- `3` Reserved

##### **VT**
Type of the host address in `VerifierHostAddr` with the same encoding as the
`DT`/`ST` fields in the SCION address header. Must be zero if `V` is not set.

##### **VL**
Length of the host address in `VerifierHostAddr` with the same encoding as the
`DT`/`ST` fields in the SCION address header. Must be zero if `V` is not set.

##### **StackLen**
Allocated space for the telemetry stack in multiples of 4 bytes. The combined
size of all telemetry options following the ID-INT main option must never exceed
this value. The ID-INT-source is responsible for reserving StackLen bytes
directly follosing the ID-INT main option header by inserting one or more
padding options.

##### **TOS** (Top of Stack)
Offset of the first byte of the last (most recently written) entry on the
telemetry stack in multiples of 4 bytes. The ID-INT source must initialize TOS
to zero and initialize the telemetry stack by pushing (potentially empty) source
telemetry.

#### **InstF** (Instruction Flags)
Instruction bitmap requesting a subset of the four bitmap-controlled telemetry
data types.

#### **AF** (Aggregation Function 1-4)
Aggregation function to use for each of the four metadata slots corresponding to
instruction byte `Inst1` to `Inst4`.
- `000b` First (never overwrite)
- `001b` Last (always overwrite)
- `010b` Minimum
- `011b` Maximum
- `100b` Sum

##### **DelayHops**
The number of AS-level hops to skip before the first telemetry data is recorded.

##### **Reserved**
Reserved. Must be set to zero when written and ignored when read.

##### **Inst** (Instruction 1-4)
Metadata request instructions for slot 1 to 4.

##### **Source Timestamp**
48-bit timestamp in nanoseconds for replay suppression. If an ID-INT source does
not support nanosecond precision timestamps, it still has to make sure packets
using the same MAC keys have different timestamps, for example by including a
sequence number in the least significant bits.

The keys used to authenticate and encrypt telemetry stack entries must be valid
at the point in time identified by the source timestamp.

The timestamp rolls around every ~3.26 days. The DRKey key epoch must not be
longer than permitted by the timestamp roll-around.

##### **Source Port**
Egress port of the INT source. The same source timestamp and egress port should
not be reused by the same ID-INT source until the verification keys have
changed.

##### **VerifierID**, **VerifierAS**, **VerifierHostAddr**
SCION address of the verifier if `Vrf == 0`, otherwise omitted.

### ID-INT Telemetry Stack

The telemetry stack immediately follows the ID-INT main option header. It
consists of a non-empty sequence of IdIntEntry options followed by zero or
more padding options to fill out unused reserved telemetry stack space.

Telemetry stack entries are variable size, but their length is always a multiple
of 4 bytes. Given the alignment requirements and size of the ID-INT main option,
entries on the telemetry stack are aligned to 4 byte boundaries.

The telemetry stack grows from top (lowest address) to bottom (highest address)
by replacing reserved stack space occupied by padding options with IdIntOption
headers. ID-INT nodes that append to the stack must ensure that the remaining
unused stack space is occupied by valid padding options. The recommended way to
ensure correct stack padding is to write a PadN option header immediately after
the last stack entry that fills out the entire remaingin space. Doing so
requires writing only two bytes, the PadN option type (OptType = 1) and length
(OptDataLen). The content of the padding data can remain unchanged as it is
ignored. The only situation in which no new padding header should be written is
when the remaining unused stack size after writing the current node's telemetry
data is exactly zero.

At any point, the stack must contain at least IdIntEntry options, called the
source entry, which is inserted simultaneously with the main option by the
ID-INT source.

#### ID-INT Stack Entry Option Header (IdIntEntry)
Entries in the telemetry stack have a minimum length of 8 bytes and must be
padded to multiple of 4 bytes in length. The metadata stack must contain at
least the source metadata (with flag `S` set to 1).

```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|    OptType    |  OptDataLen   |S|I|E|A|C| Res |    Hop    |Res|
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
| Mask  | ML1 | ML2 | ML3 | ML4 |                               | \
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+                               | |
|                          Nonce (96 bit)                       | | If encrypted
|                               +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+ |
|                               |                               | /
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+                               |
|                       Metadata (variable size)                |
|                               +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                               |  Padding to a multiple of 4B  |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                              MAC                              |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

##### **OptType**
SCION hop-by-hop option type.

#### **OptDataLen**
Length of the stack entry in bytes. Always a multiple of four.

##### **Flags**
- `S` (Source)    Set for source metadata.
- `I` (Ingress)   Set if this entry corresponds to an ingress BR.
- `E` (Egress)    Set if this entry corresponds to an egress BR.
- `A` (Aggregate) Set if this entry contains aggregated metadata from multiple
                  routers.
- `C` (Encrypted) Set if the stack entry is encrypted. If set, the nonce field
                  must be present.

##### **Res**
Reserved. Must be set to zero when written and ignored when read.

##### **Hop**
Index of the hop field this stack entry corresponds to. If the entry corresponds
to multiple hop fields, the index of the first hop field the entry relates to.

##### **Mask**
Bitmap-controlled telemetry data presence mask. Corresponds the the instruction
bitmap in the main option header and indicates which of the requested types of
telemetry are actually present in this stack entry. Each of the four
bitmap-controlled telemetry types has fixed length as indicated below.
- Bit 0: Node ID (4 bytes)
- Bit 1: Node count (2 bytes)
- Bit 2: Ingress device-level interface identifier (2 bytes)
- Bit 4: Egress device-level interface identifier (2 bytes)

##### **ML** (Metadata Length 1-4)
Length of metadata corresponding to instruction slot 1 to 4. A value of zero
indicates the metadata is not present. Encoding:
- `0xxb` = 0 bytes
- `100b` = 2 bytes
- `101b` = 4 bytes
- `110b` = 6 bytes
- `111b` = 8 bytes

##### **Reserved**
Reserved. Must be set to zero when written and ignored when read.

#### **Nonce**
12-byte random nonce for decrypting the metadata. Only present if `C` flag is
set. With a 12-byte nonce, the probability of a collision in 2^32 messages is
approximately 1.16e-10, for 2^48 the probability is ~0.4.

##### **Metadata**
Concatenation of the metadata fields without any padding or alignment.

##### **MAC**
Message Authentication Code for checking telemetry authenticity.

### Message Authentication Codes
MACs are computed using AES-CBC with a fixed initialization vector of 0. Stack
entries are chained by including the MAC of the previous entry in the next one.
The source entry is computed in a special way and includes fields from the main
header. All keys have a length of 128 bit matching SCION's DRKey.

The keys for MAC computation are derived between router and verifier using
DRKey. As a special case, if the INT source and the verifier are the same (i.e.,
the verifier is set to `Source` in the main header), the source can pick an
arbitrary secret key to MAC the source metadata.

#### Source MAC Calculation
The source MAC is calculated over:
```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
                                +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
                                |    OptType    |   OptDatLen   |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
| Ver |I|D|E|X|R|Mod|Vrf|VT |VL |   StackLen    |       0       |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|     0     |         0         | InstF | AF1 | AF2 | AF3 | AF4 |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|     Inst1     |     Inst2     |     Inst3     |     Inst4     |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                        Source Timestamp                       |
|                               +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-|
|                               |          Source Port          |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|         VerifierISD           |                               | \
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+                               | |
|                          VerifierAS                           | | If Vrf == 0
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+ |
|                       VerifierHostAddr (4-16 bytes)           | /
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|    OptType    |  OptDataLen   |1|I|E|0|C|  0  |    Hop    | 0 |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
| Mask  | ML1 | ML2 | ML3 | ML4 |                               | \
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+                               | |
|                          Nonce (96 bit)                       | | If encrypted
|                               +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+ |
|                               |                               | /
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+                               |
|                       Metadata (variable size)                |
|                               +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                               |  Padding to a multiple of 4B  |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

#### Regular MAC Calculation
The MAC of the second and all following telemetry stack entries is calculated
over:
```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|    OptType    |  OptDataLen   |S|I|E|A|C|  0  |    Hop    | 0 |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
| Mask  | ML1 | ML2 | ML3 | ML4 |                               | \
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+                               | |
|                          Nonce (96 bit)                       | | If encrypted
|                               +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+ |
|                               |                               | /
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+                               |
|                       Metadata (variable size)                |
|                               +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                               |  Padding to a multiple of 4B  |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                    MAC of the previous hop                    |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

### Encryption
If encryption is enabled, stack entries are authenticated and encrypted using a
modified AES-CCM (Counter with CBC-MAC) AEAD construction. AES-CCM first
computes the CBC-MAC as for unencrypted stack entries. In addition to the
regular header and metadata fields, the MAC must contain a 12-byte nonce used
for encryption and included in each stack entry. Encryption itself is performed
using AES in counter mode (AES-CTR). The (padded) metadata and MAC computed in
the previous step are encrypted by XORing with the the ramdom bit stream
produced by AES-CTR. The nonce must not repeat under the same key and should be
selected randomly for every packet.

### Telemetry Instructions
Telemetry instructions are encoded using a combination of a 4-bit bitmap and
four 8-bit integers. The 4-bit bitmap requests so called bitmap-controlled
telemetry data. The bitmap-controlled telemetry is used to identify an ID-INT
node and node interface in order to determine the precise source a telemetry
response. The four 8-bit integer instruction slots request status information
from a remote data plane, they do not use a bitmap in order to save space in the
header.

#### Telemetry Instructions
There are four slots for telemetry instructions. Each slot can contain any
instruction. Telemetry instructions are encoded as follows:
```
Bit 01234567
    llriiiii
```
- Bit 0:1 : Length of the corresponding metadata
  - 00 = 2 bytes
  - 01 = 4 bytes
  - 10 = 6 bytes
  - 11 = 8 bytes
- Bit 2   : Reserved, must be 0
- Bit 3:7 : Instruction

[Telemetry Instruction Table](metadata/instructions.md)
