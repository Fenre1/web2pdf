# from pathlib import Path
# import sys
# import os
import os
import sys

os.chdir(os.path.dirname(sys.path[0]))
try:
    os.chdir(os.path.dirname(sys.argv[0]))
except OSError:
    pass
testt = os.getcwd() 

temp_os_var = os.environ["Path"].split(';.')[0]
temp_os_var = temp_os_var + testt+'\\GTK3-Runtime Win64\\bin;.'
os.environ["Path"] = temp_os_var

from tkinter import *
from tkinter import ttk, filedialog
import cairocffi
import tldextract
import datetime
import locale
locale.setlocale(locale.LC_ALL, "nl_NL")
## weasyprint requires installation of https://weasyprint.readthedocs.io/en/stable/install.html#windows 
## GDK3 (perhaps just a few dll's; requires restart of IDE after installation.)

from PIL import ImageGrab
import math

from weasyprint import HTML
from bs4 import BeautifulSoup as BS
import requests
import re

### the following seems necessary for some systems BEFORE compilation...:
### In the weasyprint python library find text.py
###  find:  gobject = dlopen(ffi, 'libgobject-2.0-0', 'gobject-2.0', 'libgobject-2.0.so.0',
###             'libgobject-2.0.dylib')
###         pango = dlopen(ffi, 'libpango-1.0-0', 'pango-1.0', 'libpango-1.0.so.0',
###           'libpango-1.0.dylib')
###         pangocairo = dlopen(ffi, 'libpangocairo-1.0-0', 'pangocairo-1.0',
###                'libpangocairo-1.0.so.0', 'libpangocairo-1.0.dylib')
### 
### and make sure that in each respective case 
### 'libgobject-2.0-0', 
### 'libpango-1.0-0' and 
### 'libpangocairo-1.0-0' 
### are the first entries after ffi. For some reason the pyinstaller version of web2pdf (html2pdf) 
### needs it that way or it will not find the dlls. 


## FOR PYINSTALLER INCLUDE THE FOLLOWING FOLDERS AFTER COMPILATION WITH PYINSTALLER IN THE MAIN DIRECTORY:
    ### cairocffi
    ### cairosvg
    ### tldextract
    ### pyphen
    ### GTK3-Runtime Win64
    
### pyinstaller run from anaconda terminal: pyinstaller html2pdf_v2.py --name somename --onefile (if you want a single file). 
        
class Application(Frame,object):
    def __init__(self, master):       
        self.sel_folder = StringVar()
        self.sel_folder.set('No folder selected')
        try:
            with open("web2pdf_config.txt", "r") as folder_config_file:
               self.selected_folder = folder_config_file.read()
               self.sel_folder.set('pdf will be saved in ' + self.selected_folder)
        except FileNotFoundError:
            pass
        ## list with sites that are supported by automated processing
        self.supported_sites = ['ad.nl', 
                                'volkskrant.nl',
                                'volkskrant.nl liveblog',
                                'skipr.nl', 
                                'nrc.nl',
                                'nrcmedia.nl',
                                'rtvutrecht.nl',
                                'rtvnoord.nl',
                                'trouw.nl',
                                'trouw.nl liveblog',
                                'rtlnieuws.nl',
                                'nu.nl',
                                'nu.nl liveblog',
                                'nos.nl',
                                'gelderlander.nl',
                                'parool.nl',
                                'telegraaf.nl',
                                'rijksoverheid.nl']
        sorted(self.supported_sites, key=str.lower)
        self.num_im = 0 # for def add_user_image
        self.im_list = [] # for def add_user_image
        self.themainframe = super(Application,self).__init__(master)
        style = ttk.Style()
        style.theme_use('default')
        style.configure('.',background = '#555555',foreground = 'white') #sets background of the app to a dark theme
        style.map('.',background=[('disabled','#555555'),('active','#777777')], relief=[('!pressed','sunken'),('pressed','raised')])
        style.configure('TNotebook.Tab',background='#555555')
        style.map('TNotebook.Tab',background=[('selected','black')])
        self.create_widget()


    def create_widget(self):
        # welcome message
        self.communication_label = Message()
        self.communication_label['background'] = '#FFFFFF'        
        self.communication_label['font'] = 24
        self.communication_label.place(x=0,y=200)
        self.communication_label['width'] = 300
        self.communication_label.configure(text='Hello, with this application you can convert a webpage to pdf. Above you can set the folder where you want to save the pdf file. \n \n Paste or type a webaddress in the bar on the right.\n\n For supported sites you can use Automatically save website. Otherwise, use Analyse website and then Manually save website. \n\n Click Supported websites to see which websites can be saved automatically.')

        #button to select image folder
        self.open_ = ttk.Button()
        self.open_['text'] ="Select folder to save pdf"
        self.open_['command'] = self.select_foldere
        self.open_.place(x=10,y=70)
        self.open_['width'] = 30
        
        # text displaying selected pdf save folder
        self.selected_folder_label = ttk.Label()
        self.selected_folder_label['textvariable'] = self.sel_folder
        self.selected_folder_label['width'] = 60
        self.selected_folder_label.place(x=10,y=50)

        # button that shows websites that work with automated processing        
        self.available_sites = ttk.Button()
        self.available_sites['text'] ="Supported websites"
        self.available_sites['command'] = self.show_sites
        self.available_sites.place(x=10,y=110)
        self.available_sites['width'] = 30
        
        
        
        #enter url
        self.url_entry = Entry(background='#777777',foreground = 'white',exportselection=0,width=200)
        #self.url_entry.insert(END, 'paste URL')
        self.url_entry.place(x=450,y=50)

        self.url_entry_label = ttk.Label()
        self.url_entry_label['text'] = 'Enter URL below'
        self.url_entry_label['width'] = 60
        self.url_entry_label.place(x=450,y=20)



        
        #button to fully process pdf
        self.process_website = ttk.Button()
        self.process_website['text'] ="Automatically save website"
        self.process_website['command'] = self.process_pdf
        self.process_website.place(x=450,y=80)
        self.process_website['width'] = 30
        
        # button to analyse website (automatically extract date, source and title)
        self.analyse_site = ttk.Button()
        self.analyse_site['text'] ="Analyse website"
        self.analyse_site['command'] = self.analyse_website
        self.analyse_site.place(x=450,y=110)
        self.analyse_site['width'] = 30
        
        # will save website based on filled in fiels (title, source, date, url)
        self.process_website_manual = ttk.Button()
        self.process_website_manual['text'] ="Manually save website"
        self.process_website_manual['command'] = self.process_pdf_manual
        self.process_website_manual.place(x=450,y=140)
        self.process_website_manual['width'] = 30
        
        

        #enter title
        self.title_entry = Entry(background='#777777',foreground = 'white',exportselection=0,width=181)
        self.title_entry.insert(END, '')
        self.title_entry.place(x=565,y=170)

        self.title_label = ttk.Label()
        self.title_label['text'] = 'Title of document'
        self.title_label['justify'] = CENTER
        self.title_label.place(x=450,y=170)
        self.title_label['width'] = 18


        #enter source
        self.source_entry = Entry(background='#777777',foreground = 'white',exportselection=0,width=181)
        self.source_entry.insert(END, '')
        self.source_entry.place(x=565,y=200)

        self.source_label = ttk.Label()
        self.source_label['text'] = 'Source of document'
        self.source_label['justify'] = CENTER
        self.source_label.place(x=450,y=200)
        self.source_label['width'] = 18

        #enter date
        self.date_entry = Entry(background='#777777',foreground = 'white',exportselection=0,width=181)
        self.date_entry.insert(END, '')
        self.date_entry.place(x=565,y=230)
            
        self.date_label = ttk.Label()
        self.date_label['text'] = 'Date published \n use yyyymmdd \n e.g. 20200925'
        self.date_label['wraplength'] = 125

        self.date_label['justify'] = CENTER
        self.date_label.place(x=450,y=230)
        self.date_label['width'] = 18
        
        # button to manually add image from windows clipboard
        self.add_img = ttk.Button()
        self.add_img['text'] ="Add user image to pdf"
        self.add_img['command'] = self.create_user_image
        self.add_img.place(x=450,y=330)
        self.add_img['width'] = 30

        self.user_images_label = ttk.Label()
        self.user_images_label['text'] = '0 user images will be added to pdf'
        self.user_images_label['width'] = 60
        self.user_images_label.place(x=650,y=335)

        self.remove_img = ttk.Button()
        self.remove_img['text'] ="Remove all user images"
        self.remove_img['command'] = self.remove_all_user_img
        self.remove_img.place(x=450,y=380)
        self.remove_img['width'] = 30




    #select folder to save pdfs to. Use text file to automatically set a preferred folder
    def select_foldere(self):
        self.selected_folder = filedialog.askdirectory()   #this will make the file directory a string
        self.sel_folder.set('pdf will be saved in ' + self.selected_folder)

    # saves html to pdf, only keeps title and main text, tries to keep images as well. 
    def please_write_pdf(self, soup,export_path,datum,source,title,html,domain_name,known_page,known_soup):
        if known_page == 0: ### if the website is not in the list of websites that can be processed automatically, a generic process is used.
                            ### this means it is possible that not everything is saved properly.
            all_everything = soup.find_all(['p','img','h1']) ### extract relevant objects, such as titles, subtitles, paragraphs and images.
            all_p = soup.find_all('p') ### extract only paragraphs
            all_im = soup.find_all('img') ### extract only images.
            start = '<!DOCTYPE html>' ### start of html document that will be the basis of our pdf.
            hlink = '<a href=' + html + '>link to original article</a>' ### hyperlink of the url to the original article.
            source_txt = '<p> Source: ' + domain_name + '</p>'
            pub_date =  '<p> Publication date: '+ datum + '</p>'
            headline = soup.find_all('h1')
            p3 = '</html>'
            full_page = start + hlink + source_txt + pub_date
            did_find = 0
        
            for p in range(len(all_everything)):
                if str(all_everything[p])[0:3] == '<h1':
                    did_find = 1
                if did_find == 1:
                    if str(all_everything[p])[0:4] == '<img':                            
                        im_str = self.image_cleaner(all_everything[p]) ### extract clean image using self.image_cleaner() function.
                        full_page = full_page + im_str + '\n'
  
                    else:
                        full_page = full_page + str(all_everything[p]) + '\n'
            
            full_page = full_page + p3
            if len(title) == 0:
                title = headline[0].text
            if len(source) == 0:
                source = domain_name.split('.')[0]
        else:
            full_page = self.full_page
        if len(self.im_list) > 0:            
            full_page = full_page.split('</html>')[0]
            for user_im in self.im_list:
                full_page = full_page + 'image added by user \n'
                full_page = full_page + '<img src="file:///' +  user_im + '" alt=""> \n'
                print(user_im)
            full_page = full_page + '</html>'
        file_name = export_path + datum + '_' + source +  '_' + title + '.pdf' 
        ### file name format is export path (location where pdfs are saved) then date, then source
        ### then title of article. E.g. 'C:\\Documents\\20210328_nu.nl_Het aantal cases stijgt.pdf'
        the_page = HTML(string=full_page).render(presentational_hints=True) ### the html renderer from weasyprint, to convert our html full_page into pdf.
        
        the_page.write_pdf(file_name) ### writing the pdf file to our file_name.
        self.im_list = []
        self.num_im = 0
        self.user_images_label['text'] = str(self.num_im) + ' user images will be added to pdf'

        return file_name        
    
    # get the domain name and html soup
    def get_website(self, get_url):
            try:
                domain_name = tldextract.extract(get_url).domain + '.' + tldextract.extract(get_url).suffix
                r = requests.get(get_url)
                soup = BS(r.content, 'html.parser')
                print(soup)
            except (requests.exceptions.MissingSchema, requests.exceptions.ConnectionError) as err:
                print('xx')
                self.communication_label.configure(text='Invalid URL. Check to make sure the following is a valid website and starts with http or https:\n' + self.get_url)
                domain_name = ''
                soup = ''
            return domain_name,soup
   
    # if site is in the self.supported_sites list, below the processing can be found to extract date, title, and html. New supported sites should be added here.
    def known_site(self, html,soup,domain_name):
        export_path = self.selected_folder
        is_liveblog = 0
        full_page = ''
        ### While each website works differently, the process is generally fairly similar. Below the process for nu.nl is commented.
        if self.domain_name == 'nu.nl': ## first check whether the content is a news article or a live-blog. In case of a live-blog each short article will be 
                                        ## saved separately as a pdf
            soup_string = soup.find(class_ = "pubdate large" ).text ### date the article is published
            try:
                live_blog = soup.find('span', class_ = "label").text
            except AttributeError:
                live_blog = ''
            
            if 'Liveblog' in live_blog:
                is_liveblog = 1
                texts = soup.find_all(class_="timeline-block-wrapper text_block")[1:-1] ### find all the separate short live blog articles
                datum = datetime.datetime.today()
                datum = datetime.datetime.strftime(datum,'%Y%m%d') ## date is set to the day the user is saving the live blog                                                                   
                for tex in texts:
                    title = tex.strong.text ### extract the live blog article title and text
                    for k in title.split("\n"):
                        title = re.sub(r"[^a-zA-Z0-9]+", ' ', k)
                    blog_string = str(tex)
                    file_name = export_path + '\\' + datum +'_Nu.nl liveblog_'+title+'.pdf'
                    print(file_name)
                    the_page = HTML(string=blog_string).render(presentational_hints=True)  #unlike news articles, live blog articles are saved right here.      
                    the_page.write_pdf(file_name)
           
            else: ### this is the process in case it is a full news article.
                datum = datetime.datetime.strptime(soup_string, '%d %B %Y %H:%M')
                datum = datetime.datetime.strftime(datum,'%Y%m%d') ###date converted to yyyymmdd format (e.g. '20210328')
                title = soup.find_all('h1')[0].text.strip() ### extracting title of news article, to be used in file name and for the pdf
                
                for k in title.split("\n"):
                    title = re.sub(r"[^a-zA-Z0-9]+", ' ', k) ### cleaning up the title, so that no illegal characters are present in the file name
                file_name = export_path + datum +'_Nu.nl_'+title+'.pdf' ### file name format is export path (location where pdfs are saved) then date, then source
                                                                        ### then title of article. E.g. 'C:\\Documents\\20210328_nu.nl_Het aantal cases stijgt.pdf'                                                                                         
                all_everything = soup.find_all(['p','img','h1','h2']) ### creates a list with all the relevant objects (p=paragraphs, img = images, h1=title, 
                                                                       ####   h2 = subtitles)
                all_p = soup.find_all('p')          ### separate list with just the text paragraphs
                all_im = soup.find_all('img')       ### separate list with just the images
                start = '<!DOCTYPE html>'           ### In order to create a pdf document we first build it in HTML. This is the start of that.
                hlink = '<a href=' + html + '>link to original article</a>' ### link to the original article, so the user can click on that in the pdf.
                source_txt = '<p> Source: ' + domain_name + '</p>'          ### source of the article
                pub_date =  '<p> Publication date: '+ datum + '</p>'        ### date of publishing
                headline = soup.find_all('h1')                              ### headline = title
                p3 = '</html>'                                              ### final line to finish the html file
                full_page = start + hlink + source_txt + pub_date           ### creates the start of the full html file as a string
                strsoup = str(soup)
                if 'LocalFocus' in strsoup:
                    full_page = full_page + 'Interactive charts are present in this article but could not be included automatically \n'
                
                
                did_find = 0        # many sites contain icons and other images we do not want in our pdf document. This is a check to only include images
                                    # that appear after the title of the news article.
                start_img = 0       # in the case of nu.nl there is one image that appears right before the title of the news article, but that we do want to
                                    # include in the pdf.
                end_h2 = 0          # any remaining stuff after the final h2 item is website layout and menus that we do not want in our pdf document. 
                for p in range(len(all_everything)):
                    if str(all_everything[p])[0:9] == '<h2 class':
                        end_h2 = 1
                    if end_h2 == 1:
                        pass
                    else:                                                
                        if str(all_everything[p])[0:3] == '<h1': ### set did_find to 1 if the title of the document is found in the list of relevant objects.
                            did_find = 1
                            
                        if did_find == 1:
                            if str(all_everything[p])[0:4] == '<img': ### if the title is found and an image is encountered in all_everything, it is added to 
                                                                      ### to the pdf document. self.image_cleaner makes sure the image will work and fit on the pdf
                                im_str = self.image_cleaner(all_everything[p])
                                full_page = full_page + im_str + '\n' ### adds the image to the full_page html string
                            else:
                                full_page = full_page + str(all_everything[p]) + '\n' ### if not an image or header, this is either a subtitle or paragraph 
                                                                                      ### and is therefore added to the full_page html string
                                if did_find == 1 and start_img == 0:
                                    full_page = full_page + self.image_cleaner(all_im[3]).split('>')[0] + '>\n' ### this is the starting image that we want in the pdf
                                    start_img = 1                                
                full_page = full_page + p3 ### adds the final bit to the full_page html string. full_page is then passed on the the next part of the script. See 
                                           ### the end of this definition.
        
        elif self.domain_name == 'nos.nl':
            try:
                liveblog_text = soup.find('body', class_="page-liveblog")['id'].split('-')[0]
            except (ValueError,TypeError):
                liveblog_text = ''
            if liveblog_text == 'liveblog':
                is_liveblog = 1
                datum = datetime.datetime.now()
                datum = datetime.datetime.strftime(datum,'%Y%m%d')
                strsoup = str(soup)

                start = '<!DOCTYPE html>'
                
                p3 = '</html>'

                
                parts = strsoup.split('liveblog__update__title js-liveblog-update-title')
                for s in range(1,len(parts)):
                    title = parts[s].split('>')[1].split('<')[0]
                    final_text = parts[s].split('class="liveblog__elements">')[1].split('</div> </li>')[0]
                    full_page = start + '<p>link to original article not possible for NOS liveblog'+ '<p>' + datum +'<p>' + '<h2>'+ title + '</h2>' + '<p>' +final_text + p3

                    file_name = export_path + '\\' + datum +'_NOS.nl liveblog_'+title+'.pdf'
                    the_page = HTML(string=full_page).render(presentational_hints=True)        
                    the_page.write_pdf(file_name)

            
            else:
                
                datum = str(soup.find('time')).split('"')[1].split('T')[0]
                datum = datetime.datetime.strptime(datum,'%Y-%m-%d')
                datum = datetime.datetime.strftime(datum,'%Y%m%d')
                title = soup.find_all('h1')[0].text.strip()
                
                for k in title.split("\n"):
                    title = re.sub(r"[^a-zA-Z0-9]+", ' ', k)
                
                
                all_everything = soup.find_all(['p','img','h1','h3'])
                all_p = soup.find_all('p')
                all_im = soup.find_all('img')
                start = '<!DOCTYPE html>'
                hlink = '<a href=' + html + '>link to original article</a>'
                source_txt = '<p> Source: ' + domain_name + '</p>'
                pub_date =  '<p> Publication date: '+ datum + '</p>'
                headline = soup.find_all('h1')
                p3 = '</html>'
                full_page = start + hlink + source_txt + pub_date
                did_find = 0
                start_img = 0
                end_h3 = 0
                for p in range(len(all_everything)):
                    if end_h3 == 1:
                        pass
                    else:
                        if str(all_everything[p])[0:3] == '<h1':
                            did_find = 1
                            
                        if did_find == 1:
                            if str(all_everything[p])[0:4] == '<img':                            
                                im_str = self.image_cleaner(all_everything[p])
                                full_page = full_page + im_str + '\n'
                            elif str(all_everything[p])[0:3] == '<h3':
                                end_h3 = 1
                            else:
                                if end_h3 == 0:
                                    full_page = full_page + str(all_everything[p]) + '\n'
                                    if did_find == 1 and start_img == 0:
                                        full_page = full_page + self.image_cleaner(all_im[1]) + '\n'
                                        start_img = 1
                full_page = full_page + p3
                
        
        elif self.domain_name == 'volkskrant.nl':
            soup_string = soup.find(class_ = "artstyle__byline__date" ).text
            try:
                liveblog_text = soup.find(class_ = "artstyle__labels__label" ).text.lower()
            except ValueError:
                liveblog_text = ''
            if liveblog_text == 'liveblog':
                is_liveblog = 1
                lb_html = 'https://digital-content.dpgmedia.net/live-blog/web/' + soup.find('article-element-livefeed')['id']
                r2 = requests.get(lb_html)
                
                soup2 = BS(r2.content, 'html.parser')
                strsoup2 = str(soup2)
                datum = datetime.datetime.now()
                datum = datetime.datetime.strftime(datum,'%Y%m%d')
                start = '<!DOCTYPE html>'
                p3 = '</html>'
                
                parts = strsoup2.split('"title":')
                for s in range(1,len(parts)):
                    title = parts[s].split(',')[0]
                    if title == '"Liveblog afgesloten"':
                        pass
                    else:
                        for k in title.split("\n"):
                            title = re.sub(r"[^a-zA-Z0-9]+", ' ', k)
                        texts = parts[s].split('"text":')
                        final_text = ''
                        for ss in range(1,len(texts)):
                            final_text = final_text + '<p>' + texts[ss].split('"id":')[0][1:-2]
                        image_html = ''
                        
                        if len(parts[s].split('"type":"IMAGE"')) > 1:
                            image_part = parts[s].split('"type":"IMAGE"')[1]
                            try:
                                image_html = '<img src=' + image_part.split('rendercacheUrl":"')[1].split('","')[0] + ' alt=' + image_part.split('caption":"')[1].split('","')[0]  + ' width=600>'
                            except IndexError:
                                image_html = '<img src=' + image_part.split('rendercacheUrl":"')[1].split('","')[0] + ' width=600>'
                        
                
                        full_page = start + '<p>link to original article not possible for Volkskrant liveblog'+ '<p>' + datum +'<p>' + '<h1>'+ title + '</h1>' + '<p>' +final_text + image_html+ p3                
    
                        file_name = export_path + '\\' + datum +'_Volkskrant.nl liveblog_'+title+'.pdf'
                        the_page = HTML(string=full_page).render(presentational_hints=True)        
                        the_page.write_pdf(file_name)

                
            else:             
                datum = datetime.datetime.strptime(soup_string, '%d %B %Y')
                datum = datetime.datetime.strftime(datum,'%Y%m%d')
                title = soup.find_all('h1')[0].text.strip()
                
                for k in title.split("\n"):
                    title = re.sub(r"[^a-zA-Z0-9]+", ' ', k)
                all_everything = soup.find_all(['p','img','h1','h3'])
                all_p = soup.find_all('p')
                all_im = soup.find_all('img')
                start = '<!DOCTYPE html>'
                hlink = '<a href=' + html + '>link to original article</a>'
                source_txt = '<p> Source: ' + domain_name + '</p>'
                pub_date =  '<p> Publication date: '+ datum + '</p>'
                headline = soup.find_all('h1')
                p3 = '</html>'
                full_page = start + hlink + source_txt + pub_date
                strsoup = str(soup)
                if 'flourish' in strsoup:
                    full_page = full_page + 'Interactive charts are present in this article but could not be included automatically \n'
                
                did_find = 0
                start_img = 0
                end_h3 = 0
                for p in range(len(all_everything)):
                    if end_h3 == 1:
                        pass
                    else:
                        if str(all_everything[p])[0:3] == '<h1':
                            did_find = 1
                            
                        if did_find == 1:
                            if str(all_everything[p])[0:4] == '<img':                            
                                im_str = self.image_cleaner(all_everything[p])
                                full_page = full_page + im_str + '\n'
                            elif str(all_everything[p])[0:14] == '<h3 class="edi':
                                end_h3 = 1
                            else:                        
                                full_page = full_page + str(all_everything[p]) + '\n'
                                    # if did_find == 1 and start_img == 0:
                                    #     full_page = full_page + self.image_cleaner(all_im[1]) + '\n'
                                    #     start_img = 1
                full_page = full_page + p3
        
        elif self.domain_name == 'ad.nl':
            strsoup = str(soup)
            html = strsoup.split('window.location.href =')[1].split(';')[0].strip()[1:-1]
            r2 = requests.get(html)
            soup = BS(r2.content, 'html.parser')
            #strsoup2 = str(soup)
            datum = soup.find_all(class_="article__time")[0].text.replace('.','')
            try:
                datum = datetime.datetime.strptime(datum, '%d %b %Y')
            except ValueError:
                datum = datum.split(',')[0]
                datum = datetime.datetime.strptime(datum, '%d-%m-%y')
            datum = datetime.datetime.strftime(datum,'%Y%m%d')
            title = soup.find_all('h1')[0].text.strip()
            
            for k in title.split("\n"):
                title = re.sub(r"[^a-zA-Z0-9]+", ' ', k)
            
            all_everything = soup.find_all(['p','img','h1','h3'])
            all_p = soup.find_all('p')
            all_im = soup.find_all('img')
            start = '<!DOCTYPE html>'
            hlink = '<a href=' + html + '>link to original article</a>'
            source_txt = '<p> Source: ' + domain_name + '</p>'
            pub_date =  '<p> Publication date: '+ datum + '</p>'
            headline = soup.find_all('h1')
            p3 = '</html>'
            full_page = start + hlink + source_txt + pub_date
            did_find = 0
            start_img = 0
            end_h3 = 0
            for p in range(len(all_everything)):
                if end_h3 == 1:
                    pass
                else:
                    if str(all_everything[p])[0:3] == '<h1':
                        did_find = 1
                        
                    if did_find == 1:
                        if str(all_everything[p])[0:4] == '<img':                            
                            im_str = self.image_cleaner(all_everything[p])
                            full_page = full_page + im_str + '\n'
                        elif str(all_everything[p]) == '<h3 class="header__title">Lees ook</h3>':
                            end_h3 = 1
                        else:
                            if str(all_everything[p])[0:3] == '<h3':
                                pass
                            elif str(all_everything[p])[0:27] == '<p class="recaptcha-legal">':
                                pass
                            else:
                                full_page = full_page + str(all_everything[p]) + '\n'
                                if did_find == 1 and start_img == 0:
                                    full_page = full_page + self.image_cleaner(all_im[0]) + '\n'
                                    start_img = 1
            full_page = full_page + p3
            
        
        elif self.domain_name == 'nrc.nl' or self.domain_name == 'nrcmedia.nl':
            datum = soup.find('time', class_='article__byline__text').attrs["datetime"].split('T')[0]
            datum = datetime.datetime.strptime(datum,'%Y-%m-%d')
            datum = datetime.datetime.strftime(datum,'%Y%m%d')
            title = soup.find_all('h1')[0].text.strip()
            
            for k in title.split("\n"):
                title = re.sub(r"[^a-zA-Z0-9]+", ' ', k)
            all_everything = soup.find_all(['p','img','h1','h3'])
            all_p = soup.find_all('p')
            all_im = soup.find_all('img')
            start = '<!DOCTYPE html>'
            hlink = '<a href=' + html + '>link to original article</a>'
            source_txt = '<p> Source: ' + domain_name + '</p>'
            pub_date =  '<p> Publication date: '+ datum + '</p>'
            headline = soup.find_all('h1')
            p3 = '</html>'
            full_page = start + hlink + source_txt + pub_date
            strsoup = str(soup)
            if 'flourish' in strsoup:
                full_page = full_page + 'Interactive charts are present in this article but could not be included automatically \n'
            
            did_find = 0
            start_img = 0
            end_h3 = 0
            for p in range(len(all_everything)):
                if end_h3 == 1:
                    pass
                else:
                    if str(all_everything[p])[0:3] == '<h1':
                        did_find = 1
                        
                    if did_find == 1:
                        if str(all_everything[p])[0:4] == '<img':                            
                            im_str = self.image_cleaner(all_everything[p])
                            full_page = full_page + im_str + '\n'
                        elif str(all_everything[p]) == '<h3 class="header__title">Lees ook</h3>':
                            end_h3 = 1
                        else:
                            if str(all_everything[p])[0:3] == '<h3':
                                pass
                            elif str(all_everything[p])[0:27] == '<p class="recaptcha-legal">':
                                pass
                            else:
                                full_page = full_page + str(all_everything[p]) + '\n'
                                # if did_find == 1 and start_img == 0:
                                #     full_page = full_page + self.image_cleaner(all_im[0]) + '\n'
                                #     start_img = 1
            full_page = full_page + p3

        
        elif self.domain_name == 'rtvutrecht.nl':                   
            datum = soup.find('span', class_='news-pubdate').attrs["data-short-date"].split(',')[0][3::]
            datum = datetime.datetime.strptime(datum, '%d %B %Y')
            datum = datetime.datetime.strftime(datum,'%Y%m%d')
            strsoup = str(soup)
            title = soup.find_all('h1')[1].text.strip()
            
            for k in title.split("\n"):
                title = re.sub(r"[^a-zA-Z0-9]+", ' ', k)
            
            all_everything = soup.find_all(['p','img','h1','h4'])
            all_p = soup.find_all('p')
            all_im = soup.find_all('img')
            start = '<!DOCTYPE html>'
            hlink = '<a href=' + html + '>link to original article</a>'
            source_txt = '<p> Source: ' + domain_name + '</p>'
            pub_date =  '<p> Publication date: '+ datum + '</p>'
            headline = soup.find_all('h1')
            p3 = '</html>'
            full_page = start + hlink + source_txt + pub_date
            did_find = 0
            start_img = 0
            end_h4 = 0
            text_block = strsoup.split('<article class="article-content">')[1].split('</article>')[0]
            # for p in range(len(all_everything)):
            #     if str(all_everything[p])[0:3] == '<h1':
            #         did_find = 1
                    
            #     if did_find == 1:
            #         if str(all_everything[p])[0:4] == '<img':                            
            #             im_str = self.image_cleaner(all_everything[p])
            #             full_page = full_page + im_str + '\n'
            #         elif str(all_everything[p]) == '<h4 class="page-subtitle">Nieuwsoverzicht</h4>':
            #             end_h4 = 1
            #         else:
            #             if end_h4 == 1:
            #                 pass
            #             else:
            #                 full_page = full_page + str(all_everything[p]) + '\n'
            #                 # if did_find == 1 and start_img == 0:
            #                 #     full_page = full_page + self.image_cleaner(all_im[0]) + '\n'
            #                 #     start_img = 1
            full_page = full_page + text_block + p3
         
        
        elif self.domain_name == 'rtvnoord.nl':
            datum = soup.find('span', class_='news-pubdate').attrs["data-short-date"].split(',')[0][3::]
            datum = datetime.datetime.strptime(datum, '%d %b %Y')
            datum = datetime.datetime.strftime(datum,'%Y%m%d')
            
            title = soup.find_all('h1')[0].text.strip()
            
            for k in title.split("\n"):
                title = re.sub(r"[^a-zA-Z0-9]+", ' ', k)
              
            all_everything = soup.find_all(['p','img','h1'])
            all_p = soup.find_all('p')
            all_im = soup.find_all('img')
            start = '<!DOCTYPE html>'
            hlink = '<a href=' + html + '>link to original article</a>'
            source_txt = '<p> Source: ' + domain_name + '</p>'
            pub_date =  '<p> Publication date: '+ datum + '</p>'
            headline = soup.find_all('h1')
            p3 = '</html>'
            full_page = start + hlink + source_txt + pub_date
            did_find = 0
            start_img = 0
            end_h3 = 0
            img_set = []
            for p in range(len(all_everything)):
                if end_h3 == 1:
                    pass
                else:                
                    if str(all_everything[p])[0:3] == '<h1':
                        did_find = 1
                        
                    if did_find == 1:
                        if str(all_everything[p])[0:4] == '<img':
                            if all_everything[p]['src'] in img_set:
                                print('skipppp')
                                pass                            
                            else:
                                img_set.append(all_everything[p]['src'])
                                im_str = self.image_cleaner(all_everything[p])
                                full_page = full_page + im_str + '\n'                                
                                #print(im_str)
                        elif str(all_everything[p])[0:29] == '<p><strong>Lees ook:</strong>':
                                end_h3 = 1                        
                        else:
                            if end_h3 == 1:
                                pass
                            else:
                                full_page = full_page + str(all_everything[p]) + '\n'

            full_page = full_page + p3
            
            
        elif self.domain_name == 'trouw.nl':
            soup_string = soup.find(class_ = "artstyle__byline__date" ).text
            try:
                liveblog_text = soup.find('template')['id']
            except ValueError:
                liveblog_text = ''
            if liveblog_text == 'live-blog-updates':
                is_liveblog = 1
                lb_html = 'https://digital-content.dpgmedia.net/live-blog/web/' + soup.find('article-element-livefeed')['id']
                r = requests.get(lb_html)
                
                soup = BS(r.content, 'html.parser')
                strsoup = str(soup)
                datum = datetime.datetime.now()
                datum = datetime.datetime.strftime(datum,'%Y%m%d')
                start = '<!DOCTYPE html>'
                p3 = '</html>'
                
                parts = strsoup.split('"title":')
                for s in range(1,len(parts)):
                    title = parts[s].split(',')[0]
                    for k in title.split("\n"):
                        title = re.sub(r"[^a-zA-Z0-9]+", ' ', k)
                    texts = parts[s].split('"text":')
                    final_text = ''
                    for ss in range(1,len(texts)):
                        final_text = final_text + '<p>' + texts[ss].split('"id":')[0][1:-2]
                    image_html = ''
                    
                    if len(parts[s].split('"type":"IMAGE"')) > 1:
                        image_part = parts[s].split('"type":"IMAGE"')[1]
                        image_html = '<img src=' + image_part.split('rendercacheUrl":"')[1].split('","')[0] + ' alt=' + image_part.split('caption":"')[1].split('","')[0]  + ' width=600>'
                    
            
                    full_page = start + '<p>link to original article not possible for Trouw liveblog'+ '<p>' + datum +'<p>' + '<h1>'+ title + '</h1>' + '<p>' +final_text + image_html+ p3                

                    file_name = export_path + '\\' + datum +'_Trouw.nl liveblog_'+title+'.pdf'
                    the_page = HTML(string=full_page).render(presentational_hints=True)        
                    the_page.write_pdf(file_name)                
                            
            else:            
                datum = soup.find('time', class_='artstyle__byline__datetime').attrs["datetime"].split(',')[0]
                datum = datetime.datetime.strptime(datum, '%d %B %Y')
                datum = datetime.datetime.strftime(datum,'%Y%m%d')
                
                title = soup.find_all('h1')[0].text.strip()
                
                for k in title.split("\n"):
                    title = re.sub(r"[^a-zA-Z0-9]+", ' ', k)
                all_everything = soup.find_all(['p','img','h1','h3'])
                all_p = soup.find_all('p')
                all_im = soup.find_all('img')
                start = '<!DOCTYPE html>'
                hlink = '<a href=' + html + '>link to original article</a>'
                source_txt = '<p> Source: ' + domain_name + '</p>'
                pub_date =  '<p> Publication date: '+ datum + '</p>'
                headline = soup.find_all('h1')
                p3 = '</html>'
                full_page = start + hlink + source_txt + pub_date
                strsoup = str(soup)
                if 'flourish' in strsoup:
                    full_page = full_page + 'Interactive charts are present in this article but could not be included automatically \n'
                did_find = 0
                start_img = 0
                end_h3 = 0
                for p in range(len(all_everything)):
                    if end_h3 == 1:
                        pass
                    else:
                        if str(all_everything[p])[0:3] == '<h1':
                            did_find = 1
                            
                        if did_find == 1:
                            if str(all_everything[p])[0:4] == '<img':                            
                                im_str = self.image_cleaner(all_everything[p])
                                full_page = full_page + im_str + '\n'
                            elif str(all_everything[p]) == '<h3 class="header__title">Lees ook</h3>':
                                end_h3 = 1
                            else:
                                if str(all_everything[p])[0:3] == '<h3':
                                    pass
                                else:
                                    full_page = full_page + str(all_everything[p]) + '\n'
                                    # if did_find == 1 and start_img == 0:
                                    #     full_page = full_page + self.image_cleaner(all_im[0]) + '\n'
                                    #     start_img = 1
                full_page = full_page + p3
                
            
            
        elif self.domain_name == 'rtlnieuws.nl':
            datum = soup.find('span', class_='time time-created').text
            try:
                datum = datetime.datetime.strptime(datum, '%d %B %Y %H:%M')
            except ValueError:
                datum = datetime.datetime.today()
            datum = datetime.datetime.strftime(datum,'%Y%m%d')
            title = soup.find_all('h1')[0].text.strip()            
            for k in title.split("\n"):
                title = re.sub(r"[^a-zA-Z0-9]+", ' ', k)
           
            all_everything = soup.find_all(['p','img','h1','h3'])
            all_p = soup.find_all('p')
            all_im = soup.find_all('img')
            start = '<!DOCTYPE html>'
            hlink = '<a href=' + html + '>link to original article</a>'
            source_txt = '<p> Source: ' + domain_name + '</p>'
            pub_date =  '<p> Publication date: '+ datum + '</p>'
            headline = soup.find_all('h1')
            p3 = '</html>'
            full_page = start + hlink + source_txt + pub_date
            strsoup = str(soup)
            if 'flourish' in strsoup:
                full_page = full_page + 'Interactive charts are present in this article but could not be included automatically \n'
            
            did_find = 0
            start_img = 0
            end_h3 = 0
            for p in range(len(all_everything)):
                if end_h3 == 1:
                    pass
                else:
                    if str(all_everything[p])[0:3] == '<h1':
                        did_find = 1
                        
                    if did_find == 1:
                        if str(all_everything[p])[0:4] == '<img':      
                            im_str = self.image_cleaner(all_everything[p])
                            full_page = full_page + im_str + '\n'
                        elif str(all_everything[p])[0:29] == '<p class="app-promo-article">':
                            end_h3 = 1
                        else:
                            full_page = full_page + str(all_everything[p]) + '\n'
                                # if did_find == 1 and start_img == 0:
                                #     full_page = full_page + self.image_cleaner(all_im[0]) + '\n'
                                #     start_img = 1
            full_page = full_page + p3
            
        
        elif self.domain_name == 'telegraaf.nl':
            strsoup = str(soup)
            datum = strsoup.split('datePublished":"')[1].split('T')[0]
            datum = datetime.datetime.strptime(datum, '%Y-%m-%d')
            datum = datetime.datetime.strftime(datum,'%Y%m%d')
            
            title = soup.find_all('h1')[0].text.strip()
            
            for k in title.split("\n"):
                title = re.sub(r"[^a-zA-Z0-9]+", ' ', k)

            all_everything = soup.find_all(['p','img','h1'])
            all_p = soup.find_all('p')
            all_im = soup.find_all('img')
            start = '<!DOCTYPE html>'
            hlink = '<a href=' + html + '>link to original article</a>'
            source_txt = '<p> Source: ' + domain_name + '</p>'
            pub_date =  '<p> Publication date: '+ datum + '</p>'
            headline = soup.find_all('h1')
            p3 = '</html>'
            full_page = start + hlink + source_txt + pub_date
            did_find = 0
            start_img = 0
            end_h3 = 0
            for p in range(len(all_everything)):
                if end_h3 == 1:
                    pass
                else:
                    if str(all_everything[p])[0:3] == '<h1':
                        did_find = 1
                        
                    if did_find == 1:
                        if str(all_everything[p])[0:4] == '<img':
                            im_str = self.image_cleaner(all_everything[p])
                            full_page = full_page + im_str + '\n'
                        elif str(all_everything[p])[0:35] == '<p class="NewsletterForm__subtitle"':
                            end_h3 = 1
                        else:
                            full_page = full_page + str(all_everything[p]) + '\n'
                                # if did_find == 1 and start_img == 0:
                                #     full_page = full_page + self.image_cleaner(all_im[0]) + '\n'
                                #     start_img = 1
            full_page = full_page + p3
                
        elif self.domain_name == 'parool.nl':
            ### het menu zit nog in de weg van de PDF
            datum = soup.find('span', class_='artstyle__byline__date').text
            datum = datetime.datetime.strptime(datum, '%d %B %Y')
            datum = datetime.datetime.strftime(datum,'%Y%m%d')
            
            title = soup.find_all('h1')[0].text.strip()
            
            for k in title.split("\n"):
                title = re.sub(r"[^a-zA-Z0-9]+", ' ', k)
            all_everything = soup.find_all(['p','img','h1','h3'])
            all_p = soup.find_all('p')
            all_im = soup.find_all('img')
            start = '<!DOCTYPE html>'
            hlink = '<a href=' + html + '>link to original article</a>'
            source_txt = '<p> Source: ' + domain_name + '</p>'
            pub_date =  '<p> Publication date: '+ datum + '</p>'
            headline = soup.find_all('h1')
            p3 = '</html>'
            full_page = start + hlink + source_txt + pub_date
            did_find = 0
            start_img = 0
            end_h3 = 0
            for p in range(len(all_everything)):
                if end_h3 == 1:
                    pass
                else:
                    if str(all_everything[p])[0:3] == '<h1':
                        did_find = 1
                        
                    if did_find == 1:
                        if str(all_everything[p])[0:4] == '<img':
                            im_str = self.image_cleaner(all_everything[p])
                            full_page = full_page + im_str + '\n'
                        elif str(all_everything[p])[0:25] == '<h3 class="editorial-tips':
                            end_h3 = 1
                        else:
                            full_page = full_page + str(all_everything[p]) + '\n'
                                # if did_find == 1 and start_img == 0:
                                #     full_page = full_page + self.image_cleaner(all_im[0]) + '\n'
                                #     start_img = 1
            full_page = full_page + p3

        
        elif self.domain_name == 'gelderlander.nl': 
            ### het kan zijn dat alle DPG websites exact hetzelfde werken, dan kan ik daar een algemene voor maken 
            ### (AD en Gelderlander werken hetzelfde)
            strsoup = str(soup)
            html2 = strsoup.split('window.location.href =')[1].split(';')[0].strip()[1:-1]
            r2 = requests.get(html2)
            soup2 = BS(r2.content, 'html.parser')
            strsoup2 = str(soup2)
            datum = soup2.find_all(class_="article__time")[0].text.replace('.','')
            try:
                datum = datetime.datetime.strptime(datum, '%d %b %Y')
            except ValueError:
                datum = datum.split(',')[0]
                datum = datetime.datetime.strptime(datum, '%d-%m-%y')
                datum = datetime.datetime.strftime(datum,'%Y%m%d')
            
            soup = soup2
            html= html2
            title = soup.find_all('h1')[0].text.strip()
            
            for k in title.split("\n"):
                title = re.sub(r"[^a-zA-Z0-9]+", ' ', k)
            all_everything = soup.find_all(['p','img','h1','h3'])
            all_p = soup.find_all('p')
            all_im = soup.find_all('img')
            start = '<!DOCTYPE html>'
            hlink = '<a href=' + html + '>link to original article</a>'
            source_txt = '<p> Source: ' + domain_name + '</p>'
            pub_date =  '<p> Publication date: '+ datum + '</p>'
            headline = soup.find_all('h1')
            p3 = '</html>'
            full_page = start + hlink + source_txt + pub_date
            did_find = 0
            start_img = 0
            end_h3 = 0
            for p in range(len(all_everything)):
                if end_h3 == 1:
                    pass
                else:
                    if str(all_everything[p])[0:3] == '<h1':
                        did_find = 1
                        
                    if did_find == 1:
                        if str(all_everything[p])[0:4] == '<img':
                            try:
                                if all_everything[p]['class'] == ['ankeiler__image']:
                                    pass
                                else:
                                    im_str = self.image_cleaner(all_everything[p])
                                    full_page = full_page + im_str + '\n'
                            except KeyError:
                                    im_str = self.image_cleaner(all_everything[p])
                                    full_page = full_page + im_str + '\n'
                                    
                        elif str(all_everything[p])[0:35] == '<p class="article-login-gate__title':
                            end_h3 = 1
                        else:
                            if str(all_everything[p])[0:27] == '<p class="recaptcha-legal">':
                                pass
                            elif str(all_everything[p])[0:39] == '<h3 class="header__title">Lees ook</h3>':
                                pass
                            elif str(all_everything[p])[0:28] == '<h3 class="ankeiler__title">':
                                pass
                            else:
                                full_page = full_page + str(all_everything[p]) + '\n'
                                if did_find == 1 and start_img == 0:
                                    full_page = full_page + self.image_cleaner(all_im[0]) + '\n'
                                    start_img = 1
            full_page = full_page + p3

        elif self.domain_name == 'skipr.nl':
            #strsoup = str(soup)
            datum = soup.find('time',class_='entry-time').text
            datum = datetime.datetime.strptime(datum, '%d %B %Y')
            datum = datetime.datetime.strftime(datum,'%Y%m%d')
            title = soup.find('title').text
            for k in title.split("\n"):
                title = re.sub(r"[^a-zA-Z0-9]+", ' ', k)
            all_everything = soup.find_all(['p','img','h1','h3'])
            all_p = soup.find_all('p')
            all_im = soup.find_all('img')
            start = '<!DOCTYPE html>'
            hlink = '<a href=' + html + '>link to original article</a>'
            source_txt = '<p> Source: ' + domain_name + '</p>'
            pub_date =  '<p> Publication date: '+ datum + '</p>'
            headline = soup.find_all('h1')
            p3 = '</html>'
            full_page = start + hlink + source_txt + pub_date
            did_find = 0
            start_img = 0
            end_h3 = 0
            for p in range(len(all_everything)):
                if end_h3 == 1:
                    pass
                else:
                    if str(all_everything[p])[0:3] == '<h1':
                        did_find = 1
                        
                    if did_find == 1:
                        if str(all_everything[p])[0:4] == '<img':
                            pass
                        elif str(all_everything[p])[0:36] == '<h3 class="">Interessant voor u</h3>':
                            end_h3 = 1
                        else:
                            full_page = full_page + str(all_everything[p]) + '\n'
                                # if did_find == 1 and start_img == 0:
                                #     full_page = full_page + self.image_cleaner(all_im[0]) + '\n'
                                #     start_img = 1
            full_page = full_page + p3

        
        elif self.domain_name == 'rijksoverheid.nl':
            datum = soup.find('p', class_='article-meta').text.split('|')[1].strip()
            datum = datetime.datetime.strptime(datum, '%d-%m-%Y')
            datum = datetime.datetime.strftime(datum,'%Y%m%d')
            title = soup.find('title').text.split('|')[0].strip()
            for k in title.split("\n"):
                title = re.sub(r"[^a-zA-Z0-9]+", ' ', k)                
            all_everything = soup.find_all(['p','img','h1','h3'])
            all_p = soup.find_all('p')
            all_im = soup.find_all('img')
            start = '<!DOCTYPE html>'
            hlink = '<a href=' + html + '>link to original article</a>'
            source_txt = '<p> Source: ' + domain_name + '</p>'
            pub_date =  '<p> Publication date: '+ datum + '</p>'
            headline = soup.find_all('h1')
            p3 = '</html>'
            full_page = start + hlink + source_txt + pub_date
            did_find = 0
            start_img = 0
            end_h3 = 0
            for p in range(len(all_everything)):
                if end_h3 == 1:
                    pass
                else:
                    if str(all_everything[p])[0:3] == '<h1':
                        did_find = 1
                        
                    if did_find == 1:
                        if str(all_everything[p])[0:4] == '<img':
                            im_str = self.image_cleaner(all_everything[p])
                            full_page = full_page + im_str + '\n'
                        else:
                            full_page = full_page + str(all_everything[p]) + '\n'
                                # if did_find == 1 and start_img == 0:
                                #     full_page = full_page + self.image_cleaner(all_im[0]) + '\n'
                                #     start_img = 1
            full_page = full_page + p3
        
        
        else:
            datum = ''
            title = ''
        if is_liveblog == 0: ### this sets some stuff in the user interface, such as the title and source. 
            self.source_entry.delete(0,END)        
            self.source_entry.insert(END, self.domain_name.split('.')[0]) 
            self.date_entry.delete(0,END) 
            self.date_entry.insert(END, datum)
            self.title_entry.delete(0,END)
            self.title_entry.insert(END, title)            
        else:
            html = 'this is a liveblog @@@___@@@'  ### no stuff is set if it is a liveblog
            
        return title, datum, html, soup, full_page
    
    
    
    # automatically extract title, source and date of url, then save to pdf. Only works for sites in self.supported_sites list
    def process_pdf(self):    
        self.known_website = 0
        self.get_url = self.url_entry.get().strip()
        self.domain_name,self.soup = self.get_website(self.get_url)   ### get domain name and soup (Beautiful Soup is a Python library for pulling data out of HTML and XML files)
                                                                 ### soup is the html code of a website.
        html = self.get_url
        export_path = self.selected_folder + '\\'               ### path where the pdf documents will be saved. Standard folder can be set, or can be temporarily changed in UI
        if self.domain_name in self.supported_sites:  ### if the website is in the list of websites that can be processed automatically, it will be processed.
            self.title,self.datum,self.html,self.soup,self.full_page = self.known_site(html,self.soup,self.domain_name) ### this function extracts title, date of publication
                                    ### the final url in case of a cookie wall, the html code (soup), and the full html code that will become the pdf.
            self.known_website = 1
            if self.html == 'this is a liveblog @@@___@@@': ## if it is a liveblog the processing is done in self.known_site() function
               self.communication_label.configure(text='liveblog saved') ### UI will show when the liveblog has finished saving.
            else:
               file_name = self.please_write_pdf(self.soup,export_path,self.datum,self.domain_name.split('.')[0], self.title,self.html,self.domain_name,self.known_website,self.full_page)
               ### if the url is a news article, rather than a live blog, the extracted data from self.known_site() is passed on to self.please_write_pdf() function
               self.communication_label.configure(text='PDF saved as ' + file_name) ### once it has finished saving, the UI will tell
        else:
            self.communication_label.configure(text=self.domain_name +'\n is not compatible with automatic processing. \n Use manual processing for this website')
            ### if the URL is not in the list of automatically processed websites, the UI tells the user.
    
    # show list with supported sites
    def show_sites(self):        
        list_sites = ''
        for site in self.supported_sites:
            list_sites = list_sites + site + '\n'
        self.communication_label.configure(text='The following is the list of websites available for automatic saving: \n'+list_sites)
           
     # save pdf based on url, title, source and date filled in the fields. Not all websites are in the list of automatically processed sites. These 
     # can be saved 'manually'. The title and source are usually extracted correctly using the self.analyse_pdf() function, but the date is always 
     # set to the date the user is saving the pdf, or to the date the user put in manually.
    def process_pdf_manual(self):        
        self.known_site = 0
        self.get_url = self.url_entry.get()
        self.domain_name,soup = self.get_website(self.get_url)
        html = self.get_url
        export_path = self.selected_folder + '\\'
        title = self.title_entry.get()
        source = self.source_entry.get()
        a_date = self.date_entry.get()
        #the_page = HTML(html).render()
        for k in title.split("\n"):
                title = re.sub(r"[^a-zA-Z0-9]+", ' ', k)
        file_name = self.please_write_pdf(soup,export_path,a_date,source,title,html,self.domain_name,self.known_site, known_soup='')

        self.communication_label.configure(text='PDF saved as ' + file_name)

    # get domain name and html soup from url
    def get_website(self, get_url):
        try:
            domain_name = tldextract.extract(get_url).domain + '.' + tldextract.extract(get_url).suffix
            r = requests.get(get_url)
            soup = BS(r.content, 'html.parser')
        except (requests.exceptions.MissingSchema, requests.exceptions.ConnectionError) as err:
            self.communication_label.configure(text='Invalid URL. Check to make sure the following is a valid website and starts with http or https:\n' + self.get_url)
            domain_name = ''
            soup = ''
        return domain_name,soup
    #tries to extract title, source and date and fill in fields.
    def analyse_website(self):        
        self.get_url = self.url_entry.get()
        self.domain_name,soup = self.get_website(self.get_url)
        html = self.get_url
        export_path = self.selected_folder + '\\'
        if self.domain_name in self.supported_sites:
           self.title,self.datum,self.html,self.soup = self.known_site(html,soup,self.domain_name)
        else:
            title = soup.find('title').text
            for k in title.split("\n"):
                title = re.sub(r"[^a-zA-Z0-9]+", ' ', k)
            datum = datetime.datetime.today()
            datum = datetime.datetime.strftime(datum,'%Y%m%d')
            source = self.domain_name.split('.')[0]
            self.source_entry.delete(0,END)        
            self.source_entry.insert(END, source)
            self.date_entry.delete(0,END) 
            self.date_entry.insert(END, datum)
            self.title_entry.delete(0,END)
            self.title_entry.insert(END, title) 
        self.communication_label.configure(text='Set title as: ' + title +'\n\n' + 'Set source as: ' + source +'\n\n' + 'Set date as: ' + datum + " (today's date)")
    
    ### javascript based images, such as charts and interactive tables, cannot be extracted using requests and beautifulsoup. Therefore this function is used to manually 
    ### add a screenshot the user can make of such charts. When clicking the "Add user image to pdf" button, the current image on the clipboard is added. Multiple 
    ### images can be added. Each image will be apppended to the pdf file. 
    def create_user_image(self):
        def add_user_image(num_im, im_list):
            im = ImageGrab.grabclipboard()
            if im == None:
                self.communication_label.configure(text='No image found. Use Windows key + shift key + s to copy an image to the clipboard')
            else:
                num_im+=1    
                im = im.resize((600,math.floor(im.height/(im.width/600))))
                im = im.convert('RGB')
                im_path = testt + "\\img" + str(num_im) + ".png"
                im.save(im_path,"PNG")
                im_list.append(im_path)
            
            return num_im, im_list
       
        self.num_im, self.im_list = add_user_image(self.num_im, self.im_list)
        self.user_images_label['text'] = str(self.num_im) + ' user images will be added to pdf'

        return self.num_im, self.im_list
    
    #function to remove all currently added user images
    def remove_all_user_img(self):
        self.num_im = 0
        self.im_list = []
        self.user_images_label['text'] = str(self.num_im) + ' user images will be added to pdf'
        
        
    def image_cleaner(self, img):        
        clean_img = 'temp'
        try:
            im_source = img['src']
            if 'https://' not in im_source: ### sometimes the domain name is not put in the source, causing the image to not save properly in the pdf. This 
                                            ### bit adds the domain name to the image source.
                im_source = 'https://www.' + self.domain_name + im_source
                img['src'] = im_source
                if ';' in img['src']: # some advertisement images may get into the list of relevant objects. Mostly with English websites. 
                                      # so far these could all be filtered by looking for a semicolon in the image source link. 
                    clean_img = '@no'
                    
        except KeyError:
            clean_img = ''
        
        if len(clean_img) > 0 and clean_img != '@no':
            clean_img = str(img).split('/>')
            if len(clean_img) > 1:  # this bit makes sure the image width is no more than 600 pixels, otherwise it exceeds the pdf page width.
                                    # 1 image can contain multiple widths, only the last width is actually processed.
                clean_img = clean_img[0] + ' width=600 />'
            else:                
                clean_img = str(img).split('>')[0] + ' width=600 />'
        else:
            clean_img=str(img)
        if clean_img == '@no':
            clean_img = ''
        
        return clean_img # either returns a clean image, or no image.
    
    def client_exit(self):
        exit()


root = Tk()
root.geometry("1900x700")
root.configure(background='#555555')
app = Application(root)

root.mainloop()  

