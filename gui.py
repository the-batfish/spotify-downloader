#importing necessary libraries
from tkinter import Entry, StringVar, Tk,Button,Label,scrolledtext,LabelFrame,CENTER,OptionMenu,Scale, HORIZONTAL,LEFT#tkinter for the user interface
from PIL import Image,ImageTk #Python(PIL) image library for inserting images into the user interface
from tkinter.filedialog import askdirectory
from tkinter.ttk import Progressbar
import sys
from os import path as ospath
import downloader
from webbrowser import open_new_tab
from pickle import load,dump

#defining a window
global window
window=Tk()
window.geometry('600x600')
window.resizable(False,False)
window.configure(bg = '#3d3d3d')
window.title('Spotify Downloader')

#Widgets in the window
title=Label(window,text=' SPOTIFY DOWNLOADER',font = ("Arial Bold",18),bg = '#3d3d3d', fg = 'white')
title.place(relx=0.5,rely=0.05 ,anchor=CENTER)

entry_label=Label(window,text='Enter song/playlist link:',font = ("Arial Bold",10),bg = '#3d3d3d', fg = 'white')
entry_label.place(relx=0.15,rely=0.12,anchor=CENTER)

output_label=Label(window,text='OUTPUT:',font = ("Arial Bold",12),bg = '#3d3d3d', fg = 'white')
output_label.place(relx=0.5,rely=0.17,anchor=CENTER)

download_location=Label(window,text='Download location:',font = ("Arial Bold",10),bg = '#3d3d3d', fg = 'white',justify=LEFT)
download_location.place(relx=0.5,rely=0.84,anchor=CENTER)

thread_number=Label(window,text='Thread count:',font = ("Arial Bold",10),bg = '#3d3d3d', fg = 'white')
thread_number.place(relx=0.12,rely=0.78,anchor=CENTER)

filetype=Label(window,text='Filetype:',font = ("Arial Bold",10),bg = '#3d3d3d', fg = 'white')
filetype.place(relx=0.46,rely=0.78,anchor=CENTER)

bitrate=Label(window,text='Bitrate:',font = ("Arial Bold",10),bg = '#3d3d3d', fg = 'white')
bitrate.place(relx=0.73,rely=0.78,anchor=CENTER)

global progress
progress=Progressbar(window,orient = HORIZONTAL,mode = 'determinate',length=100)
progress.place(relx=0.5,rely=0.7,width=400,anchor=CENTER)

scrolled_cont = LabelFrame(window, font=("Arial Bold", 15), background='#1DB954', foreground='white', borderwidth=5, labelanchor="n")
scrolled_cont.place(relx=0.5,rely=0.43,height=290,width=510,anchor=CENTER)
    
global output_box
output_box=scrolledtext.ScrolledText(window, font = ("Arial",10),state='disabled',bg='#3d3d3d',fg='white')
output_box.place(relx=0.5,rely=0.43,height=280,width=500,anchor=CENTER)

dl_location_button=Button(window,text='Change download folder',fg='#3d3d3d',bg='white',font = ("Arial",14),command=lambda:directrory())
dl_location_button.place(relx=0.3,rely=0.91,anchor=CENTER)

global download_button
download_button=Button(window,text='Download songs',fg='#3d3d3d',bg='white',font = ("Arial",14),command=lambda:start_downloader())
download_button.place(relx=0.7,rely=0.91,anchor=CENTER)

global filetype_default
filetypes=['.m4a','.mp3','.wav','.flac']
filetype_default=StringVar()
filetype_default.set('.m4a')
filetype_dropdown=OptionMenu(window,filetype_default,*filetypes)
filetype_dropdown.place(relx=0.52,rely=0.755)

global bitrate_default
bitrates=['96k','128k','192k','320k']
bitrate_default=StringVar()
bitrate_default.set('192k')   
bitrate_dropdown=OptionMenu(window,bitrate_default,*bitrates)
bitrate_dropdown.place(relx=0.78,rely=0.755)

global thread_num_set
thread_num_set=Scale(window,from_=1,to=20,tickinterval=19,orient=HORIZONTAL,highlightbackground='#3d3d3d',background='#3d3d3d',fg='white')
thread_num_set.set(4)
thread_num_set.place(relx=0.2,rely=0.73)

entry_cont = LabelFrame(window, font=("Arial Bold", 15), background='#1DB954', foreground='white', borderwidth=5, labelanchor="n")
entry_cont.place(relx=0.62,rely=0.12,width=394,height=24,anchor=CENTER)

global playlist_link
playlist_link=Entry(window,bg='#3d3d3d',fg='white')
playlist_link.place(relx=0.62,rely=0.12,width=390,height=20,anchor=CENTER)
playlist_link.bind('<Return>',lambda e:start_downloader())

def server_invite():
    open_new_tab('https://discord.gg/8pTQAfAAbm')
discord_link=Label(window,text='Click here to contact us on discord if you have any problems',font = ("Arial Bold",10),bg = '#3d3d3d', fg = 'white',cursor="hand2")
discord_link.place(relx=0.5,rely=0.97,anchor=CENTER)
discord_link.bind("<Button-1>", lambda e:server_invite())

#getting path to the directory
if getattr(sys, 'frozen', False):
        application_path = ospath.dirname(sys.executable)
elif __file__:
    application_path = ospath.dirname(__file__) 

#setting default download location
global location
if ospath.exists(ospath.join(application_path,'spdconfig.dat')):
    f=open(ospath.join(application_path,'spdconfig.dat'),'rb')
    dict=load(f)
    location=dict['location']
    filetype_default.set(dict['filetype'])
    bitrate_default.set(dict['bitrate'])
    thread_num_set.set(dict['threads'])
else:
    location=ospath.join(application_path,'Downloads').replace('\\','/')
download_location.config(text='Download location:'+str(location))

#function for importing pictures into the gui
def image_import(filename,height,width):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = ospath.abspath(".")
    try:
        image_path=ospath.join(base_path,filename)
        img=Image.open(image_path)
    except:
        image_path=ospath.join(application_path,filename)
        img=Image.open(image_path)
    img=img.resize((height,width), Image.Resampling.BOX)
    pic=ImageTk.PhotoImage(img)
    return pic

#The actual images being imported
logo=image_import('logo.png',48,48)
title.config(image=logo,compound=LEFT)

download_logo=image_import('dl_logo.png',40,40)
download_button.config(image=download_logo,compound=LEFT)

#download location related stuff
def directrory():
        global location
        location=askdirectory()
        if location:
            dict={'location':location,'bitrate':bitrate_default.get(),'filetype':filetype_default.get(),'threads':thread_num_set.get()}
            f=open(ospath.join(application_path,'spdconfig.dat'),'wb')
            dump(dict,f)
            f.close()
            download_location.config(text='Download location:'+str(location))
        else:
            pass

def saveconf(*args):
    global localtion
    dict={'location':location,'bitrate':bitrate_default.get(),'filetype':filetype_default.get(),'threads':thread_num_set.get()}

    f=open(ospath.join(application_path,'spdconfig.dat'),'wb')
    dump(dict,f)
    f.close()

filetype_default.trace('w',saveconf)  
bitrate_default.trace('w',saveconf)
thread_num_set.config(command=saveconf) 
def start_downloader():
    global location
    global output_box
    global download_button
    global window
    global progress
    link=playlist_link.get()
    playlist_link.delete(0,len(link))
    threads=thread_num_set.get()
    filetype=filetype_default.get()
    bitrate=bitrate_default.get()
    downloader.start(dlbut=download_button,link=link,path=location,threadno=threads,filetype=filetype,scrltxt=output_box,progress=progress,bitrate=bitrate)  
      
window.mainloop() 