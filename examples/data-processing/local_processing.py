import can
import cantools
import csv

# Load DBC file
db = cantools.database.load_file('examples\data-processing\dbc_files\can1-honda_civic_hatchback_ex_2017_can_generated.dbc')

# Set up the PeakCAN interface
can.rc['interface'] = 'pcan'
can.rc['channel'] = 'PCAN_USBBUS1'
can.rc['bitrate'] = 500000

# Create CAN bus instance
bus = can.interface.Bus()

# Open a CSV file in write mode
with open('decoded_messages.csv', 'w', newline='') as csvfile:
    fieldnames = ['Timestamp', 'Message_ID', 'Decoded_Message']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    
    writer.writeheader()  # Write CSV header
    
    try:
        while True:
            message = bus.recv()  # Receive CAN message
            try:
                decoded_message = db.decode_message(message.arbitration_id, message.data)
                writer.writerow({'Timestamp': message.timestamp, 'Message_ID': message.arbitration_id, 'Decoded_Message': decoded_message})
            except KeyError:
                print("Error: Message not found in DBC file.")
    except KeyboardInterrupt:
        bus.shutdown()
