import can
import cantools

# Load DBC file
db = cantools.database.Database()
db.add_dbc_file('examples\data-processing\dbc_files\can1-honda_civic_hatchback_ex_2017_can_generated.dbc')

# Set up the PeakCAN interface
can.rc['interface'] = 'pcan'
can.rc['channel'] = 'PCAN_USBBUS1'
can.rc['bitrate'] = 500000

# Create CAN bus instance
bus = can.interface.Bus()

try:
    while True:
        message = bus.recv()  # Receive CAN message
        decoded_message = db.decode_message(message.arbitration_id, message.data)
        print(decoded_message)
except KeyboardInterrupt:
    bus.shutdown()
