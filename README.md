If you are going to be using only the exe:

Just download the latest version of exe from the releases tab on this repository and open the exe and paste a playlist/song link and let it download ,no pre-requsites needed unless you are downloading in mp3 format for which you will need ffmpeg to installed.Either ffmpeg has to be added to path or has to be copied to the directory where the exe file is.

If you get a Microsoft defender smartscreen popup like the one shown below do not panic it does NOT contain malware,its just that the exe isnt signed (requires money to buy a signing certificate) and thus windows thinks it is potentially dangerous.

![image](https://user-images.githubusercontent.com/74890659/173220425-ea7b3e77-b798-4cef-ac9f-e3cab624f60d.png)

If you have any problems,doubts,suggestion or any other queries you can reach me on discord at Rickyrorton#6693 or
join the spotify downloader support server at https://discord.gg/8pTQAfAAbm

Make sure you install all 3 exe provided with ffmpeg so that the program works as normal.How to install and add ffmpeg to path:https://windowsloop.com/install-ffmpeg-windows-10/#download-ffmpeg

FFMPEG Download links:

Windows: https://www.gyan.dev/ffmpeg/builds/ffmpeg-git-essentials.7z (Inside the archive there will be a bin folder in which you will find 3 executables which will have to be installed)

Mac OS: https://evermeet.cx/ffmpeg/

Debian: https://tracker.debian.org/pkg/ffmpeg

Ubuntu: https://launchpad.net/ubuntu/+source/ffmpeg

The three required ffmpeg executables if you wish to download in mp3/wav/flac format

![image](https://user-images.githubusercontent.com/74890659/154211073-fc63a638-789a-489f-883d-0b887176b620.png)

If empty command prompt windows like these open,DO NOT WORRY, they are just ffmpeg windows converting the songs into the required format
![image](https://user-images.githubusercontent.com/74890659/175236311-05766a35-f08e-45bc-a168-22ee36e11ceb.png)


If you are wondering if this has any malware here is the exe checked in virustotal: https://www.virustotal.com/gui/file/92eb314ed69573076d7b9137978d5a0412e6909557d3b133630148409ccaf6a4/detection

The 2 out of 69(nice) detections are false positives and the connections it makes are only to spotify(or their content distributors like akamai,fastly,verizon,etc).

=======================Only if you are going to use the .py file=======================

Make sure to install all required packages listed in the requirements.txt file by running the following command

```pip install -r requirements.txt```

1)You also require a client id and client secret for the program to work which you can obtain from https://developer.spotify.com/ 
by logging in and creating a new app from the dashboard which will then give you a client id and client secret 
which you paste in ```downloader.py```file 

![image](https://user-images.githubusercontent.com/74890659/130178928-61802ff8-c549-4509-b055-5c96a440e34d.png)

![image](https://user-images.githubusercontent.com/74890659/130178984-0243cc2a-d180-45c9-b132-0d1783feabc3.png)

2)Then run the ```gui.py``` file and paste the link of the playlist you want to download and click on 
the "Download songs" button and let it download and convert the songs which will take time depending 
on your cpu and number of songs in the playlist or if you are unwilling to use the .py file you can 
instead use the .exe file which does not require the libraries to beinstalled although ffmpeg has to 
installed and added to path for it to work

![image](https://user-images.githubusercontent.com/74890659/150334965-049446e5-8daa-4b65-8213-dcf2bb9247ff.png)

3)The songs will be downloaded to "Downloads" folder created within the directory itself where the py file exists

![image](https://user-images.githubusercontent.com/74890659/154210788-51e600d5-a0f9-477a-a958-a6dfbd7aa669.png)
