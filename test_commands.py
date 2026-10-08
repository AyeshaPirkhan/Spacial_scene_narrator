from services.command_processor import process_command

objects = [

    {
        "name": "chair",
        "position": "Left",
        "distance": "Close"
    },

    {
        "name": "person",
        "position": "Center",
        "distance": "Very Close"
    }

]

scene = "You are in an office with a chair and a person."

while True:

    cmd = input("Command: ")

    process_command(
        cmd,
        objects,
        scene
    )