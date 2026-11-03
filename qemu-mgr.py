#!/usr/bin/python3
import gi,sys,os
gi.require_version("Gtk", "3.0")
#gi.require_version('Vte', '2.91')
from gi.repository import Gtk,Gdk #GLib,GObject

#------------------------------------------------------------------------------
#                            default paths
#------------------------------------------------------------------------------
scriptpath = os.path.dirname(os.path.realpath(__file__))+"/"  #self dir
ta_file="/dev/shm/ta"                                         #textarea file               
#------------------------------------------------------------------------------

hosts=[]
textbuffer=[]
idx_drive=0

class FDialog(Gtk.Dialog):
    def __init__(self,curdir,btn):
      super().__init__(title="Qemu Device")
      self.set_default_size(850, 450)
      self.btn=btn
      self.data=['Cancel','']
      self.model=Gtk.ListBox()
      self.hidden=False

      self.dir_entry = Gtk.Entry()
      self.dir_entry.set_width_chars(40)
      self.dir_entry.connect("changed",self.on_txt_chg)
      #self.dir_entry.connect("activate",self.on_txt_chg)
       
      self.dir_btn_back = Gtk.Button(label='') #label='&#8594;'
      self.dir_btn_back.connect("clicked",self.dir_back)
      for child in self.dir_btn_back:
        child.set_label('<span foreground="black" font="16" weight="heavy">&#9664;</span>')
        child.set_use_markup(True)

      self.dir_btn = Gtk.Button(label='') #label='&#8594;'
      self.dir_btn.connect("clicked",self.dir_chg)
      for child in self.dir_btn:
        child.set_label('<span foreground="black" font="16" weight="heavy">&#9654;</span>')
        child.set_use_markup(True)

      # Add to scroll window
      self.scr = Gtk.ScrolledWindow()
      self.scr.set_hexpand(False)
      self.scr.set_vexpand(True)
      hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
      hbox.add(self.dir_entry)
      hbox.add(self.dir_btn_back)
      hbox.add(self.dir_btn)
      vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
      self.area = self.get_content_area()
      self.get_style_context().add_class('mainwin')
      self.area.add(vbox)
      #vbox.add(self.dir_entry)
      vbox.add(hbox)
      #tbox_hidden
      rbtnbox=Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=3)  
      tbox=Gtk.CheckButton(label="Show Hidden Files")
      tbox.get_style_context().add_class('tglbox')
      tbox.connect("toggled", self.toggle, "tgl")
      rbtnbox.add(tbox)
      #radio btns
      self.rentry=['DVD','Drive','USB']
      self.rbtn=[]
      self.rbtn.append(Gtk.RadioButton())
      self.rbtn[0].set_label(self.rentry[0])
      rbtnbox.add(self.rbtn[0])
      for i in range(1,len(self.rentry)):
        self.rbtn.append(Gtk.RadioButton.new_from_widget(self.rbtn[0]))
        self.rbtn[i].set_label(self.rentry[i])
        rbtnbox.add(self.rbtn[i])
        self.rbtn[i].connect("toggled", self.usb_click, self.rentry[i])
      vbox.add(rbtnbox)
      #add scroller and file list
      vbox.add(self.scr)
      self.ebox=Gtk.EventBox()
      self.ebox.connect("button-press-event", self.click_label)
      self.scr.add(self.ebox)
      self.ebox.add(self.model)
#      self.scr.add(self.model)

      #buttons
      btnbox=Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=30)     
      for i in range(0,len(self.btn)):
        dbtn=Gtk.Button(label=self.btn[i])
        dbtn.get_style_context().add_class('mybutton')
        dbtn.connect("clicked", self.me_click,self.btn[i])
        btnbox.add(dbtn)
      vbox.pack_end(btnbox,False,False, 0) 
      
      self.model.connect("row-activated", self.selected_row_item)
      self.row_data=None

      self.dir_entry.set_text(curdir)
      self.run()

    def click_label(self,widget,event):
      #print(event.get_click_count()[1])
      if event.get_click_count()[1]==2:
        self.dir_chg(widget)

    def usb_click(self,button,name):
      if self.r_button()=='USB':
        self.load_usb()      
      else:
        self.dir_entry.set_text(self.last_curdir)

    def toggle(self,button,name):
      if button.get_active():
        self.hidden=True
      else:
        self.hidden=False
      self.on_txt_chg(button)

    def on_txt_key(self,widget):
      print('text key')

    def on_txt_chg(self,widget):
      if self.r_button()=='USB':
        return
      rmv=self.model.get_children()
      for row in range(0,len(rmv)):
        self.model.remove(rmv[row])
      if os.path.isdir(self.dir_entry.get_text()):
        self.row_data=None
        self.load_files(self.dir_entry.get_text())

    def dir_back(self,widget):
      if self.dir_entry.get_editable()==False:
        return
      if self.dir_entry.get_text()=="/":
        return
      selected = os.path.normpath(os.path.join(self.dir_entry.get_text(),"../")) 
      if not os.path.exists(selected):
        self.dir_entry.set_text(self.last_curdir)
        return
      self.row_data=None
      self.dir_entry.set_text(selected)

    def dir_chg(self,widget):
      if self.row_data==None:
        return
      if self.dir_entry.get_text()=="/":
        selected = os.path.normpath("/"+self.row_data)
      else:
        selected = os.path.join(self.dir_entry.get_text(),self.row_data)
      if os.path.isdir(selected):
        self.row_data=None
        self.dir_entry.set_text(selected)

    def selected_row_item(self, listbox, row):
      for x in row:
        self.row_data=x.get_text()

    def me_click(self,widget,btn):
      if btn == 'Cancel':
        self.data=[btn,'']
        self.destroy()
      elif btn == 'OK':
        if self.r_button()=='USB':
          if self.row_data!=None:
            self.data=[self.r_button(),self.row_data]
            self.hide()
        else:
          if self.row_data==None:
            selected=""
          else:
            selected=self.row_data
          if os.path.isdir(os.path.join(self.dir_entry.get_text(),selected)):
            self.dir_chg(widget)
          else:
            if os.path.exists(os.path.normpath(os.path.join(self.dir_entry.get_text(),selected))):
              self.data=[self.r_button(),os.path.normpath(os.path.join(self.dir_entry.get_text(),selected))]
              self.hide()
    
    def dlg_response(self):
        rsp=self.data
        self.destroy()
        return rsp

    def load_files(self,curdir):
      myfiles=[]
      mydir=[]
      file_list =  os.listdir(curdir)
      if self.hidden==False:
        for file in file_list:
          if file[:1]!='.':
            if os.path.isdir(os.path.join(curdir, file)):
              mydir.append(file)
            else:
              myfiles.append(file) 
      else:
        for file in file_list:
          if os.path.isdir(os.path.join(curdir, file)):
            mydir.append(file)
          else:
            myfiles.append(file) 
      mydir.sort()
      myfiles.sort()
      for item in mydir: 
        #item+="/"
        lbl=Gtk.Label(label=item)
        lbl.get_style_context().add_class('directory')
        lbl.set_xalign(0)
        self.model.add( lbl )
      for item in myfiles:
        lbl=Gtk.Label(label=item)
        lbl.set_xalign(0)
        self.model.add( lbl )
      self.dir_entry.set_editable(True)
      self.dir_entry.grab_focus_without_selecting()
      self.last_curdir=curdir 
      self.txt_chg=False 
      self.show_all()

    def r_button(self):
      for i in range(0,len(self.rbtn)):
        if self.rbtn[i].get_active():
          return self.rentry[i]

    def load_usb(self):
      rdata=os.popen('lsusb').read().split('\n')
      if len(rdata[-1])==0:
        rdata.pop() 
      rmv=self.model.get_children()
      for row in range(0,len(rmv)):
        self.model.remove(rmv[row])
      for item in rdata:
        lbl=Gtk.Label(label=item)
        lbl.set_xalign(0)
        self.model.add( lbl )
      self.dir_entry.set_text("USB Devices")
      self.dir_entry.set_editable(False)
      self.dir_entry.grab_focus_without_selecting()
      self.txt_chg=False 
      self.show_all()

class Dialog(Gtk.Dialog):
    def __init__(self, parent,dtitle,dtext,btn,dentry=False,rentry=False):
      Gtk.Dialog.__init__(self, parent=parent,title=dtitle)
      self.dtext=dtext
      self.dentry=dentry
      self.rentry=rentry
      self.btn=btn
      self.data=['Cancel','']

      vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
      self.area = self.get_content_area()
      self.get_style_context().add_class('mainwin')
      self.area.add(vbox)
      vbox.add ( Gtk.Label(label=self.dtext) )
      if self.dentry:  
        self.entry = Gtk.Entry()
        self.entry.set_text(self.dentry)
        vbox.pack_start(self.entry, True, True, 0)
      if self.rentry:  
        self.rbtn=[]
        self.rbtn.append(Gtk.RadioButton())
        self.rbtn[0].set_label(self.rentry[0])
        vbox.add(self.rbtn[0])
        for i in range(1,len(self.rentry)):
          self.rbtn.append(Gtk.RadioButton.new_from_widget(self.rbtn[0]))
          self.rbtn[i].set_label(self.rentry[i])
          #rbtn[i].set_active()
          #rbtn[i].connect("toggled", self.on_button_toggled, "1")
          vbox.add(self.rbtn[i])

      #buttons
      btnbox=Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=50)     
      for i in range(0,len(self.btn)):
        dbtn=Gtk.Button(label=self.btn[i])
        dbtn.get_style_context().add_class('mybutton')
        dbtn.connect("clicked", self.me_click,btn[i])
        btnbox.add(dbtn)
      vbox.pack_end(btnbox,False,False, 0)
      self.show_all()
      self.run()

    def me_click(self,widget,btn):
      if self.dentry:
        txt=self.entry.get_text()
      elif self.rentry:
        for i in range(0,len(self.rbtn)):
          if self.rbtn[i].get_active():
            txt=self.rentry[i]
      else:
        txt=''
      self.data=[btn,txt]
      self.hide()
    
    def dlg_response(self):
        rsp=self.data
        self.destroy()
        return rsp

class MainWin(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self)
        self.set_title('Qemu Virtual Machines')
        self.connect('destroy', self.close_clicked)
        notebook = Gtk.Notebook()
        self.add(notebook)
        self.set_default_size(500,350)

        mylist=os.popen("ls "+scriptpath+"*.vm").read()
        mylistarr=mylist.split('\n')
        if len(mylistarr[-1])==0:
          mylistarr.pop() 

        for i in range(0,len(mylistarr)):
          hosts.append(mylistarr[i].replace(scriptpath,''))
          lbl=Gtk.Label()
          lbl.set_text(hosts[i])
          lbl.get_style_context().add_class('tabclass')
          notebook.append_page(self.txtwin(i),lbl)

#---------------------------------------------------
#                   css info
#---------------------------------------------------
        css = b'''
textview { 
   font-size: 14px;
   font-family: monospace;
   font-weight: normal;
}
.mainwin {   
     font-size: 16px;
     font-weight: bold;
     font-family: DejaVu Sans;
     background-image: linear-gradient(to right, #7fb70e , #a2a3a1);
     padding-left: 20px;
     padding-right: 20px;
}
.tabclass {
   font-size: 16px;
   font-weight: bold;
}
.directory {
        color:blue;
}
.mybutton { 
        border-radius: 20px; border-width: 2px; border-style: outset; 
        background: lightgray;
        margin-bottom: 4px;
        margin-top: 2px; 
}
.mybutton:hover { /*background: #dff; border-color: #8bb;*/
               background: #969696; border-color: #8bb;
 }
'''
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(css)
        context = Gtk.StyleContext()
        screen = Gdk.Screen.get_default()
        context.add_provider_for_screen(screen, css_provider,
                                        Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

#---------------------------------------------------
#        txtwin
#---------------------------------------------------

    def txtwin(self,idx):
        #self.set_default_size(800,350)
        self.vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.vbox.add ( Gtk.Label() )

        #---textview---
        self.scr = Gtk.ScrolledWindow()
        self.scr.set_hexpand(False)
        self.scr.set_vexpand(True)
        self.vbox.add(self.scr)

        self.textview = Gtk.TextView()
        textbuffer.append(self.textview.get_buffer())
        
        self.scr.add(self.textview)
        #size of large white text box w,h   
        self.scr.set_size_request(800,400)
        self.textview.set_wrap_mode(Gtk.WrapMode.WORD)
        #-------------------
        file = open(scriptpath+'/'+hosts[idx], 'r') 
        contents=file.read()
        file.close()
        textbuffer[idx].set_text(contents)

        #buttons
        btnbox=Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=50)        
        self.closebtn=Gtk.Button(label="Exit")
        self.closebtn.get_style_context().add_class('mybutton')
        self.runbtn=Gtk.Button(label="Run")
        self.runbtn.get_style_context().add_class('mybutton')
        self.saveasbtn=Gtk.Button(label="Save")
        self.saveasbtn.get_style_context().add_class('mybutton')
        self.reloadbtn=Gtk.Button(label="Reload")
        self.reloadbtn.get_style_context().add_class('mybutton')
        self.fbtn=Gtk.Button(label="Device")
        self.fbtn.get_style_context().add_class('mybutton')
        self.delbtn=Gtk.Button(label="Delete")
        self.delbtn.get_style_context().add_class('mybutton')
        btnbox.pack_end(self.closebtn,False,False,0)
        btnbox.add(self.runbtn)
        btnbox.add(self.saveasbtn)
        btnbox.add(self.reloadbtn)
        btnbox.add(self.delbtn)
        if self.mtr_ip(idx):
          btnbox.add(self.fbtn)
        self.closebtn.connect("clicked", self.close_clicked)
        self.runbtn.connect("clicked", self.run_click,idx)
        self.saveasbtn.connect("clicked",self.saveas,idx)
        self.reloadbtn.connect("clicked",self.reload,idx)    
        self.fbtn.connect("clicked",self.fdiag,idx)    
        self.delbtn.connect("clicked",self.del_click,idx)
        self.vbox.pack_end(btnbox,False,False, 0)
        self.vbox.get_style_context().add_class('mainwin')
        return self.vbox

    def close_clicked(self, widget):
      sys.exit()

    def run_click(self,widget,idx):
      start = textbuffer[idx].get_start_iter()
      end = textbuffer[idx].get_end_iter()
      file = open(ta_file, 'w') 
      file.write(textbuffer[idx].get_text(start,end,True))
      file.close()
      os.system("bash '"+ta_file+"' &")

    def del_click(self, widget,idx):
      ans=Dialog(self,"Confirm","Delete \n"+hosts[idx]+" ?",["Yes","No"]).dlg_response()
      if ans[0]=="Yes":
        cmd="rm '"+scriptpath+hosts[idx]+"'"
        os.system(cmd)
        self.loaddata()

    def saveas(self,widget,idx):
      ans=Dialog(self,"Save As","Save VM as",["OK","Cancel"],hosts[idx]).dlg_response()
      if ans[0]!='Cancel' and len(ans[1])>0:
        start = textbuffer[idx].get_start_iter()
        end = textbuffer[idx].get_end_iter() 
        contents=textbuffer[idx].get_text(start,end,True)
        fn = scriptpath+ans[1]
        file = open(fn, 'w') 
        file.write(contents)
        file.close()
        self.loaddata()

    def reload(self,widget,idx):
      fn = scriptpath+hosts[idx] 
      start = textbuffer[idx].get_start_iter()
      end = textbuffer[idx].get_end_iter()
      file = open(fn, 'r') 
      contents=file.read()
      file.close()
      textbuffer[idx].set_text(contents)

    def fdiag(self,widget,idx):
       global idx_drive
       ans=FDialog(os.getcwd(),["OK","Cancel"]).dlg_response()
       #print(ans)
       if ans[0]=='DVD':
         if self.mtr_ip(idx):
           ip  = self.mtr_ip(idx)[0]
           port= self.mtr_ip(idx)[1]
           cmd="echo 'eject ide1-cd0'|nc -N "+ip+" "+port
           cmd+="&& sleep 2 && echo 'change ide1-cd0 \""+ans[1]+"\"'|nc -N "+ip+" "+port+" &"
           os.system(cmd)
       if ans[0]=='Drive':
           ip  = self.mtr_ip(idx)[0]
           port= self.mtr_ip(idx)[1]
           #add drive and device
           cmd="echo 'drive_add 0 \"if=none,file="+ans[1]+",id=vhd"+str(idx_drive)+",format=raw\"'|nc -N "+ip+" "+port
           os.system(cmd)
           cmd="echo 'device_add virtio-blk-pci,drive=vhd"+str(idx_drive)+"'|nc -N "+ip+" "+port
           os.system(cmd)
           idx_drive+=1
       if ans[0]=='USB':
         if MainWin.mtr_ip(self,idx):
           ip  = MainWin.mtr_ip(self,idx)[0]
           port= MainWin.mtr_ip(self,idx)[1]
           vid=ans[1][ans[1].find(": ID ")+5:ans[1].find(": ID ")+9]
           prid=ans[1][ans[1].find(": ID ")+10:ans[1].find(": ID ")+14]
           #load xhci driver (fails gracefully as Duplicate if already loaded)
           cmd="echo 'device_add qemu-xhci,id=xhci'|nc -N "+ip+" "+port
           os.system(cmd)
           cmd="echo 'device_add usb-host,vendorid=0x"+vid+",productid=0x"+prid+"'|nc -N "+ip+" "+port
           #print(cmd)
           os.system(cmd)
  
    def mtr_ip(self,idx):
      #get text from txtwin
      start = textbuffer[idx].get_start_iter()
      end = textbuffer[idx].get_end_iter()
      contents=textbuffer[idx].get_text(start,end,True)
      carr=contents.split('\n')
      for i in range(0,len(carr)):
        if carr[i].rfind("-monitor ")>-1:
          ip=carr[i].split(":")[1]
          port=carr[i].split(":")[2].split(',')[0]
          return [ip,port]
      for i in range(0,len(carr)):
        if carr[i].rfind("-chardev socket")>-1:
          if carr[i].find("host=")<0:
            return False
          ip=carr[i][(carr[i].find("host=")):]
          ip=ip[:ip.find(",")].replace("host=","")
          port=carr[i][(carr[i].find("port=")):]
          port=port[:port.find(",")].replace("port=","")
          return [ip,port]
        else:
          return False

    def loaddata(self):
      os.execv(sys.argv[0], sys.argv)

if '__main__' == __name__:
  window = MainWin()
  window.show_all()
  Gtk.main()

