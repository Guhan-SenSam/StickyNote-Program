
###This is a very simple stickynote program###

#Import kivy module related objects
from kivy.lang import Builder
from kivy.animation import Animation
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.modalview import ModalView

#Import KivyMD Related stuff
from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.card import MDCard
from kivymd.uix.button import MDRaisedButton
from kivymd.theming import ThemeManager
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDIconButton
from kivymd.uix.menu import MDDropdownMenu

#import other inbuilt modules
import random
from functools import partial
from datetime import date

#import mysql connector
import mysql.connector

#Initialize connection to myql database
mydb = mysql.connector.connect(
    host = "localhost",
    user = "Rahul",
    passwd = "123",
    database = "stickynotes"
    )

#create a database cursor
mycursor = mydb.cursor()


#This class holds the function that is called when the stickynotes have to be loaded
#for the current user
class NotesLoader():

    #Loads all the stickynotes data from current user table and passes as list.
    def notes_loader(self):
        mycursor.execute("SELECT * FROM " + current_user +';')
        data = mycursor.fetchall()
        sorted_data = sorted(data, key=lambda x: x[::-1])
        ui_builders.sticky_note_builder(self, sorted_data)

#This class holds all the functions that can be executed on a stickynote

class Operations():

    #This function opens the popup window for editing a stickynotes details
    def open_edit_mode(self, instance, *args):
        self.current_open=instance
        self.popup_card = MDCard(size = (200,200),
                                 size_hint = (None,None),
                                 md_bg_color = (0.1,0.1,0.1,1),
                                 radius = (20,20,20,20),
                                 )

        self.layout = ModalView(
            size=(500,500),
            size_hint=(None, None),
            background_color=(0, 0, 0, .9),
            background='atlas://data/images/defaulttheme/action_item'
            )
        self.layout.add_widget(self.popup_card)
        #Get the full info of a sticky note from database using id
        mycursor.execute("SELECT * FROM "+current_user+' WHERE id='+instance.name)
        note_content = mycursor.fetchone()

        #create an object self.details that holds the ui of the popup window
        self.details = Details()
        #Set the content of the sticky note
        self.details.ids.content.text = note_content[1]
        #set the color of the sticky note in the drop down menu based on value
        if note_content[3] == 1:
            self.details.ids.color.text = 'Dark Red'
        elif note_content[3] == 2:
            self.details.ids.color.text = 'Orange'
        elif note_content[3] == 3:
            self.details.ids.color.text = 'Yellow'
        elif note_content[3] == 4:
            self.details.ids.color.text = 'Green'
        elif note_content[3] == 5:
            self.details.ids.color.text = 'Peach'
        elif note_content[3] == 6:
            self.details.ids.color.text = 'Blue-Green'
        elif note_content[3] == 7:
            self.details.ids.color.text = 'Purple'
        elif note_content[3] == 8:
            self.details.ids.color.text = 'Light-Purple'
        elif note_content[3] == 9:
            self.details.ids.color.text = 'Pink'
        #bind save and delete functions to their respective buttons
        self.details.ids.save.bind(on_press = partial(Operations.save_changes,self,1))
        self.details.ids.delete.bind(on_press = partial(Operations.deletion,self))
        #define the elements for the menu of colors
        items = [{'text':'Dark Red'}, {'text':'Orange'}, {'text':'Yellow'}, {'text':'Green'},
                {'text':'peach'},{'text':'Blue-Green'},{'text':'Purple'},{'text':'Light-Purple'},{'text':'Pink'}]
        #define the menue
        self.details.menu = MDDropdownMenu(
            caller = self.details.ids.color,
            position="auto",
            width_mult=4,
            items = items
            )
        self.details.menu.bind(on_release = partial(Operations.set_color, self))
        #Add the ui to the popup card
        self.popup_card.add_widget(self.details)
        #open the popup card
        self.layout.open()
        #some animation for the opening of the popup card
        anim1 = Animation(opacity = 1, duration =.2,)
        anim2 = Animation(size = (500,500), duration =.2)
        anim1.start(self.popup_card)
        anim2.start(self.popup_card)


    #This function is called when a new sticky note is to be created,uses same
    #structure for ui for the edit view popup card
    def open_create_mode(self, instance):
        self.popup_card = MDCard(size = (200,200),
                                 size_hint = (None,None),
                                 md_bg_color = (0.1,0.1,0.1,1),
                                 radius = (20,20,20,20),
                                 )

        self.layout = ModalView(
            size=(500,500),
            size_hint=(None, None),
            background_color=(0, 0, 0, .9),
            background='atlas://data/images/defaulttheme/action_item'
            )
        self.layout.add_widget(self.popup_card)
        self.details = Details()
        self.details.remove_widget(self.details.ids.delete)
        items = [{'text':'Dark Red'}, {'text':'Orange'}, {'text':'Yellow'}, {'text':'Green'},
                {'text':'peach'},{'text':'Blue-Green'},{'text':'Purple'},{'text':'Light-Purple'},{'text':'Pink'}]
        self.details.menu = MDDropdownMenu(
            caller = self.details.ids.color,
            position="auto",
            width_mult=4,
            items = items
            )
        #bind a function that changes the text of the texfield when the user selects a color
        self.details.menu.bind(on_release = partial(Operations.set_color, self))
        self.popup_card.add_widget(self.details)
        self.layout.open()
        anim1 = Animation(opacity = 1, duration =.2,)
        anim2 = Animation(size = (500,500), duration =.2)
        anim1.start(self.popup_card)
        anim2.start(self.popup_card)
        #Bind the save sticky note function to the save button of the ui
        self.details.ids.save.bind(on_press=partial(Operations.save_changes,self, 2))


    #function that sets the text of the textfield after user selects color
    def set_color(self,menu,menu_item):
        self.details.ids.color.text = menu_item.text
        menu.dismiss()

    def save_changes(self,id,caller):
        #if we are just upadting info then delete original entry in db and insert new data
        if id == 1:
            name = self.current_open.name
            mycursor.execute("DELETE FROM "+current_user+' WHERE id='+ name)
            mydb.commit()
        #inserting new data as new row in db using a random id
        new_id = random.random()
        new_content = self.details.ids.content.text
        new_date = date.today().strftime('%Y-%m-%d')
        if self.details.ids.color.text == 'Dark Red':
            new_color = 1
        elif self.details.ids.color.text == 'Orange':
            new_color = 2
        elif self.details.ids.color.text == 'Yellow':
            new_color = 3
        elif self.details.ids.color.text == 'Green':
            new_color = 4
        elif self.details.ids.color.text == 'peach':
            new_color = 5
        elif self.details.ids.color.text == 'Blue-Green':
            new_color = 6
        elif self.details.ids.color.text == 'Purple':
            new_color = 7
        elif self.details.ids.color.text == 'Light-Purple':
            new_color = 8
        elif self.details.ids.color.text == 'Pink':
            new_color = 9

        #inserting data into table of db
        new_data = (new_id,new_content,new_date,new_color)
        mycursor.execute('INSERT INTO '+current_user+' VALUES(%s,%s,%s,%s)', new_data)
        mydb.commit()
        #close popup window
        self.layout.dismiss()
        Mainscreenvar = sm.get_screen("MainScreen")
        #clear mainview to rflect new changes to any stickynote
        Mainscreenvar.ids.container.clear_widgets()
        NotesLoader.notes_loader(self)


    #Function called when a sticky note needs to be deleted
    def deletion(self,caller):
        name = self.current_open.name
        mycursor.execute("DELETE FROM "+ current_user + " WHERE id= "+ name)
        mydb.commit()
        Mainscreenvar = sm.get_screen("MainScreen")
        Mainscreenvar.ids.container.clear_widgets()
        self.layout.dismiss()
        NotesLoader.notes_loader(self)


#This class holds all the functions that can be executed regarding user accounts
class user_menu_operations():

    #This function loads the basic ui for creating,editing and deleting user data
    def users_loader(self):
        #Create three buttons and bind their respective functions to them
        self.change = MDRaisedButton(text = 'Change account details')
        self.change.bind(on_press = partial(user_menu_operations.account_changer,self))
        self.add =  MDRaisedButton(text = 'Add New Account')
        self.add.bind(on_press = partial(user_menu_operations.new_user,self))
        self.remove = MDRaisedButton(text = 'Remove current user')
        self.remove.bind(on_press = partial(user_menu_operations.remover,self))
        Mainscreenvar = sm.get_screen("MainScreen")
        #add all the three buttons to the main user interface
        Mainscreenvar.ids.container.add_widget(self.change)
        Mainscreenvar.ids.container.add_widget(self.add)
        Mainscreenvar.ids.container.add_widget(self.remove)

    #This function displays the popup for changing details of an user
    def account_changer(self,caller):
        self.popup_card = MDCard(size = (400,400),
                                 size_hint = (None,None),
                                 md_bg_color = (0.1,0.1,0.1,1),
                                 radius = (20,20,20,20),
                                 )

        self.layout = ModalView(
            size=(500,500),
            size_hint=(None, None),
            background_color=(0, 0, 0, .9),
            background='atlas://data/images/defaulttheme/action_item'
            )
        self.layout.add_widget(self.popup_card)
        #Create an object that holds the main ui using the template User_details
        self.user_details = User_Details()
        #set the current logged in user's username and password
        self.user_details.ids.user_name.text = current_user
        self.user_details.ids.password.text = current_password
        #bind the save function to the save button from the ui
        self.user_details.ids.save.bind(on_press = partial(user_menu_operations.saver,self,1))
        self.popup_card.add_widget(self.user_details)
        #dispay the popup
        self.layout.open()


    #This function displays a popup that allows the user to create a new user account
    def new_user(self,caller):
        self.popup_card = MDCard(size = (400,400),
                                 size_hint = (None,None),
                                 md_bg_color = (0.1,0.1,0.1,1),
                                 radius = (20,20,20,20),
                                 )

        self.layout = ModalView(
            size=(500,500),
            size_hint=(None, None),
            background_color=(0, 0, 0, .9),
            background='atlas://data/images/defaulttheme/action_item'
            )
        self.layout.add_widget(self.popup_card)
        self.user_details = User_Details()
        self.user_details.ids.save.bind(on_press = partial(user_menu_operations.saver,self,2))
        self.popup_card.add_widget(self.user_details)
        self.layout.open()


    #This function saves any changes and any new user account details
    def saver(self,op_id,caller):
        data = (caller.parent.ids.user_name.text,caller.parent.ids.password.text)
        #if we are updating data we delete data that is already inside the table
        if op_id == 1:
            mycursor.execute("DELETE FROM users WHERE user_id = %s", (current_user,))
            mydb.commit()
        #we insert new values into the table
        mycursor.execute("INSERT INTO users VALUES(%s,%s)",data)
        mydb.commit()
        if op_id == 1:
            #if we are updating existing details we rename the table of notes with new user name
            mycursor.execute("ALTER TABLE "+ current_user + " RENAME TO " + caller.parent.ids.user_name.text)
            #clear the widgets on screen
            sm.get_screen("MainScreen").ids.container.clear_widgets()
            #reset the screen to the login screen
            sm.current = ('LoginScreen')

        else:
            #if new user is being added we create a new table in their name
            mycursor.execute("CREATE TABLE " + caller.parent.ids.user_name.text + "(id double, content text, date date, color int(2))")
        #close the popup window
        self.layout.dismiss()

    #This function is called when the current user account has to be deleted
    def remover(self,caller):
        #First we delete the user name from the user table
        mycursor.execute("DELETE FROM users WHERE user_id = %s", (current_user,))
        mydb.commit()
        #Then we drop the table that stores all the users sticky notes
        mycursor.execute("DROP TABLE "+ current_user)
        #clear screen
        sm.get_screen("MainScreen").ids.container.clear_widgets()
        #reset to login screen
        sm.current = 'LoginScreen'



#This class contains the functions to build the user interface element for a single remainder
class ui_builders():

    #This is a recursion function and runs for the amount of times there is sticky notes for an user
    #This was done so that each note card would have its own animation. all the sticky note info is passed
    #as a list sorted based on creation date
    def sticky_note_builder(self, data):
        #run only if there is any elements within the list data
        if len(data) > 0:
            Mainscreenvar = sm.get_screen("MainScreen")
            #set color
            if data[0][3] == 1:
                self.color = (100/256, 0, 0, 1)
            elif data[0][3] == 2:
                self.color = (244/256, 81/256, 30/256, 1)
            elif data[0][3] == 3:
                self.color = (246/256, 191/256, 38/256, 1)
            elif data[0][3] == 4:
                self.color = (11/256, 128/256, 67/256, 1)
            elif data[0][3] == 5:
                self.color = (251/256, 182/256, 121/256, 1)
            elif data[0][3] == 6:
                self.color = (3/256, 155/256, 129/256, 1)
            elif data[0][3] == 7:
                self.color = (63/256, 81/256, 181/256, 1)
            elif data[0][3] == 8:
                self.color = (121/256, 134/256, 203/256, 1)
            elif data[0][3] == 9:
                self.color = (172/256, 36/256, 127/256, 1)
            #make card
            self.card = MDCard(size_hint= (None,None),
                                size = (200,200),
                                name = str(data[0][0]),
                                md_bg_color = self.color,
                                opacity = 0,
                                elevation = 14,
                                radius = (20,20,20,20))
            self.card.bind(on_press = partial(Operations.open_edit_mode, self))
            self.layout = RelativeLayout(size = self.card.size)
            self.content = MDLabel(text=data[0][1],
                                  color=(0,0,0,1),
                                  padding=("20dp", "20dp"),
                                  font_size="25sp",
                                  font_style='Body1',
                                  valign = 'top',)
            self.edit = MDIconButton(icon = 'pencil',
                                     pos_hint = {'top':1})
            self.delete = MDIconButton(icon = 'delete',
                                     pos_hint = {'top':1, 'right':1})
            self.layout.add_widget(self.edit)
            self.layout.add_widget(self.delete)
            self.layout.add_widget(self.content)
            self.card.add_widget(self.layout)

            Mainscreenvar.ids.container.add_widget(self.card)

            anim1 = Animation(opacity = 1, duration = .3)
            #when the animation is complete we call the function recursor that repeats the entire process
            anim1.bind(on_complete = partial(ui_builders.recursor,self, data))
            anim1.start(self.card)
            #remove the first element of the list of data
            del data[0]

        else:
            pass

    #This function repeats the creation of stick note cards until recquired
    def recursor(self,data, *args):
        ui_builders.sticky_note_builder(self, data)



#This class holds the main login screen
class LoginScreen(Screen):

    #This function deals with login and displaying appropriate error meesages
    def login(self,user, password):
        mycursor.execute("SELECT user_id FROM users WHERE user_id =%s", (user,))
        self.user_data = mycursor.fetchone()
        if self.user_data == None:
            self.no_user = MDDialog(
                                    text = 'This user does not exist',
                                    radius=[20, 20, 20, 20],
                                    )
            self.no_user.open()
        else:
            mycursor.execute("SELECT password FROM users WHERE user_id =%s", (user,))
            self.password_data = mycursor.fetchone()
            if self.password_data[0] != password:
                self.wrong_passwd = MDDialog(
                                        text = 'Please enter the correct password',
                                        radius=[20, 20, 20, 20],
                                        )
                self.wrong_passwd.open()
            else:
                sm.current = "MainScreen"
                #set the global variables to the currently logged in user's details
                global current_user, current_password
                current_user = user
                current_password = password

                NotesLoader.notes_loader(self)

#This class deals with everything regarding the main screen along with the screen switcher
class MainScreen(Screen):

    def screen_switcher(self,caller,screen_number):
        global current_screen
        if current_screen == 1 and screen_number == 1:
            pass
        elif current_screen == 2 and screen_number == 1:
            sm.get_screen("MainScreen").ids.container.clear_widgets()
            current_screen = 1
            NotesLoader.notes_loader(self)

        elif current_screen == 1 and screen_number == 2:
            sm.get_screen("MainScreen").ids.container.clear_widgets()
            current_screen = 2
            user_menu_operations.users_loader(self)
        elif current_screen == 2 and screen_number == 2:
            pass


class Details(RelativeLayout):
    pass

class User_Details(RelativeLayout):
    pass

#define screenmanager to easily change screens and access variables globally
sm = ScreenManager()
current_user = None
current_password = None
current_screen = 1

#The main class of the program which compiles the app and enables it to display the uo
class Mainapp(MDApp):

    def rail_open(self, object):
        if object.parent.parent.ids.sidebar.rail_state == 'open':
            object.parent.parent.ids.sidebar.rail_state = 'close'
        else:
            object.parent.parent.ids.sidebar.rail_state = 'open'

    def build(self):
        Builder.load_file('stickynotes.kv')
        ThemeManager.theme_style = "Dark"
        sm.add_widget(LoginScreen(name = 'LoginScreen'))
        sm.add_widget(MainScreen(name='MainScreen'))
        sm.get_screen('MainScreen').ids.sidebar.on_action_button = partial(Operations.open_create_mode,self)
        return sm


#The single line of code that starts the entire program
Mainapp().run()
