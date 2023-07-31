import requests
import json
import os
import time
import threading
import re

# Set to keep track of retrieved message IDs and user messages
retrieved_message_ids = set()
replied_message_ids = set()

# Variable to indicate if the script is running
running = True

def display_message(message):
    message_id = message.get('id')
    if message_id not in retrieved_message_ids:
        retrieved_message_ids.add(message_id)
        content = message.get('content')
        if message_id not in replied_message_ids:
            for item in target_replies:
                target_word = item.get('target_word')
                reply = item.get('reply')
                if re.search(r'\b' + re.escape(target_word) + r'\b', content, flags=re.IGNORECASE):
                    print("Message:")
                    print(content)
                    reply_to_original_sender(channel_id, reply, message_id)
                    # Mark the message as old by adding it to replied_message_ids set
                    replied_message_ids.add(message_id)
                    break  # Break the loop if a target word is found

def retrieve_latest_messages(channelid):
    headers = {
        'authorization': bot_token
    }
    params = {
        'limit': 5  # Fetch the last 5 messages
    }
    r = requests.get(f'https://discord.com/api/v9/channels/{channelid}/messages', headers=headers, params=params)
    try:
        messages = json.loads(r.text)
    except json.JSONDecodeError as e:
        print("JSON decode error:", e)
        return []

    if not isinstance(messages, list) or len(messages) == 0:
        return []

    return messages

def reply_to_original_sender(channelid, content, message_id):
    headers = {
        'authorization': bot_token
    }
    data = {
        'content': content,
        'message_reference': {
            'message_id': message_id,
            'channel_id': channelid
        }
    }

    requests.post(f'https://discord.com/api/v9/channels/{channelid}/messages', headers=headers, json=data)

def input_thread():
    global running
    while True:
        if not running:
            user_input = input()
            if user_input.lower() == 'ctrl+z':
                running = True
                print("Script resumed.")
            else:
                print("Invalid input. Type 'ctrl+z' to resume script.")
        time.sleep(1)

# Read the configurations from config.json
def read_config():
    with open('config.json', 'r') as config_file:
        try:
            config = json.load(config_file)
        except json.JSONDecodeError as e:
            print("JSON decode error:", e)
            config = {}  # If there's an error, initialize an empty config dictionary
    return config

# Clear the console and print "The bot is working, showing messages in the channel."
print("The bot is working, showing messages in the channel.")

# Start a separate thread to listen for user input
input_thread = threading.Thread(target=input_thread)
input_thread.daemon = True
input_thread.start()

# Set the loop to run indefinitely
while True:
    if running:
        config = read_config()

        bot_token = config.get("bot_token", "")
        channel_id = config.get("channel_id", "")
        target_replies = config.get("target_replies", [])

        headers = {
            'authorization': bot_token
        }

        latest_messages = retrieve_latest_messages(channel_id)
        if latest_messages:
            for message in latest_messages:
                display_message(message)

    time.sleep(0.2)  # Add a wait time of 0.2 seconds before the next iteration
