SCION Inter-Domain In-band Network Telemetry Extension
======================================================

The goal of the SCION INT extension is to enable in-band telemetry in an inter-domain context.

Possible applications for INT in SCION are:
- Monitoring and debugging of connection issues
- Provide information for paths selection
- Verification of SLAs

Existing in-band telemetry specifications (such as one from the P4.org Applications Working Group)
do not meet our needs:
- No authentication of telemetry data
- No way to relate telemetry data to SCION hop fields
- Need a way to requests AS-level, BR-level, or internal router telemetry
- Domain-specific metadata does not make sense in an inter-domain setting


ID-INT Main Header
------------------

```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
| Ver |I|D|E|X|F|Mod|Vrf|VT |VL |    Length     |    NextHdr    |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
| DelayHops |Res| RemHopCnt |Res| InstF | AF1 | AF2 | AF3 | AF4 |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|     Inst1     |     Inst2     |     Inst3     |     Inst4     |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                        Source Timestamp                       |
|                               +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-|
|                               |          Source Port          |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|         VerifierISD           |                               | \
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+                               | |
|                          VerifierAS                           | | Only if Vrf == 0
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
- `I` INT between infrastructure nodes (e.g., border routers) instead of end host. The address of
      the verifier is given explicitly in the telemetry header. If set, the border router of the
      destination AS may remove the INT header before the packet reaches the destination host,
      otherwise the INT header should not be removed.
- `D` Discard Packet: Discard the packet at the INT sink. This is useful for probe packets that do
      not carry application data.
- `E` Encrypt the telemetry.
- `X` Max Hop Count exceeded: Some metadata was omitted, because `RemHopCnt` has reached zero.
- `F` Some metadata was omitted, because the stack is full.

##### **Mod** (Aggregation Mode)
- `0` Unlimited stack entries per AS. All border routers and internal routers report telemetry.
- `1` At most one stack entry per AS.
- `2` Telemetry stack entries from ingress and egress BR.
- `3` Stack entries from ingress/egress BR and one internal router.

##### **Vrf** (Verifier)
- `0` Verifier is a 3rd party
- `1` Destination
- `2` Source
- `3` Reserved

##### **VT**
Type of the host address in `VerifierHostAddr` with the same encoding as the `DT`/`ST` fields in the
SCION address header. Must be zero if `V` is not set.

##### **VL**
Length of the host address in `VerifierHostAddr` with the same encoding as the `DT`/`ST` fields in
the SCION address header. Must be zero if `V` is not set.

##### **Length**
Length of the telemetry stack in multiples of 4 bytes.

##### **NextHdr**
Indicates the next header following ID-INT. Equivalent to the NextHdr field in SCION.

##### **DelayHops**
The number of AS-level hops to skip before the first telemetry data is recorded.

##### **RemHopCnt** (Remaining Hop Count)
The maximum number of AS-level hops that are allowed to push telemetry to the stack.

#### **InstF** (Instruction Flags)
Instruction flags for fixed-length metadata.

#### **AF** (Aggregation Function 1-4)
Aggregation function to use for variable length metadata.
- `000b` First (never overwrite)
- `001b` Last (always overwrite)
- `010b` Minimum
- `011b` Maximum
- `100b` Sum

##### **Inst** (Instruction 1-4)
Variable length metadata requests.

##### **Source Timestamp**
48-bit timestamp in nanoseconds for replay suppression. If an INT source does not support nanosecond
precision timestamps, it still has to make sure packets using the same MAC keys have different
timestamps, for example by including a sequence number in the least significant bits.

The timestamp rolls around every ~3.26 days.

##### **Source Port**
Egress port of the INT source. The same source timestamp and egress port should not be reused by the
same INT source until the verification keys have changed.

##### **VerifierID**, **VerifierAS**, **VerifierHostAddr**
SCION address of the verifier if `Vrf == 0`, otherwise omitted.


ID-INT Metadata Header
----------------------
Entries in the telemetry stack have a minimum length of 8 bytes and must be padded to be a multiple
of 4 bytes in length. The metadata stack must contain at least the source metadata
(with flags S set to 1).

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
- `A` (Aggregate) Set if this entry contains aggregated metadata from multiple routers.
- `C` (Encrypted) Set if the stack entry is encrypted. ALso implies the presence of the nonce field.

##### **Hop**
Index of the hop field this stack entry corresponds to.

##### **Mask**
Indicates which of the fixed-length metadata that was requested in the main header is actually
present.

##### **ML** (Metadata Length 1-4)
Length of variable-length metadata slot 1 to 4. A value of zero indicates the metadata is not
present.
- `0xxb` = 0 bytes
- `100b` = 2 bytes
- `101b` = 4 bytes
- `110b` = 6 bytes
- `111b` = 8 bytes

##### **Metadata**
Concatenation of the metadata fields without any special alignment.

##### **MAC**
Message Authentication Code for checking telemetry authenticity.


MAC Computation
---------------
MAC are computed using AES-CMAC with 128 bit keys.

### INT Source
Key: Symmetric key shared between INT source and verifier.
If the source and the verifier are identical, the source can just pick an arbitrary key.

Input block:
```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
| Ver |I|D|E|0|0|Mod|Vrf|VT |VL |       0       |       0       |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|     0     |     0     |   0   | InstF | AF1 | AF2 | AF3 | AF4 |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|     Inst1     |     Inst2     |     Inst3     |     Inst4     |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                        Source Timestamp                       |
|                               +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-|
|                               |          Source Port          |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|         VerifierISD           |                               | \
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+                               | |
|                          VerifierAS                           | | Only if Vrf == 0
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

### INT Transit Hops
Key: Symmetric key shared between transit node and verifier.

Input block:
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


Supported Metadata
------------------
### Fixed-Length Metadata
Some types of metadata are very likely to be used in combination with other metadata. To avoid
taking up slots for variable-length metadata, these metadata items have their own separate
instruction bitmap.

- Node ID (4 bytes)
- Node count (2 bytes)
- Ingress device-level interface identifier (2 bytes)
- Egress device-level interface identifier (2 bytes)

### Variable-Length Metadata
- [Metadata List](metadata/metadata.md)
- [Assigned Instructions Overview](metadata/instructions.md)

#### Instruction Encoding
```
Bit 01234567
    llriiiii

- Bit 0:1 : Length of the corresponding metadata
  - 00 = 2 bytes
  - 01 = 4 bytes
  - 10 = 6 bytes
  - 11 = 8 bytes
- Bit 2   : Reserved, must be 0
- Bit 3:7 : Instruction
```
