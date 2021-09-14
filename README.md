If you are going to be using only the exe:
1)Make sure you have downloaded ffmpeg from https://www.ffmpeg.org/download.html and extract it to any location of your choice.

![image](https://user-images.githubusercontent.com/74890659/128459452-62e3fcec-4c50-4d93-a074-23a1dc215666.png)

2)Then add ffmpeg/bin to path in environment variables in system properties:

![image](https://user-images.githubusercontent.com/74890659/128459795-4761e777-8d14-4025-b395-40d6c67a5be5.png)

3)Make sure to have python and the ffmpeg python library installed.You can install the ffmpeg python library by executing the following command:
```pip install ffmpeg```

=======================Only if you are going to use the .py file=======================

Spotipy:
```pip install spotipy --upgrade```

youtube_search:
```pip install youtube-search```

pytube:
```pip install pytube```

pydub:
```pip install pydub```

eyeD3:
```pip install eyeD3``` 

4)You also require a client id and client secret for the program to work which you can obtain from https://developer.spotify.com/ 
by logging in and creating a new app from the dashboard which will then give you a client id and client secret 
which you paste in the code

![image](https://user-images.githubusercontent.com/74890659/130178928-61802ff8-c549-4509-b055-5c96a440e34d.png)

![image](https://user-images.githubusercontent.com/74890659/130178984-0243cc2a-d180-45c9-b132-0d1783feabc3.png)

5)Then download the repository and open the ```spotify playlist downloader.py``` file and paste the link of 
the playlist you want to download and click on the "Download songs" button and let it download and convert 
the songs which will take time depending on your cpu and number of songs in the playlist or if you are 
unwilling to use the .py file you can instead use the .exe file which does not require the libraries to be
installed although ffmpeg has to installed and added to path for it to work

![image](https://user-images.githubusercontent.com/74890659/128459967-6c0b7b94-4ea0-43b3-a509-e3f906a876da.png)

6)The songs will be downloaded to "Downloads" folder created within the directory itself where the py file exists

![image](https://user-images.githubusercontent.com/74890659/130122888-4063f898-22de-4df9-95e2-fbdaaf3c9ecf.png)

If you have any problems,doubts,suggestion or any other queries you can reach me on discord at Rickyrorton#6693
