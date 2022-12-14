// Metadata Instructions
enum bit<8> idint_mdid_t {
    ZERO_2           = 0x00,
    ISD              = 0x01,
    BR_LINK_TYPE     = 0x02,
    DEVICE_TYPE_ROLE = 0x03,
    CPU_MEM_USAGE    = 0x04,
    CPU_TEMP         = 0x05,
    ASIC_TEMP        = 0x06,
    FAN_SPEED        = 0x07,
    TOTAL_POWER      = 0x08,
    ENERGY_MIX       = 0x09,
    ZERO_4           = 0x40,
    DEVICE_VENDOR    = 0x41,
    DEVICE_MODEL     = 0x42,
    SOFTWARE_VERSION = 0x43,
    NODE_IPV4_ADDR   = 0x44,
    INGRESS_IF_SPEED = 0x45,
    EGRESS_IF_SPEED  = 0x46,
    UPTIME           = 0x47,
    FWD_ENERGY       = 0x48,
    CO2_EMISSION     = 0x49,
    INGRESS_LINK_RX  = 0x4A,
    EGRESS_LINK_TX   = 0x4B,
    QUEUE_ID         = 0x4C,
    INST_QUEUE_LEN   = 0x4D,
    AVG_QUEUE_LEN    = 0x4E,
    BUFFER_ID        = 0x4F,
    INST_BUFFER_OCC  = 0x50,
    AVG_BUFFER_OCC   = 0x51,
    ZERO_6           = 0x80,
    ASN              = 0x81,
    INGRESS_TSTAMP   = 0x82,
    EGRESS_TSTAMP    = 0x83,
    IG_SCIF_PKT_CNT  = 0x84,
    EG_SCIF_PKT_CNT  = 0x85,
    IG_SCIF_PKT_DROP = 0x86,
    EG_SCIF_PKT_DROP = 0x87,
    IG_SCIF_BYTES    = 0x88,
    EG_SCIF_BYTES    = 0x89,
    IG_PKT_CNT       = 0x8A,
    EG_PKT_CNT       = 0x8B,
    IG_PKT_DROP      = 0x8C,
    EG_PKT_DROP      = 0x8D,
    IG_BYTES         = 0x8E,
    EG_BYTES         = 0x8F,
    ZERO_8           = 0xC0,
    NODE_IPV6_ADDR_H = 0xC1,
    NODE_IPV6_ADDR_L = 0xC2,
    GPS_LAT          = 0xC3,
    GPS_LONG         = 0xC4
}
