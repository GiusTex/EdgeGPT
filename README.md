# EdgeGPT
Extension for Text Generation Webui based on [EdgeGPT](https://github.com/acheong08/EdgeGPT) by acheong08, a reverse engineered API of Microsoft's Bing Chat AI.
Now you can give a sort of Internet access to your characters, easily, quickly and free.

## How to Run
1. Clone [oobabooga's  original repository](https://github.com/oobabooga/text-generation-webui) and follow the instructions until you can chat with a chatbot.

2. Open the extensions folder and clone here this repo:
```bash
git clone https://github.com/GiusTex/EdgeGPT.git
```

3. Activate the `textgen` conda environment (from the linked instructions, or TextGenerationWebui\installer_files\env if you used the one-click installer), then if you see in console: `(path\to\textgen) path\to\text-generation-webui\extensions>` or `(path\to\TextGenerationWebui\installer_files\env) path\to\TextGenerationWebui\text-generation-webui\extensions>`, run the following commands to install EdgeGPT:
```bash
pip install -r EdgeGPT/requirements.txt
```

## How to update
- Open `cmd_windows.bat` (or `Linux` or `macOS` depending on the platform you have) and type `pip install EdgeGPT==0.10.11`.
- Go in the EdgeGPT extension folder, copy the path, then in the `cmd.bat` file type `cd your\copied\path git pull`.

## Features
- Changeable keyword to activate Bing when you need and how you want
- Button to leave activated Bing
- 5 debug buttons to show or print different parts of the prompt
- Works in chat-mode, so you can use your desired characters
- Editable Bing context within the webui
- Bing conversation style (creative,balanced,precise). No inside the webui
- It works on Colab now, without cookies. I uploaded a colab you can test, scroll down to open it
- Added an option to use cookies

#### Keyword
> Start the prompt with Hey Bing, the default keyword to activate Bing when you need, and Bing will search and give an answer, that will be fed to the 
  character memory before it answers you.
<img src="https://user-images.githubusercontent.com/112352961/235326069-26f33ebf-8378-452f-bacf-85f192346ba2.png" width="568" height="431" />

#### Debug buttons
 > If the bot answer doesn't suit you, you can turn on "Show Bing Output" to show the Bing output in the webui, sometimes it doesn't answer well and need better search words.
  <img src="https://user-images.githubusercontent.com/112352961/235326217-81b3e9eb-9523-4c18-94b0-f141c841ab98.png" width="663" height="472" />
  
  You can also print in the console other prompt parts (user input, whole prompt, "raw" Bing output, Bing output + custom context):
  
<img src="https://user-images.githubusercontent.com/112352961/235358313-776d9ffa-8c6e-4f57-ac56-ea1f557d1360.png" width="690" height="200" />

#### Chat-mode
> It works with "chat, streaming, non-streaming, listen" modes.

#### Change keyword
> Change the Bing activation word within the webui, from EdgeGPT options (punctuation marks are not supported, they give error).
 <img src="https://user-images.githubusercontent.com/112352961/235366184-f943d8a1-387c-4788-bf24-45f81a9f2a31.png" width="655" height="156" />
 <img src="https://user-images.githubusercontent.com/112352961/235366206-2c56e367-c09c-4367-897e-2a1d73e3abac.png" width="211" height="96" />
<img src="https://user-images.githubusercontent.com/112352961/235366218-5fc44f39-11a0-468a-bb63-7566fb327ed0.png" width="614" height="139" />

#### Edit Bing context
> Now you can customize the context around the Bing output.
<img src="https://user-images.githubusercontent.com/112352961/235373510-7cdd969c-9762-4f56-8dc2-2ea0c6691fbc.png" width="708" height="203" />

#### Overwrite Activation Word
> Added Overwrite Activation Word, while this is turned on Bing will always answer you without the need of an activation word, if you don't want to mess your prompt 
  with a keyword that doesn't fit in.
<img src="https://user-images.githubusercontent.com/112352961/235376642-32435472-23f1-4ee0-ac6c-e070d1867305.png" width="710" height="157" />

#### Bing conversation style
> You can choose 3 Bing conversation styles between `creative`, `balanced` or `precise` from EdgeGPT options.

#### Colab
> I merged and created a colab version of the text-generation-webui where you can use the new EdgeGPT (it works on Colab without cookies), and use different models and extensions: [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/GiusTex/EdgeGPT/blob/main/Text-generation-webui-EdgeGPT.ipynb)

#### Cookies
> Since many people had login issues, now there is an option to use cookies, thanks to [Simplegram](https://github.com/GiusTex/EdgeGPT/issues/12#issuecomment-1573176097) and some other edits of mine, you can turn them on from EdgeGPT options. To use them follow the instructions [here](how-to-use-cookies.md).

## How it works
Inside the function "input_modifier" the code looks for the chosen word:
```bash
BingOutput = re.search(ChosenWord, UserInput)
```
Then, if it finds it, it adds it to "custom_generate_chat_prompt" at line 172 and then it calls the function:
```bash
        #Adding BingString
        async def EdgeGPT():
            global UserInput
            global RawBingString
            global PrintRawBingString
            bot = await Chatbot.create()
            response = await bot.ask(prompt=UserInput, conversation_style=ConversationStyle.creative)
            # Select only the bot response from the response dictionary
            for message in response["item"]["messages"]:
                if message["author"] == "bot":
                    bot_response = message["text"]
            # Remove [^#^] citations in response
            RawBingString = re.sub('\[\^\d+\^\]', '', str(bot_response))
            await bot.close()
            return RawBingString
            
        # Different ways to run the same EdgeGPT function:
        # From chosen word
        if(BingOutput!=None) and not OverwriteWord:
            asyncio.run(EdgeGPT())
        # of from OverwriteWord button
        elif OverwriteWord:
            asyncio.run(EdgeGPT())
            
        # When Bing has given his answer we print (if requested) and save the output
        if RawBingString != None and not "":
            # Add Bing output to character memory
            rows.append(BingString)
``` 
And at the end it takes RawBingString and adds it Bing context (useful to tell the character what to do with the informations), generating BingString. If you want you can also change the context around the RawBingString from the webui within EdgeGPT options > EdgeGPT context, to better suit your desidered answer.

## Weaknesses:
Being still a new application, you are welcome to make tests to find your optimal result, be it clearing the conversation, changing the context around the Bing output, or something else.
- Sometimes the character ignores the Bing output, even if it is in his memory, in this case asking "Can you repeat me [whatever you asked]" may help.
- The character could start his answer with `:`, but after some messages it goes away.
- If you get a `captcha error` you can try writing something on `bing.com` to complete the captcha, and if you still get the error you can use the `cookies option` (after writing something on `bing.com`).
<img src="https://github.com/GiusTex/EdgeGPT/assets/112352961/6312e628-da7b-4390-babd-043d7881971b.png" width="634" height="160">

## Contributing
Pull requests, suggestions and bug reports are welcome, but as I'm not a programmer I can't guarantee I'll be of help.

## Credits and inspiration
 - acheong08 for his amazing default [EdgeGPT](https://github.com/acheong08/EdgeGPT).
 - The tutorial video by [Ai Austin](https://youtu.be/aokn48vB0kc), where he shows the code to install EdgeGPT and use it, and gave me a bit of inspiration.
 - You.

[![Star History Chart](https://api.star-history.com/svg?repos=GiusTex/EdgeGPT&type=Date)](https://star-history.com/#GiusTex/EdgeGPT&Date)
