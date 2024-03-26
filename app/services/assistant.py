import time
from flask import current_app, session
import json
from config import Config
from mistralai.models.chat_completion import ChatMessage
from mistralai.client import MistralClient

class AssistantService:
    def __init__(self):
        current_app.logger.info(Config.MISTRALAI_KEY)
        self.client = MistralClient(api_key="2h2ssQ5NarqXAlpFxjdxMjvrXsCr1qEL")

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
                self.define_function__get_permissions_by_username(), 
                self.define_function__get_user_id_by_username(), 
                self.define_function__update_user_permission()
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
            ai_response = self.client.chat(
                model=self.model_id,
                messages=self.discussion,
                tools=[
                self.define_function__get_permissions_by_username(), 
                self.define_function__get_user_id_by_username(), 
                self.define_function__update_user_permission()
                ],
                tool_choice="auto"
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
    
    def define_function__get_user_id_by_username(self):
        function = {
            "type": "function",
            "function": {
                "name": "getUserIdByUsername",
                "description": "Get the user ID based on the username.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "username": {"type": "string", "description": "The username of the user."}
                    },
                    "required": ["username"]
                }
            }
        }
        return function
    
    def define_function__get_permissions_by_username(self):
        function = {
            "type": "function",
            "function": {
                "name": "getPermissionsByUsername",
                "description": "Get the permissions of a user by their username.",
                "parameters": {
                "type": "object",
                "properties": {
                    "username": {"type": "string", "description": "The username of the user."}
                },
                "required": ["username"]
                }
            }
        }
        return function
    
    def define_function__update_user_permission(self):
        function = {
            "type": "function",
            "function": {
                "name": "updateUserPermission",
                "description": "Update the value of a permission for a user by their username.",
                "parameters": {
                "type": "object",
                "properties": {
                    "username": {"type": "string", "description": "The username of the user."},
                    "permission": {"type": "string", "description": "The permission to update."},
                    "value": {"type": "boolean", "description": "The new value of the permission."}
                },
                "required": ["username"]
                }
            }
        }
        return function
    
    def getUserIdByUsername(self, username):
        current_app.logger.info(f'getUserIdByUsername: {username}')
        user_id = current_app.permissions_service.get_user_id_by_username(username)
        if user_id:
            current_app.logger.info(f'User found with id: {user_id}')
            return user_id
        else:
            current_app.logger.info('User not found')
            return "No user found"
    
    def getPermissionsByUsername(self, username):
        current_app.logger.info(f'getPermissionsByUsername: {username}')
        user_id = current_app.permissions_service.get_user_id_by_username(username)
        if user_id:
            current_app.logger.info(f'User found with id: {user_id}')
            permissions = current_app.permissions_service.get_permissions_by_user_id(user_id)
            current_app.logger.info(permissions)
            return permissions
        current_app.logger.info('User not found')
        return "No user found"
    
    def updateUserPermission(self, username, permission, value):
        current_app.logger.info(f'updateUserPermission: {username}, {permission}, {value}')
        user_id = current_app.permissions_service.get_user_id_by_username(username)
        if user_id:
            current_app.logger.info(f'User found with id: {user_id}')
            updated_permission = current_app.permissions_service.update_user_permission(user_id, permission, value)
            current_app.logger.info(updated_permission) 
            return updated_permission
        else:
            current_app.logger.info('User not found')
            return "No user found"