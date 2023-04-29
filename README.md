# EdgeGPT
Extension for Text Generation Webui based on [EdgeGPT](https://github.com/acheong08/EdgeGPT) by acheong08, a reverse engineered API of Microsoft's Bing Chat AI.
Now you can give Internet access to your chatbot, quickly and easy, without Openai API or other paid methods.

## How to Run
1. Clone [oobabooga's  original repository](https://github.com/oobabooga/text-generation-webui) and follow the instructions until you can chat with a chatbot.

2. Open the extensions folder and clone here this repo:
```bash
git clone https://github.com/GiusTex/EdgeGPT.git
```

3. Within the `textgen` conda environment (from the linked instructions, or TextGenerationWebui\installer_files\env if you used the one-click installer), run the following commands to install dependencies:
```bash
pip install -r EdgeGPT/requirements.txt
```

4. Install [Cookie Editor](https://microsoftedge.microsoft.com/addons/detail/cookie-editor/ajfboaconbpkglpfanbmlfgojgndmhmc) for Microsoft Edge.
![CookieEditor](https://user-images.githubusercontent.com/112352961/235325561-9c85c199-8e50-484f-ac64-a25928de7281.png)

5. Copy the cookies in a file.
     If you can't find the extension on Microsoft Edge, follow these steps:
     ![ExportCookies](https://user-images.githubusercontent.com/112352961/235325568-61ad404c-d8d7-46f5-833d-7aee2b3c9d44.png)
     
      1- Click the puzzle icon;
     
      2- Click the cookie icon;
     
      3- Click the fifth option on top, to copy them.
   
   Now that you have copied them, go inside text-generation-webui\extensions\EdgeGPT and paste the cookies settings in cookies.txt, then rename it to cookies.json and    press enter.

6. Run the server with the EdgeGPT extension. If all goes well, you should see it reporting "ok"
```bash
python server.py --chat --extensions EdgeGPT
```

## Features
- Start the prompt with Hey Bing, and Bing will search and give an answer, that will be fed to the bot memory before it answers you.
![Example1](https://user-images.githubusercontent.com/112352961/235326069-26f33ebf-8378-452f-bacf-85f192346ba2.png)

- If the bot answer doesn't suit you, you can turn on "Show Bing Output" to show the Bing output, sometimes it doesn't answer well and need better search words.
![Example2](https://user-images.githubusercontent.com/112352961/235326217-81b3e9eb-9523-4c18-94b0-f141c841ab98.png)

- You can change the chosen word to start the search, inside the script at line 30:
```bash
BingOutput = re.search('^Hey Bing', UserInput)
```

## How does it work
Inside the function "input_modifier" the code looks for the chosen word:
```bash
BingOutput = re.search('^Hey Bing', UserInput)
```
Then, if it finds it, it adds it to "custom_generate_chat_prompt" at line 100:
```bash
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
``` 
And at the end it takes RawBingString and adds it another bit of context, generating BingString so the bot memory has the Bing output. If you want you can also change the context around the RawBingString at line 118 inside script.py, to better suit your desidered answer.
```bash
BingString="Important informations:" + RawBingString + "\n" + "Now answer the following question based on the given informations. If my sentence starts with \"Hey Bing\" ignore that part, I'm referring to you anyway, so don't say you are Bing.\n"
```

## Contributing
Pull requests, suggestions and bug reports are welcome, but as I'm not a programmer I can't guarantee I'll be of help.
I could add something but I don't know if I'll have the will; some ideas I had in mind, and they should be moderately simple, are configuring it to be usable with the oobabooga API, and activating EdgeGPT with another button, without having to write "Hey Bing", but I didn't put them because I don't know if it's worth it.

## Credits and inspiration
 - acheong08 for his amazing default [EdgeGPT](https://github.com/acheong08/EdgeGPT).
 - The tutorial video by [Ai Austin](https://youtu.be/aokn48vB0kc), where he shows the code to install EdgeGPT and use it, and gave me a bit of inspiration.
