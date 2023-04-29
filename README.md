# EdgeGPT
Extension for Text Generation Webui based on [EdgeGPT](https://github.com/acheong08/EdgeGPT) by acheong08, a reverse engineered API of Microsoft's Bing Chat AI.
Now you can give Internet access to your chatbot, quickly and easy, without Openai API or other paid methods.

## How to Run
1. Clone [oobabooga's  original repository](https://github.com/oobabooga/text-generation-webui) and follow the instructions until you can chat with a chatbot.

2. Open the extensions folder and clone here this repo:
```bash
git clone https://github.com/GiusTex/EdgeGPT
```

3. Within the `textgen` conda environment (from the linked instructions, or TextGenerationWebui\installer_files\env if you used the one-click installer), run the following commands to install dependencies:
```bash
pip install -r EdgeGPT/requirements.txt
```

4. Install [Cookie Editor](https://microsoftedge.microsoft.com/addons/detail/cookie-editor/ajfboaconbpkglpfanbmlfgojgndmhmc) for Microsoft Edge.
![CookieEditor](https://user-images.githubusercontent.com/112352961/235325561-9c85c199-8e50-484f-ac64-a25928de7281.png)

5. Copy the cookies in a file.
     If you can't find the extension on Microsoft Edge, follow the steps in the image:
     ![ExportCookies](https://user-images.githubusercontent.com/112352961/235325568-61ad404c-d8d7-46f5-833d-7aee2b3c9d44.png)
     
     1- Click the puzzle icon;
     2- Click the cookie icon;
     3- Click the fifth option on top, to copy them.
   Now that you copied them, go inside text-generation-webui\extensions\EdgeGPT and create a txt file, then paste here the cookies settings, then rename the text file    to cookies.json

6. Run the server with the EdgeGPT extension. If all goes well, you should see it reporting "ok"
```bash
python server.py --chat --extensions EdgeGPT
```
