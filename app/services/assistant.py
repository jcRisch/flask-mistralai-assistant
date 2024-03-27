import time
from flask import current_app, session
import json
from config import Config
from mistralai.models.chat_completion import ChatMessage
from mistralai.client import MistralClient

class AssistantService:
    def __init__(self):
        current_app.logger.info(Config.MISTRALAI_KEY)
        self.client = MistralClient(api_key=Config.MISTRALAI_KEY)

        self.assistant_name = 'IT Administrator Assistant'
        self.model_id= 'mistral-large-latest'
        self.instruction= 'You are an IT administrator. You are responsible for managing user permissions. You have a list of users and their permissions. You can get the permissions of a user by their username, update the permissions of a user by their username, and get the user ID based on the username. You can use the following functions: getPermissionsByUsername, updatePermissionsByUsername, getUserIdByUsername.'
        self.discussion = []
    
    def run_assistant(self, message):
        current_app.logger.info(f'Running assistant: {message}')
        self.discussion.append(ChatMessage(role="user", content=message))

        ai_response = self.client.chat(
            model=self.model_id,
            messages=self.discussion,
            tools=[
                self.define_function__list_available_zones(), 
                self.define_function__list_device_status_by_zone(), 
                self.define_function__update_zone_device_status()
            ],
            tool_choice="auto"
        )

        # Add the assistant response to the discussion   
        self.discussion.append(ai_response.choices[0].message)

        # Check if there is a tool call in the response
        tool_calls = ai_response.choices[0].message.tool_calls

        if tool_calls:
            current_app.logger.info(f'Tool calls found: {tool_calls}')
            self.generate_tool_outputs(tool_calls)
            current_app.logger.info(f'Discussion after tool call: {self.discussion}')
            ai_response = self.client.chat(
                model=self.model_id,
                messages=self.discussion
            )
            current_app.logger.info(f'Assistant response after tool call: {ai_response.choices[0].message}')
            self.discussion.append(ChatMessage(role="assistant", content=ai_response.choices[0].message.content))

        current_app.logger.info(f'Assistant response: {ai_response.choices[0].message.content}')
        return ai_response.choices[0].message.content
        
    def generate_tool_outputs(self, tool_calls):
        current_app.logger.info('Generating tool outputs')
        tool_outputs = []

        for tool_call in tool_calls:
            function_name = tool_call.function.name
            arguments = tool_call.function.arguments

            args_dict = json.loads(arguments)

            if hasattr(self, function_name):
                function_to_call = getattr(self, function_name)
                output = function_to_call(**args_dict) 
                current_app.logger.info(f'Tool output: {output}')
                self.discussion.append(ChatMessage(role="tool", function_name=function_name, content=output))

        return tool_outputs
    
    def define_function__list_available_zones(self):
        function = {
            "type": "function",
            "function": {
                "name": "list_available_zones",
                "description": "List the available zones of the house.",
                "parameters": {
                    "type": "object"
                }
            }
        }
        return function
    
    def define_function__list_device_status_by_zone(self):
        function = {
            "type": "function",
            "function": {
                "name": "list_device_status_by_zone",
                "description": "List the status of devices in a specific zone.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "zone": {"type": "string", "description": "The zone to list the device status for. Can be 'kitchen' or 'outdoor'."}
                    },
                    "required": ["zone"]
                }
            }
        }
        return function
    
    def define_function__update_zone_device_status(self):
        function = {
            "type": "function",
            "function": {
                "name": "update_zone_status",
                "description": "Update the status of a device in a specific zone.",
                "parameters": {
                "type": "object",
                "properties": {
                    "zone": {"type": "string", "description": "The zone to update the status for. Can be 'kitchen' or 'outdoor'."},
                    "device": {"type": "string", "description": "The device to update the status for. Can be 'light', 'door', or 'camera'."},
                },
                "required": ["zone", "device"]
                }
            }
        }
        return function
    
    def list_available_zones(self):
        current_app.logger.info(f'list_available_zones')
        available_zones = current_app.domotics_service.list_available_zones()
        if available_zones:
            current_app.logger.info(f'Available zones found with ref: {available_zones}')
            return json.dumps(available_zones)
        else:
            current_app.logger.info('No available zones found')
            return "No available zone found"
    
    def list_device_status_by_zone(self, zone):
        current_app.logger.info(f'list_device_status_by_zone: {zone}')
        devices = current_app.domotics_service.list_device_status_by_zone(zone)
        if devices:
            current_app.logger.info(f'Devices found')
            return json.dumps(devices)
        current_app.logger.info('No devices found')
        return "No device found"
    
    def update_zone_status(self, zone, device):
        current_app.logger.info(f'update_zone_status: {zone}, {device}')
        updated_status = current_app.domotics_service.update_zone_status(zone, device)
        if updated_status:
            current_app.logger.info(updated_status) 
            return json.dumps(updated_status)
        else:
            current_app.logger.info('Zone or device not found')
            return "Zone or device not found"