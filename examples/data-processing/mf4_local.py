import can

# Set up the PeakCAN interface
can.rc['interface'] = 'pcan'
can.rc['channel'] = 'PCAN_USBBUS1'
can.rc['bitrate'] = 500000

# Create a CAN bus instance
bus = can.interface.Bus()

# CSV file name
mf4_file = 'test.mf4'

# Initialize CSVWriter
with can.MF4Writer(mf4_file, database=None, compression_level=2) as writer:
    # Define a message handler function
    def handle_message(msg):
        writer.on_message_received(msg)

    # Add the message handler to the bus
    notifier = can.Notifier(bus, [handle_message])

    # Keep the script running to receive messages
    while True:
        pass