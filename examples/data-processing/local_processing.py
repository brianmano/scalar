import can

# Set up the PeakCAN interface
can.rc['interface'] = 'pcan'
can.rc['channel'] = 'PCAN_USBBUS1'
can.rc['bitrate'] = 500000

# Create a CAN bus instance
bus = can.interface.Bus()

# CSV file name
csv_file = 'received_messages.csv'

# Initialize CSVWriter
with can.CSVWriter(csv_file, append=True) as writer:
    # Define a message handler function
    def handle_message(msg):
        # Write the message to the CSV file
        writer.on_message_received(msg)

    # Add the message handler to the bus
    notifier = can.Notifier(bus, [handle_message])

    # Keep the script running to receive messages
    while True:
        pass


