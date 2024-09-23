ID-INT: Inter-Domain In-band Network Telemetry
==============================================

ID-INT (inter-domain in-band network telemetry) is an extension to the SCION
Internet architecture that allows routers of different ASes to share telemetry
information with other outers and end host via INT headers.

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

The ID-INT header is inserted between the SCION hop-by-hop and end-to-end option
headers. If no other options are present, ID-INT immediately follows the SCION
header (ane the path contained within the SCION header). ID-INT is not a
hop-by-hop extension header itself to simplify parsing in hardware routers and
to allow for a larger maximum size. ID-INT is identifyied by a value of 253 in
the next header field of the SCION or hop-by-hop extension header. 253 is
reserved for experiments by the SCION specification and will be replaced with a
standardized value in the future.

In the following, we describe the layout and semantics of the ID-INT header and
the telemetry stack entries it contains.

### ID-INT Main Header
The ID-INT main header not including the telemetry stack is 20 to 40 bytes long.

```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
| Ver |I|D|E|X|R|Mod|Vrf|VT |VL |    Length     |    NextHdr    |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
| DelayHops |Res|  MaxStackLen  | InstF | AF1 | AF2 | AF3 | AF4 |
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
|                        Telemetry Stack                        |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                              ...                              |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

##### **Ver** (Version)
Version of the telemetry header. Currently 0.

##### **Flags**
- `I` INT between infrastructure nodes (e.g., border routers) instead of end
      host. If set, the border router of the destination AS may remove the INT
      header before the packet reaches the destination host, otherwise the INT
      header should not be removed.
- `D` Discard Packet: Discard the packet at the INT sink. This is useful for
      probe packets that do not carry application data.
- `E` Encrypt the telemetry.
- `X` Max header size exceeded: Some metadata was omitted, because `Length`
      would have exceeded `MaxStackLen`.
- `R` Reserved. Must be zero.

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

##### **Length**
Length of the telemetry stack in multiples of 4 bytes.

##### **NextHdr**
Indicates the next header following ID-INT. Equivalent to the NextHdr field in
SCION.

##### **DelayHops**
The number of AS-level hops to skip before the first telemetry data is recorded.

##### **MaxStackLen**
Maximum length of the telemetry stack in multiples of 4 bytes. If pushing
another entry would increase the stack size beyond this value, the entry is not
pushed and the `X` flag is set.

#### **InstF** (Instruction Flags)
Instruction flags requesting a subset of the four default metadata.

#### **AF** (Aggregation Function 1-4)
Aggregation function to use for each of the four metadata slots corresponding to
instruction byte `Inst1` to `Inst4`.
- `000b` First (never overwrite)
- `001b` Last (always overwrite)
- `010b` Minimum
- `011b` Maximum
- `100b` Sum

##### **Inst** (Instruction 1-4)
Metadata request instructions for slot 1 to 4.

##### **Source Timestamp**
48-bit timestamp in nanoseconds for replay suppression. If an INT source does
not support nanosecond precision timestamps, it still has to make sure packets
using the same MAC keys have different timestamps, for example by including a
sequence number in the least significant bits.

The keys used to authenticate and encrypt telemetry stack entries must be valid
at the point in time identified by the source timestamp.

The timestamp rolls around every ~3.26 days.

##### **Source Port**
Egress port of the INT source. The same source timestamp and egress port should
not be reused by the same INT source until the verification keys have changed.

##### **VerifierID**, **VerifierAS**, **VerifierHostAddr**
SCION address of the verifier if `Vrf == 0`, otherwise omitted.

##### Telemetry Stack
The length of the telemetry stack is always a multiple of 4 bytes and all
entries are 4-byte aligned. The stack is extended by inserting new stack entries
at the top causing the entire packet to grow. At any point, the stack must
contain at least one entry, called the source entry, which is added by the node
inserting ID-INT into the header stack.

#### Telemetry Stack Entries
Entries in the telemetry stack have a minimum length of 8 bytes and must be
padded to be a multiple of 4 bytes in length. The metadata stack must contain at
least the source metadata (with flag `S` set to 1).

```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|S|I|E|A|C| Res |    Hop    |Res| Mask  | ML1 | ML2 | ML3 | ML4 |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                                                               | \
|                             Nonce                             | | If encrypted
|                                                               | /
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                           Metadata                            |
|                               +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                               |  Padding to a multiple of 4B  |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                              MAC                              |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

##### **Flags**
- `S` (Source)    Set for source metadata.
- `I` (Ingress)   Set if this entry corresponds to an ingress BR.
- `E` (Egress)    Set if this entry corresponds to an egress BR.
- `A` (Aggregate) Set if this entry contains aggregated metadata from multiple
                  routers.
- `C` (Encrypted) Set if the stack entry is encrypted. If set the nonce field
                  must be present.

##### **Hop**
Index of the hop field this stack entry corresponds to. If the entry corresponds
to multiple hop fields, the index of the first hop field the entry relates to.

##### **Mask**
Metadata presence flags, indication which of the default metadata are present.
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
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
| Ver |I|D|E|0|0|Mod|Vrf|VT |VL |       0       |       0       |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|       0       |  MaxStackLen  | InstF | AF1 | AF2 | AF3 | AF4 |
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
|1|I|E|0|C|  0  |    Hop    | 0 | Mask  | ML1 | ML2 | ML3 | ML4 |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                                                               | \
|                             Nonce                             | | If encrypted
|                                                               | /
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                           Metadata                            |
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
|S|I|E|A|C|  0  |    Hop    | 0 | Mask  | ML1 | ML2 | ML3 | ML4 |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                                                               | \
|                             Nonce                             | | If encrypted
|                                                               | /
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                           Metadata                            |
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
Telemetry is requested in two different ways. Information identifying a node and
the interfaces taken by the packet are requested using instruction flags.
Additionally, there is an instruction flags for requesting the number of
telemetry entries that have been aggregated into one. All other metadata is
requested using an instruction byte in one of the four instruction slots of the
ID-INT main header.

#### Metadata Instructions
There are four slots for metadata instructions. Each slot can contain any
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

The full table of all metadata instructions is given
[here](metadata/instructions.md).
