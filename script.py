import re
import asyncio
import subprocess
import json
import modules.shared as shared
import gradio as gr

from EdgeGPT.EdgeGPT import Chatbot, ConversationStyle
from modules.chat import replace_all, get_turn_substrings
from modules.text_generation import (get_max_prompt_length, get_encoded_length)
from modules.extensions import apply_extensions


#------------------------------------------------------------
# Get current acheong08 EdgeGPT version installed
#------------------------------------------------------------
# Run "conda list EdgeGPT" and get output
command = "conda list EdgeGPT"
conda_version = subprocess.check_output(command, shell=True)
# Decode output into string
conda_version_output = conda_version.decode("utf-8")
# Find version
pattern = r"edgegpt\s+(\S+)"
match = re.search(pattern, conda_version_output)
if match:
    version = match.group(1)
    print("acheong08 EdgeGPT core script: ", version)
else:
    print("Version not found.")

#------------------------------------------------------------
# Normal oobaboga webui
#------------------------------------------------------------
BingOutput=None
RawBingString=None
BingString=None
ShowBingString=False
OverwriteWord=False
PrintUserInput=False
PrintWholePrompt=False
PrintRawBingString=False
PrintBingString=False
UseCookies=False

BingConversationStyle="creative"
ChosenWord="Hey Bing"
BingContext1="Important informations: "
BingContext2="Now answer the following question based on the given informations. If I say \"Hey Bing\" I am referring to you anyway. Do not say you are Bing.\n"

print("\nThanks for using the EdgeGPT extension! If you encounter any bug or you have some nice idea to add, write it on the issue page here: https://github.com/GiusTex/EdgeGPT/issues")

params = {
    'ShowBingString': False,
    'OverwriteWord': False,
    'PrintUserInput': False,
    'PrintWholePrompt': False,
    'PrintRawBingString': False,
    'PrintBingString': False,
    'UseCookies': False,
}

def input_modifier(string):
    global UserInput
    global BingOutput
    global RawBingString
    global ChosenWord
    # Reset Bing output shown in the webui
    RawBingString=None

    UserInput=string
    # Find out if the chosen word appears in the sentence.
    BingOutput = re.search(ChosenWord, UserInput)

    if params['ShowBingString']:
        global ShowBingString
        ShowBingString=True
    else:
        ShowBingString=False

    if params['OverwriteWord']:
        global OverwriteWord
        OverwriteWord=True
    else:
        OverwriteWord=False

    if params['PrintUserInput']:
        global PrintUserInput
        PrintUserInput=True
        print("User input:\n", UserInput)
    else:
        PrintUserInput=False
    
    if params['PrintWholePrompt']:
        global PrintWholePrompt
        PrintWholePrompt=True
    else:
        PrintWholePrompt=False
    
    if params['PrintRawBingString']:
        global PrintRawBingString
        PrintRawBingString=True
    else:
        PrintRawBingString=False

    if params['PrintBingString']:
        global PrintBingString
        PrintBingString=True
    else:
        PrintBingString=False

    if params['UseCookies']:
        global UseCookies
        UseCookies=True
    else:
        UseCookies=False

    if(BingOutput!=None) and not OverwriteWord:
        shared.processing_message = "*Is searching...*"
    elif OverwriteWord:
        shared.processing_message = "*Is searching...*"
    else:
        shared.processing_message = "*Is typing...*"
    return string
    

    # Prompt + BingString (if requested)
def custom_generate_chat_prompt(user_input, state, **kwargs):
    impersonate = kwargs.get('impersonate', False)
    _continue = kwargs.get('_continue', False)
    also_return_rows = kwargs.get('also_return_rows', False)
    history = kwargs.get('history', shared.history)['internal']
    is_instruct = state['mode'] == 'instruct'

    # Finding the maximum prompt size
    max_length = get_max_prompt_length(state)
    all_substrings = {
        'chat': get_turn_substrings(state, instruct=False),
        'instruct': get_turn_substrings(state, instruct=True)
    }

    substrings = all_substrings['instruct' if is_instruct else 'chat']
        
    # Create the template for "chat-instruct" mode
    if state['mode'] == 'chat-instruct':
        wrapper = ''
        command = state['chat-instruct_command'].replace('<|character|>', state['name2'] if not impersonate else state['name1'])
        wrapper += state['context_instruct']
        wrapper += all_substrings['instruct']['user_turn'].replace('<|user-message|>', command)
        wrapper += all_substrings['instruct']['bot_turn_stripped']
        if impersonate:
            wrapper += substrings['user_turn_stripped'].rstrip(' ')
        elif _continue:
            wrapper += apply_extensions("bot_prefix", substrings['bot_turn_stripped'])
            wrapper += history[-1][1]
        else:
            wrapper += apply_extensions("bot_prefix", substrings['bot_turn_stripped'].rstrip(' '))
    else:
        wrapper = '<|prompt|>'

    # Build the prompt
    min_rows = 3
    i = len(history) - 1
    rows = [state['context_instruct'] if is_instruct else f"{state['context'].strip()}\n"]
    while i >= 0 and get_encoded_length(wrapper.replace('<|prompt|>', ''.join(rows))) < max_length:
        if _continue and i == len(history) - 1:
            if state['mode'] != 'chat-instruct':
                rows.insert(1, substrings['bot_turn_stripped'] + history[i][1].strip())
        else:
            rows.insert(1, substrings['bot_turn'].replace('<|bot-message|>', history[i][1].strip()))

        string = history[i][0]
        if string not in ['', '<|BEGIN-VISIBLE-CHAT|>']:
            rows.insert(1, replace_all(substrings['user_turn'], {'<|user-message|>': string.strip(), '<|round|>': str(i)}))

        i -= 1

    if impersonate:
        if state['mode'] == 'chat-instruct':
            min_rows = 1
        else:
            min_rows = 2
            rows.append(substrings['user_turn_stripped'].rstrip(' '))
    elif not _continue:

        #------------------------------------------------------------
        # Add Bing output
        #------------------------------------------------------------
        async def EdgeGPT():
            global UserInput
            global RawBingString
            global PrintRawBingString
            global UseCookies        
            
            
            if BingConversationStyle=="creative":
                style = ConversationStyle.creative
            elif BingConversationStyle=="balanced":
                style = ConversationStyle.balanced
            elif BingConversationStyle=="precise":
                style = ConversationStyle.precise
            
            # Define and create one time the bot
            bot_created=False
            if (bot_created==False):
                if UseCookies:
                    cookies = json.loads(open("./extensions/EdgeGPT/cookies.json", encoding="utf-8").read())
                    bot = await Chatbot.create(cookies=cookies)
                else:
                    bot = await Chatbot.create()
                bot_created=True

            response = await bot.ask(prompt=UserInput, conversation_style=style, simplify_response=True)
            
            # If required, end bot and create a new one
            if response["messages_left"] < 2:
                print("WARNING: You are almost out of Bing messages! Recreating bot...")
                await bot.close()
                if UseCookies:
                    bot = await Chatbot.create(cookies=cookies)
                    return bot
                else:
                    bot = await Chatbot.create()
                    return bot

            # Select only the bot response from the response dictionary
            bot_response = response["text"] # You can also get citations via ["sources_text"]
            
            # Remove [^#^] citations in response
            bot_response_fixed = re.sub(r"\*", "", bot_response)
            RawBingString = re.sub('\[\^\d+\^\]', '', str(bot_response_fixed))
            
            await bot.close()
            return RawBingString
        
        # Different ways to run the same EdgeGPT function:
        # From chosen word
        if(BingOutput!=None) and not OverwriteWord:
            asyncio.run(EdgeGPT())
        # of from OverwriteWord button
        elif OverwriteWord:
            asyncio.run(EdgeGPT())
        # When Bing has given his answer we print (if requested) and save 
        # the output
        if RawBingString != None and not "" or OverwriteWord==True:
            BingString=BingContext1 + RawBingString + "\n" + BingContext2
            if PrintUserInput:
                print("\nUser input:\n", UserInput)
            if PrintRawBingString:
                print("\nBing output:\n", RawBingString)
            if PrintBingString:
                print("\nBing context + Bing output:\n", BingString)
            # Add Bing output to character memory
            rows.append(BingString)

        # Adding the user message
        if len(user_input) > 0:
            rows.append(replace_all(substrings['user_turn'], {'<|user-message|>': user_input.strip(), '<|round|>': str(len(history))}))

        # Add the character prefix
        if state['mode'] != 'chat-instruct':
            rows.append(apply_extensions("bot_prefix", substrings['bot_turn_stripped'].rstrip(' ')))

    while len(rows) > min_rows and get_encoded_length(wrapper.replace('<|prompt|>', ''.join(rows))) >= max_length:
        rows.pop(1)

    prompt = wrapper.replace('<|prompt|>', ''.join(rows))
    if RawBingString != None and not "" or OverwriteWord==True:
            if PrintWholePrompt:
                print("\nWhole prompt:\n", prompt + "\n")
    if also_return_rows:
        return prompt, rows
    else:
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


def FunChooseWord(CustomWordRaw):
    global ChosenWord
    ChosenWord = CustomWordRaw
    return CustomWordRaw

def Context1Func(Context1Raw):
    global BingContext1
    BingContext1 = Context1Raw
    return Context1Raw

def Context2Func(Context2Raw):
    global BingContext2
    BingContext2 = Context2Raw
    return Context2Raw

def ConversationStyleFunc(ConversationStyleRaw):
    global BingConversationStyle
    BingConversationStyle = ConversationStyleRaw
    return ConversationStyleRaw

def ui():
    with gr.Accordion("Instructions", open=False):
        with gr.Box():
            gr.Markdown(
                """
                To use it, just start the prompt with Hey Bing; it doesn't start if you don't use uppercase and lowercase as in the example. You can change the activation word from EdgeGPT options. If the output is strange turn on Show Bing Output to see the result of Bing, maybe you need to correct your question.
                
                """)
            
    with gr.Accordion("EdgeGPT options", open=True):
        with gr.Row():
            ShowBingString = gr.Checkbox(value=params['ShowBingString'], label='Show Bing Output')
        with gr.Row():
            WordOption = gr.Textbox(label='Choose and use a word to activate Bing', placeholder="Choose your word. Empty = Hey Bing")
            OverwriteWord = gr.Checkbox(value=params['OverwriteWord'], label='Overwrite Activation Word. Bing will always search, ignoring the activation word.')
        with gr.Row():
            UseCookies = gr.Checkbox(value=params['UseCookies'], label='Use cookies. If you have login problems turn this on to use cookies (you need cookies.json). Instructions here: https://github.com/GiusTex/EdgeGPT/blob/main/how-to-use-cookies.md')
        with gr.Row():
            ConversationStyleOption = gr.Textbox(label='Choose Bing Conversation Style', placeholder="Supported Conversation Styles: creative, balanced, precise. Empty = default creative")

        with gr.Accordion("EdgeGPT context", open=False):
            with gr.Row():
                Context1Option = gr.Textbox(label='Choose Bing context-1', placeholder="First context, is injected before the Bing output. Empty = default context-1")
            with gr.Row():
                Context2Option = gr.Textbox(label='Choose Bing context-2', placeholder="Second context, is injected after the Bing output. Empty = default context-2")
            with gr.Row():
                gr.Markdown(
                    """
                    You can see the default context (with Bing output in the middle) by turning on the fourth option in "Print in console options": "Print Bing string in command console".
                    """)
            
    with gr.Accordion("Print in console options", open=False):
        with gr.Row():
            PrintUserInput = gr.Checkbox(value=params['PrintUserInput'], label='Print User input in command console. The user input will be fed first to Bing, and then to the default bot.')
        with gr.Row():
            PrintWholePrompt = gr.Checkbox(value=params['PrintWholePrompt'], label='Print whole prompt in command console. Prompt has: context, Bing search output, and user input.')
        with gr.Row():
            PrintRawBingString = gr.Checkbox(value=params['PrintRawBingString'], label='Print Bing output in command console.')
        with gr.Row():
            PrintBingString = gr.Checkbox(value=params['PrintBingString'], label='Print Bing output + Bing context in command console.')
    

    ShowBingString.change(lambda x: params.update({"ShowBingString": x}), ShowBingString, None)
    WordOption.change(fn=FunChooseWord, inputs=WordOption)
    OverwriteWord.change(lambda x: params.update({"OverwriteWord": x}), OverwriteWord, None)
    UseCookies.change(lambda x: params.update({"UseCookies": x}), UseCookies, None)
    ConversationStyleOption.change(fn=ConversationStyleFunc, inputs=ConversationStyleOption)

    Context1Option.change(fn=Context1Func, inputs=Context1Option)
    Context2Option.change(fn=Context2Func, inputs=Context2Option)

    PrintUserInput.change(lambda x: params.update({"PrintUserInput": x}), PrintUserInput, None)
    PrintWholePrompt.change(lambda x: params.update({"PrintWholePrompt": x}), PrintWholePrompt, None)
    PrintRawBingString.change(lambda x: params.update({"PrintRawBingString": x}), PrintRawBingString, None)
    PrintBingString.change(lambda x: params.update({"PrintBingString": x}), PrintBingString, None)
