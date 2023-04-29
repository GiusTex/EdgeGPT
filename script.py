import re
import asyncio
import modules.shared as shared
import gradio as gr

from EdgeGPT import Chatbot, ConversationStyle
from modules.chat import replace_all
from modules.text_generation import (encode, get_max_prompt_length)
from modules.extensions import apply_extensions


RawBingString=None
BingString=None
ShowBingString=False

params = {
    'ShowBingString': False
}

def input_modifier(string):
    global UserInput
    global BingOutput
    global RawBingString
    # Reset Bing output shown in the webui
    RawBingString=None

    UserInput=string
    # Find out if the chosen word appears in the sentence.
    # If you want to change the chosen word, change "Hey Bing"
    BingOutput = re.search('^Hey Bing', UserInput)

    if params['ShowBingString']:
        global ShowBingString
        ShowBingString=True
    else:
        ShowBingString=False
        
    if(BingOutput!=None):
        shared.processing_message = "*Is searching...*"
    else:
        shared.processing_message = "*Is typing...*"
    return string


    # Default prompt + BingString (if requested)
def custom_generate_chat_prompt(user_input, state, **kwargs):
    impersonate = kwargs['impersonate'] if 'impersonate' in kwargs else False
    _continue = kwargs['_continue'] if '_continue' in kwargs else False
    also_return_rows = kwargs['also_return_rows'] if 'also_return_rows' in kwargs else False
    is_instruct = state['mode'] == 'instruct'
    rows = [state['context'] if is_instruct else f"{state['context'].strip()}\n"]
    min_rows = 3

    # Finding the maximum prompt size
    chat_prompt_size = state['chat_prompt_size']
    if shared.soft_prompt:
        chat_prompt_size -= shared.soft_prompt_tensor.shape[1]

    max_length = min(get_max_prompt_length(state), chat_prompt_size)

    # Building the turn templates
    if 'turn_template' not in state or state['turn_template'] == '':
        if is_instruct:
            template = '<|user|>\n<|user-message|>\n<|bot|>\n<|bot-message|>\n'
        else:
            template = '<|user|>: <|user-message|>\n<|bot|>: <|bot-message|>\n'
    else:
        template = state['turn_template'].replace(r'\n', '\n')

    replacements = {
        '<|user|>': state['name1'].strip(),
        '<|bot|>': state['name2'].strip(),
    }

    user_turn = replace_all(template.split('<|bot|>')[0], replacements)
    bot_turn = replace_all('<|bot|>' + template.split('<|bot|>')[1], replacements)
    user_turn_stripped = replace_all(user_turn.split('<|user-message|>')[0], replacements)
    bot_turn_stripped = replace_all(bot_turn.split('<|bot-message|>')[0], replacements)

    # Building the prompt
    i = len(shared.history['internal']) - 1
    while i >= 0 and len(encode(''.join(rows))[0]) < max_length:
        if _continue and i == len(shared.history['internal']) - 1:
            rows.insert(1, bot_turn_stripped + shared.history['internal'][i][1].strip())
        else:
            rows.insert(1, bot_turn.replace('<|bot-message|>', shared.history['internal'][i][1].strip()))

        string = shared.history['internal'][i][0]
        if string not in ['', '<|BEGIN-VISIBLE-CHAT|>']:
            rows.insert(1, replace_all(user_turn, {'<|user-message|>': string.strip(), '<|round|>': str(i)}))

        i -= 1

    if impersonate:
        min_rows = 2
        rows.append(user_turn_stripped.rstrip(' '))
    elif not _continue:

        #Adding BingString
        if(BingOutput!=None):
            async def EdgeGPT():
                global UserInput
                global RawBingString
                bot = Chatbot(cookie_path='extensions/EdgeGPT/cookies.json')
                response = await bot.ask(prompt=UserInput, conversation_style=ConversationStyle.creative)
                # Select only the bot response from the response dictionary
                for message in response["item"]["messages"]:
                    if message["author"] == "bot":
                        bot_response = message["text"]
                # Remove [^#^] citations in response
                RawBingString = re.sub('\[\^\d+\^\]', '', str(bot_response))
                await bot.close()
                #print("\nBingString output:\n", RawBingString)
                return RawBingString
            asyncio.run(EdgeGPT())
            global RawBingString
            global BingString
            BingString="Important informations:" + RawBingString + "\n" + "Now answer the following question based on the given informations. If my sentence starts with \"Hey Bing\" ignore that part, I'm referring to you anyway, so don't say you are Bing.\n"
            rows.append(BingString)

        # Adding the user message
        if len(user_input) > 0:
            rows.append(replace_all(user_turn, {'<|user-message|>': user_input.strip(), '<|round|>': str(len(shared.history["internal"]))}))

        # Adding the Character prefix
        rows.append(apply_extensions("bot_prefix", bot_turn_stripped.rstrip(' ')))

    while len(rows) > min_rows and len(encode(''.join(rows))[0]) >= max_length:
        rows.pop(1)

    prompt = ''.join(rows)
    if also_return_rows:
        return prompt, rows
    else:
       # print("prompt:\n", prompt)
        return prompt
    

def output_modifier(string):
    """
    This function is applied to the model outputs.
    """
    global BingOutput
    global RawBingString
    global ShowBingString
    if ShowBingString:
        string = "Bing:" + str(RawBingString) + "\n\n\n" + string
        return string
    else:
        return string


def bot_prefix_modifier(string):
    """
    This function is only applied in chat mode. It modifies
    the prefix text for the Bot and can be used to bias its
    behavior.
    """
    
    return string


def ui():
    with gr.Accordion("Instructions"):
        with gr.Box():
            gr.Markdown(
                """
                To use it, just start the prompt with Hey Bing; it doesn't start if you don't use uppercase and lowercase as in the example. You can change the word used by editing it inside script.py in the extension folder. If the output is strange turn on ShowBingString to see the result of Bing, maybe you need to correct your answer.
                
                """)
    with gr.Row():
        ShowBingString = gr.Checkbox(value=params['ShowBingString'], label='Show Bing Output')

    ShowBingString.change(lambda x: params.update({"ShowBingString": x}), ShowBingString, None)