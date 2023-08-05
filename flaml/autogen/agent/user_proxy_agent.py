from .responsive_agent import ResponsiveAgent
from typing import Callable, Dict, Optional, Union
import asyncio

class UserProxyAgent(ResponsiveAgent):
    """(Experimental) A proxy agent for the user, that can execute code and provide feedback to the other agents.

    UserProxyAgent is a subclass of ResponsiveAgent configured with `human_input_mode` to ALWAYS
    and `oai_config` to False. By default, the agent will prompt for human input every time a message is received.
    Code execution is enabled by default. LLM-based auto reply is disabled by default.
    To modify auto reply, override `generate_reply` method.
    To modify the way to get human input, override `get_human_input` method.
    To modify the way to execute code blocks, single code block, or function call, override `execute_code_blocks`,
    `run_code`, and `execute_function` methods respectively.
    To customize the initial message when a conversation starts, override `generate_init_message` method.
    """

    def __init__(
        self,
        name: str,
        is_termination_msg: Optional[Callable[[Dict], bool]] = None,
        max_consecutive_auto_reply: Optional[int] = None,
        human_input_mode: Optional[str] = "ALWAYS",
        function_map: Optional[Dict[str, Callable]] = None,
        code_execution_config: Optional[Union[Dict, bool]] = None,
        oai_config: Optional[Union[Dict, bool]] = False,
        system_message: Optional[str] = "",
    ):
        """
        Args:
            name (str): name of the agent.
            is_termination_msg (function): a function that takes a message in the form of a dictionary
                and returns a boolean value indicating if this received message is a termination message.
                The dict can contain the following keys: "content", "role", "name", "function_call".
            max_consecutive_auto_reply (int): the maximum number of consecutive auto replies.
                default to None (no limit provided, class attribute MAX_CONSECUTIVE_AUTO_REPLY will be used as the limit in this case).
                The limit only plays a role when human_input_mode is not "ALWAYS".
            human_input_mode (str): whether to ask for human inputs every time a message is received.
                Possible values are "ALWAYS", "TERMINATE", "NEVER".
                (1) When "ALWAYS", the agent prompts for human input every time a message is received.
                    Under this mode, the conversation stops when the human input is "exit",
                    or when is_termination_msg is True and there is no human input.
                (2) When "TERMINATE", the agent only prompts for human input only when a termination message is received or
                    the number of auto reply reaches the max_consecutive_auto_reply.
                (3) When "NEVER", the agent will never prompt for human input. Under this mode, the conversation stops
                    when the number of auto reply reaches the max_consecutive_auto_reply or when is_termination_msg is True.
            function_map (dict[str, callable]): Mapping function names (passed to openai) to callable functions.
            code_execution_config (dict or False): config for the code execution.
                To disable code execution, set to False. Otherwise, set to a dictionary with the following keys:
                - work_dir (Optional, str): The working directory for the code execution.
                    If None, a default working directory will be used.
                    The default working directory is the "extensions" directory under
                    "path_to_flaml/autogen".
                - use_docker (Optional, list, str or bool): The docker image to use for code execution.
                    If a list or a str of image name(s) is provided, the code will be executed in a docker container
                    with the first image successfully pulled.
                    If None, False or empty, the code will be executed in the current environment.
                    Default is True, which will be converted into a list.
                    If the code is executed in the current environment,
                    the code must be trusted.
                - timeout (Optional, int): The maximum execution time in seconds.
            oai_config (dict or False): oai inference configuration.
                Please refer to [oai.Completion.create](/docs/reference/autogen/oai/completion#create)
                for available options.
                Default to false, which disables oai-based auto reply.
            system_message (str): system message for oai inference.
                Only used when oai_config is not False. Use it to reprogram the agent.
        """
        super().__init__(
            name,
            system_message,
            is_termination_msg,
            max_consecutive_auto_reply,
            human_input_mode,
            function_map,
            code_execution_config,
            oai_config,
        )
        self._added_msg = []
        self._data_available_event = asyncio.Event()

    async def a_add(self, added_msg):
        """Add data for learning."""
        self._added_msg = added_msg
        print("Ding! New data added!!")
        self._data_available_event.set()

    async def a_receive(self, message: Union[Dict, str], sender: "Agent"):
        """Receive a message from another agent.

        Once a message is received, this function sends a reply to the sender or stop.
        The reply can be generated automatically or entered manually by a human.

        Args:
            message (dict or str): message from the sender. If the type is dict, it may contain the following reserved fields (All fields are optional).
                1. "content": content of the message, can be None.
                2. "function_call": a dictionary containing the function name and arguments.
                3. "role": role of the message, can be "assistant", "user", "function".
                    This field is only needed to distinguish between "function" or "assistant"/"user".
                4. "name": In most cases, this field is not needed. When the role is "function", this field is needed to indicate the function name.
            sender: sender of an Agent instance.
        """
        # await self._data_available_event.wait()
        # # await asyncio.wait_for(self._data_available_event.wait(), timeout=10.0)
        # # Reset the event
        # self._data_available_event.clear()
        while not self._added_msg:
            try:
                # Wait until the event is set or timeout after 10 seconds
                await asyncio.wait_for(self._data_available_event.wait(), timeout=2.0)
                # Reset the event
                print("New data addition waited!")
                self._data_available_event.clear()
            except asyncio.TimeoutError:
                # If no new data has been added after 10 seconds, do something else
                print("Wait data time out in ", self.name)
                break
        
        message = self._message_to_dict(message)
        # When the agent receives a message, the role of the message is "user". (If 'role' exists and is 'function', it will remain unchanged.)
        valid = self._append_oai_message(message, "user", sender.name)
        if not valid:
            return
        self._print_received_message(message, sender)

        # default reply is empty (i.e., no reply, in this case we will try to generate auto reply)
        reply = ""
        if self.human_input_mode == "ALWAYS":
            reply = self.get_human_input(
                "Provide feedback to the sender. Press enter to skip and use auto-reply, or type 'exit' to end the conversation: "
            )
        elif self._consecutive_auto_reply_counter[
            sender.name
        ] >= self.max_consecutive_auto_reply or self._is_termination_msg(message):
            if self.human_input_mode == "TERMINATE":
                reply = self.get_human_input(
                    "Please give feedback to the sender. (Press enter or type 'exit' to stop the conversation): "
                )
                reply = reply if reply else "exit"
            else:
                # this corresponds to the case when self._human_input_mode == "NEVER"
                reply = "exit"
        if reply == "exit" or (self._is_termination_msg(message) and not reply):
            # reset the consecutive_auto_reply_counter
            self._consecutive_auto_reply_counter[sender.name] = 0
            return
        if reply:
            # reset the consecutive_auto_reply_counter
            self._consecutive_auto_reply_counter[sender.name] = 0
            await self.a_send(reply, sender)
            return
        
        self._consecutive_auto_reply_counter[sender.name] += 1
        if self.human_input_mode != "NEVER":
            print("\n>>>>>>>> NO HUMAN INPUT RECEIVED. USING AUTO REPLY FOR THE USER...", flush=True)
        reply = self.generate_reply(self._oai_conversations[sender.name], default_reply=reply)
        
        #NOTE: added new data here
        if self._added_msg:
            print("\n>>>>>>>> ADDING ADDITIONAL DATA...", flush=True)
            reply = reply + "\n BTW: " + self._added_msg
            self._added_msg = []
        await self.a_send(reply, sender)
